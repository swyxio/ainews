import json
from typing import Dict, Any, List
from datetime import datetime

def seed_objects(db):

    print("Seeding DB Objects")
  
    #db = sqlite_utils.Database('./data/ainews.db')

    user_count = next(db.query("SELECT count(*) FROM user"))['count(*)']
    if user_count == 0:
    
        with open('./seed_data/seed.jsonl', 'r') as file:
            for line in file:
                if not line.strip():
                    print("Encountered an empty line, skipping...")
                    continue
                obj = json.loads(line)
                obj_type = obj.pop('table')  # Remove and ge
                print(f"Seeding {obj_type} with values of {obj}")
                db.table(obj_type).insert(obj)

 