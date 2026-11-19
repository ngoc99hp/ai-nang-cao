"""Cấu hình dùng chung."""
from pathlib import Path

# --- Đường dẫn ---
ROOT      = Path.home() / 'aai_misconception'
SRC       = ROOT / 'src'
RAW       = ROOT / 'data' / 'raw'
INTERIM   = ROOT / 'data' / 'interim'
PROCESSED = ROOT / 'data' / 'processed'
FIGURES   = ROOT / 'results' / 'figures'
TABLES    = ROOT / 'results' / 'tables'
WORK      = ROOT / 'work'          # binary + file tạm

# --- Tái lập kết quả ---
SEED = 42

# --- Runner ---
COMPILE_TIMEOUT = 10   # giây (wall)
RUN_TIMEOUT     = 2    # giây CPU / test case
GCC_FLAGS       = ['-O0', '-w', '-std=gnu99']
GCC_LIBS        = ['-lm']

# --- Quyết định domain (điền theo DP, mục 7) ---
PROBLEMS = []          # DP1
FEATURE_WEIGHTS = {    # DP3 — giá trị khởi điểm
    'test': 1.0,
    'outdiff': 1.5,
    'ast': 0.5,
}
