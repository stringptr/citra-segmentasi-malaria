import sys, time
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from pathlib import Path

nb_path = Path("/home/archian/Kuliah/Semester5/ADCB/Project/draft/citra-segmentasi-malaria/malaria_parasite_segmentation_enhanced.ipynb")

print(f"Membaca notebook: {nb_path}...")
with open(nb_path) as f:
    nb = nbformat.read(f, as_version=4)

ep = ExecutePreprocessor(timeout=600, kernel_name='python3')

start_time = time.time()
print("Memulai eksekusi notebook (kernel python3)...")
try:
    ep.preprocess(nb, {'metadata': {'path': str(nb_path.parent)}})
    print(f"Eksekusi notebook selesai dengan sukses dalam {time.time() - start_time:.2f} detik!")
    with open(nb_path, 'w') as f:
        nbformat.write(nb, f)
    print("Notebook tersimpan dengan seluruh output visualisasi!")
except Exception as e:
    print(f"Terjadi error saat eksekusi: {e}")
    # Simpan progress sampai cell yang error
    with open(nb_path, 'w') as f:
        nbformat.write(nb, f)
    sys.exit(1)
