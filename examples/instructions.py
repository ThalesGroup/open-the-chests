"""
Instructions are usually defined using a YAML file, however it is possible to define them via a dictionary of commands.
"""


instructions = [
    [
        {'command': 'delay', 'parameters': 10},
        {'command': 'noise', 'parameters': 0},
        {'command': 'instantiate', 'parameters': ('A', {'bg': 'blue', 'fg': 'blue'}, {'mu': 5, 'sigma': 2}), 'variable_name': 'distinct'},
        {'command': 'instantiate', 'parameters': ('E', {'bg': 'pink', 'fg': 'green'}, {'mu': 6, 'sigma': 2}), 'variable_name': 'e1'},
        {'command': 'instantiate', 'parameters': ('E', {'bg': 'red', 'fg': 'green'}, {'mu': 8, 'sigma': 0}), 'variable_name': 'e2'},
        {'command': 'instantiate', 'parameters': ('C', {'bg': 'orange', 'fg': 'red'}, {'mu': 5, 'sigma': 1}), 'variable_name': 'c1'},
        {'command': 'met_by', 'parameters': ['e2', 'c1'], 'variable_name': 'e2', 'other': {}},
        {'command': 'during', 'parameters': ['e1', 'e2'], 'variable_name': 'e1', 'other': {}},
        {'command': 'after', 'parameters': ['distinct', 'e2'], 'variable_name': 'distinct', 'other': {'gap_dist': {'mu': 4, 'sigma': 1}}}
    ],
    [
        {'command': 'delay', 'parameters': 2},
        {'command': 'noise', 'parameters': 0},
        {'command': 'instantiate', 'parameters': ('B', {'bg': 'red', 'fg': 'red'}, {'mu': 6, 'sigma': 2}), 'variable_name': 'distinct'},
        {'command': 'instantiate', 'parameters': ('E', {'bg': 'orange', 'fg': 'red'}, {'mu': 7, 'sigma': 4}), 'variable_name': 'e1'},
        {'command': 'instantiate', 'parameters': ('D', {'bg': 'blue', 'fg': 'green'}, {'mu': 3, 'sigma': 0}), 'variable_name': 'd1'},
        {'command': 'met_by', 'parameters': ['e1', 'd1'], 'variable_name': 'e1', 'other': {}},
        {'command': 'after', 'parameters': ['distinct', 'e1'], 'variable_name': 'distinct', 'other': {'gap_dist': {'mu': 2, 'sigma': 1}}}
    ],
    [
        {'command': 'delay', 'parameters': 15},
        {'command': 'noise', 'parameters': 0},
        {'command': 'instantiate', 'parameters': ('C', {'bg': 'pink', 'fg': 'pink'}, {'mu': 4, 'sigma': 2}), 'variable_name': 'distinct'},
        {'command': 'instantiate', 'parameters': ('D', {'bg': 'red', 'fg': 'green'}, {'mu': 5, 'sigma': 1}), 'variable_name': 'd1'},
        {'command': 'instantiate', 'parameters': ('D', {'bg': 'blue', 'fg': 'orange'}, {'mu': 10, 'sigma': 1}), 'variable_name': 'd2'},
        {'command': 'during', 'parameters': ['d1', 'd2'], 'variable_name': 'd1', 'other': {}},
        {'command': 'after', 'parameters': ['distinct', 'd2'], 'variable_name': 'distinct', 'other': {'gap_dist': {'mu': 2, 'sigma': 1}}}
    ]
]

