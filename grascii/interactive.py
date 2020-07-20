

def get_choice(prompt, choices):
    for i, choice in enumerate(choices):
        print(str(i) + ":", choice)

    while True:
        try:
            index = int(input(prompt))
            if index >= 0 and index < len(choices):
                return index
        except ValueError:
            continue
