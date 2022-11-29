import unittest

import numpy as np

from src.openthechests.env.elements.Event import Event
from src.openthechests.env.elements.Generator import Generator
from src.openthechests.env.elements.Parser import Parser
from src.openthechests.env.elements.Pattern import Pattern

instruction = [
    {'command': 'delay', 'parameters': 10},
    {'command': 'noise', 'parameters': 0},
    {'command': 'instantiate', 'parameters': ('A', {}, {'mu': 5, 'sigma': 2}), 'variable_name': 'distinct'},
    {'command': 'instantiate', 'parameters': ('B', {}, {'mu': 6, 'sigma': 2}), 'variable_name': 'e1'},
    {'command': 'instantiate', 'parameters': ('B', {}, {'mu': 8, 'sigma': 0}), 'variable_name': 'e2'},
    {'command': 'instantiate', 'parameters': ('A', {}, {'mu': 5, 'sigma': 1}), 'variable_name': 'c1'},
    {'command': 'met_by', 'parameters': ['e2', 'c1'], 'variable_name': 'e2', 'other': {}},
    {'command': 'during', 'parameters': ['e1', 'e2'], 'variable_name': 'e1', 'other': {}},
    {'command': 'after', 'parameters': ['distinct', 'e2'], 'variable_name': 'distinct',
     'other': {'gap_dist': {'mu': 4, 'sigma': 1}}}
]

simple_instruction = [
    {'command': 'instantiate', 'parameters': ('A', {}, {'mu': 5, 'sigma': 2}), 'variable_name': 'distinct'},
]

unknown_instruction = [
    {'command': 'instantiate', 'parameters': ('?', {}, {'mu': 5, 'sigma': 2}), 'variable_name': 'distinct'},
]

all_event_types = ['A', 'B']
all_event_attributes = {'fg': ['red', 'blue'],
                        'bg': ['red', 'blue']}
all_noise_types = ['G']
all_noise_attributes = {'fg': ['yellow'], 'bg': ['yellow']}


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

    def testBox(self):
        pass

    def testParser(self):
        parser = Parser(all_event_types=all_event_types,
                        all_noise_types=all_noise_types,
                        all_event_attributes=all_event_attributes,
                        all_noise_attributes=all_noise_attributes)
        noise = parser.make_noise(before=10)
        self.assertTrue(noise.get_type() in all_noise_types)
        self.assertTrue(all(
            [noise.get_attribute_val(attr_name) in all_noise_attributes[attr_name]
             for attr_name in all_noise_attributes.keys()]
        ))
        self.assertTrue(noise.end <= 10)

        labelled_noise = parser.event_to_labelled(noise)
        self.assertEqual(labelled_noise.start, noise.start)
        self.assertEqual(labelled_noise.end, noise.end)
        self.assertEqual(labelled_noise.get_type(), 2)
        self.assertEqual(labelled_noise.get_attribute_val("fg"), 2)
        self.assertEqual(labelled_noise.get_attribute_val("bg"), 2)

        event_instruction = instruction[2:]
        instantiated_pattern = parser.instantiate_pattern(instructions=event_instruction)
        self.assertEqual(len(instantiated_pattern),
                         len([event_instr for event_instr in instruction
                              if event_instr["command"] == "instantiate"]))
        with self.assertRaises(AssertionError):
            shifted_backward = parser.instantiate_pattern(instructions=unknown_instruction)

        single_event_pattern = parser.instantiate_pattern(simple_instruction)
        self.assertEqual(simple_instruction[0]["parameters"][0], single_event_pattern[0].type)
        self.assertTrue(all(
            [attr in all_event_attributes[attr_name] for attr_name, attr in single_event_pattern[0].attributes.items()]
        ))

    def testGenerator(self):
        pass


if __name__ == '__main__':
    unittest.main()
