#!/usr/bin/env python3

import os
import base64
import sys

os.system("echo 'Это тестовый вредоносный код'")

encoded_cmd = "cHJpbnQoJ1Rlc3Q6IGV2YWwgdGhyb3VnaCBiYXNlNjQnKQ=="
decoded_cmd = base64.b64decode(encoded_cmd).decode('utf-8')
eval(decoded_cmd)

dynamic_code = "print('Динамически сгенерированный код')"
exec(dynamic_code)

try:
    import marshal
except ImportError:
    pass

high_entropy_string = "U28gc29ycnkgZm9yIHRoZSBjb25mdXNpb24uIFRoaXMgaXMganVzdCBhIHRlc3Q="

import urllib.request
urllib.request.urlopen("http://example.com")

with open("/tmp/test_taiga.txt", "w") as f:
    f.write("Тестовый файл создан Taiga")

print("Тестовый скрипт завершен (это легитимный код для демонстрации)")
