# Database Migrations

This directory contains database migration scripts for the Life Stats application.

## Running Migrations

### Local Development
```bash
cd migrations
python3 run_migration.py <migration_file>
```

### Production
1. Copy the migration files to your production server
2. Run the migration script:
```bash
python3 run_migration.py <migration_file>
```

## Available Migrations

### 001_add_user_metrics_config.sql
- **Purpose**: Adds per-user metrics configuration support
- **Changes**: 
  - Creates `user_metrics_config` table
  - Migrates existing users to use default metrics configuration
  - Preserves existing goals from the `goal` table
- **Rollback**: Not provided (would require dropping the table and reverting to global config)

## Migration Script Usage

The `run_migration.py` script:
- Automatically locates the database file
- Executes SQL statements safely
- Provides clear success/error feedback
- Supports both local and production database paths

### Example
```bash
# Run the user metrics config migration
python3 run_migration.py 001_add_user_metrics_config.sql
```

## Database Schema Changes

After running `001_add_user_metrics_config.sql`:

### New Table: `user_metrics_config`
- Stores per-user metric configurations
- Replaces global `metrics_config.yaml` for user-specific settings
- Allows users to customize their tracked metrics
- Supports enabling/disabling metrics per user

### Migration Details
- Existing users get default metrics configuration automatically
- User goals are preserved and migrated from the `goal` table
- All metrics start as "active" for existing users
- New users will get default configuration on registration

## Notes for Production

1. **Backup First**: Always backup your database before running migrations
2. **Test Locally**: Run migrations on a copy of production data first
3. **Downtime**: Some migrations may require brief application downtime
4. **Validation**: Verify the migration succeeded by checking the new table structure

## Adding New Migrations

1. Create a new `.sql` file with incremental naming (e.g., `002_your_migration.sql`)
2. Include comments explaining the purpose and changes
3. Test thoroughly in development
4. Update this README with migration details 