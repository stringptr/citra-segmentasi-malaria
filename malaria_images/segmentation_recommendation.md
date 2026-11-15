# Rekomendasi Segmentasi (Progress 1)

Metode terbaik pada data uji (Dice tertinggi):
- Otsu multilevel 3 + koreksi background closing: Dice ~0.2644
- Baseline tanpa preprocessing: Dice ~0.0849

Rekomendasi: gunakan Otsu multilevel 3 setelah koreksi background closing untuk citra mikroskopis Giemsa ini. Adaptive threshold dan k-means k=3 kurang cocok pada dataset ini.