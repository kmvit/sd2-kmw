#!/usr/bin/env bash
# Выкладка сайта на сервер.
#
#   ./deploy.sh              обновить код, зависимости, миграции и статику
#   ./deploy.sh --seed       дополнительно залить контент (первый запуск)
#   SD2_SSH="ssh -J vpn" ./deploy.sh   через промежуточный сервер, если напрямую не пускает
#
# На сервер уезжает только код: база, медиафайлы и виртуальное окружение
# живут там и не перезаписываются. Команды Django читают настройки из .env.
set -euo pipefail

HOST="${SD2_HOST:-ganin-prod2}"
DEST="${SD2_DEST:-/opt/sd2}"
SSH="${SD2_SSH:-ssh}"
cd "$(dirname "$0")"

rsync -az --delete -e "$SSH" \
  --include='manage.py' --include='requirements.txt' \
  --include='sd2_site/***' --include='core/***' --include='catalog/***' \
  --include='content/***' --include='leads/***' --include='calc/***' \
  --include='pages/***' --include='templates/***' --include='static/***' \
  --exclude='__pycache__' --exclude='*.pyc' --exclude='*' \
  ./ "$HOST:$DEST/"

$SSH "$HOST" "cd $DEST && set -a && . ./.env && set +a && \
  .venv/bin/pip install -q -r requirements.txt && \
  .venv/bin/python manage.py migrate --noinput && \
  .venv/bin/python manage.py collectstatic --noinput --clear >/dev/null && \
  chown -R www-data:www-data $DEST/media $DEST/staticfiles"

if [[ "${1:-}" == "--seed" ]]; then
  $SSH "$HOST" "cd $DEST && set -a && . ./.env && set +a && \
    .venv/bin/python manage.py seed_content && \
    .venv/bin/python manage.py seed_redirects"
fi

$SSH "$HOST" "systemctl restart sd2 && sleep 2 && systemctl is-active sd2"
echo "выложено: $HOST:$DEST"
