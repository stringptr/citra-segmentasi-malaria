# Ringkasan Eksperimen C

- Data: 32 citra (falciparum + vivax; 16 tuning, 16 uji), resize 50%.
- Dua basis: Adaptive threshold (metode utama) dan Pixel if-else (metode tambahan).
- Ambang luas dari GT train: kecil 64 px, sedang 110 px, besar 249 px; `MIN_AREA` = 12 px.
- Pemilihan varian terbaik per basis memakai mean Dice pada train.

## Varian terbaik per basis (dipilih dari train)

- `Adaptive threshold`: varian `C5_area_small` (train Dice 0.1767); test Dice 0.1443 vs raw 0.1450; object recall 0.230 vs raw 0.288.
- `Pixel if-else (tambahan)`: varian `C7_area_large` (train Dice 0.2833); test Dice 0.1819 vs raw 0.1946; object recall 0.375 vs raw 0.464.

## Mean Dice pada test per basis x varian

```
variant                   C0_raw  C1_opening  C2_closing  C3_open_close  C4_area_min  C5_area_small  C6_area_medium  C7_area_large  C8_object_ifelse  C9_open_area_med
base_method                                                                                                                                                           
Adaptive threshold        0.1450      0.1629      0.1462         0.1636       0.1649         0.1443          0.0825         0.0478            0.1385            0.0752
Pixel if-else (tambahan)  0.1946      0.2018      0.1947         0.2025       0.1998         0.1991          0.1923         0.1819            0.1991            0.1948
```

## Catatan

- `C4_area_min` memakai `MIN_AREA` yang sama dengan Eksperimen A, sehingga harus mereproduksi Dice Eksperimen A untuk kedua basis.
- Filter luas besar berpotensi menghapus parasit asli; lihat penurunan object recall pada tabel `experiment_c_summary.csv`.
- Object-level if-else hanya memakai luas dan rata-rata warna per komponen; parameter dituning pada 16 citra tuning.
- Selisih Dice berasal dari 16 citra uji; hasil tetap eksploratif.