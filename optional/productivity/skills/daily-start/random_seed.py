#!/usr/bin/env python3
"""Generate two random 3-letter sequences for daily art + quote seeds."""
import random
import string
import json

alphabet = string.ascii_lowercase

# Pick two independent random starting positions (a-x, so 3 sequential fit)
art_start = random.randint(0, 23)
quote_start = random.randint(0, 23)

art_letters = [alphabet[art_start + i] for i in range(3)]
quote_letters = [alphabet[quote_start + i] for i in range(3)]

print(json.dumps({
    "art_letters": art_letters,
    "quote_letters": quote_letters,
}))
