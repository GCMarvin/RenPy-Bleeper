init python in bleeper:
    from threading import Timer
    from renpy.text.textsupport import TAG, TEXT #, PARAGRAPH, DISPLAYABLE

    segments = []
    timers = []
    offset = 0.05 # Should be set to half of the length of the soundbits. Can this be done dynamically?

    def screen_callback():
        """
        Set this function as the "on show" callback for the say screen
        by inserting the following line into the say screen definition:
            on "show" action Function(bleeper.screen_callback, _update_screens = False)

        Give a character a voice by including
            who_voice="audiofile"
        in the character definition. The audio file should be a sound file in the game's audio folder.
        If you want different letters to use different audio files, the audio file argument should be
        named with an asterisk in place of the letter.

        For example, if the character's voice for the letter "a" is "char_a.wav",
        for the letter "b" is "char_b.wav", etc., the argument should be "char_*.wav".
        """
        who_props = renpy.get_displayable_properties("who", "say")
        what_display = renpy.get_displayable("say", "what")
        tokens = what_display.tokenize(what_display.text)

        if "voice" not in who_props:
            return

        voice = who_props["voice"]

        cps_base = renpy.store.preferences.text_cps
        cps_fixed = None
        cps_mult = 1.0

        segments.clear()
        segments.append([])
        delay = 0.0

        for kind, token in tokens:
            if kind == TEXT:
                for char in token:
                    delay += 1 / (cps_fixed or cps_base * cps_mult)

                    if char.isalnum():
                        sound = voice.replace("*", char.lower())
                        segments[-1].append((sound, delay - offset))

            elif kind == TAG:
                if "=" in token:
                    tag, args = token.split("=", 1)
                else:
                    tag, args = token, None

                if tag == "w":
                    segments.append([])
                    delay = 0.0

                elif tag == "cps":
                    if args[0] == "*":
                        cps_mult = float(args[1:])
                    else:
                        cps_fixed = float(args)

                elif tag == "/cps":
                    cps_fixed = None
                    cps_mult = 1.0

            else:
                raise ValueError(f"Token kind '{kind}' is not supported yet. Better get to work!")


    def character_callback(event: str, interact: bool, type: str):
        if not interact or type != "say":
            return

        for timer in timers:
            timer.cancel()
        timers.clear()

        if event == "show_done":
            for sound, delay in segments.pop(0):
                if sound is not None:
                    timer = Timer(delay, renpy.sound.play, (sound, "voice"), {"tight": True})
                    timer.daemon = True
                    timers.append(timer)
                    timer.start()


define config.all_character_callbacks += [bleeper.character_callback]
