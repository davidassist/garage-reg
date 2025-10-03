#!/bin/bash
# =============================================================================
# POSTGRESQL INITIALIZATION SCRIPT
# Sets up database extensions and initial configuration
# =============================================================================

set -e

# Run as postgres user
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- =================================================================
    -- EXTENSIONS SETUP
    -- =================================================================
    
    -- Enable UUID extension for primary keys
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    
    -- Enable crypto extension for password hashing
    CREATE EXTENSION IF NOT EXISTS "pgcrypto";
    
    -- Enable full-text search
    CREATE EXTENSION IF NOT EXISTS "pg_trgm";
    CREATE EXTENSION IF NOT EXISTS "unaccent";
    
    -- Enable statistics extension for query monitoring
    CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
    
    -- Enable JSON operations
    CREATE EXTENSION IF NOT EXISTS "btree_gin";
    CREATE EXTENSION IF NOT EXISTS "btree_gist";
    
    -- =================================================================
    -- PERFORMANCE MONITORING VIEWS
    -- =================================================================
    
    -- View for slow queries
    CREATE OR REPLACE VIEW slow_queries AS
    SELECT 
        query,
        calls,
        total_time,
        total_time/calls as avg_time,
        rows,
        100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
    FROM pg_stat_statements
    WHERE calls > 1
    ORDER BY total_time DESC;
    
    -- View for database size monitoring
    CREATE OR REPLACE VIEW database_sizes AS
    SELECT 
        datname,
        pg_size_pretty(pg_database_size(datname)) as size
    FROM pg_database
    WHERE datistemplate = false
    ORDER BY pg_database_size(datname) DESC;
    
    -- View for table sizes
    CREATE OR REPLACE VIEW table_sizes AS
    SELECT 
        schemaname,
        tablename,
        attname,
        n_distinct,
        correlation,
        most_common_vals
    FROM pg_stats
    WHERE schemaname = 'public'
    ORDER BY n_distinct DESC;
    
    -- =================================================================
    -- GARAGEREG SPECIFIC FUNCTIONS
    -- =================================================================
    
    -- Function to generate secure random tokens
    CREATE OR REPLACE FUNCTION generate_token(length INT DEFAULT 32)
    RETURNS TEXT AS \$\$
    BEGIN
        RETURN encode(gen_random_bytes(length), 'base64');
    END;
    \$\$ LANGUAGE plpgsql;
    
    -- Function for audit logging
    CREATE OR REPLACE FUNCTION audit_trigger()
    RETURNS TRIGGER AS \$\$
    BEGIN
        IF TG_OP = 'DELETE' THEN
            INSERT INTO audit_log (
                table_name,
                operation,
                old_values,
                performed_at,
                performed_by
            ) VALUES (
                TG_TABLE_NAME,
                TG_OP,
                row_to_json(OLD),
                NOW(),
                current_setting('app.current_user_id', true)
            );
            RETURN OLD;
        ELSIF TG_OP = 'UPDATE' THEN
            INSERT INTO audit_log (
                table_name,
                operation,
                old_values,
                new_values,
                performed_at,
                performed_by
            ) VALUES (
                TG_TABLE_NAME,
                TG_OP,
                row_to_json(OLD),
                row_to_json(NEW),
                NOW(),
                current_setting('app.current_user_id', true)
            );
            RETURN NEW;
        ELSIF TG_OP = 'INSERT' THEN
            INSERT INTO audit_log (
                table_name,
                operation,
                new_values,
                performed_at,
                performed_by
            ) VALUES (
                TG_TABLE_NAME,
                TG_OP,
                row_to_json(NEW),
                NOW(),
                current_setting('app.current_user_id', true)
            );
            RETURN NEW;
        END IF;
        RETURN NULL;
    END;
    \$\$ LANGUAGE plpgsql;
    
    -- Function for full-text search
    CREATE OR REPLACE FUNCTION search_vehicles(search_term TEXT)
    RETURNS TABLE (
        id UUID,
        make TEXT,
        model TEXT,
        year INTEGER,
        vin TEXT,
        license_plate TEXT,
        rank REAL
    ) AS \$\$
    BEGIN
        RETURN QUERY
        SELECT 
            v.id,
            v.make,
            v.model,
            v.year,
            v.vin,
            v.license_plate,
            ts_rank_cd(
                to_tsvector('english', 
                    COALESCE(v.make, '') || ' ' ||
                    COALESCE(v.model, '') || ' ' ||
                    COALESCE(v.vin, '') || ' ' ||
                    COALESCE(v.license_plate, '') || ' ' ||
                    COALESCE(v.description, '')
                ),
                plainto_tsquery('english', search_term)
            ) as rank
        FROM vehicles v
        WHERE to_tsvector('english', 
            COALESCE(v.make, '') || ' ' ||
            COALESCE(v.model, '') || ' ' ||
            COALESCE(v.vin, '') || ' ' ||
            COALESCE(v.license_plate, '') || ' ' ||
            COALESCE(v.description, '')
        ) @@ plainto_tsquery('english', search_term)
        ORDER BY rank DESC;
    END;
    \$\$ LANGUAGE plpgsql;
    
    -- =================================================================
    -- INITIAL DATA
    -- =================================================================
    
    -- Create application settings table
    CREATE TABLE IF NOT EXISTS app_settings (
        key VARCHAR(255) PRIMARY KEY,
        value JSONB NOT NULL,
        description TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    -- Insert default settings
    INSERT INTO app_settings (key, value, description) VALUES 
    ('app_version', '"1.0.0"', 'Application version'),
    ('database_version', '"1.0.0"', 'Database schema version'),
    ('timezone', '"UTC"', 'Application timezone'),
    ('max_file_size', '10485760', 'Maximum file upload size in bytes (10MB)'),
    ('allowed_file_types', '["jpg", "jpeg", "png", "pdf", "doc", "docx"]', 'Allowed file upload types'),
    ('session_timeout', '3600', 'Session timeout in seconds'),
    ('password_min_length', '8', 'Minimum password length'),
    ('backup_retention_days', '30', 'Number of days to retain backups')
    ON CONFLICT (key) DO NOTHING;
    
    -- =================================================================
    -- PERMISSIONS
    -- =================================================================
    
    -- Grant usage on extensions to application user
    GRANT USAGE ON SCHEMA public TO \${POSTGRES_USER};
    GRANT CREATE ON SCHEMA public TO \${POSTGRES_USER};
    
    -- Grant execute on functions
    GRANT EXECUTE ON FUNCTION generate_token(INT) TO \${POSTGRES_USER};
    GRANT EXECUTE ON FUNCTION search_vehicles(TEXT) TO \${POSTGRES_USER};
    
    -- =================================================================
    -- PERFORMANCE OPTIMIZATION
    -- =================================================================
    
    -- Create indexes for common search patterns
    -- Note: Actual table indexes will be created by Alembic migrations
    
    -- Analyze all tables for better query planning
    ANALYZE;
    
    -- =================================================================
    -- COMPLETION MESSAGE
    -- =================================================================
    
    \echo 'GarageReg database initialization completed successfully!'
    \echo 'Extensions enabled: uuid-ossp, pgcrypto, pg_trgm, unaccent, pg_stat_statements, btree_gin, btree_gist'
    \echo 'Custom functions created: generate_token, audit_trigger, search_vehicles'
    \echo 'Performance monitoring views: slow_queries, database_sizes, table_sizes'
    
EOSQL

echo "Database initialization completed!"
echo "PostgreSQL is ready for GarageReg application."