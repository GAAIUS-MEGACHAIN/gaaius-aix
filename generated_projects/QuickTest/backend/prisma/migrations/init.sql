-- Migration: init.sql
-- Created: 2026-01-14T15:29:49.768439

BEGIN;

CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(255) NOT NULL,
  password VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  price DECIMAL(10, 2) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMIT;

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details

-- Migration details
