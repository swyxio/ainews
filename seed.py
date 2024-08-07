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
                try:
                    obj = json.loads(line)
                    obj_type = obj.pop('table')  # Remove and get the table name
                    print(f"Seeding {obj_type} with values of {obj}")
                    db.table(obj_type).insert(obj)
                except Exception as e:
                    print(f"Error processing line: {line}")
                    raise e
            

 