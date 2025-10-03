#!/bin/bash
set -e

# Database initialization script for GarageReg

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Create extensions
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pgcrypto";
    CREATE EXTENSION IF NOT EXISTS "ltree";
    
    -- Create additional databases
    CREATE DATABASE ${POSTGRES_DB}_test;
    
    -- Grant permissions
    GRANT ALL PRIVILEGES ON DATABASE ${POSTGRES_DB} TO ${POSTGRES_USER};
    GRANT ALL PRIVILEGES ON DATABASE ${POSTGRES_DB}_test TO ${POSTGRES_USER};
    
    -- Create schemas
    \c ${POSTGRES_DB}
    CREATE SCHEMA IF NOT EXISTS auth;
    CREATE SCHEMA IF NOT EXISTS gate;
    CREATE SCHEMA IF NOT EXISTS maintenance;
    CREATE SCHEMA IF NOT EXISTS audit;
    
    -- Grant schema permissions
    GRANT ALL ON SCHEMA auth TO ${POSTGRES_USER};
    GRANT ALL ON SCHEMA gate TO ${POSTGRES_USER};
    GRANT ALL ON SCHEMA maintenance TO ${POSTGRES_USER};
    GRANT ALL ON SCHEMA audit TO ${POSTGRES_USER};
    
    -- Set search path
    ALTER DATABASE ${POSTGRES_DB} SET search_path TO public,auth,gate,maintenance,audit;
    
    -- Create basic tables for health check
    CREATE TABLE IF NOT EXISTS health_check (
        id SERIAL PRIMARY KEY,
        status VARCHAR(10) DEFAULT 'ok',
        last_check TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    INSERT INTO health_check (status) VALUES ('ok');
    
    COMMENT ON DATABASE ${POSTGRES_DB} IS 'GarageReg main database';
    COMMENT ON DATABASE ${POSTGRES_DB}_test IS 'GarageReg test database';
EOSQL

echo "Database initialization completed successfully!"