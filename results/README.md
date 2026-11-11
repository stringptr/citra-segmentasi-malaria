# Struktur hasil

- `progress1/` — hasil revisi sesuai `docs/report-progress1.md`: 32 citra
  (P. falciparum + P. vivax; 16 tuning, 16 uji; 2 citra per spesies per stadium per
  split), resize 50%. Berisi Eksperimen A (perbandingan metode segmentasi),
  Eksperimen B (pengaruh preprocessing), dan Eksperimen C (morfologi
  pasca-segmentasi: opening/closing, tiga ambang luas, object-level if-else).
- `legacy_20img/` — arsip desain sebelumnya: 20 citra P. falciparum (10 tuning,
  10 uji), resize 50%. Disimpan untuk jejak revisi, bukan hasil yang dilaporkan.
- `legacy_8img/` — arsip hasil eksperimen lama: 8 citra (4 train, 4 test),
  falciparum + vivax, stadium schizont, resolusi penuh.

Setiap eksperimen menyimpan: hasil per citra (`.csv`), ringkasan mean/median/std
(`_summary.csv`), narasi singkat (`_summary.md`), visualisasi overlay (`.png`), dan
parameter (`_params.json`). Eksperimen A juga menyimpan rincian per stadium dan per
spesies (`experiment_a_by_stage.csv`, `experiment_a_by_species.csv`).