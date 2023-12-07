
# RESET_DIR=${LIB_DIR:-/usr/local/lib}

createuser -U "ecr_viewer_user" -w ecr_viewer_app
createdb -U "ecr_viewer_user" -w ecr_viewer --maintenance-db="$POSTGRES_DB"


# psql -v ON_ERROR_STOP=1  -U "$POSTGRES_USER" simple_report -f "$RESET_DIR/reset-db.sql"