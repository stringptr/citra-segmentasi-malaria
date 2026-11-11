# Ringkasan Eksperimen B

- Data: 32 citra (falciparum + vivax; 16 tuning, 16 uji), resize 50%.
- Kanal terpilih: `b`; polaritas `dark`.
- Setiap metode mempertahankan formulasi Eksperimen A sebagai baseline; hanya preprocessing yang divariasikan (faktor lain tetap).
- Pemilihan varian terbaik per metode memakai mean Dice pada train (16 citra tuning).

## Varian terbaik per metode (dipilih dari train)

- `Otsu multilevel 3`: varian `B4_bg_closing` (train Dice 0.1785); test Dice 0.2644 vs B1_median 0.0849 (delta +0.1795).
- `Adaptive threshold`: varian `B2_gaussian` (train Dice 0.1779); test Dice 0.1707 vs B1_median 0.1649 (delta +0.0058).
- `k-means k=3`: varian `B5_bg_opening` (train Dice 0.0445); test Dice 0.0325 vs B1_median 0.0252 (delta +0.0073).
- `Pixel if-else (tambahan)`: varian `B0_none` (train Dice 0.2387); test Dice 0.2095 vs B1_median 0.1998 (delta +0.0097).

## Mean Dice pada test per metode x varian

```
variant                   B0_none  B1_median  B2_gaussian  B3_clahe  B4_bg_closing  B5_bg_opening  B6_combo  B7_texture
method                                                                                                                 
Adaptive threshold         0.1601     0.1649       0.1707    0.0660         0.1151         0.1201    0.0449         NaN
Otsu multilevel 3          0.0649     0.0849       0.0841    0.0583         0.2644         0.1047    0.1201         NaN
Pixel if-else (tambahan)   0.2095     0.1998       0.1999    0.1999         0.1995         0.1054    0.1981      0.1766
k-means k=3                0.0258     0.0252       0.0252    0.0301         0.0548         0.0325    0.0345      0.0281
```

## Catatan

- `B5_bg_opening` adalah kontrol negatif: jika closing benar, varian opening seharusnya tidak lebih baik.
- `B7_texture` hanya berlaku untuk k-means dan pixel-if-else; Otsu/adaptive tidak dijalankan pada varian tekstur.
- Selisih Dice antar varian kecil dan berasal dari 16 citra uji; hasil tetap eksploratif, bukan klaim generalisasi.
- Eksperimen C (morfologi pasca-segmentasi, tiga ambang luas, object-level if-else) dijalankan pada sel berikutnya.