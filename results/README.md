# Struktur hasil

- `progress1/` — hasil revisi sesuai `docs/report-progress1.md`: 20 citra P. falciparum
  (10 tuning, 10 uji), resize 50%. Berisi Eksperimen A (perbandingan metode segmentasi)
  dan Eksperimen B (pengaruh preprocessing).
- `legacy_8img/` — arsip hasil eksperimen lama: 8 citra (4 train, 4 test),
  falciparum + vivax, stadium schizont, resolusi penuh.
- Eksperimen C (morfologi pasca-segmentasi, tiga ambang luas, object-level if-else)
  belum dijalankan pada revisi ini.

Setiap eksperimen menyimpan: hasil per citra (`.csv`), ringkasan mean/median/std
(`_summary.csv`), narasi singkat (`_summary.md`), visualisasi overlay (`.png`), dan
parameter (`_params.json`).
