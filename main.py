# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from Dynamics.Environment import Environment
from Elements.Pattern import Pattern


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # define patterns to be used for boxes
    patterns = [Pattern(["A"], True), Pattern(["B"], True), Pattern(["C"], True)]
    env = Environment(patterns, True)
    for i in range(10):
        env.step([])


