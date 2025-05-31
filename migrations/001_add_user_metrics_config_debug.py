#!/usr/bin/env python3
"""
Enhanced Migration: Add user_metrics_config table for per-user metric configurations
This version includes debug output and verification steps
"""

import sqlite3
import sys
import os
from datetime import datetime

def connect_to_db():
    """Connect to the database"""
    db_path = "/srv/lifestats.me/backend/life_metrics.db"
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        sys.exit(1)
    return sqlite3.connect(db_path)

def execute_query(conn, query, description="", fetch=True):
    """Execute a query and return results"""
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        if fetch:
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            return results, columns
        else:
            conn.commit()
            return cursor.rowcount, []
    except Exception as e:
        print(f"❌ Error executing query: {e}")
        if description:
            print(f"   Query: {description}")
        return [], []

def print_results(results, columns, title=""):
    """Print query results in a formatted way"""
    if title:
        print(f"\n{title}")
    
    if not results:
        print("   No results found.")
        return
    
    if columns:
        # Print header
        header = " | ".join(f"{col:15}" for col in columns)
        print(f"   {header}")
        print(f"   {'-' * len(header)}")
        
        # Print rows
        for row in results:
            row_str = " | ".join(f"{str(val):15}" for val in row)
            print(f"   {row_str}")
    else:
        for row in results:
            print(f"   {row}")

def main():
    print("=== Enhanced Migration: Add user_metrics_config table ===")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    conn = connect_to_db()
    
    # Step 1: Check existing database structure
    print("\n=== STEP 1: Checking existing database structure ===")
    
    results, _ = execute_query(conn, "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    print("Current tables:")
    for table in results:
        print(f"   - {table[0]}")
    
    # Check user table
    results, columns = execute_query(conn, "PRAGMA table_info(user)")
    print_results(results, columns, "User table structure:")
    
    # Check goal table
    try:
        results, columns = execute_query(conn, "PRAGMA table_info(goal)")
        print_results(results, columns, "Goal table structure:")
    except:
        print("\nGoal table structure: Table does not exist")
    
    # Count users
    results, _ = execute_query(conn, "SELECT COUNT(*) as user_count FROM user")
    if results:
        user_count = results[0][0]
        print(f"\nCurrent user count: {user_count}")
    
    # Sample users
    results, columns = execute_query(conn, "SELECT id, username, email FROM user LIMIT 5")
    print_results(results, columns, "Sample users (first 5):")
    
    # Check goals
    try:
        results, _ = execute_query(conn, "SELECT COUNT(*) as goal_count FROM goal")
        if results:
            goal_count = results[0][0]
            print(f"\nCurrent goal entries: {goal_count}")
            
        if goal_count > 0:
            results, columns = execute_query(conn, "SELECT * FROM goal LIMIT 10")
            print_results(results, columns, "Sample goals (first 10):")
    except:
        print("\nCurrent goal entries: Goal table does not exist")
    
    # Step 2: Create user_metrics_config table
    print("\n=== STEP 2: Creating user_metrics_config table ===")
    
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS user_metrics_config (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        metric_key VARCHAR NOT NULL,
        metric_name VARCHAR NOT NULL,
        unit VARCHAR NOT NULL,
        type VARCHAR NOT NULL CHECK (type IN ('min', 'max')),
        goal REAL,
        default_goal REAL,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES user (id) ON DELETE CASCADE,
        UNIQUE (user_id, metric_key)
    )
    """
    
    execute_query(conn, create_table_sql, fetch=False)
    print("Table created successfully.")
    
    # Step 3: Create indexes
    print("\n=== STEP 3: Creating indexes ===")
    
    indexes = [
        "CREATE INDEX IF NOT EXISTS ix_user_metrics_config_user_id ON user_metrics_config (user_id)",
        "CREATE INDEX IF NOT EXISTS ix_user_metrics_config_metric_key ON user_metrics_config (metric_key)",
        "CREATE INDEX IF NOT EXISTS ix_user_metrics_config_is_active ON user_metrics_config (is_active)"
    ]
    
    for index_sql in indexes:
        execute_query(conn, index_sql, fetch=False)
    
    print("Indexes created successfully.")
    
    # Step 4: Verify table structure
    print("\n=== STEP 4: Verifying table structure ===")
    results, columns = execute_query(conn, "PRAGMA table_info(user_metrics_config)")
    print_results(results, columns, "user_metrics_config table info:")
    
    # Step 5: Populate with default metrics
    print("\n=== STEP 5: Populating default metrics for all users ===")
    
    metrics = [
        ('water_litres', 'water', 'litres', 'min', 2.0),
        ('calories_kcal', 'calories', 'kilocalories', 'max', 2000.0),
        ('sleep_hours', 'sleep', 'hours', 'min', 8.0),
        ('productivity_hours', 'productivity', 'hours', 'min', 8.0),
        ('exercise_hours', 'exercise', 'hours', 'min', 1.0),
        ('spend_rupees', 'spends', 'INR', 'max', 10000.0)
    ]
    
    for metric_key, metric_name, unit, type_val, default_goal in metrics:
        print(f"\nInserting {metric_name} metrics...")
        
        insert_sql = """
        INSERT OR IGNORE INTO user_metrics_config (user_id, metric_key, metric_name, unit, type, goal, default_goal, is_active)
        SELECT 
            u.id as user_id,
            ? as metric_key,
            ? as metric_name,
            ? as unit,
            ? as type,
            COALESCE(g.target_value, ?) as goal,
            ? as default_goal,
            TRUE as is_active
        FROM user u
        LEFT JOIN goal g ON u.id = g.user_id AND g.metric_key = ?
        """
        
        try:
            cursor = conn.cursor()
            cursor.execute(insert_sql, (metric_key, metric_name, unit, type_val, default_goal, default_goal, metric_key))
            rows_affected = cursor.rowcount
            conn.commit()
            print(f"{metric_name.capitalize()} metrics inserted. Rows affected: {rows_affected}")
        except Exception as e:
            print(f"❌ Error inserting {metric_name}: {e}")
    
    # Step 6: Verification and testing
    print("\n=== STEP 6: Verification and Testing ===")
    
    # Total entries
    results, _ = execute_query(conn, "SELECT COUNT(*) as total_entries FROM user_metrics_config")
    if results:
        print(f"\nTotal user_metrics_config entries: {results[0][0]}")
    
    # Entries per user
    results, columns = execute_query(conn, """
        SELECT user_id, COUNT(*) as metric_count 
        FROM user_metrics_config 
        GROUP BY user_id 
        ORDER BY user_id
    """)
    print_results(results, columns, "Entries per user:")
    
    # Entries per metric type
    results, columns = execute_query(conn, """
        SELECT metric_key, COUNT(*) as user_count 
        FROM user_metrics_config 
        GROUP BY metric_key 
        ORDER BY metric_key
    """)
    print_results(results, columns, "Entries per metric type:")
    
    # Sample entries
    results, columns = execute_query(conn, """
        SELECT 
            umc.id,
            umc.user_id,
            u.username,
            umc.metric_key,
            umc.metric_name,
            umc.unit,
            umc.type,
            umc.goal,
            umc.is_active
        FROM user_metrics_config umc
        JOIN user u ON umc.user_id = u.id
        ORDER BY umc.user_id, umc.metric_key
        LIMIT 10
    """)
    print_results(results, columns, "Sample user_metrics_config entries (first 10):")
    
    # Active metrics for first user
    results, columns = execute_query(conn, """
        SELECT 
            metric_key,
            metric_name,
            unit,
            type,
            goal,
            is_active
        FROM user_metrics_config 
        WHERE user_id = (SELECT MIN(id) FROM user) 
          AND is_active = TRUE
        ORDER BY metric_key
    """)
    print_results(results, columns, "Active metrics for first user:")
    
    # Step 7: Test specific user queries
    print("\n=== STEP 7: Testing user-specific queries ===")
    
    # Test frontend query
    results, columns = execute_query(conn, """
        SELECT 
            metric_key,
            metric_name,
            unit,
            type,
            goal
        FROM user_metrics_config 
        WHERE user_id = 1 AND is_active = TRUE
        ORDER BY metric_key
    """)
    print_results(results, columns, "Testing query that frontend might use - get active metrics for user ID 1:")
    
    print("\nChecking for data issues:")
    
    # Users without metrics
    results, columns = execute_query(conn, """
        SELECT u.id, u.username 
        FROM user u 
        LEFT JOIN user_metrics_config umc ON u.id = umc.user_id 
        WHERE umc.user_id IS NULL
    """)
    if results:
        print_results(results, columns, "Users without metrics:")
    else:
        print("Users without metrics: None (Good!)")
    
    # Inactive metrics
    results, _ = execute_query(conn, "SELECT COUNT(*) FROM user_metrics_config WHERE is_active = FALSE")
    if results:
        inactive_count = results[0][0]
        print(f"Inactive metrics: {inactive_count}")
        if inactive_count > 0:
            results, columns = execute_query(conn, "SELECT user_id, metric_key, is_active FROM user_metrics_config WHERE is_active = FALSE")
            print_results(results, columns, "Inactive metrics details:")
    
    # Duplicates
    results, columns = execute_query(conn, """
        SELECT user_id, metric_key, COUNT(*) as count
        FROM user_metrics_config 
        GROUP BY user_id, metric_key 
        HAVING COUNT(*) > 1
    """)
    if results:
        print_results(results, columns, "Duplicate entries (should be none):")
    else:
        print("Duplicate entries: None (Good!)")
    
    # Final summary
    print("\n=== MIGRATION COMPLETED ===")
    
    # Get final counts
    user_count_result, _ = execute_query(conn, "SELECT COUNT(*) FROM user")
    config_count_result, _ = execute_query(conn, "SELECT COUNT(*) FROM user_metrics_config")
    
    if user_count_result and config_count_result:
        user_count = user_count_result[0][0]
        config_count = config_count_result[0][0]
        expected_configs = user_count * 6
        
        print(f"Users: {user_count}")
        print(f"Configurations: {config_count}")
        print(f"Expected: {expected_configs}")
        
        if config_count == expected_configs:
            print("✅ Migration successful! Each user has 6 metrics configured.")
        else:
            print("❌ Migration incomplete - some configurations are missing.")
    
    print("\nNext steps:")
    print("1. Update backend code to read from user_metrics_config instead of YAML")
    print("2. Test the API endpoints")
    print("3. Check if frontend is calling the correct endpoints")
    
    conn.close()

if __name__ == "__main__":
    main() 