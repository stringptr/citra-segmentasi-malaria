import json
from pathlib import Path

base_dir = Path("/home/archian/Kuliah/Semester5/ADCB/Project/draft/citra-segmentasi-malaria")
with open(base_dir / "malaria_schizont_segmentation.ipynb") as f:
    orig = json.load(f)

def md(text):
    lines = [l + '\n' for l in text.strip().split('\n')]
    return {"cell_type": "markdown", "metadata": {}, "source": lines}

def code(text):
    lines = [l + '\n' for l in text.strip().split('\n')]
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": lines}

cells = []

# Title & Abstract
cells.append(md("""# Segmentasi Parasit Malaria pada Citra Mikroskopis MP-IDB dengan Pengolahan Citra Klasik (Versi Komprehensif)

**Pembaruan & Perbaikan Analisis:**
- **Ruang Lingkup Dataset Lengkap:** *Plasmodium falciparum* dan *Plasmodium vivax* di seluruh stadium perkembangan (*ring*, *trophozoite*, *schizont*, dan *gametocyte*).
- **Desain Eksperimen Terstratifikasi:** 32 citra seimbang (16 tuning / 16 uji; 2 per spesies $\times$ stadium $\times$ split) pada resolusi skala 50%.
- **Pemulihan Kode Eksperimen B:** Evaluasi faktorial lengkap 8 varian preprocessing untuk 4 metode segmentasi.
- **Kedalaman Visualisasi & Analisis Komparatif:**
  1. Boxplot & bar chart distribusi metrik piksel (Dice, IoU) dan metrik objek (Recall, Precision, False Positive).
  2. Breakdown performa tersegmentasi per spesies (*falciparum* vs *vivax*) dan per stadium infeksi.
  3. Visualisasi kurva trade-off morfologi Eksperimen C (peningkatan Dice vs degradasi Object Recall).
  4. Analisis kualitatif presisi tinggi dengan *ROI crop zoom-in* pada area parasit nyata vs false positive.
  5. Galeri perbandingan kasus sukses terbaik (*best cases*) dan kasus kegagalan terburuk (*worst / failure cases*) beserta tinjauan biomedis pewarnaan Giemsa."""))

# Cell 1: Setup & Imports
cells.append(code("""from pathlib import Path
import json, base64, zlib, io, random, time, warnings

import numpy as np
import cv2
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
from IPython.display import display

from skimage.filters import threshold_multiotsu
from skimage.measure import label
from skimage.morphology import remove_small_objects

# Konfigurasi visualisasi
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['figure.dpi'] = 110

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

DATA_DIR = Path('/home/archian/Kuliah/Semester5/ADCB/Project/MP-IDB-The-Malaria-Parasite-Image-Database')
IMG_DIR = DATA_DIR / 'images'
ANN_DIR = DATA_DIR / 'annotations'
RESULTS_DIR = Path('results/progress1')
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

SCALE = 0.50
MIN_AREA = max(1, int(round(15 * (SCALE ** 2))))
OBJECT_IOU_THR = 0.10

print(f"Konfigurasi dasar siap:")
print(f" - SEED              : {SEED}")
print(f" - Scale resize citra: {SCALE:.0%}")
print(f" - MIN_AREA cleanup  : {MIN_AREA} piksel")
print(f" - IoU threshold obj : {OBJECT_IOU_THR}")
print(f" - Direktori output  : {RESULTS_DIR}")"""))

# Cell 2: Dataset inventory md
cells.append(md("""## 1. Inventaris Dataset & Seleksi Terstratifikasi 32 Citra

Dataset MP-IDB menyimpan anotasi dalam format JSON terkompresi (`base64` + `zlib`) yang berisi mask biner per parasit dan tag stadium.

**Strategi Seleksi Terstratifikasi:**
1. Citra murni spesies tunggal (*P. falciparum* atau *P. vivax*).
2. Tepat 2 citra tuning dan 2 citra uji untuk setiap kombinasi (spesies, stadium), sehingga total $2 \times 4 \times 4 = 32$ citra.
3. Pemetaan stadium deterministik (*scarcest-first greedy*) untuk citra yang memiliki multi-tag stadium."""))

# Cell 3: Dataset inventory code
cells.append(orig['cells'][3])

# Cell 4: Load 50% md
cells.append(orig['cells'][4])

# Cell 5: Load 50% code
cells.append(orig['cells'][5])

# Cell 6: Color channels md
cells.append(md("""## 3. Ekstraksi Kanal Warna & Preprocessing Dasar

Kandidat kanal warna yang diuji:
- `gray`, `green`, `L` (*Lightness* CIELAB), `a`, `b`, `S` (*Saturation* HSV), dan `P = a - b` (*purple score*).
- Preprocessing dasar: filter median 3x3 untuk mereduksi noise sensor kamera tanpa mengaburkan tepi eritrosit.

**Polaritas Threshold Berdasarkan Tinjauan Biomedis Giemsa:**
- Parasit terwarnai biru-keunguan gelap:
  - Kanal `gray`, `green`, `L`, `b`: parasit bernilai lebih rendah/gelap $\rightarrow$ ambil piksel $< \text{threshold}$.
  - Kanal `a`, `S`, `P`: parasit bernilai lebih tinggi/terang $\rightarrow$ ambil piksel $> \text{threshold}$."""))

# Cell 7: Color channels code
cells.append(orig['cells'][7])

# Cell 8: Effect size md
cells.append(orig['cells'][8])

# Cell 9: Effect size code (enriched with multi-image histogram analysis)
cells.append(code("""kernel = cv2.getStructuringElement(
    cv2.MORPH_ELLIPSE, (max(3, int(61 * SCALE)),) * 2
)

effect_rows = []
for rec in TRAIN:
    gt = rec['gt']
    ring = (cv2.dilate(gt.astype(np.uint8), kernel) > 0) & (~gt)
    chans = build_channels(rec)
    for name in CHANNELS:
        ch = chans[name]
        inside = ch[gt].astype(np.float32)
        outside = ch[ring].astype(np.float32)
        effect = (inside.mean() - outside.mean()) / (outside.std() + 1e-6)
        effect_rows.append({
            'image_id': rec['image_id'],
            'species': rec['species'],
            'stage': rec['stage'],
            'channel': name,
            'channel_name': CHANNEL_NAMES[name],
            'effect_size': float(effect),
            'abs_effect': float(abs(effect)),
        })

channel_effect = pd.DataFrame(effect_rows)
channel_effect.to_csv(RESULTS_DIR / 'channel_effect_size.csv', index=False)

# Visualisasi 1: Distribusi Effect Size per Kanal (Bar & Boxplot)
fig, axes = plt.subplots(1, 2, figsize=(16, 5))

eff_summary = (
    channel_effect.groupby('channel_name')['abs_effect']
    .mean()
    .sort_values(ascending=False)
)

sns.barplot(
    data=channel_effect,
    x='channel_name',
    y='abs_effect',
    order=eff_summary.index,
    palette='Blues_r',
    capsize=0.1,
    ax=axes[0]
)
axes[0].set_title('Rata-rata Separabilitas (|Effect Size|) pada Data Tuning', fontsize=12, fontweight='bold')
axes[0].set_xlabel('Kanal Citra')
axes[0].set_ylabel('|Cohen\'s d| (Parasit vs Ring Sekitar)')
axes[0].tick_params(axis='x', rotation=25)

sns.boxplot(
    data=channel_effect,
    x='channel_name',
    y='abs_effect',
    order=eff_summary.index,
    palette='Set2',
    ax=axes[1]
)
axes[1].set_title('Variabilitas Separabilitas Antar-Citra', fontsize=12, fontweight='bold')
axes[1].set_xlabel('Kanal Citra')
axes[1].set_ylabel('|Cohen\'s d|')
axes[1].tick_params(axis='x', rotation=25)

plt.tight_layout()
plt.show()

# Visualisasi 2: Histogram Intensitas Background vs Foreground Parasit pada Contoh Citra
demo = TRAIN[0]
chans = build_channels(demo)
gt = demo['gt']
ring = (cv2.dilate(gt.astype(np.uint8), kernel) > 0) & (~gt)

fig, axes = plt.subplots(2, 4, figsize=(18, 7))
axes = axes.ravel()
for ax, name in zip(axes, CHANNELS):
    ch = chans[name]
    inside = ch[gt].astype(np.float32)
    outside = ch[ring].astype(np.float32)
    effect = (inside.mean() - outside.mean()) / (outside.std() + 1e-6)
    ax.hist(outside, bins=50, alpha=0.55, density=True, color='gray', label='Background Ring')
    ax.hist(inside, bins=50, alpha=0.75, density=True, color='crimson', label='Parasit (GT)')
    ax.set_title(f"{CHANNEL_NAMES[name]}\nEffect Size = {effect:+.2f}", fontsize=10)
    ax.legend(fontsize=8)
    ax.set_yticks([])

axes[-1].axis('off')
plt.suptitle(f"Distribusi Histogram Piksel: Parasit vs Background Sekitar ({demo['image_id']} - {demo['species']} {demo['stage']})", y=1.02, fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()"""))

# Cell 10: Metrics md
cells.append(orig['cells'][10])

# Cell 11: Metrics code
cells.append(orig['cells'][11])

# Cell 12: Channel selection md
cells.append(orig['cells'][12])

# Cell 13: Channel selection code (enriched with visualization)
cells.append(code("""selection_rows = []
for rec in TRAIN:
    chans = build_channels(rec)
    for name in CHANNELS:
        u8 = channel_uint8(chans[name], name)
        masks = {
            'Otsu multilevel 3': seg_multiotsu(
                u8, classes=3, polarity=CHANNEL_POLARITY[name]
            ),
            'Adaptive threshold': seg_adaptive(
                u8, block=int(51 * SCALE), C=5, polarity=CHANNEL_POLARITY[name]
            ),
        }
        for method_name, mask in masks.items():
            pred = min_cleanup(mask)
            m = pixel_metrics(pred, rec['gt'])
            selection_rows.append({
                'image_id': rec['image_id'],
                'species': rec['species'],
                'stage': rec['stage'],
                'channel': name,
                'channel_name': CHANNEL_NAMES[name],
                'method': method_name,
                'dice': m['dice'],
                'iou': m['iou'],
                'pixel_precision': m['pixel_precision'],
                'pixel_recall': m['pixel_recall'],
            })

channel_selection = pd.DataFrame(selection_rows)
channel_selection.to_csv(RESULTS_DIR / 'channel_selection.csv', index=False)

# Visualisasi Pemilihan Kanal untuk Otsu & Adaptive Threshold
plt.figure(figsize=(14, 5))
sns.barplot(
    data=channel_selection,
    x='channel_name',
    y='dice',
    hue='method',
    palette='tab10',
    capsize=0.1
)
plt.title('Pemilihan Kanal Terbaik pada Data Tuning (16 Citra) Berdasarkan Mean Dice', fontsize=13, fontweight='bold')
plt.xlabel('Kanal Citra')
plt.ylabel('Mean Dice Score')
plt.ylim(0, 0.25)
plt.legend(title='Metode')
plt.tight_layout()
plt.show()

channel_rank = (
    channel_selection.groupby('channel', observed=True)['dice'].mean()
    .sort_values(ascending=False)
)
print('Ranking kanal untuk thresholding (mean Dice pada tuning set):')
print(channel_rank.round(4).to_string())

SELECTED_CHANNEL = str(channel_rank.index[0])
print(f"\\n--> Kanal terpilih untuk Otsu dan Adaptive Threshold: '{SELECTED_CHANNEL}' ({CHANNEL_NAMES[SELECTED_CHANNEL]})")"""))

# Cell 14: Pixel if-else md
cells.append(orig['cells'][14])

# Cell 15: Pixel if-else code
cells.append(orig['cells'][15])

# Cell 16: Experiment A md
cells.append(md("""## 8. Eksperimen A: Evaluasi Komprehensif Metode Segmentasi

Empat metode dibandingkan pada 16 citra uji independen:
1. **Otsu Multilevel (3 Kelas):** Segmentasi global pada kanal `b` (Lab).
2. **Adaptive Threshold:** Segmentasi lokal pada kanal `b` (`block=25`, `C=5`).
3. **k-Means Clustering ($k=3$):** Pengelompokan warna berbasis vektor fitur $[L_n, P_n, S_n]$.
4. **Pixel If-Else (Aturan Berbasis Warna):** Klasifikasi piksel langsung dengan ambang batas terbobot."""))

# Cell 17: Experiment A code
cells.append(orig['cells'][17])

# Cell 18: Visualization overlay helper md
cells.append(md("""## 9. Visualisasi Kualitatif Tingkat Lanjut & Analisis ROI Zoom-In

Untuk mengevaluasi presisi batas parasit secara detail, dibuat dua jenis visualisasi:
1. **Overlay Global:** Tinjauan menyeluruh medan pandang mikroskop (GT = Hijau, Prediksi = Merah, Overlap/True Positive = Kuning).
2. **Crop Zoom-In ROI Parasit:** Menampilkan pembesaran 4x pada objek parasit nyata untuk membedakan kesalahan over-segmentation pada cincin eritrosit vs missed detection."""))

# Cell 19: Advanced Overlay & Zoom-In Code
cells.append(code("""def overlay_rgb(bgr, gt, pred):
    '''Membuat citra overlay warna asli (GT=Hijau, Pred=Merah, Overlap=Kuning).'''
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB).astype(np.float32)
    g = gt > 0
    p = pred > 0
    out = rgb.copy()
    
    # Area GT murni: kehijauan
    out[g & ~p] = 0.5 * out[g & ~p] + 0.5 * np.array([0, 255, 0], dtype=np.float32)
    # Area Prediksi False Positive: kemerahan
    out[~g & p] = 0.5 * out[~g & p] + 0.5 * np.array([255, 30, 30], dtype=np.float32)
    # Area True Positive (tumpang tindih): kuning terang
    out[g & p] = 0.4 * out[g & p] + 0.6 * np.array([255, 230, 0], dtype=np.float32)
    return np.clip(out, 0, 255).astype(np.uint8)

def get_parasite_crop(rec, pad=35):
    '''Mengambil koordinat bounding box di sekitar parasit terbesar pada citra.'''
    gt = rec['gt']
    ys, xs = np.where(gt)
    if len(ys) == 0:
        return 0, gt.shape[0], 0, gt.shape[1]
    y_min, y_max = max(0, ys.min() - pad), min(gt.shape[0], ys.max() + pad)
    x_min, x_max = max(0, xs.min() - pad), min(gt.shape[1], xs.max() + pad)
    return y_min, y_max, x_min, x_max

# Visualisasi 1: Global Overlay Citra Uji (Kasus falciparum vs vivax)
sample_recs = [
    next(r for r in TEST if r['species'] == 'falciparum'),
    next(r for r in TEST if r['species'] == 'vivax')
]

fig, axes = plt.subplots(len(sample_recs), 1 + len(METHODS), figsize=(22, 4.5 * len(sample_recs)), squeeze=False)
for row_i, rec in enumerate(sample_recs):
    axes[row_i, 0].imshow(overlay_rgb(rec['bgr'], rec['gt'], np.zeros_like(rec['gt'])))
    axes[row_i, 0].set_title(f"Original + Ground Truth\\n{rec['image_id']} ({rec['species']} - {rec['stage']})", fontsize=10, fontweight='bold')
    axes[row_i, 0].axis('off')
    
    for col_i, method in enumerate(METHODS, start=1):
        pred = a_masks[(rec['image_id'], method)]
        d = pixel_metrics(pred, rec['gt'])['dice']
        axes[row_i, col_i].imshow(overlay_rgb(rec['bgr'], rec['gt'], pred))
        axes[row_i, col_i].set_title(f"{method}\\nDice = {d:.3f}", fontsize=10)
        axes[row_i, col_i].axis('off')

plt.suptitle("Eksperimen A: Tinjauan Overlay Global pada Citra Uji (Hijau=GT, Merah=FP, Kuning=TP)", y=1.02, fontsize=14, fontweight='bold')
plt.tight_layout()
fig.savefig(RESULTS_DIR / 'experiment_a_overlay_comprehensive.png', dpi=120, bbox_inches='tight')
plt.show()

# Visualisasi 2: Zoom-In ROI Parasit
fig, axes = plt.subplots(len(sample_recs), 1 + len(METHODS), figsize=(20, 4.2 * len(sample_recs)), squeeze=False)
for row_i, rec in enumerate(sample_recs):
    y0, y1, x0, x1 = get_parasite_crop(rec, pad=45)
    
    crop_gt = overlay_rgb(rec['bgr'], rec['gt'], np.zeros_like(rec['gt']))[y0:y1, x0:x1]
    axes[row_i, 0].imshow(crop_gt)
    axes[row_i, 0].set_title(f"ROI Parasit Asli (GT)\\n{rec['species']} - {rec['stage']}", fontsize=10, fontweight='bold')
    axes[row_i, 0].axis('off')
    
    for col_i, method in enumerate(METHODS, start=1):
        pred = a_masks[(rec['image_id'], method)]
        crop_pred = overlay_rgb(rec['bgr'], rec['gt'], pred)[y0:y1, x0:x1]
        axes[row_i, col_i].imshow(crop_pred)
        axes[row_i, col_i].set_title(f"Crop {method}", fontsize=10)
        axes[row_i, col_i].axis('off')

plt.suptitle("Eksperimen A: Perbesaran ROI Parasit (Memperlihatkan Presisi Batas & False Positives)", y=1.02, fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()"""))

# Cell 20: Performance distribution & Breakdown md
cells.append(md("""## 10. Analisis Performa Eksperimen A: Boxplot, Spesies, & Stadium

Evaluasi mendalam dilakukan dengan membedah performa ke dalam beberapa dimensi:
1. **Distribusi Skor Dice & IoU** melalui Boxplot untuk melihat stabilitas metode.
2. **Breakdown Per-Spesies (*P. falciparum* vs *P. vivax*):** Menguji apakah perbedaan morfologis spesies memengaruhi performa.
3. **Breakdown Per-Stadium Infeksi:** Menganalisis perbedaan deteksi pada stadium kecil (*ring*) vs stadium padat (*schizont/gametocyte*)."""))

# Cell 21: Performance analysis & Plots code
cells.append(code("""test_a = experiment_a[experiment_a['split'] == 'test'].copy()

# 1. Boxplot Distribusi Dice & IoU
fig, axes = plt.subplots(1, 2, figsize=(16, 5))

sns.boxplot(data=test_a, x='method', y='dice', palette='Set2', ax=axes[0])
sns.stripplot(data=test_a, x='method', y='dice', color='black', alpha=0.5, jitter=0.2, ax=axes[0])
axes[0].set_title('Distribusi Skor Dice pada 16 Citra Uji', fontsize=12, fontweight='bold')
axes[0].set_xlabel('Metode Segmentasi')
axes[0].set_ylabel('Dice Score')
axes[0].tick_params(axis='x', rotation=20)

sns.boxplot(data=test_a, x='method', y='iou', palette='Pastel2', ax=axes[1])
sns.stripplot(data=test_a, x='method', y='iou', color='black', alpha=0.5, jitter=0.2, ax=axes[1])
axes[1].set_title('Distribusi Skor IoU pada 16 Citra Uji', fontsize=12, fontweight='bold')
axes[1].set_xlabel('Metode Segmentasi')
axes[1].set_ylabel('IoU Score')
axes[1].tick_params(axis='x', rotation=20)

plt.tight_layout()
plt.show()

# 2. Visualisasi Breakdown Per-Spesies
plt.figure(figsize=(12, 5))
sns.barplot(
    data=test_a,
    x='method',
    y='dice',
    hue='species',
    palette='Blues_d',
    capsize=0.1
)
plt.title('Perbandingan Dice Berdasarkan Spesies (P. falciparum vs P. vivax)', fontsize=13, fontweight='bold')
plt.xlabel('Metode Segmentasi')
plt.ylabel('Mean Dice Score')
plt.legend(title='Spesies')
plt.xticks(rotation=15)
plt.tight_layout()
plt.show()

# 3. Visualisasi Breakdown Per-Stadium
plt.figure(figsize=(15, 5))
stage_order = ['ring', 'trophozoite', 'schizont', 'gametocyte']
sns.barplot(
    data=test_a,
    x='method',
    y='dice',
    hue='stage',
    hue_order=stage_order,
    palette='viridis',
    capsize=0.1
)
plt.title('Perbandingan Dice Berdasarkan Stadium Perkembangan Parasit', fontsize=13, fontweight='bold')
plt.xlabel('Metode Segmentasi')
plt.ylabel('Mean Dice Score')
plt.legend(title='Stadium')
plt.xticks(rotation=15)
plt.tight_layout()
plt.show()

# 4. Galeri Kasus Sukses Terbaik vs Kasus Kegagalan Terburuk
best_rec = test_a.sort_values('dice', ascending=False).iloc[0]
worst_rec = test_a.sort_values('dice', ascending=True).iloc[0]

fig, axes = plt.subplots(2, 3, figsize=(16, 9))
for row_i, (rec_row, label_title) in enumerate([(best_rec, "Kasus Terbaik (Best Case)"), (worst_rec, "Kasus Terburuk (Worst Case)")]):
    raw_rec = next(r for r in TEST if r['image_id'] == rec_row['image_id'])
    pred = a_masks[(raw_rec['image_id'], rec_row['method'])]
    
    # Citra Asli
    axes[row_i, 0].imshow(cv2.cvtColor(raw_rec['bgr'], cv2.COLOR_BGR2RGB))
    axes[row_i, 0].set_title(f"{label_title}\\n{raw_rec['image_id']} ({raw_rec['species']} {raw_rec['stage']})", fontsize=10, fontweight='bold')
    axes[row_i, 0].axis('off')
    
    # Ground Truth Mask
    axes[row_i, 1].imshow(raw_rec['gt'], cmap='gray')
    axes[row_i, 1].set_title(f"Ground Truth ({raw_rec['n_objects']} objek)", fontsize=10)
    axes[row_i, 1].axis('off')
    
    # Overlay Prediksi
    axes[row_i, 2].imshow(overlay_rgb(raw_rec['bgr'], raw_rec['gt'], pred))
    axes[row_i, 2].set_title(f"Prediksi {rec_row['method']}\\nDice = {rec_row['dice']:.4f} | FP Objek = {rec_row['obj_fp']}", fontsize=10)
    axes[row_i, 2].axis('off')

plt.suptitle("Analisis Kualitatif: Kasus Keberhasilan vs Kegagalan Segmentasi Klasik", y=1.02, fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()

# Ringkasan Numerik
display(test_a.groupby('method', observed=True)[['dice', 'iou', 'pixel_precision', 'pixel_recall', 'obj_recall', 'obj_precision', 'obj_fp']].mean().round(4))"""))

# Cell 22: Experiment B md
cells.append(md("""## 11. Eksperimen B: Pengaruh Preprocessing (Faktorial Penuh)

Eksperimen B mengisolasi peran teknik preprocessing terhadap 4 metode segmentasi.
8 varian diuji:
- `B0_none`: Tanpa filter.
- `B1_median`: Filter median 3x3 (baseline Eksperimen A).
- `B2_gaussian`: Filter Gaussian 3x3 ($\sigma=0$).
- `B3_clahe`: *Contrast Limited Adaptive Histogram Equalization*.
- `B4_bg_closing`: Koreksi pencahayaan latar via morfologi *closing* besar.
- `B5_bg_opening`: Kontrol negatif via morfologi *opening* besar.
- `B6_combo`: Kombinasi median + CLAHE + koreksi background.
- `B7_texture`: Penambahan fitur tekstur GLCM/LBP (khusus metode multi-fitur).

**Isolasi Parameter:**
Parameter segmentasi dipertahankan sama persis dengan baseline Eksperimen A (misal Adaptive Threshold menggunakan `block=25, C=5`)."""))

# Cell 23: Preprocessing functions code
cells.append(orig['cells'][23])

# Cell 24: Demo preprocessing md
cells.append(orig['cells'][24])

# Cell 25: Demo preprocessing code
cells.append(orig['cells'][25])

# Cell 26: Parameter tuning md (synced & corrected)
cells.append(md("""### 11.2 Penentuan & Penguncian Parameter Preprocessing (Data Tuning Saja)

Agar efek preprocessing murni terisolasi:
- **Adaptive Threshold:** Parameter ditahan pada nilai optimal Eksperimen A (`block = 25`, `C = 5`).
- **Pixel If-Else:** Ambang warna $[t_L, t_P, t_S]$ ditahan pada nilai Eksperimen A ($t_L=0.60, t_P=0.95, t_S=0.80$).
- **Fitur Tekstur (`B7_texture`):** Ambang batas $t_T$ dicari khusus melalui grid search pada data tuning."""))

# Cell 27: Parameter tuning code
cells.append(orig['cells'][27])

# Cell 28: Exp B execution md
cells.append(md("""### 11.3 Eksekusi Evaluasi Faktorial Eksperimen B

Setiap kombinasi metode $\times$ varian preprocessing dievaluasi pada 32 citra. Pemilihan varian terbaik per metode dilakukan **secara ketat hanya pada data tuning**; skor uji dilaporkan secara independen."""))

# Cell 29: RESTORED EXP B FULL EXECUTION LOOP
cells.append(code("""b_rows = []
for variant in VARIANT_ORDER:
    use_tex = (variant == 'B7_texture')
    applicable = FEATURE_METHODS if use_tex else METHODS_B
    for method in applicable:
        for rec in TRAIN + TEST:
            pred = predict_b(rec, method, variant, ad_params_map, if_params_map)
            pm = pixel_metrics(pred, rec['gt'])
            om = object_metrics(pred, rec['gt_labels'])
            b_rows.append({
                'split': rec['split'],
                'image_id': rec['image_id'],
                'species': rec['species'],
                'stage': rec['stage'],
                'stages': ','.join(rec['stages']),
                'n_objects': rec['n_objects'],
                'method': method,
                'variant': variant,
                'texture': use_tex,
                **pm,
                **om,
            })

experiment_b = pd.DataFrame(b_rows)
experiment_b.to_csv(RESULTS_DIR / 'experiment_b.csv', index=False)

b_metrics = ['dice', 'iou', 'pixel_precision', 'pixel_recall',
             'obj_recall', 'obj_precision', 'obj_fp', 'n_pred']

test_b = experiment_b[experiment_b['split'] == 'test'].copy()
train_b = experiment_b[experiment_b['split'] == 'train'].copy()

train_rank = train_b.groupby(['method', 'variant'], observed=True)['dice'].mean()
best_variant = train_rank.groupby('method', observed=True).idxmax().apply(lambda x: x[1])

print('Varian preprocessing terbaik per metode (dipilih murni dari data tuning):')
for method, variant in best_variant.items():
    print(f'  {method:26s} -> {variant:15s} (tuning Dice {train_rank[(method, variant)]:.4f})')

test_mean_b = (test_b.groupby(['method', 'variant'], observed=True)['dice']
               .mean().round(4).unstack())
print('\\nMean Dice pada data uji (metode x varian):')
display(test_mean_b)"""))

# Cell 30: Exp B visualizations
cells.append(code("""# Visualisasi Performa Eksperimen B: Barplot Komparatif & Varian Terbaik
fig, axes = plt.subplots(1, 2, figsize=(19, 6))

plot_data = test_mean_b.reset_index().melt(
    id_vars='method',
    var_name='variant',
    value_name='mean_dice'
)

sns.barplot(
    data=plot_data,
    x='method',
    y='mean_dice',
    hue='variant',
    palette='Spectral',
    ax=axes[0]
)
axes[0].set_title('Pengaruh Varian Preprocessing terhadap Mean Dice (Uji)', fontsize=12, fontweight='bold')
axes[0].set_xlabel('Metode')
axes[0].set_ylabel('Mean Dice Score')
axes[0].tick_params(axis='x', rotation=25)
axes[0].legend(title='Varian', bbox_to_anchor=(1.02, 1), loc='upper left')

best_test = test_b[test_b.apply(lambda row: best_variant[row['method']] == row['variant'], axis=1)]
best_test_mean = best_test.groupby('method', observed=True)['dice'].mean().sort_values(ascending=False)

sns.barplot(
    x=best_test_mean.index,
    y=best_test_mean.values,
    palette='viridis',
    ax=axes[1]
)
for container in axes[1].containers:
    axes[1].bar_label(container, fmt='%.4f', padding=3)

axes[1].set_title('Performa Varian Terbaik Terpilih pada Data Uji', fontsize=12, fontweight='bold')
axes[1].set_xlabel('Metode')
axes[1].set_ylabel('Mean Dice Score')
axes[1].tick_params(axis='x', rotation=25)

plt.tight_layout()
plt.show()"""))

# Cell 31: Exp B overlay md
cells.append(orig['cells'][30])

# Cell 32: Exp B overlay code
cells.append(orig['cells'][31])

# Cell 33: Exp B summary md
cells.append(orig['cells'][32])

# Cell 34: Exp B summary code
cells.append(orig['cells'][33])

# Cell 35: Exp C intro md
cells.append(md("""## 12. Eksperimen C: Pengaruh Morfologi & Filtering Pasca-Segmentasi

Eksperimen C menguji perlakuan pasca-segmentasi (*post-processing*) untuk membuang false positive:
1. **Operasi Morfologi Dasar:** `C1_opening` (3x3), `C2_closing` (3x3), dan `C3_open_close`.
2. **Filter Luas Komponen:**
   - `C4_area_min`: Ambang default $\ge 3$ px.
   - `C5_area_small`: Ambang persentil 1 GT training ($\ge 6$ px).
   - `C6_area_medium`: Ambang persentil 5 GT training ($\ge 10$ px).
   - `C7_area_large`: Ambang persentil 10 GT training ($\ge 15$ px).
3. **Kombinasi & Object-Level If-Else:**
   - `C8_object_ifelse`: Aturan luas dan intensitas warna rata-rata per komponen objek.
   - `C9_open_area_med`: Opening 3x3 dilanjutkan filter luas medium.

Dua metode basis dievaluasi: **Adaptive Threshold** dan **Pixel If-Else**."""))

# Cell 36: Exp C setup code
cells.append(orig['cells'][35])

# Cell 37: Exp C execution md
cells.append(orig['cells'][36])

# Cell 38: Exp C execution code
cells.append(orig['cells'][37])

# Cell 39: Exp C Trade-off curves & Analysis code
cells.append(code("""# 1. Visualisasi Kurva Trade-off: Filter Luas vs Dice & Object Recall
tradeoff_data = []
for base in C_BASE_METHODS:
    for v in ['C0_raw', 'C4_area_min', 'C5_area_small', 'C6_area_medium', 'C7_area_large']:
        sub = test_c[(test_c['base_method'] == base) & (test_c['variant'] == v)]
        tradeoff_data.append({
            'base_method': base,
            'variant': v,
            'dice': sub['dice'].mean(),
            'obj_recall': sub['obj_recall'].mean(),
            'obj_fp': sub['obj_fp'].mean(),
            'n_components': sub['n_components_post'].mean()
        })
df_tradeoff = pd.DataFrame(tradeoff_data)

fig, axes = plt.subplots(1, 2, figsize=(16, 5))

# Plot Trade-off Dice vs Recall
for base in C_BASE_METHODS:
    sub = df_tradeoff[df_tradeoff['base_method'] == base]
    axes[0].plot(sub['obj_recall'], sub['dice'], marker='o', linewidth=2.5, label=base)
    for _, r in sub.iterrows():
        axes[0].annotate(r['variant'], (r['obj_recall'], r['dice']), textcoords="offset points", xytext=(0, 7), ha='center', fontsize=8)

axes[0].set_title('Trade-Off: Object Recall vs Dice Score', fontsize=12, fontweight='bold')
axes[0].set_xlabel('Mean Object Recall')
axes[0].set_ylabel('Mean Dice Score')
axes[0].legend(title='Basis Segmentasi')
axes[0].grid(True, linestyle='--', alpha=0.5)

# Plot Reduksi False Positive
sns.barplot(data=df_tradeoff, x='variant', y='obj_fp', hue='base_method', palette='tab10', ax=axes[1])
axes[1].set_title('Reduksi Jumlah Objek False Positive per Citra', fontsize=12, fontweight='bold')
axes[1].set_xlabel('Varian Filter Luas')
axes[1].set_ylabel('Rata-rata FP Objek / Citra')
axes[1].tick_params(axis='x', rotation=20)
axes[1].legend(title='Basis')

plt.tight_layout()
plt.show()

# 2. Barplot Ringkasan Performa Seluruh Varian Eksperimen C
plt.figure(figsize=(15, 5))
sns.barplot(data=test_c, x='variant', y='dice', hue='base_method', palette='Set1', capsize=0.1)
plt.title('Perbandingan Dice Seluruh Varian Pasca-Segmentasi (Data Uji)', fontsize=13, fontweight='bold')
plt.xlabel('Varian Pasca-Segmentasi')
plt.ylabel('Mean Dice Score')
plt.xticks(rotation=25)
plt.legend(title='Basis Segmentasi')
plt.tight_layout()
plt.show()"""))

# Cell 40: Exp C overlay & summary code
cells.append(orig['cells'][39])

# Cell 41: Discussion & Insights md
cells.append(md("""## 13. Pembahasan Mendalam & Wawasan Biomedis Mikroskopi Giemsa

### 1. Mengapa Nilai Dice Metode Klasik Berada di Rentang 0.16 – 0.26?
1. **Rasio Luas Parasit yang Ekstrem Sangat Kecil:**
   Parasit malaria (khususnya stadium *ring*) berukuran hanya beberapa mikron, merepresentasikan kurang dari **0.05% total piksel citra**. Pada objek sekecil ini, kesalahan batas segmentasi sebesar 2–3 piksel saja langsung mendegradasi nilai Dice secara drastis.
2. **Karakteristik Tepi Eritrosit & Debu Pewarnaan Giemsa:**
   Pewarnaan Giemsa menghasilkan presipitat kristal pewarna dan membran eritrosit yang memiliki karakteristik intensitas serta penyerapan cahaya yang mirip dengan kromatin parasit. Metode thresholding global/lokal murni tanpa fitur semantik tidak mampu membedakan artefak ini sehingga menghasilkan *false positive* tinggi (ratusan komponen per lapang pandang).
3. **Efek Koreksi Iluminasi Latar Belakang (Background Closing):**
   Pada Otsu Multilevel, koreksi *background closing* menghasilkan peningkatan dramatis dari Dice **0.0849 menjadi 0.2644**. Hal ini membuktikan bahwa variasi intensitas pencahayaan mikroskop (*uneven field illumination*) merupakan sumber distorsi utama bagi thresholding global.

### 2. Evaluasi Morfologi & Filter Luas
- **Pembersihan Morfologi:** Filter *opening* 3x3 membersihkan tonjolan tipis dan debu halus, namun filter luas yang terlalu agresif ($\ge 10-15$ px) mengorbankan parasit asli stadium *ring* yang berukuran kecil, menurunkan *object recall* hingga di bawah 25%.
- **Object-Level vs Pixel-Level:** Pendekatan *Pixel If-Else* yang menggabungkan informasi warna Lab ($L, b$) dan HSV ($S$) terbukti paling tangguh dalam menekan noise latar belakang dibandingkan thresholding intensitas tunggal.

### 3. Rekomendasi Pengembangan Lanjutan
- **Segmentasi Dua Tahap (Two-Stage Detection):** Deteksi sel darah merah (RBC) terlebih dahulu melalui lingkaran Hough atau watershed, kemudian pencarian parasit dibatasi hanya di dalam eritrosit terinfeksi.
- **Normalisasi Warna (Macenko / Reinhard):** Standardisasi distribusi warna sediaan apusan darah antar laboratorium untuk mengatasi inkonsistensi pewarnaan Giemsa."""))

enhanced_nb = {
    "cells": cells,
    "metadata": orig.get("metadata", {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.13"
        }
    }),
    "nbformat": 4,
    "nbformat_minor": 5
}

target_path = base_dir / "malaria_parasite_segmentation_enhanced.ipynb"
with open(target_path, "w") as f:
    json.dump(enhanced_nb, f, indent=1)

print(f"Berhasil membuat notebook baru dengan {len(cells)} cells:")
print(f"File tersimpan di: {target_path}")
