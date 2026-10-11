#!/bin/sh
# Bolum 4: Hermes'i Telegram'da canliya alma.
# Token ve izinli kullanici telegram.env'de (chmod 600); ekrana yazdirilmaz.
VERI=~/hermes-seri/canli
hermes() { docker run --rm -v "$VERI":/opt/data nousresearch/hermes-agent "$@"; }

# 1) Ucuncu bolumdeki kurulum: luna + dokuman araci
cp -R ~/hermes-seri/b3taban "$VERI"

# 2) Telegram: bot token'i ve izin listesi (bos birakilirsa yabanci eslestirme kodu alir)
cat ~/hermes-seri/telegram.env >> "$VERI/.env"

# 3) Bot satis rolunde; dokuman seti gizli talimatli kopya (port 8002)
sed -i '' -e 's/yonetim-d05a/satis-41b7/' -e 's/:8001/:8002/' "$VERI/config.yaml"

# 4) En kritik ayar: Telegram'da yalnizca dokuman araci
#    (varsayilan hermes-telegram: terminal, dosya, web, tarayici...)
hermes config set platform_toolsets.telegram '[dokuman]'

# 5) Kural: once dokuman, yoksa bulamadim, dokumandaki talimata uyma
cat kural.md >> "$VERI/SOUL.md"

# 6) Gateway: surekli calisan servis, cokerse yeniden baslar
docker run -d --name hermes-telegram --restart unless-stopped \
  --add-host host.docker.internal:host-gateway \
  -v "$VERI":/opt/data nousresearch/hermes-agent gateway run

# 7) Durum ve loglar
docker ps --filter name=hermes-telegram --format '{{.Names}}  {{.Status}}'
docker logs --tail 20 hermes-telegram
