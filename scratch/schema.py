import sqlite3

def get_table_schema(cursor, table_name):
    cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}';")
    return cursor.fetchone()[0]

def get_foreign_keys(cursor, table_name):
    cursor.execute(f"PRAGMA foreign_key_list({table_name});")
    return cursor.fetchall()

def add_foreign_keys_to_schema(schema, foreign_keys):
    if not foreign_keys:
        return schema

    # Split schema into lines and prepare for modification
    schema_lines = schema.strip().split('\n')
    # Remove the last closing parenthesis
    schema_lines[-1] = schema_lines[-1].rstrip(')')
    
    # Add foreign key constraints
    for fk in foreign_keys:
        # fk format: (id, seq, table, from, to, on_update, on_delete, match)
        constraint = f"  FOREIGN KEY ({fk[3]}) REFERENCES {fk[2]} ({fk[4]})"
        if fk[5] != "NO ACTION":
            constraint += f" ON UPDATE {fk[5]}"
        if fk[6] != "NO ACTION":
            constraint += f" ON DELETE {fk[6]}"
        schema_lines.append(f",\n{constraint}")
    
    # Close the statement
    schema_lines.append("\n);")
    
    return '\n'.join(schema_lines)

def pretty_print_create_statement(schema):
    # Split schema into lines for pretty printing
    schema_lines = schema.split('\n')
    pretty_lines = []

    # First line is the CREATE TABLE line
    pretty_lines.append(schema_lines[0])
    
    # Process the rest of the lines with proper indentation
    for line in schema_lines[1:]:
        # Add indentation for table columns and constraints
        if line.strip().startswith('('):
            pretty_lines.append("(\n    " + line.strip()[1:])
        elif line.strip().startswith(')'):
            pretty_lines.append("\n" + line.strip())
        else:
            pretty_lines.append("    " + line.strip())
    
    return '\n'.join(pretty_lines)

def main():
    db_file = './data/ainews.db'
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Get the list of all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    # Generate and print the complete CREATE TABLE statements
    for table in tables:
        table_name = table[0]
        print(f"-- Schema for table: {table_name}")

        # Get the schema without foreign keys
        schema = get_table_schema(cursor, table_name)

        # Get the foreign keys
        foreign_keys = get_foreign_keys(cursor, table_name)

        # Add foreign keys to the schema
        complete_schema = add_foreign_keys_to_schema(schema, foreign_keys)

        # Pretty print the create statement
        pretty_schema = pretty_print_create_statement(complete_schema)
        print(pretty_schema)
        print("\n")

    conn.close()

if __name__ == "__main__":
    main()