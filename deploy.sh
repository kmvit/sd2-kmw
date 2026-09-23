#!/usr/bin/env bash
# Выкладка вёрстки на тестовую площадку.
#
#   ./deploy.sh            пересобрать и залить (сайт закрыт от индексации)
#   ./deploy.sh --prod     то же, но собрать боевую версию — индексация открыта
#
# На сервер уезжает только то, что нужно браузеру: страницы, static/, иконки
# и robots.txt. Исходники, сборщик и макеты остаются в репозитории.
set -euo pipefail

HOST="${SD2_HOST:-root@201.24.62.135}"
DEST="${SD2_DEST:-/opt/sd2-kmv}"
cd "$(dirname "$0")"

python3 build.py "$@"

rsync -az --delete --delete-excluded \
  --include='*.html' \
  --include='favicon.ico' \
  --include='robots.txt' \
  --include='static/***' \
  --exclude='*' \
  ./ "$HOST:$DEST/"

ssh "$HOST" "chown -R www-data:www-data $DEST && find $DEST -type d -exec chmod 755 {} + && find $DEST -type f -exec chmod 644 {} +"

echo "выложено: $HOST:$DEST"
