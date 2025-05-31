#!/usr/bin/env python3
"""
FIXED Enhanced Migration: Add user_metrics_config table for per-user metric configurations
This version fixes the issues found in production
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

def execute_query(conn, query, params=None, description="", fetch=True):
    """Execute a query and return results"""
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
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
        print(f"   SQL: {query}")
        if params:
            print(f"   Params: {params}")
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
    print("=== FIXED Enhanced Migration: Add user_metrics_config table ===")
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
    
    # Count users - FIXED: Remove email column reference
    results, _ = execute_query(conn, "SELECT COUNT(*) as user_count FROM user")
    if results:
        user_count = results[0][0]
        print(f"\nCurrent user count: {user_count}")
    
    # Sample users - FIXED: Remove email column reference
    results, columns = execute_query(conn, "SELECT id, username FROM user LIMIT 5")
    print_results(results, columns, "Sample users (first 5):")
    
    # Check goals
    results, _ = execute_query(conn, "SELECT COUNT(*) as goal_count FROM goal")
    if results:
        goal_count = results[0][0]
        print(f"\nCurrent goal entries: {goal_count}")
        
    # Step 2: Check if table exists and has data
    print("\n=== STEP 2: Checking user_metrics_config table ===")
    
    results, _ = execute_query(conn, "SELECT COUNT(*) FROM user_metrics_config")
    if results:
        existing_count = results[0][0]
        print(f"Existing user_metrics_config entries: {existing_count}")
        
        if existing_count > 0:
            print("⚠️  Table already has data. Clearing existing data...")
            execute_query(conn, "DELETE FROM user_metrics_config", fetch=False)
            print("   Existing data cleared.")
    
    # Step 3: Get all users
    print("\n=== STEP 3: Getting all users ===")
    results, _ = execute_query(conn, "SELECT id FROM user ORDER BY id")
    user_ids = [row[0] for row in results]
    print(f"Found {len(user_ids)} users: {user_ids}")
    
    # Step 4: Define metrics and insert them
    print("\n=== STEP 4: Inserting metrics for all users ===")
    
    metrics = [
        ('water_litres', 'water', 'litres', 'min', 2.0),
        ('calories_kcal', 'calories', 'kilocalories', 'max', 2000.0),
        ('sleep_hours', 'sleep', 'hours', 'min', 8.0),
        ('productivity_hours', 'productivity', 'hours', 'min', 8.0),
        ('exercise_hours', 'exercise', 'hours', 'min', 1.0),
        ('spend_rupees', 'spends', 'INR', 'max', 10000.0)
    ]
    
    total_inserted = 0
    
    for user_id in user_ids:
        print(f"\nProcessing user {user_id}:")
        
        # Get existing goals for this user
        goal_query = "SELECT metric_key, target_value FROM goal WHERE user_id = ?"
        goal_results, _ = execute_query(conn, goal_query, (user_id,))
        goal_map = {row[0]: row[1] for row in goal_results}
        print(f"   Found {len(goal_map)} existing goals: {list(goal_map.keys())}")
        
        for metric_key, metric_name, unit, type_val, default_goal in metrics:
            # Use existing goal if available, otherwise use default
            goal = goal_map.get(metric_key, default_goal)
            
            insert_query = """
            INSERT INTO user_metrics_config 
            (user_id, metric_key, metric_name, unit, type, goal, default_goal, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            now = datetime.utcnow().isoformat()
            params = (user_id, metric_key, metric_name, unit, type_val, goal, default_goal, True, now, now)
            
            rows_affected, _ = execute_query(conn, insert_query, params, f"Insert {metric_name} for user {user_id}", fetch=False)
            
            if rows_affected > 0:
                print(f"   ✅ {metric_name}: goal={goal}")
                total_inserted += 1
            else:
                print(f"   ❌ Failed to insert {metric_name}")
    
    print(f"\nTotal configurations inserted: {total_inserted}")
    
    # Step 5: Verification
    print("\n=== STEP 5: Verification ===")
    
    # Total entries
    results, _ = execute_query(conn, "SELECT COUNT(*) FROM user_metrics_config")
    if results:
        final_count = results[0][0]
        print(f"Final user_metrics_config entries: {final_count}")
    
    # Entries per user
    results, columns = execute_query(conn, """
        SELECT user_id, COUNT(*) as metric_count 
        FROM user_metrics_config 
        GROUP BY user_id 
        ORDER BY user_id
    """)
    print_results(results, columns, "Entries per user:")
    
    # Sample entries
    results, columns = execute_query(conn, """
        SELECT 
            umc.user_id,
            umc.metric_key,
            umc.metric_name,
            umc.goal,
            umc.is_active
        FROM user_metrics_config umc
        ORDER BY umc.user_id, umc.metric_key
        LIMIT 10
    """)
    print_results(results, columns, "Sample configurations:")
    
    # Check for missing users
    results, columns = execute_query(conn, """
        SELECT u.id, u.username 
        FROM user u 
        LEFT JOIN user_metrics_config umc ON u.id = umc.user_id 
        WHERE umc.user_id IS NULL
    """)
    if results:
        print_results(results, columns, "❌ Users still missing metrics:")
    else:
        print("\n✅ All users have metrics configured!")
    
    # Final summary
    print("\n=== MIGRATION SUMMARY ===")
    
    expected_configs = len(user_ids) * len(metrics)
    print(f"Users: {len(user_ids)}")
    print(f"Metrics per user: {len(metrics)}")
    print(f"Expected configurations: {expected_configs}")
    print(f"Actual configurations: {final_count if 'final_count' in locals() else 0}")
    
    if final_count == expected_configs:
        print("✅ Migration completed successfully!")
        print("✅ All users have all 6 metrics configured!")
    else:
        print("❌ Migration incomplete - some configurations are missing.")
        print(f"   Missing: {expected_configs - final_count} configurations")
    
    conn.close()

if __name__ == "__main__":
    main() 