# Ren'Py Blipper

Ren'Py has a [guide](https://www.renpy.org/wiki/renpy/doc/cookbook/Expanded_Text_Bleeps) on how to have characters make a blip sound while they're talking, similar to games like Ace Attorney. The results of this guide, however, are very limited. They only allow an infinite loop of the same sound to be played, it has lots of bugs in which the game doesn't stop playing the sound when it should, it's not easily configurable for many characters, or expandable for example to have each letter associated with its own sound file.

That's what this project aims to fix!

In short: A callback is added to the say screen, which uses the passed character and text to setup how and at which delays the sequence of letters should be played, since several text tags like the wait tag or the cps tag might modify this. Another character callback that is added to every character will then play these sequences every time the interaction is started.

## How To Use

1. Simply add [`blipper.rpy`](blipper.rpy) to your project.
2. Add the following to the end of your say screen definition (most likely found in `screens.rpy`):

   ```renpy
   on "show" action Function(blipper.screen_callback, _update_screens=False)
   ```

3. Add a `what_voice` parameter to your character definition that is the name of the audio file in your project which should be played for each character. For example, if you have the blip for Eileen stored in `eileen_blip.wav`, the definition should look similar to this:

   ```renpy
   define eileen = Character("Eileen", what_voice="eileen_blip.wav")
   ```

   You may also provide a file name including an asterisk, in which case different files will be used for each letter, replacing the asterisk in the filename. For example, if Eileen's blip sound for the letter "a" is named "eileen_a.wav", for the letter "b" "eileen_b.wav", etc., it should look like this:

   ```renpy
   define eileen = Character("Eileen", what_voice="eileen_*.wav")
   ```
