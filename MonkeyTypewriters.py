

import os, string, random

def MonkeyTypewriter(search):
    letters = string.ascii_uppercase + " "
    typed = ""
    search = search.upper()
    found = False

    while not found:
        char = random.choice(letters)
        typed = typed + char
        if typed[-(len(search)):] == search:
            found = True
    return len(typed)

search = "lua w"
for x in range(0, 10000):
    chars = MonkeyTypewriter(search)
    print(chars)
    break