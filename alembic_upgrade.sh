set -a && source .env && set +a
alembic upgrade head
exec $SHELL
