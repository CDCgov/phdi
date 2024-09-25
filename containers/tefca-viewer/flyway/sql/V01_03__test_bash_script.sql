
CREATE OR REPLACE FUNCTION run_bash_script()
RETURNS VOID AS $$
BEGIN
    SELECT plsh('bash /docker-entrypoint-initdb.d/setup-env.sh');
END;
$$ LANGUAGE plpgsql;

SELECT run_bash_script();