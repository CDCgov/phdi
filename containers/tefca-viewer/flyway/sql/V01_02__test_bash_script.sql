CREATE EXTENSION IF NOT EXISTS plsh;

SELECT plsh('bash /docker-entrypoint-initdb.d/setup-env.sh');
