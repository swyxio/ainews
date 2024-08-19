import json
import os
from typing import Dict, Any, List
from datetime import datetime
from dotenv import load_dotenv

def seed_objects(sqlite_db_path, db):
    load_dotenv(override=True)

    user_count = next(db.query("SELECT count(*) FROM user"))['count(*)']
    if user_count == 0:
        # Check if RUN_SEED_FILE_GENERATOR is set to true in the .env file
        run_seed_generator = os.getenv('RUN_SEED_FILE_GENERATOR', 'false').lower() == 'true'

        if run_seed_generator:
            print("Generating new seed file...")
            from seed_data.seed_generator import main as generate_seed
            generate_seed()
            print("New seed file generated.")

        seed_file = os.getenv('SEED_FILE', './seed_data/seed.jsonl')
        print(f"Seeding DB Objects from {seed_file} to {sqlite_db_path}")
    
        with open(seed_file, 'r') as file:
            for line in file:
                if not line.strip():
                    print("Encountered an empty line, skipping...")
                    continue
                try:
                    obj = json.loads(line)
                    obj_type = obj.pop('table')  # Remove and get the table name
                    print(f"Seeding {obj_type} with values of {obj}")
                    db.table(obj_type).insert(obj)
                except Exception as e:
                    print(f"Error processing line: {line}")
                    raise e
    else:
        print(f"Existing users of count {user_count} found in db.  Skipping seeding.")