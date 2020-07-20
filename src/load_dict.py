
with open("/usr/share/dict/words", "r") as words:
    en_dict = set(line.strip().capitalize() for line in words)

print("accedence" in en_dict)

