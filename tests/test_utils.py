import unittest
from assistant.main import validate_alias, detect_shell

class TestTassUtils(unittest.TestCase):
    def test_validate_alias_valid(self):
        self.assertTrue(validate_alias("ask"))
        self.assertTrue(validate_alias("ai123"))
    
    def test_validate_alias_invalid_length(self):
        self.assertFalse(validate_alias("thisiswaytoolongforanalias"))
    
    def test_validate_alias_invalid_chars(self):
        self.assertFalse(validate_alias("ask!"))
        self.assertFalse(validate_alias("ai space"))

    def test_detect_shell_returns_string(self):
        shell = detect_shell()
        self.assertIsInstance(shell, str)
        self.assertTrue(len(shell) > 0)

if __name__ == '__main__':
    unittest.main()
