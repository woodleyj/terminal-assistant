import unittest
import os
import json
from pathlib import Path
from assistant.main import (
    get_max_memory, 
    save_memory, 
    load_memory, 
    get_user_aliases,
    add_user_alias,
    remove_user_alias,
    ENV_FILE,
    MEMORY_FILE
)

class TestTassLogic(unittest.TestCase):
    def setUp(self):
        # Backup existing env and memory if they exist
        self.env_backup = None
        if ENV_FILE.exists():
            self.env_backup = ENV_FILE.read_text()
            ENV_FILE.unlink()
        
        self.mem_backup = None
        if MEMORY_FILE.exists():
            self.mem_backup = MEMORY_FILE.read_text()
            MEMORY_FILE.unlink()

        # Clear os.environ to ensure no leaks from local .env
        for key in ["TASS_MEMORY_LIMIT", "TASS_USER_ALIASES", "GEMINI_TASS_API_KEY", "TASS_SETUP_COMPLETE"]:
            if key in os.environ:
                del os.environ[key]

    def tearDown(self):
        # Restore backups
        if self.env_backup is not None:
            ENV_FILE.write_text(self.env_backup)
        elif ENV_FILE.exists():
            ENV_FILE.unlink()

        if self.mem_backup is not None:
            MEMORY_FILE.write_text(self.mem_backup)
        elif MEMORY_FILE.exists():
            MEMORY_FILE.unlink()

    def test_memory_limit_pruning(self):
        # Force a small limit for testing
        with open(ENV_FILE, "w") as f:
            f.write("TASS_MEMORY_LIMIT=2\n")
        
        # Add 3 items
        save_memory("q1", "r1")
        save_memory("q2", "r2")
        save_memory("q3", "r3")
        
        mem = load_memory()
        self.assertEqual(len(mem), 2)
        self.assertEqual(mem[0]["query"], "q2")
        self.assertEqual(mem[1]["query"], "q3")

    def test_alias_management(self):
        # Start fresh
        self.assertEqual(get_user_aliases(), [])
        
        # Add valid alias
        self.assertTrue(add_user_alias("tester"))
        self.assertIn("tester", get_user_aliases())
        
        # Add duplicate
        self.assertFalse(add_user_alias("tester"))
        
        # Remove alias
        self.assertTrue(remove_user_alias("tester"))
        self.assertNotIn("tester", get_user_aliases())

    def test_max_memory_default(self):
        # Should default to 5 if not set or invalid
        self.assertEqual(get_max_memory(), 5)
        
        with open(ENV_FILE, "w") as f:
            f.write("TASS_MEMORY_LIMIT=invalid\n")
        self.assertEqual(get_max_memory(), 5)

if __name__ == '__main__':
    unittest.main()
