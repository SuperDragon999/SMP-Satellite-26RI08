# batch edit
import sqlite3

def batch_delete_entries_beyond_id(target_folder: Path, table_name: str, max_valid_id: int):
    # 1. Validate the directory structure
    if not target_folder.exists() or not target_folder.is_dir():
        print(f"[ERROR] Target directory not found: {target_folder}")
        return

    # 2. Collect all target SQLite databases
    db_files = list(target_folder.glob("*.db"))
    if not db_files:
        print(f"No .db files found in {target_folder.resolve()}")
        return

    print(f"Found {len(db_files)} database files. Initiating batch deletion...\n")

    for db_path in db_files:
        print(f"Processing: {db_path.name}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # 3. Verify the target table exists in this specific database file
            cursor.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?;", 
                (table_name,)
            )
            if not cursor.fetchone():
                print(f"  -> Table '{table_name}' does not exist in this file. Skipping.")
                conn.close()
                continue

            # 4. Execute deletion inside an atomic transaction block
            cursor.execute("BEGIN TRANSACTION;")
            
            # Execute the targeted mass deletion
            cursor.execute(
                f"DELETE FROM {table_name} WHERE ID > ?;", 
                (max_valid_id,)
            )
            
            # Track how many rows were purged
            deleted_rows = cursor.rowcount
            
            cursor.execute("COMMIT;")
            print(f"  -> [SUCCESS] Purged {deleted_rows} entries with ID > {max_valid_id}.")
            
        except sqlite3.Error as e:
            cursor.execute("ROLLBACK;")
            print(f"  -> [FAIL] SQL Error encountered in {db_path.name}: {e}. Changes rolled back.")
            
        finally:
            conn.close()
            print("-" * 50)

    print("\nBatch deletion operation finalized.")

from pathlib import Path

# Resolve the target directory relative to main.py
project_root = Path(__file__).resolve().parent
data_directory = project_root / "backend" / "storage" / "data"

batch_delete_entries_beyond_id(
    target_folder=data_directory,
    table_name="processing",
    max_valid_id=191
)