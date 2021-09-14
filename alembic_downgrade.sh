set -a && source .env && set +a
alembic downgrade -1
exec $SHELL
