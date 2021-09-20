# Test script to generate labels

import random
import base64

for i in range(100):
    s = random.randint(0, 2 ** 20 - 1).to_bytes(5, 'big')
    l = base64.b32encode(s)[4:].decode()
    print(l)