import unittest

import numpy as np

from src.openthechests.env.elements.Event import Event
from src.openthechests.env.elements.Generator import Generator
from src.openthechests.env.elements.Pattern import Pattern

instruction = [
    {'command': 'delay', 'parameters': 10},
    {'command': 'noise', 'parameters': 0},
    {'command': 'instantiate', 'parameters': ('A', {}, {'mu': 5, 'sigma': 2}), 'variable_name': 'distinct'},
    {'command': 'instantiate', 'parameters': ('E', {}, {'mu': 6, 'sigma': 2}), 'variable_name': 'e1'},
    {'command': 'instantiate', 'parameters': ('E', {}, {'mu': 8, 'sigma': 0}), 'variable_name': 'e2'},
    {'command': 'instantiate', 'parameters': ('C', {}, {'mu': 5, 'sigma': 1}), 'variable_name': 'c1'},
    {'command': 'met_by', 'parameters': ['e2', 'c1'], 'variable_name': 'e2', 'other': {}},
    {'command': 'during', 'parameters': ['e1', 'e2'], 'variable_name': 'e1', 'other': {}},
    {'command': 'after', 'parameters': ['distinct', 'e2'], 'variable_name': 'distinct',
     'other': {'gap_dist': {'mu': 4, 'sigma': 1}}}
]


class TestElements(unittest.TestCase):
    def testEvent(self):
        event = Event("A", {"color": "blue"}, 5, 10)
        shifted_forward = event.shifted(10)
        self.assertEqual([shifted_forward.start, shifted_forward.end], [15, 20])
        with self.assertRaises(AssertionError):
            shifted_backward = event.shifted(-10)
        self.assertEqual(event.shifted(-5).to_dict(),
                         {"e_type": "A",
                          "color": "blue",
                          "start": 0,
                          "end": 5,
                          "duration": 5})

    def testPattern(self):
        pattern = Pattern(instruction=instruction, id=0)
        self.assertEqual(pattern.get_timeout(), 10)
        self.assertEqual(pattern.get_noise(), 0)
        self.assertTrue(all(
            np.array([pattern.generate_timeout() for _ in range(1000)]) <= pattern.get_timeout()
        ))

    def testParser(self):
        pass

    def testGenerator(self):
        pass



if __name__ == '__main__':
    unittest.main()
