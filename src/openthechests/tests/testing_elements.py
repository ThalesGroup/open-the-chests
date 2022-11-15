import unittest

from src.openthechests.env.elements.Event import Event


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
                          "start" : 0,
                          "end": 5,
                          "duration": 5})


if __name__ == '__main__':
    unittest.main()

