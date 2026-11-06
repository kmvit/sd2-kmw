#!/usr/bin/env bash
# Выкладка коммита из GitHub на сервер.
#
#   ./deploy.sh              git pull, зависимости, миграции, статика, перезапуск
#   ./deploy.sh --seed       дополнительно залить контент (только на пустой базе)
#   SD2_SSH="ssh -J vpn" ./deploy.sh   маршрут через vpn (по умолчанию)
#
# База, медиафайлы, .env и виртуальное окружение не входят в репозиторий.
set -euo pipefail

HOST="${SD2_HOST:-ganin-prod2}"
DEST="${SD2_DEST:-/opt/sd2}"
SSH="${SD2_SSH:-ssh -J vpn}"

$SSH "$HOST" "set -e; cd $DEST; \
  git fetch origin main; \
  git merge --ff-only origin/main; \
  set -a; . ./.env; set +a; \
  .venv/bin/pip install -q -r requirements.txt; \
  .venv/bin/python manage.py migrate --noinput; \
  .venv/bin/python manage.py collectstatic --noinput --clear >/dev/null; \
  chown -R www-data:www-data $DEST/media $DEST/staticfiles"

if [[ "${1:-}" == "--seed" ]]; then
  $SSH "$HOST" "set -e; cd $DEST; set -a; . ./.env; set +a; \
    .venv/bin/python manage.py seed_content; \
    .venv/bin/python manage.py seed_redirects"
fi

$SSH "$HOST" "systemctl restart sd2 && sleep 2 && systemctl is-active sd2"
echo "выложено из GitHub: $HOST:$DEST"
