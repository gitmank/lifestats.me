#!/usr/bin/env python3
"""
Test script for user_metrics_config table
Run this after the migration to verify everything is working
"""

import sqlite3
import sys
import os

def connect_to_db():
    """Connect to the database"""
    db_path = "/srv/lifestats.me/backend/life_metrics.db"
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        sys.exit(1)
    return sqlite3.connect(db_path)

def execute_query(conn, query, description=""):
    """Execute a query and return results"""
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        return results, columns
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
    print("=== TESTING USER METRICS CONFIG ===")
    
    conn = connect_to_db()
    
    # 1. Check table structure
    results, columns = execute_query(conn, "PRAGMA table_info(user_metrics_config)")
    print_results(results, columns, "1. Table structure:")
    
    # 2. Total configurations
    results, _ = execute_query(conn, "SELECT COUNT(*) as total_configs FROM user_metrics_config")
    if results:
        print(f"\n2. Total number of metric configurations: {results[0][0]}")
    
    # 3. Users with metrics
    results, _ = execute_query(conn, "SELECT COUNT(DISTINCT user_id) as users_with_metrics FROM user_metrics_config")
    if results:
        print(f"\n3. Number of users with metrics configured: {results[0][0]}")
    
    # 4. Available metric types
    results, columns = execute_query(conn, "SELECT DISTINCT metric_key, metric_name FROM user_metrics_config ORDER BY metric_key")
    print_results(results, columns, "4. All metric types available:")
    
    # 5. Sample configuration for user 1
    query = """
    SELECT 
        metric_key,
        metric_name,
        unit,
        type,
        goal,
        default_goal,
        is_active
    FROM user_metrics_config 
    WHERE user_id = 1
    ORDER BY metric_key
    """
    results, columns = execute_query(conn, query)
    print_results(results, columns, "5. Sample configuration for user ID 1:")
    
    # 6. Verify all users have metrics
    query = """
    SELECT 
        user_id,
        COUNT(*) as metric_count
    FROM user_metrics_config 
    GROUP BY user_id 
    ORDER BY user_id
    """
    results, columns = execute_query(conn, query)
    print_results(results, columns, "6. Metrics per user:")
    
    # Also show the metric keys for first few users
    query = """
    SELECT 
        user_id,
        GROUP_CONCAT(metric_key ORDER BY metric_key) as metrics
    FROM user_metrics_config 
    GROUP BY user_id 
    ORDER BY user_id
    LIMIT 3
    """
    results, columns = execute_query(conn, query)
    print_results(results, columns, "   Sample metric keys per user:")
    
    # 7. Check for data issues
    print("\n7. Checking for data issues:")
    
    # Users without metrics
    query = """
    SELECT u.id, u.username 
    FROM user u 
    LEFT JOIN user_metrics_config umc ON u.id = umc.user_id 
    WHERE umc.user_id IS NULL
    LIMIT 5
    """
    results, columns = execute_query(conn, query)
    if results:
        print_results(results, columns, "   - Users without any metrics:")
    else:
        print("   - Users without metrics: None (Good!)")
    
    # Inactive metrics
    results, _ = execute_query(conn, "SELECT COUNT(*) as inactive_count FROM user_metrics_config WHERE is_active = FALSE")
    if results:
        inactive_count = results[0][0]
        print(f"   - Inactive metrics count: {inactive_count}")
        if inactive_count > 0:
            print("     ⚠️  Warning: Some metrics are inactive")
        else:
            print("     ✅ All metrics are active")
    
    # 8. Test API query
    query = """
    SELECT 
        metric_key,
        metric_name,
        unit,
        type,
        goal
    FROM user_metrics_config 
    WHERE user_id = 1 AND is_active = TRUE
    ORDER BY metric_key
    """
    results, columns = execute_query(conn, query)
    print_results(results, columns, "8. Test query that the API would use (active metrics for user 1):")
    
    # Summary
    print("\n=== TEST SUMMARY ===")
    
    # Get total users and total configs
    user_count_result, _ = execute_query(conn, "SELECT COUNT(*) FROM user")
    config_count_result, _ = execute_query(conn, "SELECT COUNT(*) FROM user_metrics_config")
    
    if user_count_result and config_count_result:
        user_count = user_count_result[0][0]
        config_count = config_count_result[0][0]
        expected_configs = user_count * 6
        
        print(f"Total users: {user_count}")
        print(f"Total configurations: {config_count}")
        print(f"Expected configurations: {expected_configs}")
        
        if config_count == expected_configs:
            print("✅ Migration appears successful!")
        else:
            print("❌ Migration incomplete - missing configurations")
            print(f"   Missing: {expected_configs - config_count} configurations")
    
    conn.close()

if __name__ == "__main__":
    main() 