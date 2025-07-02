def print_completion_summary(files: list[str], missing_time: list[str], missing_loc: list[str]):
    if len(files) != 0:
        print("\nThe following files could not be stamped: ")
        for path in files:
            print(path)
    if len(missing_time) != 0:
        print("\nThe following files are missing their time, but a photo with stamped location has been created: ")
        for path in missing_time:
            print(path)
    if len(missing_loc) != 0:
        print("\nThe following files are missing their location, but a photo with stamped time has been created: ")
        for path in missing_loc:
            print(path)

def getYesNo(question_text: str) -> bool:
    answer = 'q'
    while(answer not in ['y', 'n', 'yes', 'no']):
        answer = input(f"{question_text} (y/n) ").lower()
    if answer in ['y', 'yes']:
        return True
    return False

def manual_mode(files: list[str], missing_time: list[str], missing_loc: list[str]):
    print("MANUAL FIX is WIP")
    
