#!/usr/bin/env python3
"""
Run the credits migration to fix existing users
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import the migration function
from api.migrations.fix_initial_credits import fix_initial_credits

if __name__ == "__main__":
    print("Running credits migration...")
    success = fix_initial_credits()
    if success:
        print("Migration completed successfully!")
    else:
        print("Migration failed!")
        sys.exit(1)
