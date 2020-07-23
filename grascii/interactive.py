
import questionary
from questionary.prompts.common import Choice, Separator

from grascii import regen
from grascii.search import flatten_tree, interpretationToString, get_unique_interpretations, perform_search, parse_grascii

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

def choose_interpretation(interpretations):
    if len(interpretations) == 1:
        # print()
        # print("Found 1 possible interpretation")
        # print("Beginning search")
        return 0
    else:
        # print("Interpretations: ", len(interpretations))
        # print()
        # print("0: all")
        choices = [Choice(title="all", value=0)]
        i = 1
        for interp in interpretations:
            choices.append(Choice(title=interpretationToString(interp), value=i))
            i += 1
        return questionary.select("Choose an interpretation to use in the search:", choices).ask()

def run_interactive(parser, args):
    previous_search = None

    while True:
        action = questionary.select("What would you like to do?",
                ["New Search",
                 Choice("Modify Search", disabled=not previous_search),
                 # "Modify Search",
                 "Edit Settings",
                 "Exit"]).ask()

        if action is None or action == "Exit":
            exit()
        elif action == "New Search":
            previous_search = interactive_search(parser, args)
        elif action == "Modify Search":
            previous_search = interactive_search(parser, args, previous_search)
        elif action == "Edit Settings":
            # print("previous search:", previous_search)
            while True:
                action = questionary.select("Search Settings",
                        [Choice(title="Uncertainty [{}]".format(args.uncertainty), value=1),
                         Choice(title="Search Mode [{}]".format(args.search_mode.value), value=2),
                         Choice(title="Annotation Mode [{}]".format(args.annotation_mode.value), value=3),
                         Choice(title="Aspirate Mode [{}]".format(args.aspirate_mode.value), value=4),
                         Choice(title="Disjoiner Mode [{}]".format(args.disjoiner_mode.value), value=5),
                         Choice(title="Fix First [{}]".format(args.fix_first), value=6),
                         "Back"]
                        ).ask()

                if action is None or action == "Back":
                    break
                elif action == 1:
                    change_arg(args, "uncertainty", range(3), display_name="Uncertainty")
                elif action == 2:
                    change_arg(args, "search_mode", list(regen.SearchMode), convert=get_enum_value, display_name="Search mode")
                elif action == 3:
                    change_arg(args, "annotation_mode", list(regen.Strictness), convert=get_enum_value, display_name="Annotation mode")
                elif action == 4:
                    change_arg(args, "aspirate_mode", list(regen.Strictness), convert=get_enum_value, display_name="Aspirate mode")
                elif action == 5:
                    change_arg(args, "disjoiner_mode", list(regen.Strictness), convert=get_enum_value, display_name="Disjoiner mode")
                elif action == 6:
                    change_arg(args, "fix_first", [True, False], display_name="Fix First")
                                       

    # action = interactive.get_choice("", ["exit", 
        # "edit search",
        # "perform another search"])

    # if action == 1:
        # pass
    # elif action == 2:
        # interactive_search(parser, args)

def get_enum_value(enum):
    return enum.value

def change_arg(args, arg_name, options, display_name=None, convert=str):
    choices = list()
    for option in options:
        selected = getattr(args, arg_name) == option
        choices.append(Choice(title=convert(option), value=option, checked=selected))
    title = display_name if display_name else "Set " + arg_name
    setting = questionary.select(title, choices).ask()
    if setting is not None:
        setattr(args, arg_name, setting)

def interactive_search(parser, args, previous=None):
    search, tree = get_grascii_search(parser, previous)
    if search is None:
        return previous
    parses = flatten_tree(tree)
    display_interpretations = get_unique_interpretations(parses)
    interpretations = list(display_interpretations.values())
    assert len(interpretations)
    index = choose_interpretation(interpretations)
    builder = regen.RegexBuilder(args.uncertainty, args.search_mode, args.fix_first, args.annotation_mode, args.aspirate_mode, args.disjoiner_mode)
    if index == 0:
        interps = interpretations
    else:
        interps = interpretations[index - 1: index]
    patterns = builder.generate_patterns(interps)
    starting_letters = builder.get_starting_letters(interps)
    results = perform_search(patterns, starting_letters, args.dict_path)
    count = 0
    display_all = False
    for result in results:
        count += 1
        if not display_all:
            # action = input(result + "e(x)it, (d)isplay all, (e)nd search: ")
            action = questionary.select("Search Results",
                    ["Next",
                     "Display All",
                     "End Search" 
                    ]).ask()
        print(result.strip())
        if action is None or action == "End Search":
            break
        elif action == "Display All":
            display_all = True
        
    print("Results:", count)
    print()
    return search
        
def get_grascii_search(parser, previous):
    while True:
        # search = input("Enter search: ").upper()
        if previous:
            search = questionary.text("Enter Search:",
                    default=previous).ask()
        else:
            search = questionary.text("Enter Search:").ask()
        if search is None:
            return search, None
        if search == "":
            continue
        search = search.upper()
        result = parse_grascii(parser, search)
        if not result:
            previous = search
            continue
        return search, result
