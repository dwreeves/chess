from .test_game import TestGame
from .test_display import TestDisplay
from .test_grid import TestGrid

if __name__ == '__main__':
    import unittest
    suite = unittest.TestSuite()
    suite.addTest(TestGame())
    suite.addTest(TestDisplay())
    suite.addTest(TestGrid())
    unittest.run()
