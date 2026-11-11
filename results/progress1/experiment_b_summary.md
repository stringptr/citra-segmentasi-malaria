# Ringkasan Eksperimen B

- Data: 20 citra P. falciparum (10 tuning, 10 uji), resize 50%.
- Kanal terpilih: `b`; polaritas `dark`.
- Setiap metode mempertahankan formulasi Eksperimen A sebagai baseline; hanya preprocessing yang divariasikan (faktor lain tetap).
- Pemilihan varian terbaik per metode memakai mean Dice pada train (10 citra tuning).

## Varian terbaik per metode (dipilih dari train)

- `Otsu multilevel 3`: varian `B4_bg_closing` (train Dice 0.1612); test Dice 0.1054 vs B1_median 0.0878 (delta +0.0176).
- `Adaptive threshold`: varian `B2_gaussian` (train Dice 0.0998); test Dice 0.0914 vs B1_median 0.0972 (delta -0.0059).
- `k-means k=3`: varian `B5_bg_opening` (train Dice 0.0630); test Dice 0.0440 vs B1_median 0.0336 (delta +0.0104).
- `Pixel if-else (tambahan)`: varian `B0_none` (train Dice 0.1149); test Dice 0.0846 vs B1_median 0.0845 (delta +0.0001).

## Mean Dice pada test per metode x varian

```
variant                   B0_none  B1_median  B2_gaussian  B3_clahe  B4_bg_closing  B5_bg_opening  B6_combo  B7_texture
method                                                                                                                 
Adaptive threshold         0.1018     0.0972       0.0914    0.0686         0.1232         0.0497    0.0373         NaN
Otsu multilevel 3          0.0901     0.0878       0.0872    0.0195         0.1054         0.0465    0.1023         NaN
Pixel if-else (tambahan)   0.0846     0.0845       0.0858    0.1027         0.1041         0.0911    0.1036      0.0762
k-means k=3                0.0346     0.0336       0.0347    0.0352         0.0349         0.0440    0.0378      0.0332
```

## Catatan

- `B5_bg_opening` adalah kontrol negatif: jika closing benar, varian opening seharusnya tidak lebih baik.
- `B7_texture` hanya berlaku untuk k-means dan pixel-if-else; Otsu/adaptive tidak dijalankan pada varian tekstur.
- Selisih Dice antar varian kecil dan berasal dari 10 citra uji; hasil tetap eksploratif, bukan klaim generalisasi.
- Eksperimen C (morfologi pasca-segmentasi, tiga ambang luas, object-level if-else) belum dijalankan.