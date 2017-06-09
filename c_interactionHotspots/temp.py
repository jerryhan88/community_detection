from unicodedata import name
print {unichr(i) for i in range(32, 256) if 'SIGN' in name(unichr(i), '')}