# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import random

from Dynamics.Environment import Environment
from Dynamics.Parser import Parser
from Elements.Event import Event
from Elements.Pattern import Pattern


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # define patterns to be used for boxes

    all_event_types = ["A", "B", "C"]
    all_event_attributes = {"fg": ["red", "blue", "green"], "bg": ["red", "blue", "green"]}
    parser = Parser(all_event_types, all_event_attributes)

    instr1 = [{"command": "instantiate", "parameters": ("A", {"bg": "blue"}, (4, 2)), "variable_name": "a1"},
                {"command": "instantiate", "parameters": ("C", {"fg": "red"}, (10, 1)), "variable_name": "c1"},
                {"command": "after", "parameters": ("c1", "a1"), "variable_name": "c1", "gap_dist": (2, 1)},
                {"command": "instantiate", "parameters": ("C", {}, (4, 1)), "variable_name": "c2"},
                {"command": "during", "parameters": ("c2", "c1"), "variable_name": "c2"},
                {"command": "instantiate", "parameters": ("A",), "variable_name": "a2"},
                {"command": "met_by", "parameters": ("a2", "c1"), "variable_name": "c1"}]

    instr2 = [{"command": "instantiate", "parameters": ("B", {"bg": "blue"}, (4, 2)), "variable_name": "b1"},
              {"command": "instantiate", "parameters": ("B", {"fg": "red"}, (10, 1)), "variable_name": "b2"},
              {"command": "after", "parameters": ("b2", "b1"), "variable_name": "b2", "gap_dist": (2, 1)}]

    pattern1 = Pattern(parser, instr1, True, 5)
    pattern2 = Pattern(parser, instr2, True, 7)
    all_patterns = [pattern1, pattern2]

    env = Environment(patterns=all_patterns,
                      verbose=True,
                      types=all_event_types,
                      attributes=all_event_attributes)
    env.reset()
    done = False
    while not done:
        action = [random.randint(0, 1) for i in range(2)]
        reward, context, done = env.step(action)
