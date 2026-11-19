"""Data contract giữa các phase. Mọi file Parquet đều ghi/đọc qua module này."""
import os
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

STATUS = ('PASS', 'FAIL', 'TIMEOUT', 'CRASH', 'OUTPUT_LIMIT', 'COMPILE_ERROR')
SOURCES = ('introclass', 'itsp', 'synthetic', 'bench')

SUBMISSIONS = pa.schema([
    ('sub_id',     pa.string()),   # duy nhất toàn cục, hợp lệ làm tên file
    ('source',     pa.string()),
    ('problem',    pa.string()),
    ('code_path',  pa.string()),   # tương đối so với config.ROOT
    ('is_correct', pa.bool_()),    # pass toàn bộ test
    ('label_true', pa.string()),   # mã misconception, chỉ có ở synthetic
])

TEST_RESULTS = pa.schema([
    ('sub_id',  pa.string()),
    ('problem', pa.string()),
    ('test_id', pa.string()),      # null khi COMPILE_ERROR
    ('status',  pa.string()),      # DP0 strict (mô phỏng checker IntroClass)
    ('status_sem', pa.string()),   # DP0 semantic (dùng cho clustering)
    ('returncode', pa.int32()),    # null khi COMPILE_ERROR / TIMEOUT theo wall
    ('stdout',  pa.string()),      # output gốc, đã cắt; chấm lại được không cần chạy lại
])

_ENUMS = {'status': STATUS, 'status_sem': STATUS, 'source': SOURCES}
_INT_COLS = {'returncode'}         # int nullable → pandas Int32


def validate(df: pd.DataFrame, schema: pa.Schema) -> None:
    missing = set(schema.names) - set(df.columns)
    if missing:
        raise ValueError(f'Thiếu cột: {sorted(missing)}')
    for col, allowed in _ENUMS.items():
        if col in schema.names:
            bad = set(df[col].dropna().unique()) - set(allowed)
            if bad:
                raise ValueError(f'Giá trị không hợp lệ ở cột {col!r}: {sorted(bad)}')
    if schema is SUBMISSIONS and df['sub_id'].duplicated().any():
        raise ValueError('sub_id bị trùng trong submissions')


def save(df: pd.DataFrame, schema: pa.Schema, path) -> Path:
    """Validate rồi ghi atomic (ghi file tạm, sau đó đổi tên)."""
    validate(df, schema)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df = df[schema.names].astype({c: 'Int32' for c in _INT_COLS & set(schema.names)})
    table = pa.Table.from_pandas(df, schema=schema, preserve_index=False)
    tmp = path.with_suffix('.tmp')
    pq.write_table(table, tmp, compression='zstd')
    os.replace(tmp, path)
    return path


def load(path, schema: pa.Schema) -> pd.DataFrame:
    return pq.read_table(path, schema=schema).to_pandas(
        types_mapper={pa.int32(): pd.Int32Dtype()}.get)
