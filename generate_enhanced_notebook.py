import json
from pathlib import Path

# Load original notebook to preserve base logic and constants
with open('malaria_schizont_segmentation.ipynb') as f:
    orig_nb = json.load(f)

print("Original cells count:", len(orig_nb['cells']))

