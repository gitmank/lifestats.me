-- Migration: Add user_metrics_config table for per-user metric configurations
-- Date: $(date)
-- Description: Replace global metrics_config.yaml with per-user configuration

-- Create user_metrics_config table
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

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS ix_user_metrics_config_user_id ON user_metrics_config (user_id);
CREATE INDEX IF NOT EXISTS ix_user_metrics_config_metric_key ON user_metrics_config (metric_key);
CREATE INDEX IF NOT EXISTS ix_user_metrics_config_is_active ON user_metrics_config (is_active);

-- Populate existing users with default metrics configuration
-- This data comes from the current metrics_config.yaml
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