init python in bleeper:
    from time import sleep
    from renpy.text.textsupport import TAG, TEXT, PARAGRAPH, DISPLAYABLE

    def screen_callback(who: str, what: str):
        if who is None and what == "":
            return

        cps_base = renpy.store.preferences.text_cps
        cps_fixed = None
        cps_mult = 1.0

        what_displayable = renpy.get_displayable("say", "what")
        tokens = what_displayable.tokenize(what_displayable.text)

        global segments
        segments = [[]]

        for kind, token in tokens:
            if kind == TEXT:
                wait = 1 / (cps_fixed or cps_base * cps_mult)
                for char in token:
                    if char.isalnum():
                        segments[-1].append(("o.wav" if who == "Azzy" else "a.wav", wait))
                    else:
                        segments[-1].append((None, wait))

            elif kind == TAG:
                if "=" in token:
                    tag, args = token.split("=", 1)
                else:
                    tag, args = token, None

                if tag == "w":
                    segments.append([])

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

        renpy.log((event, interact, type))

        global active
        active = False

        if event == "show_done":
            active = True
            renpy.invoke_in_thread(__play_segment)


    def __play_segment():
        for sound, wait in segments.pop(0):
            sleep(wait)

            if not active:
                return

            if sound is not None:
                renpy.sound.play(sound, "voice", tight=True)

define config.all_character_callbacks += [bleeper.character_callback]
define config.log = "config.log"
