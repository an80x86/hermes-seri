#!/bin/bash
# Bolum 2: Hermes'in sakladiklarini bulmak ve silmek
VERI=~/hermes-b2
hermes() { docker run --rm -v "$VERI:/opt/data" nousresearch/hermes-agent "$@"; }
say() { cat "$VERI"/state.db* "$VERI"/memories/*.md 2>/dev/null | grep -a -c "$1"; }

# 1) Neler saklaniyor?
hermes sessions list
cat "$VERI"/memories/*.md
say "Tekstil"

# 2) Oturumlari sil: satirlar gider, baytlar dosyada kalir
hermes sessions prune --older-than 0h --yes
say "Tekstil"

# 3) VACUUM: silinen baytlari dosyadan da at
hermes sessions optimize
say "Tekstil"

# 4) Hafiza dosyasi ayri: o satiri elle cikar
for f in "$VERI"/memories/*.md; do sed -i '' '/Tekstil/d' "$f"; done
say "Tekstil"
