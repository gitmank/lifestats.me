#!/usr/bin/env python3
"""
Migration runner script for Life Stats application
Usage: python run_migration.py <migration_file>
"""

import sys
import sqlite3
from pathlib import Path

def run_migration(migration_file: str, db_path: str = None):
    """Run a SQL migration file against the database."""
    
    # Default database path
    if db_path is None:
        db_path = Path(__file__).parent.parent / "backend" / "life_metrics.db"
    
    migration_path = Path(__file__).parent / migration_file
    
    if not migration_path.exists():
        print(f"❌ Migration file not found: {migration_path}")
        return False
    
    if not Path(db_path).exists():
        print(f"❌ Database not found: {db_path}")
        return False
    
    print(f"🔄 Running migration: {migration_file}")
    print(f"📁 Database: {db_path}")
    
    try:
        # Read migration SQL
        with open(migration_path, 'r') as f:
            sql_commands = f.read()
        
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Execute migration (split by semicolon for multiple statements)
        for statement in sql_commands.split(';'):
            statement = statement.strip()
            if statement:  # Skip empty statements
                cursor.execute(statement)
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print(f"✅ Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python run_migration.py <migration_file>")
        print("Example: python run_migration.py 001_add_user_metrics_config.sql")
        sys.exit(1)
    
    migration_file = sys.argv[1]
    success = run_migration(migration_file)
    sys.exit(0 if success else 1) 