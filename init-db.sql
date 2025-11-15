-- PsyAI Database Initialization Script
-- This script runs automatically when PostgreSQL container is first created

-- Ensure the database exists
SELECT 'CREATE DATABASE psyai'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'psyai')\gexec

-- Connect to the database
\c psyai

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Log successful initialization
SELECT 'PsyAI database initialized successfully' AS status;
