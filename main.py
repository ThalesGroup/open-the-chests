# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from Dynamics.Environment import Environment
from Elements.Event import Event
from Elements.Pattern import Pattern


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # define patterns to be used for boxes
    instr1 = [Event("A", [0], 0, 5), Event("A", [0], 7, 12)]
    instr2 = [Event("B", [0], 4, 5), Event("B", [0], 6, 15)]

    pattern1 = Pattern(instr1, True)
    pattern2 = Pattern(instr2, True)
    env = Environment([pattern1, pattern2], True)
    for i in range(10):
        env.step([])


