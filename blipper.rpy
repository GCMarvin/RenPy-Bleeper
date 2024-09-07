init python in blipper:
    from threading import Timer
    from renpy.text.textsupport import TAG, TEXT

    renpy.music.register_channel(name="blips", mixer="voice", file_prefix="blips/")

    segments = []
    timers = []
    spacing = 0.040        # The expected average duration of blips in seconds. TODO: Calculate this dynamically.
    offset = -spacing / 2  # Offset to play the sound a bit earlier, so it's at its peak when the character is shown.

    def screen_callback() -> None:
        """
        Set this function as the "on show" callback for the say screen
        by inserting the following line into the say screen definition:
            on "show" action Function(blipper.screen_callback, _update_screens=False)

        Give a character a voice by including
            what_voice="audiofile.wav"
        in the character definition. The audio file should be a sound file in a "blips" folder in the
        game's audio folder. If you want different letters to use different audio files, the audio file
        argument should be named with an asterisk in place of the letter.

        For example, if the character's voice for the letter "a" is "char_a.wav",
        for the letter "b" is "char_b.wav", etc., the argument should be "char_*.wav".
        """
        # Get the currently displaying text and its properties.
        # The text is tokenized using RenPy's included tokenizer.
        what_props = renpy.get_displayable_properties("what", "say")
        what_display = renpy.get_displayable("say", "what")
        tokens = what_display.tokenize(what_display.text)

        voice = what_props.get("voice", None)

        cps_base = renpy.store.preferences.text_cps
        cps_fixed = None
        cps_mult = 1.0

        if (
            renpy.is_skipping()  # Return early if the game is currently skipping text,
            or cps_base == 0     # or the text speed is set to instant,
            or not voice         # or the character doesn't have a voice.
        ):
            return

        segments.clear()
        segments.append([])
        delay = 0.0

        # Iterate over the tokens and create a list of segments with the appropriate sound files and delays.
        for kind, token in tokens:
            # If the token is text, iterate over each character and add the sound file to the segment.
            # The delay is calculated based on the character per second rate.
            if kind == TEXT:
                for char in token:
                    delay += 1 / (cps_fixed or cps_base * cps_mult)

                    if char.isalnum():
                        sound = voice.replace("*", char.lower())
                        segments[-1].append((sound, delay + offset))

            # If the token is a tag, check if it's a tag that influences character speed or segment count.
            elif kind == TAG:
                if "=" in token:
                    tag, args = token.split("=", 1)
                else:
                    tag, args = token, None

                # If the tag is a wait tag, add a new segment, as the wait tag will trigger a new character callback.
                if tag == "w":
                    segments.append([])
                    delay = 0.0

                # If the tag is a cps tag, adjust the character per second rate.
                elif tag == "cps":
                    if args[0] == "*":
                        cps_mult = float(args[1:])
                    else:
                        cps_fixed = float(args)

                # If the tag is a closing cps tag, reset the character per second rate.
                elif tag == "/cps":
                    cps_fixed = None
                    cps_mult = 1.0

    def play_blip(sound: str) -> None:
        if not renpy.music.get_playing("blips"):
            renpy.sound.play(sound, "blips")

    def character_callback(event: str, interact: bool, type: str, what: str, **__) -> None:
        # Having the callback triggered in any case means that the previous text is
        # no longer available. Thus, all remaining timers should be cancelled.
        for timer in timers:
            timer.cancel()
        timers.clear()

        # If the event is non-interactive, or the type isn't say, return early.
        if not interact or type != "say":
            return

        # If the event is "show_done", meaning the text is currently in the process of
        # being shown, and segments exist, set the timers to play the sound files.
        if event == "show_done" and segments:
            for sound, delay in segments.pop(0):
                timer = Timer(delay, play_blip, (sound,))
                timer.daemon = True
                timers.append(timer)
                timer.start()

# Add the blipper callback to all characters.
define config.all_character_callbacks += [blipper.character_callback]
