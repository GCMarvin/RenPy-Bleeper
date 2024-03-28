init python in bleeper:
    from threading import Timer
    from renpy.text.textsupport import TAG, TEXT, PARAGRAPH, DISPLAYABLE

    segments = []
    timers = []
    offset = 0.05 # Should be set to half of the length of the soundbits.

    def screen_callback(who: str, what: str):
        if who is None and what == "":
            return

        cps_base = renpy.store.preferences.text_cps
        cps_fixed = None
        cps_mult = 1.0

        what_displayable = renpy.get_displayable("say", "what")
        tokens = what_displayable.tokenize(what_displayable.text)

        segments.clear()
        segments.append([])
        delay = 0.0

        for kind, token in tokens:
            if kind == TEXT:
                for char in token:
                    delay += 1 / (cps_fixed or cps_base * cps_mult)
                    if char.isalnum():
                        segments[-1].append(("o.wav" if who == "Azzy" else "a.wav", delay - offset))

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
                raise ValueError(f"Token kind '{kind}' is not supported yet.")


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
define config.log = "config.log"
