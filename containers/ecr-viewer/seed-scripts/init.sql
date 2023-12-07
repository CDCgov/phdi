-- ./seed-scripts/init.sql

-- CREATE DATABASE IF NOT EXISTS ecrviewer_db

ECHO "hello world"

CREATE TABLE IF NOT EXISTS fhir (
  ecr_id VARCHAR NOT NULL,
  data JSONB NOT NULL,
  PRIMARY KEY (ecr_id)
);



-- Create a user table
-- CREATE TABLE IF NOT EXISTS users (
--     id SERIAL PRIMARY KEY,
--     username VARCHAR(50) NOT NULL,
--     password VARCHAR(50) NOT NULL
-- );

-- -- Insert an example user
-- INSERT INTO users (username, password) VALUES ('admin', 'admin_password');
