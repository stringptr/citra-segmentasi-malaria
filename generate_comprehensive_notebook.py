import json
from pathlib import Path

# Load original notebook
base_dir = Path("/home/archian/Kuliah/Semester5/ADCB/Project/draft/citra-segmentasi-malaria")
with open(base_dir / "malaria_schizont_segmentation.ipynb") as f:
    orig = json.load(f)

# Helper to build cells
def md_cell(source):
    if isinstance(source, list):
        src = [s if s.endswith('\n') else s + '\n' for s in source]
    else:
        src = [s + '\n' for s in source.strip().split('\n')]
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": src
    }

def code_cell(source):
    if isinstance(source, list):
        src = [s if s.endswith('\n') else s + '\n' for s in source]
    else:
        src = [s + '\n' for s in source.strip().split('\n')]
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": src
    }

print("Loaded original notebook successfully!")
