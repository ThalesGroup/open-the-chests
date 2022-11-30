import unittest

from src.openthechests.env.OpenTheChests import OpenTheChests
from src.openthechests.env.elements.Event import Event
from src.openthechests.env.utils.helper_functions import bug_print


def simple_instruction_of_type(type):
    return [{'command': 'delay', 'parameters': 10},
            {'command': 'noise', 'parameters': 0},
            {'command': 'instantiate', 'parameters': (type, {}, {'mu': 5, 'sigma': 2}), 'variable_name': 'distinct'}
            ]


all_event_types = ['A', 'B']
all_event_attributes = {'fg': ['red', 'blue'],
                        'bg': ['red', 'blue']}
all_noise_types = ['G']
all_noise_attributes = {'fg': ['yellow'], 'bg': ['yellow']}


# TODO: priority 3 make a list of risky scenarios and test

class TestElements(unittest.TestCase):

    def setUp(self):
        self.one_event_env = OpenTheChests(instructions=[simple_instruction_of_type(e_type)
                                                         for e_type in all_event_types],
                                           all_event_types=all_event_types,
                                           all_event_attributes=all_event_attributes,
                                           all_noise_types=all_noise_types,
                                           all_noise_attributes=all_noise_attributes,
                                           verbose=False)

    def testReset(self):
        obs = self.one_event_env.reset()
        box_info, event_info = obs["state"], obs["context"]
        self.assertFalse(any(box_info["open"]))
        self.assertIsInstance(event_info, Event)
        self.assertEqual(event_info.end, self.one_event_env._time)

    def testOneStep(self):
        self.one_event_env.reset()
        obs, reward, done, info = self.one_event_env.step([1, 1])
        box_info, event_info = obs["state"], obs["context"]
        self.assertEqual(0, reward)
        self.assertTrue(any(box_info["open"]))
        self.assertFalse(all(box_info["active"]))
        self.assertFalse(done)

    def testConstantButtonPush(self):
        obs0 = self.one_event_env.reset()
        box_info0, event_info0 = obs0["state"], obs0["context"]
        obs1, reward1, done1, info1 = self.one_event_env.step([1, 1])
        box_info1, event_info1 = obs1["state"], obs1["context"]
        obs2, reward2, done2, info2 = self.one_event_env.step([1, 1])
        box_info2, event_info2 = obs2["state"], obs2["context"]
        self.assertFalse(done1)
        self.assertTrue(done2)
        seen_types = list(map(lambda labelled_event:
                              self.one_event_env.parser.labelled_to_event(labelled_event).get_type(),
                              [event_info0, event_info1, event_info2]))

        self.assertTrue(all(
            [e_type in seen_types for e_type in all_event_types]
        ))
