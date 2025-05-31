-- Test script for user_metrics_config table
-- Run this after the migration to verify everything is working

.headers on
.mode column

.print "=== TESTING USER METRICS CONFIG ==="

.print ""
.print "1. Table exists and has correct structure:"
PRAGMA table_info(user_metrics_config);

.print ""
.print "2. Total number of metric configurations:"
SELECT COUNT(*) as total_configs FROM user_metrics_config;

.print ""
.print "3. Number of users with metrics configured:"
SELECT COUNT(DISTINCT user_id) as users_with_metrics FROM user_metrics_config;

.print ""
.print "4. All metric types available:"
SELECT DISTINCT metric_key, metric_name FROM user_metrics_config ORDER BY metric_key;

.print ""
.print "5. Sample configuration for user ID 1:"
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
ORDER BY metric_key;

.print ""
.print "6. Verify all users have the same 6 metrics:"
SELECT 
    user_id,
    COUNT(*) as metric_count,
    GROUP_CONCAT(metric_key ORDER BY metric_key) as metrics
FROM user_metrics_config 
GROUP BY user_id 
ORDER BY user_id;

.print ""
.print "7. Check for any data issues:"
.print "   - Users without any metrics:"
SELECT u.id, u.username 
FROM user u 
LEFT JOIN user_metrics_config umc ON u.id = umc.user_id 
WHERE umc.user_id IS NULL
LIMIT 5;

.print ""
.print "   - Any inactive metrics:"
SELECT COUNT(*) as inactive_count FROM user_metrics_config WHERE is_active = FALSE;

.print ""
.print "8. Test query that the API would use (active metrics for user 1):"
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
.print "=== TEST COMPLETED ==="
.print "Expected results:"
.print "- Total configs should be: (number of users) × 6"
.print "- Each user should have exactly 6 metrics"
.print "- All metrics should be active (is_active = TRUE)"
.print "- No users should be missing metrics" 