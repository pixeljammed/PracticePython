### Milo Tek - 15/05/2025 - Tiktok Print ###
## Based off a TikTok I saw ages ago, which showed someone making their own print function in a cool way!

import string, time

def tiktokprint(text):
    text = text.upper()
    letters = " " + string.ascii_uppercase
    output = [""]*len(text)
    for x in range(len(text)):
        for letter in letters:
            time.sleep(0.05)
            output[x] = letter
            print(*output)
            if text[x] == output[x]:
                break
                
## Example
text = "I eat and devour babies"
tiktokprint(text)