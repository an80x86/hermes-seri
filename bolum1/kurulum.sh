#!/bin/bash
# Bolum 1: Hermes Agent'i Docker'da sifirdan kurmak
VERI=~/hermes-b1
mkdir -p "$VERI/calisma"

# 1) API anahtari: ekrana yazmadan, kabuktaki degiskenden .env'e
printf 'OPENAI_API_KEY=%s\n' "$OPENAI_API_KEY" > "$VERI/.env"
chmod 600 "$VERI/.env"

# 2) Kisa yol: her komut yeni bir konteynerde calisir
hermes() {
  docker run --rm -v "$VERI:/opt/data" -w /opt/data/calisma \
    nousresearch/hermes-agent "$@"
}

# 3) Model ve saglayici
hermes config set model.default gpt-5.6-luna
hermes config set model.provider openai-api

# 4) Saglik kontrolu
hermes doctor
hermes status

# 5) Ilk konusma, maliyet raporuyla
hermes -z "Merhaba, kendini tek cümleyle tanıt." \
  --usage-file /opt/data/usage.json

# 6) Ayni soru, yalnizca hafiza araciyla
hermes -z "Merhaba, kendini tek cümleyle tanıt." -t memory \
  --usage-file /opt/data/usage_dar.json
