### Milo Tek - 18/05/2025 - Typewriter
## Crap typewriter fx I loved when I was 14

import os, time

def typewriter(text):
    for x in range(len(text)):
        print(text[x], end="", flush=True)
        time.sleep(0.05)
    print("") # Line break

## Example
typewriter("Google pls hire me 4 apprenticeship :3")
time.sleep(1)
typewriter("I'm super handsome... it's the truth!")
time.sleep(1)
typewriter("ig: @milo.tek yall come follow me fr ;)")