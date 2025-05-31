-- Enhanced Migration: Add user_metrics_config table for per-user metric configurations
-- Date: 2024-01-xx
-- Description: Replace global metrics_config.yaml with per-user configuration
-- This version includes debug output and verification steps

.headers on
.mode column

-- Step 1: Check existing database structure
.print "=== STEP 1: Checking existing database structure ==="
.print "Current tables:"
SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;

.print ""
.print "Checking user table structure:"
PRAGMA table_info(user);

.print ""
.print "Checking goal table structure (if exists):"
PRAGMA table_info(goal);

.print ""
.print "Current user count:"
SELECT COUNT(*) as user_count FROM user;

.print ""
.print "Sample users (first 5):"
SELECT id, username, email FROM user LIMIT 5;

.print ""
.print "Current goal entries (if any):"
SELECT COUNT(*) as goal_count FROM goal;

.print ""
.print "Sample goals (first 10):"
SELECT * FROM goal LIMIT 10;

-- Step 2: Create user_metrics_config table
.print ""
.print "=== STEP 2: Creating user_metrics_config table ==="

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
);

.print "Table created successfully."

-- Step 3: Create indexes
.print ""
.print "=== STEP 3: Creating indexes ==="

CREATE INDEX IF NOT EXISTS ix_user_metrics_config_user_id ON user_metrics_config (user_id);
CREATE INDEX IF NOT EXISTS ix_user_metrics_config_metric_key ON user_metrics_config (metric_key);
CREATE INDEX IF NOT EXISTS ix_user_metrics_config_is_active ON user_metrics_config (is_active);

.print "Indexes created successfully."

-- Step 4: Verify table structure
.print ""
.print "=== STEP 4: Verifying table structure ==="
.print "user_metrics_config table info:"
PRAGMA table_info(user_metrics_config);

-- Step 5: Start populating with default metrics
.print ""
.print "=== STEP 5: Populating default metrics for all users ==="

-- Water metric
.print ""
.print "Inserting water metrics..."
INSERT OR IGNORE INTO user_metrics_config (user_id, metric_key, metric_name, unit, type, goal, default_goal, is_active)
SELECT 
    u.id as user_id,
    'water_litres' as metric_key,
    'water' as metric_name,
    'litres' as unit,
    'min' as type,
    COALESCE(g.target_value, 2.0) as goal,
    2.0 as default_goal,
    TRUE as is_active
FROM user u
LEFT JOIN goal g ON u.id = g.user_id AND g.metric_key = 'water_litres';

.print "Water metrics inserted. Rows affected: " || changes();

-- Calories metric
.print ""
.print "Inserting calories metrics..."
INSERT OR IGNORE INTO user_metrics_config (user_id, metric_key, metric_name, unit, type, goal, default_goal, is_active)
SELECT 
    u.id as user_id,
    'calories_kcal' as metric_key,
    'calories' as metric_name,
    'kilocalories' as unit,
    'max' as type,
    COALESCE(g.target_value, 2000.0) as goal,
    2000.0 as default_goal,
    TRUE as is_active
FROM user u
LEFT JOIN goal g ON u.id = g.user_id AND g.metric_key = 'calories_kcal';

.print "Calories metrics inserted. Rows affected: " || changes();

-- Sleep metric
.print ""
.print "Inserting sleep metrics..."
INSERT OR IGNORE INTO user_metrics_config (user_id, metric_key, metric_name, unit, type, goal, default_goal, is_active)
SELECT 
    u.id as user_id,
    'sleep_hours' as metric_key,
    'sleep' as metric_name,
    'hours' as unit,
    'min' as type,
    COALESCE(g.target_value, 8.0) as goal,
    8.0 as default_goal,
    TRUE as is_active
FROM user u
LEFT JOIN goal g ON u.id = g.user_id AND g.metric_key = 'sleep_hours';

.print "Sleep metrics inserted. Rows affected: " || changes();

-- Productivity metric
.print ""
.print "Inserting productivity metrics..."
INSERT OR IGNORE INTO user_metrics_config (user_id, metric_key, metric_name, unit, type, goal, default_goal, is_active)
SELECT 
    u.id as user_id,
    'productivity_hours' as metric_key,
    'productivity' as metric_name,
    'hours' as unit,
    'min' as type,
    COALESCE(g.target_value, 8.0) as goal,
    8.0 as default_goal,
    TRUE as is_active
FROM user u
LEFT JOIN goal g ON u.id = g.user_id AND g.metric_key = 'productivity_hours';

.print "Productivity metrics inserted. Rows affected: " || changes();

-- Exercise metric
.print ""
.print "Inserting exercise metrics..."
INSERT OR IGNORE INTO user_metrics_config (user_id, metric_key, metric_name, unit, type, goal, default_goal, is_active)
SELECT 
    u.id as user_id,
    'exercise_hours' as metric_key,
    'exercise' as metric_name,
    'hours' as unit,
    'min' as type,
    COALESCE(g.target_value, 1.0) as goal,
    1.0 as default_goal,
    TRUE as is_active
FROM user u
LEFT JOIN goal g ON u.id = g.user_id AND g.metric_key = 'exercise_hours';

.print "Exercise metrics inserted. Rows affected: " || changes();

-- Spend metric
.print ""
.print "Inserting spend metrics..."
INSERT OR IGNORE INTO user_metrics_config (user_id, metric_key, metric_name, unit, type, goal, default_goal, is_active)
SELECT 
    u.id as user_id,
    'spend_rupees' as metric_key,
    'spends' as metric_name,
    'INR' as unit,
    'max' as type,
    COALESCE(g.target_value, 10000.0) as goal,
    10000.0 as default_goal,
    TRUE as is_active
FROM user u
LEFT JOIN goal g ON u.id = g.user_id AND g.metric_key = 'spend_rupees';

.print "Spend metrics inserted. Rows affected: " || changes();

-- Step 6: Verification and testing
.print ""
.print "=== STEP 6: Verification and Testing ==="

.print ""
.print "Total user_metrics_config entries:"
SELECT COUNT(*) as total_entries FROM user_metrics_config;

.print ""
.print "Entries per user:"
SELECT user_id, COUNT(*) as metric_count 
FROM user_metrics_config 
GROUP BY user_id 
ORDER BY user_id;

.print ""
.print "Entries per metric type:"
SELECT metric_key, COUNT(*) as user_count 
FROM user_metrics_config 
GROUP BY metric_key 
ORDER BY metric_key;

.print ""
.print "Sample user_metrics_config entries (first 10):"
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
LIMIT 10;

.print ""
.print "Active metrics for first user:"
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
ORDER BY metric_key;

-- Step 7: Test specific user queries
.print ""
.print "=== STEP 7: Testing user-specific queries ==="

.print ""
.print "Testing query that frontend might use - get active metrics for user ID 1:"
SELECT 
    metric_key,
    metric_name,
    unit,
    type,
    goal
FROM user_metrics_config 
WHERE user_id = 1 AND is_active = TRUE
ORDER BY metric_key;

.print ""
.print "Check if we have any data issues:"
.print "Users without metrics:"
SELECT u.id, u.username 
FROM user u 
LEFT JOIN user_metrics_config umc ON u.id = umc.user_id 
WHERE umc.user_id IS NULL;

.print ""
.print "Inactive metrics:"
SELECT user_id, metric_key, is_active 
FROM user_metrics_config 
WHERE is_active = FALSE;

.print ""
.print "Duplicate entries (should be none due to UNIQUE constraint):"
SELECT user_id, metric_key, COUNT(*) as count
FROM user_metrics_config 
GROUP BY user_id, metric_key 
HAVING COUNT(*) > 1;

.print ""
.print "=== MIGRATION COMPLETED ==="
.print "If you see 6 metrics per user and no users without metrics, the migration was successful."
.print "Next steps:"
.print "1. Update backend code to read from user_metrics_config instead of YAML"
.print "2. Test the API endpoints"
.print "3. Check if frontend is calling the correct endpoints" 