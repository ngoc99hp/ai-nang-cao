# PROJECT_PLAN — Misconceptions Clustering (BTL AI nâng cao, Đề tài 5)

> Tài liệu bàn giao cho **Claude Code** chạy trên server Ubuntu; mọi thao tác compile/chạy diễn ra trong Docker container `aai-lab` (mục 3).
> Chứa: bối cảnh, quy tắc làm việc, môi trường, mã nguồn đã kiểm chứng (Phase 0), các phát hiện về dữ liệu (Phase 1 đang dở) và kế hoạch Phase 1–6.
> Ngôn ngữ giao tiếp với người dùng: **tiếng Việt**. Thuật ngữ kỹ thuật giữ tiếng Anh.

---

## 0. Hướng dẫn dành cho Claude Code (đọc trước tiên)

### 0.1. Quy trình làm việc bắt buộc

1. **Làm từng bước nhỏ.** Mỗi bước: giải thích ngắn mục tiêu → viết/chạy code → hiển thị output → **dừng lại chờ người dùng xác nhận** rồi mới sang bước tiếp theo.
2. Mỗi bước phải nêu rõ **output mong đợi** và **tiêu chí đạt** trước khi chạy.
3. **Không tự quyết các điểm quyết định domain (DP0–DP5, mục 7).** Trình bày phương án + trade-off, để người dùng chốt. Người dùng là người ra quyết định về domain logic và thiết kế.
4. Sau mỗi bước đạt: `git commit` với message dạng `P1.4: parse IntroClass submissions`.
5. Khi sửa module trong `src/`: chạy lại `docker exec aai-lab pytest -q` trước khi báo hoàn thành.
7. Code Python/C của dự án **chỉ chạy trong container** (`docker exec aai-lab ...`, xem 3.6). Trên host chỉ sửa file, git, và clone dataset.
6. Phong cách: ngắn gọn, kỹ thuật, có trade-off. Không giải thích lý thuyết chung chung.

### 0.2. Quy tắc an toàn (không được vi phạm)

- Chương trình chạy **code C của người khác** (bài sinh viên + mutant). Mọi thao tác compile/chạy **bắt buộc đi qua `src/runner.py`** (có giới hạn CPU/RAM/output). Không bao giờ chạy trực tiếp binary của sinh viên bằng lệnh khác.
- Server **dùng chung với dịch vụ thật** (stack `hpstin`: postgres, caddy, meilisearch) → mọi compile/chạy code nằm trong container `aai-lab` (user `aai` không sudo, `network_mode: none`, giới hạn CPU/RAM/PID — mục 3.2). **Không** chạy `src/runner.py` hay binary nào trên host; **không** gỡ các giới hạn trong `compose.yaml` khi chưa hỏi.
- **Không động vào** container/network/volume của `hpstin` (không `docker compose down`, `docker system prune`, `docker network prune`...). Chỉ thao tác với project compose `aai`.
- `data/raw/` là **chỉ đọc** (mount `:ro` vào container). Không sửa dataset gốc.
- Mọi file Parquet **ghi/đọc qua `src/schema.py`** (có validate). Không ghi Parquet trực tiếp.
- Binary và file tạm chỉ nằm trong `work/` (gitignored).

### 0.3. Trạng thái hiện tại

| Phase | Trạng thái |
|---|---|
| Phase 0 — Setup, runner, schema | ✅ Hoàn tất trên server (phương án A — Docker). `docker exec aai-lab pytest -q` → **9 passed** (~12 s; 6 test plan + 3 test môi trường `tests/test_env.py`) |
| Phase 1 — Dữ liệu IntroClass | ✅ Xong 1.1–1.8 (ITSP), DP0 + DP1 đã chốt |
| Phase 2 — Mutation | ✅ Xong (480 mutant có nhãn, mục 8) |
| Phase 3 — OAV | ✅ Xong (mục 9) |
| Phase 4 — Clustering | ✅ Xong (DP3, DP4 đã chốt) |
| Phase 5 — Luật + đánh giá | ✅ Xong (DP5 tạm chốt) |
| Phase 6 — Trực quan + báo cáo | ✅ Hình + bảng + tên cụm (DP5) + E4b ITSP + **báo cáo Word** (`report/`, mục 12.2) |
| Phase 7 — Demo giao diện | ✅ Streamlit (`aai-ui`) + worker trong `aai-lab`; xem mục 12.1 và `demo/README.md` |

---

## 1. Bối cảnh đề tài

- **Môn:** AI nâng cao (cao học CNTT).
- **Đề tài 5:** *Tự động phân loại và cụm hóa các quan niệm sai lầm (Misconceptions Clustering) của sinh viên thông qua khai phá cấu trúc bài làm sai.*
- **Yêu cầu gốc của đề:**
  - Hình thức hóa bài làm lỗi bằng bộ ba **Đối tượng – Thuộc tính – Giá trị (OAV)**, bám theo các test case bị trượt.
  - **Gom cụm phi giám sát** (đề gợi ý ILA cải tiến hoặc K-means + Hamming/Euclid có trọng số).
  - **Sinh hệ luật** dạng: `NẾU [hàm hoán vị dùng biến thường] VÀ [giá trị không đổi sau hàm] THÌ [Lỗi: chưa hiểu truyền tham chiếu bằng con trỏ]`.
  - Mục tiêu ứng dụng: **macro-feedback** cho giảng viên lớp lập trình C quy mô lớn.
- **Thay đổi dữ liệu:** dữ liệu của giảng viên không truy cập được (máy chủ lỗi) → **tự thu thập dữ liệu**. Người dùng sẽ xin xác nhận của giảng viên về việc đổi nguồn dữ liệu.

### 1.1. Ghi chú học thuật quan trọng

- **ILA (Inductive Learning Algorithm) là thuật toán học có giám sát để quy nạp luật, không phải thuật toán gom cụm.** Thiết kế hợp lý: clustering trước → dùng `cluster_id` làm nhãn lớp → ILA/ID3 sinh luật.
- **K-means tối ưu theo Euclid**, ghép với Hamming là không nhất quán toán học. Với dữ liệu categorical dùng **K-modes** hoặc **Agglomerative + Hamming/Jaccard (precomputed)**. K-means trên one-hot chỉ làm baseline.

---

## 2. Chiến lược dữ liệu

| Nguồn | Vai trò | Ghi chú |
|---|---|---|
| **IntroClass** (UC Davis) — nguồn chính | Dữ liệu thật | 6 bài C nhập môn, 1.143 phiên bản, có test blackbox + whitebox, có metadata pass/fail. Repo: `https://github.com/ProgramRepair/IntroClass`. Trích dẫn: Le Goues et al., *The ManyBugs and IntroClass Benchmarks for Automated Repair of C Programs*, IEEE TSE 2015 |
| **ITSP** (IIT Kanpur) — nguồn phụ | Dữ liệu thật + cặp buggy/correct | 661 bài, mỗi bài sai có bản đúng của chính sinh viên đó → diff chỉ ra chỗ sửa. Repo: `https://github.com/jyi/ITSP`. Trích dẫn: Yi et al., FSE 2017 |
| **C-Pack-IPAs** — tùy chọn | Dữ liệu thật bổ sung | 25 bài tập, có test suite. `https://github.com/pmorvalho/C-Pack-IPAs` |
| **Mutation có nhãn** (tự sinh) | **Ground truth** để đo ARI/NMI | Cấy lỗi theo từng misconception vào lời giải đúng (Phase 2) |

**Hạn chế đã biết:** các dataset công khai chủ yếu là bài cơ bản (vòng lặp, rẽ nhánh, số học), gần như không có misconception con trỏ/tham chiếu → phần này bù bằng dữ liệu mutation.

**Thiết kế thí nghiệm:** báo cáo **tách riêng** kết quả trên dữ liệu sinh (có nhãn, sạch) và dữ liệu thật (không nhãn, nhiễu).

---

## 3. Môi trường server (phương án A — Docker container cách ly)

### 3.1. Server thực tế (khảo sát 2026-11-19)

| | Thực tế | Ghi chú |
|---|---|---|
| OS | Ubuntu 24.04.3, kernel 6.8 | |
| CPU | **2 core** | dưới mức khuyến nghị 4 → Phase 1.6 chậm hơn ~2× |
| RAM | 7.8 GB, **không có swap** | |
| Disk | còn ~125 GB | |
| GPU | không có | chỉ ảnh hưởng phần mở rộng CodeBERT |
| Host | Python 3.12.3, git 2.43, Docker 29.9, Compose v5.7 | **không có** gcc/make/tmux/indent/venv trên host — và không cần cài |
| User host | `tuyendv` (nhóm `docker`; sudo cần mật khẩu) | người dùng là quản trị server |
| **Dịch vụ đang chạy chung** | Docker stack `hpstin`: postgres:16 (`0.0.0.0:5434`), caddy (`:80/:443`), meilisearch (`127.0.0.1:7700`) | **server chia sẻ với dịch vụ thật** → lý do chọn phương án A |

**Quyết định (người dùng chốt):** mọi thao tác compile/chạy/Python của dự án diễn ra **bên trong container `aai-lab`**, không cài gì lên host, không cần sudo.

### 3.2. Mô hình cách ly

| Biện pháp | Mục đích |
|---|---|
| `network_mode: none` lúc chạy | Code C lạ không truy cập được mạng — kể cả postgres hpstin đang publish `0.0.0.0:5434` (container ở bridge mặc định vẫn với tới được) |
| User `aai` (UID 1000, không sudo) + `cap_drop: ALL` + `no-new-privileges` | Không leo thang quyền trong container |
| `cpus: 1.5`, `cpu_shares: 256` | Chừa ≥ 0.5 core và ưu tiên CPU cho hpstin khi tranh chấp |
| `mem_limit: 3g` (= `memswap_limit`) | Host không có swap → chặn OOM ảnh hưởng hpstin |
| `pids_limit: 512` | Chặn fork bomb (`ulimit` trong runner không giới hạn số tiến trình) |
| `data/raw` mount `:ro` | Dataset gốc chỉ đọc ở mức kernel, không chỉ `chmod` |
| `tmpfs /tmp` (512 MB) | File output tạm của runner không ghi vào layer container |
| Runner (`ulimit -t/-f/-v/-c`) giữ nguyên | Lớp bảo vệ thứ hai, theo từng tiến trình |

Image chỉ cần mạng **lúc build** (apt + pip). Dataset được clone **trên host** (host có git + mạng), rồi container đọc qua mount `:ro`.

### 3.3. Ánh xạ đường dẫn

| Host (`tuyendv`) | Container (`aai`) |
|---|---|
| `/home/tuyendv/ngoc/thacsi/ai-nangcao/` (= thư mục dự án, Claude Code mở tại đây) | `/home/aai/aai_misconception/` |

→ `config.ROOT = Path.home() / 'aai_misconception'` **giữ nguyên** và đúng bên trong container. Hệ quả: code trong `src/`, `scripts/`, `tests/` **chỉ chạy trong container**; trên host chỉ sửa file và dùng git. UID 1000 trùng `tuyendv` nên file sinh ra trong container thuộc quyền `tuyendv` trên host.

### 3.4. File hạ tầng

**`docker/Dockerfile`**
```dockerfile
FROM ubuntu:24.04
ARG UID=1000
ARG GID=1000
ENV DEBIAN_FRONTEND=noninteractive PYTHONDONTWRITEBYTECODE=1
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential python3 python3-venv tmux indent git ca-certificates \
    && rm -rf /var/lib/apt/lists/*
# ubuntu:24.04 có sẵn user 'ubuntu' UID 1000 → xóa để aai dùng UID 1000 (trùng tuyendv trên host)
RUN userdel -r ubuntu 2>/dev/null || true; \
    groupadd -g ${GID} aai && useradd -m -u ${UID} -g ${GID} -s /bin/bash aai
USER aai
RUN python3 -m venv /home/aai/venv
ENV PATH=/home/aai/venv/bin:$PATH
COPY --chown=aai:aai requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
WORKDIR /home/aai/aai_misconception
```

**`compose.yaml`** (ở gốc dự án)
```yaml
name: aai
services:
  lab:
    build: { context: ., dockerfile: docker/Dockerfile }
    image: aai-lab:1
    container_name: aai-lab
    command: sleep infinity
    init: true
    network_mode: none
    working_dir: /home/aai/aai_misconception
    volumes:
      - .:/home/aai/aai_misconception
      - ./data/raw:/home/aai/aai_misconception/data/raw:ro
    tmpfs: ["/tmp:size=512m"]
    cpus: 1.5
    cpu_shares: 256
    mem_limit: 3g
    memswap_limit: 3g
    pids_limit: 512
    cap_drop: [ALL]
    security_opt: ["no-new-privileges:true"]
    restart: "no"
```

**`pytest.ini`** — `/tmp` trong container là tmpfs **`noexec`** (cố ý giữ: binary chỉ được chạy trong `work/`), nên thư mục tạm của pytest phải nằm trong `work/`:
```ini
[pytest]
testpaths = tests
addopts = --basetemp=work/pytest
```
Mọi binary/file tạm cần thực thi phải đặt trong `config.WORK`, **không** dùng `tempfile.mkdtemp()` mặc định (rơi vào `/tmp` → `Permission denied`, rc 126 → runner báo FAIL giả). `tempfile.TemporaryFile()` cho output trong runner thì vẫn dùng được (không cần exec).

**`.dockerignore`** — build context chỉ cần `requirements.txt`:
```
*
!requirements.txt
```

### 3.5. Dựng môi trường (chạy trên host, không cần sudo)

```bash
cd /home/tuyendv/ngoc/thacsi/ai-nangcao
mkdir -p docker src scripts tests notebooks work/logs \
         data/{raw,interim,processed} results/{figures,tables}
git init
# tạo docker/Dockerfile, compose.yaml, .dockerignore, requirements.txt, .gitignore, CLAUDE.md
docker compose build
docker compose up -d
docker exec aai-lab bash -c 'id; gcc --version | head -1; python --version; nproc'
docker exec aai-lab python -c "import socket; socket.create_connection(('1.1.1.1',53),2)"  # PHẢI lỗi (no network)
```

### 3.6. Quy ước chạy lệnh (dành cho Claude Code)

| Việc | Lệnh |
|---|---|
| Sửa file, git | trên host, trực tiếp |
| Test | `docker exec aai-lab pytest -q` |
| Script ngắn | `docker exec aai-lab python scripts/<x>.py` |
| Job dài (thay cho tmux trên host) | `docker exec -d aai-lab bash -c 'python scripts/<x>.py > work/logs/<x>.log 2>&1'` rồi theo dõi `work/logs/<x>.log` từ host. Người dùng muốn xem tương tác: `docker exec -it aai-lab tmux new -As main` |
| Đổi `requirements.txt` | `docker compose build && docker compose up -d` (hỏi người dùng trước khi đổi pin) |
| Dừng / khởi động lại | `docker compose stop` / `docker compose up -d` (dữ liệu nằm ở bind mount, không mất) |
| Jupyter (tùy chọn) | container riêng, **không** chạy runner trong đó: `docker run --rm -p 127.0.0.1:8888:8888 -v "$PWD":/home/aai/aai_misconception aai-lab:1 jupyter lab --ip 0.0.0.0 --no-browser`, truy cập qua SSH tunnel |

### 3.7. Cấu trúc thư mục

```
ai-nangcao/                 # host; = ~/aai_misconception trong container
├── CLAUDE.md               # chứa dòng: @PROJECT_PLAN.md
├── PROJECT_PLAN.md         # tài liệu này
├── compose.yaml
├── .dockerignore
├── docker/Dockerfile
├── requirements.txt
├── .gitignore
├── src/                    # module dùng chung
│   ├── config.py
│   ├── runner.py
│   ├── schema.py
│   └── (sẽ thêm) introclass.py, normalize.py, ast_utils.py, mutators.py, features.py, ila.py
├── scripts/                # job chạy dài, mỗi bước một script
├── tests/                  # pytest
├── notebooks/              # khám phá dữ liệu, vẽ hình
├── data/
│   ├── raw/                # dataset gốc — CHỈ ĐỌC (mount :ro)
│   ├── interim/            # submissions/, test_results/ (theo từng problem)
│   └── processed/          # ma trận OAV
├── results/{figures,tables}
└── work/                   # binary + file tạm + logs/ — gitignored
```

### 3.8. `.gitignore`

```gitignore
data/
work/
__pycache__/
*.pyc
.pytest_cache/
.ipynb_checkpoints/
```

### 3.9. `requirements.txt` (đã pin theo phiên bản kiểm chứng)

```text
tree-sitter==0.26.1
tree-sitter-c==0.24.2
kmodes==0.12.2
pyarrow==23.0.1
pandas==2.2.3
scikit-learn==1.6.1
scipy==1.16.3
pytest
jupyterlab
```

Cài lúc `docker compose build` (Python 3.12 của ubuntu:24.04 — trùng phiên bản đã kiểm chứng).

> Nếu một phiên bản pin không cài được trên Python 3.12, báo người dùng trước khi đổi pin. Đặc biệt **không nâng tree-sitter** khi chưa kiểm tra lại: API `Query/captures` thay đổi nhiều qua các bản. Code trong dự án duyệt cây bằng đệ quy (`node.children`, `child_by_field_name`) để tránh phụ thuộc API này.

---

## 4. Phase 0 — Mã nguồn đã kiểm chứng

Tạo đúng 3 file dưới đây (trên host, trong `src/`), sau đó tạo test ở mục 4.4 và chạy `docker exec aai-lab pytest -q`. `config.py` không cần sửa: `Path.home()` trong container là `/home/aai` (mục 3.3).

### 4.1. `src/config.py`

```python
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
```

### 4.2. `src/runner.py`

```python
"""Compile & chạy bài C của sinh viên an toàn, có giới hạn tài nguyên.

Status:
  PASS / FAIL    : chạy xong, so khớp hoặc không khớp output mong đợi
  TIMEOUT        : vượt CPU time (thường do vòng lặp vô hạn)
  CRASH          : bị signal kill (segfault, abort, FPE...)
  OUTPUT_LIMIT   : in quá MAX_OUTPUT_BYTES
  COMPILE_ERROR  : không biên dịch được (chỉ xuất hiện trong run_batch)
"""
import math
import os
import signal
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

import config

MAX_OUTPUT_BYTES = 1 << 20          # 1 MB
MAX_MEMORY_KB    = 256 * 1024       # 256 MB
WALL_FACTOR      = 3                # wall timeout = CPU limit * 3 (lưới an toàn)
DEFAULT_WORKERS  = (os.cpu_count() or 2) * 2

# Giới hạn đặt bằng ulimit trong bash rồi exec -> an toàn với thread (không dùng preexec_fn)
_LIMIT_SH = 'ulimit -t {cpu} -f {fsize} -v {mem} -c 0; exec "$0"'

_TIMEOUT_SIGNALS = {-signal.SIGXCPU, -signal.SIGKILL}


def compile_c(src, exe) -> tuple[bool, str]:
    """Trả về (thành_công, stderr rút gọn)."""
    cmd = ['gcc', *config.GCC_FLAGS, str(src), '-o', str(exe), *config.GCC_LIBS]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                           timeout=config.COMPILE_TIMEOUT)
    except subprocess.TimeoutExpired:
        return False, 'COMPILE_TIMEOUT'
    return r.returncode == 0, r.stderr[-2000:]


@dataclass
class RunResult:
    status: str
    stdout: str
    returncode: int | None


def run_once(exe, input_path, cpu_limit: float | None = None) -> RunResult:
    """Chạy exe với stdin từ file; chưa so sánh output."""
    cpu = math.ceil(cpu_limit or config.RUN_TIMEOUT)
    sh = _LIMIT_SH.format(cpu=cpu, fsize=MAX_OUTPUT_BYTES // 1024, mem=MAX_MEMORY_KB)
    with open(input_path, 'rb') as fin, tempfile.TemporaryFile() as fout:
        try:
            p = subprocess.run(['bash', '-c', sh, str(Path(exe).resolve())],
                               stdin=fin, stdout=fout, stderr=subprocess.DEVNULL,
                               timeout=cpu * WALL_FACTOR)
        except subprocess.TimeoutExpired:
            return RunResult('TIMEOUT', '', None)
        fout.seek(0)
        out = fout.read(MAX_OUTPUT_BYTES).decode('utf-8', errors='replace')

    rc = p.returncode
    if rc in _TIMEOUT_SIGNALS:
        return RunResult('TIMEOUT', out, rc)
    if rc == -signal.SIGXFSZ:
        return RunResult('OUTPUT_LIMIT', out, rc)
    if rc < 0:
        return RunResult('CRASH', out, rc)
    return RunResult('OK', out, rc)


def normalize_output(s: str) -> list[str]:
    """Chuẩn hóa tối thiểu. Sẽ được thay bằng src/normalize.py ở Phase 1 (theo DP0)."""
    return s.split()


def judge(exe, input_path, expected_path, cpu_limit: float | None = None) -> RunResult:
    r = run_once(exe, input_path, cpu_limit)
    if r.status != 'OK':
        return r
    expected = Path(expected_path).read_text(errors='replace')
    r.status = 'PASS' if normalize_output(r.stdout) == normalize_output(expected) else 'FAIL'
    return r


def run_batch(subs, tests, workdir, max_workers: int | None = None) -> list[dict]:
    """
    subs : [(sub_id, src_path), ...]   sub_id phải hợp lệ làm tên file
    tests: [(test_id, in_path, out_path), ...]
    Trả về list dict khớp schema test_results: sub_id, test_id, status, stdout.
    Song song hóa ở mức (bài × test) để cân bằng tải.
    """
    workdir = Path(workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    max_workers = max_workers or DEFAULT_WORKERS

    def _compile(item):
        sub_id, src = item
        exe = workdir / f'{sub_id}.out'
        ok, err = compile_c(src, exe)
        return sub_id, (exe if ok else None), err

    with ThreadPoolExecutor(max_workers) as ex:
        compiled = list(ex.map(_compile, subs))

    rows, jobs = [], []
    for sub_id, exe, err in compiled:
        if exe is None:
            rows.append(dict(sub_id=sub_id, test_id=None, status='COMPILE_ERROR', stdout=err))
        else:
            jobs.extend((sub_id, exe, t) for t in tests)

    def _run(job):
        sub_id, exe, (tid, inp, exp) = job
        r = judge(exe, inp, exp)
        return dict(sub_id=sub_id, test_id=tid, status=r.status, stdout=r.stdout[:2000])

    with ThreadPoolExecutor(max_workers) as ex:
        rows.extend(ex.map(_run, jobs))
    return rows
```

#### Quyết định thiết kế của runner (đã kiểm chứng — không được thay đổi khi chưa hỏi)

| Quyết định | Lý do |
|---|---|
| Giới hạn tài nguyên bằng `bash -c 'ulimit ...; exec'` thay vì `preexec_fn` | `preexec_fn` không an toàn khi có thread (tài liệu Python cảnh báo có thể deadlock); runner chạy với `ThreadPoolExecutor` |
| Timeout theo **CPU time** (`ulimit -t`), wall timeout = 3× làm lưới an toàn | Timeout theo wall-clock gây **TIMEOUT oan** cho bài đúng khi CPU bị các bài lặp vô hạn chiếm. Đã kiểm chứng: 110/110 bài đúng PASS khi chạy song song cùng bài lặp vô hạn |
| Output ghi ra file tạm, giới hạn 1 MB (`ulimit -f`) → `OUTPUT_LIMIT` | Bài in vô hạn có thể sinh hàng trăm MB trong 2 s; `capture_output` sẽ làm tràn RAM |
| Exit code ≥ 0 không bị coi là lỗi; chỉ `rc < 0` (signal) mới là `CRASH` | Bài C cũ hay thiếu `return 0;` → exit code là rác |
| `-std=gnu99` | gcc 13 mặc định C17, chặt hơn; bài sinh viên ~2014–2015 có thể dùng khai báo hàm ngầm định |
| Song song ở mức (bài × test) đã làm phẳng | Cân bằng tải tốt hơn song song theo bài |
| `RLIMIT_CORE = 0` (`ulimit -c 0`) | Không sinh core dump |
| Mỗi lần chạy: `start_new_session=True` + `killpg(SIGKILL)` sau khi xong (thêm 2026-11-23) | Không sót tiến trình con / fork bomb của bài nộp; không đổi kết quả chấm (`test_no_orphan_processes`) |

**Ước lượng thời gian chạy:** bài chạy bình thường mất vài ms; thời gian bị chi phối bởi số lần TIMEOUT → xấp xỉ `(số lần TIMEOUT × 2 s) / số core`. Đo trên Colab 2 core: 150 runs (15 TIMEOUT) mất 32.8 s tuần tự, 19.4 s với 4 workers.

### 4.3. `src/schema.py`

```python
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
    ('status',  pa.string()),
    ('stdout',  pa.string()),      # output gốc, đã cắt; chuẩn hóa ở bước sau
])

_ENUMS = {'status': STATUS, 'source': SOURCES}


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
    table = pa.Table.from_pandas(df[schema.names], schema=schema, preserve_index=False)
    tmp = path.with_suffix('.tmp')
    pq.write_table(table, tmp, compression='zstd')
    os.replace(tmp, path)
    return path


def load(path, schema: pa.Schema) -> pd.DataFrame:
    return pq.read_table(path, schema=schema).to_pandas()
```

**Quy ước dữ liệu:**
- `test_results` lưu **stdout gốc** (cắt 2000 ký tự), không lưu bản đã chuẩn hóa → đổi quy tắc chuẩn hóa không phải chạy lại test.
- `code_path` lưu **đường dẫn tương đối** so với `ROOT`.
- Ghi **theo từng problem**: `data/interim/{submissions,test_results}/<problem>.parquet` (checkpoint).
- Bảng OAV (Phase 3) có 2 dạng: `oav_long` (`sub_id, object, attribute, value` — đúng hình thức OAV cho báo cáo) và `oav_wide` (pivot cho thuật toán).

### 4.4. Test kiểm chứng Phase 0

**`tests/conftest.py`**
```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
```

**`tests/test_runner.py`**
```python
import pytest
import runner

HEAD = '#include <stdio.h>\nint main(){int n,i,x,s=0;scanf("%d",&n);'
BODY = {
    'correct'      : 'for(i=0;i<n;i++){scanf("%d",&x);s+=x;} printf("%d\\n",s); return 0;}',
    'off_by_one'   : 'for(i=1;i<n;i++){scanf("%d",&x);s+=x;} printf("%d\\n",s); return 0;}',
    'infinite_loop': 'while(1){} return 0;}',
    'segfault'     : 'int *p=0; *p=1; return 0;}',
    'output_flood' : 'while(1) printf("x\\n"); return 0;}',
    'syntax_error' : 'printf("%d\\n",s) return 0;}',
    'nonzero_exit' : 'for(i=0;i<n;i++){scanf("%d",&x);s+=x;} printf("%d\\n",s); return 3;}',
}
EXPECTED = {
    'correct': 'PASS', 'off_by_one': 'FAIL', 'infinite_loop': 'TIMEOUT',
    'segfault': 'CRASH', 'output_flood': 'OUTPUT_LIMIT',
    'syntax_error': 'COMPILE_ERROR', 'nonzero_exit': 'PASS',
}


@pytest.fixture
def io_files(tmp_path):
    (tmp_path / 'in.txt').write_text('3\n1 2 3\n')
    (tmp_path / 'out.txt').write_text('6\n')
    return tmp_path


def test_all_statuses(io_files):
    subs = []
    for name, body in BODY.items():
        src = io_files / f'{name}.c'
        src.write_text(HEAD + body)
        subs.append((name, src))
    rows = runner.run_batch(subs, [('t0', io_files / 'in.txt', io_files / 'out.txt')],
                            io_files / 'bin')
    got = {r['sub_id']: r['status'] for r in rows}
    assert got == EXPECTED


def test_no_false_timeout_under_load(io_files):
    """Bài đúng không được TIMEOUT oan khi chạy song song với bài lặp vô hạn."""
    subs = []
    for i in range(12):
        kind = 'infinite_loop' if i < 3 else 'correct'
        src = io_files / f's{i:02d}_{kind}.c'
        src.write_text(HEAD + BODY[kind])
        subs.append((src.stem, src))
    rows = runner.run_batch(subs, [('t0', io_files / 'in.txt', io_files / 'out.txt')],
                            io_files / 'bin', max_workers=8)
    for r in rows:
        expected = 'TIMEOUT' if r['sub_id'].endswith('infinite_loop') else 'PASS'
        assert r['status'] == expected, r
```

**`tests/test_schema.py`**
```python
import pandas as pd
import pytest
import schema


def _tr():
    return pd.DataFrame({
        'sub_id': ['a', 'a', 'b'], 'problem': 'p', 'test_id': ['t0', 't1', None],
        'status': ['PASS', 'FAIL', 'COMPILE_ERROR'], 'stdout': ['6', '5', 'err'],
    })


def test_round_trip(tmp_path):
    df = _tr()
    p = schema.save(df, schema.TEST_RESULTS, tmp_path / 'tr.parquet')
    back = schema.load(p, schema.TEST_RESULTS)
    pd.testing.assert_frame_equal(back, df[schema.TEST_RESULTS.names])


@pytest.mark.parametrize('bad, sch, msg', [
    (_tr().assign(status='PASSED'), schema.TEST_RESULTS, 'không hợp lệ'),
    (_tr().drop(columns='stdout'),  schema.TEST_RESULTS, 'Thiếu cột'),
])
def test_validate_rejects(bad, sch, msg):
    with pytest.raises(ValueError, match=msg):
        schema.validate(bad, sch)


def test_duplicate_sub_id():
    df = pd.DataFrame({'sub_id': ['x', 'x'], 'source': 'bench', 'problem': 'p',
                       'code_path': ['a', 'b'], 'is_correct': [True, False],
                       'label_true': [None, None]})
    with pytest.raises(ValueError, match='trùng'):
        schema.validate(df, schema.SUBMISSIONS)
```

**Tiêu chí đạt Phase 0 trên server:**
```bash
docker exec aai-lab pytest -q
# Kỳ vọng: 6 passed (thời gian ~5–15 s do các test TIMEOUT; container chỉ có 1.5 CPU)
```
Thêm kiểm tra môi trường (trong container): `gcc --version`, `python --version`, `nproc`, xác nhận **không có mạng** (3.5), xác nhận `data/raw` không ghi được, và smoke test tree-sitter:

```python
import tree_sitter_c as tsc
from tree_sitter import Language, Parser
C = Language(tsc.language()); parser = Parser(C)
code = b"int f(int a[],int n){int s=0;for(int i=0;i<=n;i++)s+=a[i];return s;}"
def walk(n):
    yield n
    for c in n.children: yield from walk(c)
t = parser.parse(code)
assert not t.root_node.has_error
for n in walk(t.root_node):
    if n.type == 'for_statement':
        print(n.child_by_field_name('condition').child_by_field_name('operator').text)  # b'<='
```

---

## 5. Kiến thức đã thu thập về IntroClass (Bước 1.1–1.2)

### 5.1. Lấy dữ liệu trên server

Chạy **trên host** (container không có mạng):
```bash
cd /home/tuyendv/ngoc/thacsi/ai-nangcao/data/raw
git clone --depth 1 https://github.com/ProgramRepair/IntroClass.git introclass
rm -rf introclass/.git
chmod -R a-w introclass     # chỉ đọc (container còn mount :ro)
```
(Không cần nén/cache như trên Colab.) Nếu container đang chạy lúc clone, dữ liệu vẫn hiện ra ngay qua bind mount.

### 5.2. Cấu trúc

```
introclass/
├── LICENSE, Makefile, README.md
├── defect-classification.json      # list[1143] — xem 5.4
├── bin/
│   ├── genprog_tests.py            # LOGIC CHẤM — chưa đọc (Bước 1.3)
│   ├── gp_repatch.py
│   └── metadataGenerator.py
└── <problem>/                      # checksum, digits, grade, median, smallest, syllables
    ├── Makefile
    ├── program-metadata.json       # danh sách defect duy nhất
    ├── tests/{blackbox,whitebox}/N.in, N.out
    └── <repo_hash>/                # 1 repo = 1 sinh viên
        └── <revision 001..>/       # 1 phiên bản (snapshot)
            ├── <problem>.c
            ├── metadata.json
            ├── defect-metadata.json
            ├── blackbox_test.sh, whitebox_test.sh, Makefile
            └── gp-*.log, ae-*.log, trp-*.log   # log thí nghiệm APR (~1.5 MB/phiên bản) — KHÔNG cần
```

### 5.3. Thống kê đã đo

| problem | blackbox tests | whitebox tests | repos | versions | có `.c` |
|---|---:|---:|---:|---:|---:|
| checksum  | 6 | 10 | 21 | 69  | 69  |
| digits    | 6 | 10 | 55 | 236 | 236 |
| grade     | 9 | 9  | 50 | 268 | 268 |
| median    | 7 | 6  | 44 | 232 | 232 |
| smallest  | 8 | 8  | 45 | 177 | 177 |
| syllables | 6 | 10 | 44 | 161 | 161 |
| **Tổng**  |   |    | **259** | **1143** | **1143** |

### 5.4. Metadata

**`<version>/metadata.json`** — keys: `output`, `revision`, `nondeterministic`, `blackbox`, `whitebox`
- `blackbox` / `whitebox`: `{"pass": [...], "fail": [...]}` → **ground truth để kiểm định runner**.
- `output.blackbox` / `output.whitebox`: dict theo số test → list các output đã ghi nhận (nhiều lần chạy; dạng chuỗi bytes repr).
- `nondeterministic`: bool. Phiên bản mẫu có giá trị `True` (thường do biến chưa khởi tạo) → loại khỏi phép đo độ khớp runner hoặc xử lý riêng.

**`<version>/defect-metadata.json`** — `identicalDefects`, `nbIdenticalDefects`, `program`, `repo`, `revision` → thông tin trùng lặp giữa các phiên bản.

**`<problem>/program-metadata.json`** — `nbUniqueDefects` (checksum: 47), `uniqueDefects: [{repo, revision}]` → dataset đã khử trùng sẵn; dùng được cho bước dedup.

**`defect-classification.json`** — list[1143], mỗi phần tử: `bugclasses: [str]`, `isReferenceDefect: bool`, `program`, `repo`, `revision`. Giá trị mẫu: `"output mismatch"` → nhiều khả năng là phân loại **theo triệu chứng**, không phải misconception. **Cần xem phân bố đầy đủ** trước khi quyết định có dùng làm nhãn tham chiếu cho E4.

### 5.5. Cách chấm của dataset

`blackbox_test.sh` ánh xạ **định danh test tương đối** → **file test**, và **ánh xạ khác nhau giữa các phiên bản**. Ví dụ một phiên bản checksum:

```bash
case $2 in
p1) $DIR/../../../bin/genprog_tests.py --program checksum $1 $DIR/../../tests/blackbox/5.out $DIR/../../tests/blackbox/5.in && exit 0;;
n1) ... blackbox/3.out ... 3.in
n2) ... blackbox/2.out ... 2.in
n3) ... blackbox/1.out ... 1.in
n4) ... blackbox/6.out ... 6.in
n5) ... blackbox/4.out ... 4.in
esac
```
- `pN` = test thứ N đang **pass**, `nN` = test thứ N đang **fail** của *phiên bản đó*.
- So sánh output do `bin/genprog_tests.py --program <problem>` thực hiện → **có thể có logic riêng theo từng bài**.

### 5.6. Output mong đợi chứa câu nhắc nhập

```
IN : '1234567890\n'
OUT: 'Enter an abitrarily long string, ending with carriage return > Check sum is -\n'
```
→ So sánh token thô sẽ đánh FAIL cả bài chỉ khác chữ trong câu nhắc. Quy tắc chuẩn hóa phụ thuộc **DP0** và logic trong `genprog_tests.py`.

---

### 5.7. Kết quả Bước 1.3 (log: `work/logs/p1_3_survey.log`, `p1_3b_survey.log`)

Dataset: commit `897fd9c` (2016-02-24), 2.0 GB.

**Logic chấm `genprog_tests.py`** — mỗi bài một hàm `check_<problem>`, **trích đáp án bằng regex, bỏ qua câu nhắc**; ngoài ra có "negative match" (không được in thêm đáp án sai):

| problem | Điều kiện PASS | Ghi chú / lỗi của checker gốc |
|---|---|---|
| checksum | `Check[ ]?sum is X` đúng ký tự X; không có `Check sum is [^X]` | IGNORECASE |
| digits | `findall('[-]?\d\n')` bằng nhau (mỗi chữ số kết thúc bằng `\n`) | chữ số in cùng dòng với text khác vẫn bắt được nếu ngay trước `\n` |
| grade | `Student has an X grade` / `Student has failed the course`; không in grade khác | IGNORECASE; **sai chính tả** (`Studetn`) → FAIL |
| median | `(-?\d+) is the median` bằng giá trị đúng; không in "N is the median" với N khác | **phân biệt hoa thường** |
| smallest | `(-?\d+) is the smallest` bằng giá trị đúng | **bug: negative check tìm trong `test_input` thay vì output → không bao giờ có tác dụng** |
| syllables | `syllables is X`; không có `syllables is [^X]` | `[^X]` là lớp ký tự → sai với X nhiều chữ số |

Khác biệt cần lưu ý khi đối chiếu runner ↔ metadata (Bước 1.6): dataset dùng `subprocess.check_output` → **exit code ≠ 0 làm test FAIL** (exception), timeout 2 s **wall-clock**; runner của ta coi exit code ≥ 0 là bình thường và dùng CPU time.

**`metadata.json`**: `pass`/`fail` là **số file test** (`'5'` ↔ `tests/blackbox/5.*`), đầy đủ cho mọi phiên bản (đã kiểm chứng bằng `tests/test_introclass.py`, khớp ánh xạ `pN/nN` trong `*_test.sh`).

**`defect-classification.json`**: revision dạng `N_<sha>` ↔ thư mục `{N:03d}` (sha = `metadata['revision']`, khớp 1143/1143). `bugclasses` gồm `output mismatch` (4317), `human fix - not a defect` (135 — đúng bằng các phiên bản pass toàn bộ), `other` (113), `nondeterminism` (26), `timeout` (4); 1000/1143 phiên bản có `len(bugclasses) == số test fail` → **nhãn theo triệu chứng từng test, không phải misconception → không dùng làm nhãn tham chiếu cho E4** (chỉ dùng để lọc). `isReferenceDefect` không tương ứng với pass/fail (438 True vẫn fail) — chưa rõ ngữ nghĩa, không dùng.

**Số bài sai** (theo metadata của dataset):

| problem | versions | pass all | fail ≥ 1 | & deterministic | & unique | fail toàn bộ & det |
|---|---:|---:|---:|---:|---:|---:|
| checksum | 69 | 17 | 52 | 22 | **12** | 0 |
| digits | 236 | 32 | 204 | 180 | **92** | 0 |
| grade | 268 | 40 | 228 | 159 | **63** | 0 |
| median | 232 | 26 | 206 | 178 | **57** | 0 |
| smallest | 177 | 10 | 167 | 155 | **66** | 0 |
| syllables | 161 | 10 | 151 | 63 | **39** | 0 |

Nondeterministic: 251/1143 (syllables 88/161 — thường do biến đếm chưa khởi tạo, chính là một misconception). checksum quá ít bài → gần như chắc bị loại ở DP1.

**Ví dụ output fail** (minh họa cho DP0): grade `Studetn has an C grade` (sai chính tả, đáp án đúng) và `Student has an F grade` (thay vì `failed the course`); median `seperated` trong câu nhắc (không ảnh hưởng checker); smallest không in gì sau câu nhắc.

## 6. Phase 1 — Các bước tiếp theo

### Bước 1.3 — Đọc logic chấm + thống kê metadata (TIẾP TỤC TỪ ĐÂY)

Tạo `scripts/p1_3_survey.py`, chạy và hiển thị toàn bộ output cho người dùng:

```python
"""P1.3: Đọc logic chấm của IntroClass + thống kê metadata."""
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import config

LOCAL = config.RAW / 'introclass'
problems = sorted(p.name for p in LOCAL.iterdir() if p.is_dir() and (p / 'tests').is_dir())


def versions_of(prob):
    return sorted(v for r in (LOCAL / prob).iterdir() if r.is_dir() and r.name != 'tests'
                  for v in r.iterdir() if v.is_dir())


def section(t):
    print(f'\n{"=" * 70}\n{t}\n{"=" * 70}')


section('1. bin/genprog_tests.py')
print((LOCAL / 'bin' / 'genprog_tests.py').read_text())

ver = versions_of('checksum')[0]
section(f'2. metadata.json pass/fail: {ver.relative_to(LOCAL)}')
m = json.loads((ver / 'metadata.json').read_text())
print('blackbox:', m['blackbox'])
print('whitebox:', m['whitebox'])
print('blackbox_test.sh:\n' + (ver / 'blackbox_test.sh').read_text())

section('3. defect-classification.json: phân bố')
dc = json.loads((LOCAL / 'defect-classification.json').read_text())
print('Số nhãn / phiên bản :', dict(Counter(len(d['bugclasses']) for d in dc)))
print('isReferenceDefect   :', dict(Counter(d['isReferenceDefect'] for d in dc)))
for c, n in Counter(c for d in dc for c in d['bugclasses']).most_common():
    print(f'  {n:5d}  {c}')

section('4. Thống kê theo bài')
print(f'{"problem":10s} {"vers":>5s} {"uniq":>5s} {"nondet":>7s} {"bb_all_pass":>12s} {"wb_all_pass":>12s}')
for p in problems:
    pm = json.loads((LOCAL / p / 'program-metadata.json').read_text())
    vs = versions_of(p)
    nondet = bb_ok = wb_ok = 0
    for v in vs:
        mm = json.loads((v / 'metadata.json').read_text())
        nondet += bool(mm.get('nondeterministic'))
        bb_ok += len(mm['blackbox']['fail']) == 0
        wb_ok += len(mm['whitebox']['fail']) == 0
    print(f'{p:10s} {len(vs):5d} {pm["nbUniqueDefects"]:5d} {nondet:7d} {bb_ok:12d} {wb_ok:12d}')
```

**Phân tích cần trình bày cho người dùng sau khi chạy:**
1. Logic so sánh output trong `genprog_tests.py` (có xử lý riêng theo bài không, bỏ câu nhắc thế nào) → đề xuất phương án cho **DP0**.
2. Định dạng các phần tử trong `pass`/`fail` của `metadata.json` (là `pN/nN` hay số file test).
3. Phân bố `bugclasses` → có dùng làm nhãn tham chiếu cho E4 được không.
4. Số phiên bản nondeterministic và số phiên bản thực ra đã pass toàn bộ.

### Bước 1.4 — `src/normalize.py` (sau khi người dùng chốt DP0)

✅ **Xong.** `src/normalize.py` (`check(problem, out, expected, input, mode)`), runner `judge/run_batch(..., problem=)`, schema `TEST_RESULTS` thêm `status_sem`, `returncode` (Int32). Kiểm định offline trên output đã ghi trong metadata (`scripts/p1_4_validate_checkers.py`): strict khớp metadata 100% (checksum/digits/grade), 99.8% (median/smallest), 99.1% (syllables). Số test `format_only`: grade 252, digits 14, smallest 11, median 2. Semantic chặt hơn strict chỉ ở các ca bug checker gốc (in nhiều đáp án mâu thuẫn, `18` khớp nhầm `1`) — metadata cũng đánh FAIL các ca này.

- Hiện thực đúng logic so sánh của `genprog_tests.py` (hoặc phiên bản người dùng chọn).
- Thay `runner.normalize_output` bằng hàm từ module này (truyền `problem` vào `judge`).
- Viết unit test với các cặp output mẫu từ `metadata.json`.

### Bước 1.5 — `src/introclass.py`: parser

- Duyệt `<problem>/<repo>/<revision>/` → `submissions` (`source='introclass'`, `sub_id = f'ic_{problem}_{repo[:12]}_{revision}'`, `code_path` tương đối).
- Parse ánh xạ `pN/nN → số file test` từ `blackbox_test.sh` / `whitebox_test.sh` (regex trên dòng `^(p|n)\d+\)` lấy `tests/(blackbox|whitebox)/(\d+)\.out`) để đối chiếu với metadata.
- Danh sách test của problem: `test_id = 'bb1'..`, `'wb1'..` từ `tests/{blackbox,whitebox}`.

### Bước 1.6 — Chạy test + **kiểm định runner với metadata**

- Script `scripts/p1_6_run_tests.py`, chạy nền trong container (`docker exec -d ...`, log ở `work/logs/`, xem 3.6), ghi `test_results/<problem>.parquet` theo từng problem (bỏ qua problem đã có file → resume được).
- **Kiểm định:** so kết quả PASS/FAIL của runner với `metadata.json` cho các phiên bản *deterministic*. Báo cáo tỷ lệ khớp theo problem. Tiêu chí: ≥ 95% khớp; liệt kê và phân tích các trường hợp lệch trước khi đi tiếp.
- Ghi chú: gợi ý `make` của dataset có thể dùng flag khác — nếu lệch nhiều do compile, so với `<problem>/Makefile`.

✅ **Xong.** `scripts/p1_6_run_tests.py` (~6 phút, 18.144 lượt chạy, 0 COMPILE_ERROR; container ở đúng 1.5 CPU, hpstin không bị ảnh hưởng). Kiểm định `scripts/p1_6_validate.py` → `results/tables/p1_6_validation.csv`:

| problem | khớp (deterministic) | lệch |
|---|---:|---:|
| checksum / digits / grade | 100% | 0 |
| median | 99.81% | 5 |
| smallest | 99.81% | 5 |
| syllables | 98.20% | 21 |

Quá trình: lần chạy đầu smallest chỉ 90.4%. Nguyên nhân: (1) luật rc ≠ 0 → FAIL sai với metadata (đã bỏ, xem DP0); (2) biến chưa khởi tạo — `scripts/p1_6b_uninit_probe.py` compile với `-ftrivial-auto-var-init=zero` vs `=pattern`, **79/1143 phiên bản phụ thuộc giá trị rác** (median 26, smallest 33, syllables 11, digits 5, checksum 4, grade 2; bảng `data/interim/uninit/`). Build `=zero` khớp metadata gần tuyệt đối → môi trường gốc 2014 cũng nhận 0. 31 ca lệch còn lại đều là meta FAIL / runner PASS, output trùng output metadata đã ghi (nhiễu nhãn của dataset) hoặc output ghi nhận rỗng.

Runner thêm tham số `extra_flags` cho `compile_c`/`run_batch` (mặc định rỗng).

### Bước 1.7 — Lọc + dedup + thống kê

- Giữ bài sai ngữ nghĩa: compile được + fail ≥ 1 test.
- Gắn cờ (không xóa) bài fail **toàn bộ** test — thường là lỗi I/O chứ không phải misconception.
- Dedup: dùng `uniqueDefects` + hash code đã chuẩn hóa (bỏ comment, `indent`).
- Xử lý phiên bản nondeterministic: loại hoặc tách riêng (hỏi người dùng).
- Xuất `results/tables/p1_stats.csv`: số bài sai theo problem sau từng bước lọc.
- → Trình bày cho **DP1**.

✅ **Xong** (`scripts/p1_7_filter.py`; bảng `results/tables/p1_stats.csv`; ghi `data/interim/{submissions,flags}/<problem>.parquet`, schema `SUB_FLAGS` mới). Khử trùng bằng `ast_utils.code_hash` (chuỗi token tree-sitter, bỏ comment + định dạng) — số giữ lại ≈ `uniqueDefects` của dataset.

| problem | versions | SV | buggy strict | buggy semantic | chỉ lỗi định dạng | **giữ (unique)** | SV giữ | fail toàn bộ | uninit | nondet (dataset) | mẫu test khác nhau |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| checksum | 69 | 21 | 52 | 52 | 0 | **29** | 21 | 1 | 2 | 17 | 9 |
| digits | 236 | 55 | 204 | 196 | 8 | **108** | 54 | 0 | 3 | 18 | 24 |
| grade | 268 | 50 | 228 | 105 | **123** | **38** | 22 | 1 | 1 | 13 | 14 |
| median | 232 | 44 | 203 | 203 | 1 | **69** | 44 | 2 | 9 | 16 | 24 |
| smallest | 177 | 45 | 163 | 155 | 8 | **64** | 42 | 0 | 12 | 10 | 14 |
| syllables | 161 | 44 | 123 | 123 | 0 | **38** | 28 | 1 | 6 | 23 | 11 |

Nhận xét: (1) grade: 123/228 bài "sai" theo dataset thực ra chỉ sai định dạng (`Stdent`, `F grade`...) → DP0 semantic loại nhiễu lớn. (2) Mỗi sinh viên đóng góp nhiều phiên bản (digits: 108 bản / 54 SV). (3) Số mẫu kết quả test khác nhau chỉ 9–24 / bài → nhóm thuộc tính Test thô, cần Output-diff + AST.

### Bước 1.8 (tùy chọn) — ITSP

✅ **Xong (2026-11-20).** `src/itsp.py`, `scripts/p1_8_itsp_run.py` (661 cặp, 74 bài, ~5 phút), `scripts/p1_8_itsp_validate.py` → `results/tables/p1_8_itsp_validation.csv`. Mỗi file ITSP có comment đầu ghi verdict của hệ chấm gốc → kiểm định: khớp **95.7%** (8.721 test). Lệch chủ yếu "gốc PASS / ta FAIL" (279) tập trung ở vài bài (3078, 2932, 3076, 3075) — UB phụ thuộc nền tảng (chuỗi thiếu `\0`, tràn `char`, ngoài mảng); 96 "gốc FAIL / ta PASS" phần lớn chỉ khác khoảng trắng (ta so token, DP0). Lọc: correct pass hết + buggy fail ≥ 1 → **602 cặp / 72 bài**.

Tương tự cho ITSP (`dataset/Lab-*/<problem_id>/*_buggy.c`, `*_correct.c`, test ở `dataset/test/in.<pid>.N.txt`, `out.<pid>.N.txt`). Lưu diff buggy/correct để dùng cho đánh giá định tính ở E4.

---

## 7. Điểm quyết định (người dùng chốt — Claude Code chỉ đề xuất)

| DP | Câu hỏi | Thời điểm |
|---|---|---|
| **DP0** | Lỗi định dạng (sai câu nhắc, khoảng trắng) có tính là misconception không? Mô phỏng đúng cách chấm của dataset hay chuẩn hóa mạnh hơn? | Sau Bước 1.3|
| | ✅ **Đã chốt (2026-11-19): hai chế độ.** `status` = strict (port nguyên văn `genprog_tests.py`; **exit code không tính** — đính chính sau P1.6: metadata ghi PASS cho 90/90 test rc ≠ 0 có output đúng) dùng kiểm định runner; `status_sem` = semantic (trích đáp án lỏng, sửa bug checker, bỏ qua rc) dùng cho clustering; OAV `format_only` = strict FAIL & semantic PASS. Lỗi định dạng không phải misconception nhưng được ghi nhận. Runner/schema lưu `returncode` (chỉ làm thuộc tính OAV) | |
| | ✅ **Biến chưa khởi tạo (2026-11-19):** giữ các phiên bản phụ thuộc UB, gắn cờ `uninit_dependent` (thuộc tính OAV); build chuẩn dùng `-ftrivial-auto-var-init=zero` (trong `config.GCC_FLAGS`) để tái lập. Bản nondeterministic của dataset xử lý tương tự | |
| **DP1** | Chọn 3–5 bài trọng tâm (≥ ~50 bài sai, misconception rõ ràng) | Sau Bước 1.7 |
| | ✅ **Đã chốt (2026-11-19): `digits, grade, median, smallest`** (`config.PROBLEMS`; 108/38/69/64 bài sai unique). Bỏ syllables, checksum. **Theo SV:** giữ mọi phiên bản unique khi gom cụm; macro-feedback đếm **số SV distinct** mỗi cụm (cột `repo` trong `SUB_FLAGS`) | |
| **DP2** | Taxonomy misconception cho mutation | Đầu Phase 2 |
| | ✅ **Đã chốt (2026-11-19): M1–M6 + M7 (biên so sánh trong chuỗi if) + M8 (số âm với `%`, `/`)** — xem mục 8. M2/M4 cấy vào lời giải tự viết. ITSP (1.8) để sau Phase 4 | |
| **DP3** | Trọng số nhóm thuộc tính (Test / Output-diff / AST) | Phase 3, tinh chỉnh sau ablation E3 |
| | ✅ **Đã chốt (2026-11-19): T 0, O 0.5, A 0.5, D 3** (thêm nhóm D; trọng số chuẩn hóa theo nhóm). ARI synthetic TB 0.58, thấp nhất 0.51 (agglomerative, k = số nhãn đơn) | |
| **DP4** | Số cụm k cho từng bài | Phase 4 |
| | ✅ **Đã chốt (2026-11-19):** dữ liệu thật K-modes **digits 5, grade 4, median 5, smallest 4** (`config.K_REAL`; k lớn nhất trong 3–6 có silhouette gần tối đa và cụm nhỏ nhất ≥ 2–3). Dữ liệu sinh: k = số nhãn đơn (E1) | |
| **DP5** | Đặt tên misconception cho từng cụm từ luật sinh ra | Phase 5 |
| | ✅ **Tạm chốt (2026-11-19):** dùng tên đề xuất trong `results/tables/p5_cluster_names.csv` (cột `name_draft`); người dùng sẽ sửa sau — Phase 6 đọc tên từ file này | |

---

## 8. Phase 2 — Sinh dữ liệu mutation có nhãn

**Taxonomy (DP2 đã chốt):**

| Mã | Misconception | Toán tử đột biến |
|---|---|---|
| M1 | Điều kiện biên vòng lặp | `<` ↔ `<=`, `i=0` → `i=1` |
| M2 | Truyền tham trị vs tham chiếu | bỏ `*` ở tham số và `&` ở lời gọi |
| M3 | Nhầm gán và so sánh | `==` → `=` trong điều kiện |
| M4 | Chia nguyên | bỏ ép kiểu `(float)` |
| M5 | Khởi tạo biến tích lũy | bỏ `sum=0`; `max=a[0]` → `max=0` |
| M6 | Phạm vi `return`/`break` | đưa `return` vào trong vòng lặp |
| M7 | Biên so sánh trong chuỗi `if` | `>` ↔ `>=`, `<` ↔ `<=` trong điều kiện `if` (không phải vòng lặp) — grade, ca bằng nhau ở median/smallest |
| M8 | Số âm với `%` và `/` | bỏ `abs()`, bỏ lệnh đổi dấu `n = -n`, bỏ dấu `-` khi in — digits |

**Yêu cầu:**
- `src/mutators.py`: sửa theo **byte offset từ AST tree-sitter**, không dùng regex. Duyệt cây đệ quy (không dùng `Query`).
- Nguồn bản đúng: phiên bản IntroClass pass toàn bộ test, bản `_correct.c` của ITSP, + 5–8 lời giải tự viết có con trỏ (cho M2: swap, đổi giá trị qua tham số, ...) kèm test tự viết.
- **Kiểm định mutant:** giữ nếu (1) compile được, (2) fail ≥ 1 test, (3) hành vi khác bản gốc (loại equivalent mutant).
- 30–50 mutant / misconception / bài; ~15% mutant kết hợp 2 lỗi (nhãn đa trị — ghi rõ trong `label_true`, ví dụ `M1+M4`).
- `source='synthetic'`, `label_true` bắt buộc.

**Tiến độ (2026-11-19):** P2.1 `src/mutators.py` (M1–M8, sửa theo byte offset AST, 17 unit test) · P2.2 `bench/` 11 lời giải tự viết (+ bài phụ `average` có 8 test riêng cho M4) · P2.3 `scripts/p2_3_generate.py` → `data/interim/synthetic/`, bảng `results/tables/p2_mutants.csv`.

Mutant đơn được chọn (valid = compile + fail ≥ 1 test semantic + khác hành vi bản gốc):

| problem | M1 | M2 | M3 | M4 | M5 | M6 | M7 | M8 | kép | tổng |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| digits | 24 | 5 | 50 | 0 | 4 | 50 | 29 | 48 | 37 | 247 |
| grade | 4 | 2 | 8 | 0 | 0 | 3 | 50 | 0 | 12 | 79 |
| median | 16 | 12 | 13 | 0 | 4 | 17 | 5 | 3 | 12 | 82 |
| smallest | 9 | 9 | 1 | 0 | 6 | 18 | 0 | 0 | 8 | 51 |
| average | 5 | 2 | 0 | 3 | 3 | 5 | 0 | 0 | 3 | 21 |

Tỷ lệ hợp lệ: M7 thấp nhất (26%) — ở median/smallest **mọi** mutant `>`↔`>=` đều tương đương (khi hai giá trị bằng nhau, chọn bên nào cũng ra cùng kết quả) → 0 mutant M7. M2/M4 ít vì chỉ có trong lời giải tự viết. **Bổ sung (người dùng chọn):** thêm 8 lời giải tự viết cho median/smallest (vòng lặp, mảng, hàm con trỏ) → median 36 → 82, smallest 20 → 51 mutant. Tổng `bench/`: 19 lời giải.

---

## 9. Phase 3 — Trích xuất OAV

| Nhóm | Thuộc tính ví dụ | Kiểu |
|---|---|---|
| **Test** | `bb1 … wbN` | PASS/FAIL/TIMEOUT/CRASH/OUTPUT_LIMIT |
| **Output-diff** | `off_by_one`, `output_unchanged`, `output_zero`, `truncated_decimal`, `missing_last`, `format_only` | bool |
| **AST** | `loop_cmp_op`, `has_ptr_param`, `assign_in_cond`, `int_div_on_avg`, `accum_init`, `return_in_loop` | categorical/bool |

- Lưu `oav_long.parquet` và `oav_wide.parquet` (thêm schema tương ứng vào `schema.py`).
- **Cảnh báo data leakage:** đặc trưng AST mô tả cấu trúc, nhưng có thể trùng 1-1 với toán tử mutation (ví dụ `assign_in_cond` ↔ M3) → ARI trên dữ liệu sinh đẹp giả tạo. Ưu tiên nhóm Test + Output-diff; chứng minh bằng ablation E3.
- Trọng số theo `config.FEATURE_WEIGHTS` (DP3).

✅ **Xong (2026-11-19).** `src/features.py`, `scripts/p3_extract.py` → `data/processed/oav_{long,wide}/<real|synthetic>_<problem>.parquet`, bảng `results/tables/p3_features.csv`. Cột wide: `<G>:<object>.<attribute>` (G ∈ T/O/A). Thuộc tính thực tế:
- **T** — `T:<test_id>.status` (13–18 cột/bài).
- **O** — `O:output.<kiểu sai>` (bool, trên các test fail: `missing_answer, multiple_answers, off_by_one, output_zero, wrong_input_elem, not_input_elem, sign_error, truncated_decimal, digits_reversed, missing_last, missing_items, extra_items, wrong_digit, adjacent_grade, far_grade, grade_too_low/high, timeout, crash, output_limit`); `O:tests_<prop>.fail` ∈ none/some/all với prop = `tie, negative, zero, sorted` (median/smallest), `negative, zero, single_digit, inner_zero` (digits), `boundary, failing, top` (grade); `O:tests.fail_frac` ∈ low/mid/high/all; dữ liệu thật thêm `O:run.{uninit_dependent, nondet_dataset, format_only_any}`.
- **A** — 17 cột: `loop.{count, cmp_op, output_in_loop, return_in_loop, break_in_loop}`, `condition.{assign_in_cond, if_cmp, n_if}`, `function.{n_user_funcs, has_ptr_param, addr_arg_user_call}`, `extremum.init`, `accumulator.init`, `division.{int_div_float_ctx, has_cast}`, `negation.{uses_abs, unary_minus}`.

Kiểm tra định tính (synthetic): M8 → `sign_error` 60%, M6 → `missing_items/missing_last`, M4 → `truncated_decimal` 100%.

**Bổ sung nhóm D (người dùng chọn sau chẩn đoán P4)** — `src/diff_features.py`: so bài sai với **bản đúng gần nhất** (dữ liệu thật: bản đúng sớm nhất về sau của chính SV nếu có — digits 64/108, grade 35/38, median 44/69, smallest 18/64; còn lại: gần nhất theo token trong kho IntroClass đúng + bench). Dữ liệu sinh dùng cùng quy trình (không dùng `parent_id`) → tìm đúng chương trình gốc 100% ⇒ **trên synthetic, D gần như "oracle" của phép đột biến; phép thử thật của D là dữ liệu thật (E4)**. 24 thuộc tính `D:diff.*`: `cmp_loop, cmp_if, cmp_kind (strictness/reversed), eq_assign, logic_op, loop_init, init_value, literal_other, ptr_missing/extra, cast_missing, neg_missing/extra, moved_into/out_of_loop, extra/missing_break, extra/missing_output, var_changed, arith_changed, stmt_missing/extra, size`. Bảng tham chiếu: `data/processed/refs/`.
Bỏ 4 thuộc tính A chỉ mô tả phong cách: `loop.count, condition.n_if, function.n_user_funcs, function.addr_arg_user_call`.

---

## 10. Phase 4 — Clustering

Chạy **theo từng bài**, **tách riêng** synthetic và dữ liệu thật.

| Phương pháp | Cấu hình | Vai trò |
|---|---|---|
| K-modes | `kmodes`, `init='Cao'`, `n_init≥5`, `random_state=SEED` | Chính |
| Agglomerative | average linkage, `metric='precomputed'` trên Hamming có trọng số | Dendrogram (cấu trúc cha–con) |
| K-means trên one-hot | sklearn | Baseline |
| (tùy chọn) HDBSCAN | precomputed | Phát hiện outlier / lỗi hiếm |

```python
import numpy as np
from scipy.spatial.distance import pdist, squareform

def weighted_hamming(X_codes: np.ndarray, w: np.ndarray) -> np.ndarray:
    """X_codes: ma trận mã hóa số nguyên theo cột; w: trọng số theo cột."""
    D = np.zeros((X_codes.shape[0],) * 2)
    for j in range(X_codes.shape[1]):              # vector hóa theo cột, nhanh hơn lambda trong pdist
        col = X_codes[:, j]
        D += w[j] * (col[:, None] != col[None, :])
    return D / w.sum()
```

Chọn k: quét 2–12, silhouette (precomputed) + cost K-modes (elbow) + dendrogram → **DP4**.

Output: `data/processed/clusters.parquet` (`sub_id, method, k, cluster_id`), hình silhouette/elbow/dendrogram.

**Lần chạy đầu (2026-11-19)** — `src/cluster.py`, `scripts/p4_cluster.py` → `results/tables/p4_k_sweep.csv`, `data/processed/clusters.parquet` (mọi k). Trọng số khởi điểm, chuẩn hóa theo nhóm (cột trọng số = W_nhóm / số cột nhóm). Hình để Phase 6 (image chưa có matplotlib).

- Silhouette không cho k rõ ràng: tăng dần theo k ở real median/smallest (nhiều hàng trùng hệt nhau).
- **Synthetic ARI thấp**: digits 0.14, median 0.12, smallest 0.11, average 0.15 (K-modes, k = số nhãn đơn); grade 0.88 (do M7 chiếm 50/79).
- **Ablation chẩn đoán**: nhóm A gom theo **chương trình gốc** (ARI vs `parent_id` 0.47–0.64 ở median/smallest/average) chứ không theo misconception; T/O cũng chỉ đạt ARI 0.06–0.25 → cùng một misconception biểu hiện khác nhau tùy chương trình gốc.
- Khả thi của đặc trưng "khác biệt so với lời giải đúng gần nhất": bài sai thật có bản đúng về sau của chính SV: digits 59%, grade 92%, median 64%, smallest 28%.

**Sau khi thêm D** (agglomerative, k = số nhãn đơn): D riêng lẻ ARI digits 0.49, grade 0.60, median 0.61, smallest 0.34, average 0.34 (T+O: 0.06–0.17). Ghép với trọng số khởi điểm (T1, O1.5, A0.5, D1.5) → D bị pha loãng, ARI TB 0.31. Lưới trọng số (`results/tables/p4_weight_grid.csv`): D = 3 → ARI TB 0.55–0.59; silhouette dữ liệu thật (k = 6) 0.32–0.42 gần như không đổi. ⚠ Chọn trọng số theo ARI synthetic rồi báo cáo ARI synthetic là tối ưu trên chính tập đánh giá → báo cáo E1/E3 cần ghi rõ hoặc dùng leave-one-problem-out.

---

## 11. Phase 5 — Quy nạp luật + Đánh giá

**Luật:**
- `src/ila.py`: **tự cài đặt ILA** (~100–150 dòng; thuộc nội dung môn học). So sánh với `DecisionTreeClassifier(criterion='entropy')`.
- Input: thuộc tính OAV; lớp: `cluster_id`.
- Xuất luật dạng `R3: NẾU output_unchanged=True VÀ has_ptr_param=False THÌ Cụm 2 [coverage 41/45, accuracy 0.91]`.
- → **DP5**: người dùng đặt tên misconception cho cụm.

**Thí nghiệm:**

| ID | Mục tiêu | Dữ liệu | Độ đo |
|---|---|---|---|
| E1 | Khôi phục misconception đã cấy | synthetic | ARI, NMI, Purity |
| E2 | So sánh phương pháp | synthetic | K-modes vs Agglomerative vs K-means one-hot |
| E3 | **Ablation đặc trưng** (quan trọng nhất) | synthetic | Test-only / +Output-diff / +AST |
| E4 | Áp lên dữ liệu thật | IntroClass (+ITSP) | Silhouette, Davies-Bouldin, định tính; (nếu dùng được) đối chiếu `bugclasses`; ~30 bài ITSP gán nhãn tay từ diff |
| E5 | Chất lượng luật | cả hai | coverage, accuracy, số điều kiện/luật; ILA vs ID3 |

Xuất `results/tables/E*.csv`.

**Kết quả (2026-11-19)** — `src/ila.py` (tự cài, kiểm chứng trên ví dụ của bài báo gốc), `scripts/p5_experiments.py`; luật: `results/rules/<dataset>_<problem>.txt`; cụm chính: `data/processed/clusters_main.parquet`.

- **E1/E2** (synthetic, ARI, k = số nhãn đơn): K-modes 0.48–0.73 (avg 0.54, digits 0.66, grade 0.73, median 0.48, smallest 0.67); K-means one-hot 0.47–0.98; Agglomerative 0.51–0.67. Không có phương pháp thắng tuyệt đối.
- **E1b — leave-one-problem-out cho trọng số**: ARI held-out digits 0.28, grade 0.67, median 0.51, smallest 0.15, average 0.34 (so với DP3: 0.64/0.67/0.51/0.56/0.54) → trọng số tối ưu **nhạy theo bài**; ARI với DP3 có phần lạc quan, phải nêu trong báo cáo.
- **E3 — ablation** (K-modes ARI): D là nhóm quyết định (A+D, O+D, O+A+D ≫ O, A, O+A); O+A+D tốt nhất cho digits (0.66) và smallest (0.67); T+O+A+D (bật T) giảm ở 3/5 bài.
- **E4 — dữ liệu thật** (K_REAL): silhouette digits 0.30, grade 0.50, median 0.25, smallest 0.45; cụm lệch cỡ (digits 60/4/19/15/10; smallest 48/2/7/7). Không có nhãn tham chiếu (bugclasses theo triệu chứng; ITSP để sau).
**E4b — ITSP (2026-11-20)** — `scripts/p5_itsp.py`, gom cụm **gộp 72 bài** (O tổng quát `features.output_features_generic` + A + D so với **bản sửa của chính SV**, 52 thuộc tính). Nhãn tham chiếu: `results/tables/itsp_labels.csv` — 45 cặp diff nhỏ (1–4 dòng, ≤ 1 cặp/bài, seed 42) do **Claude gán blind trước khi gom cụm, chưa qua người duyệt**; 41 còn lại sau lọc; 9 lớp (M1, M2, M6, M7, IDX, VAR, LOGIC, MISSING, FMT). Bảng `results/tables/E4b_itsp.csv`, luật `results/rules/itsp_all.txt`.
- O+A+D K-modes k = 9: **ARI 0.20, NMI 0.54, purity 0.51** (O, A riêng lẻ ≈ 0; D 0.02–0.06; O+D đến 0.18 ở k = 20).
- Cụm nhận diện được: `cmp_if + strictness` (M7, 3/3 thuần), `cmp_loop + strictness` (M1), `stmt_missing` (MISSING). Hai cụm lớn (226, 158 bài) gom theo cỡ diff + `text_only`, trộn FMT/VAR/LOGIC/M1 → D hiện chưa phân biệt được nhầm biến / sai công thức.
- Hạn chế: mẫu nhãn nhỏ (41) → ARI dao động mạnh; nhãn một người gán.
- **E5 — luật**: ILA luật ngắn hơn (1.5–2.0 điều kiện/luật vs ID3 2.8–4.6), nhiều luật hơn (8–46 vs 6–18); CV accuracy ILA 0.70–0.92, ID3 0.72–0.97.

---

## 12. Phase 6 — Trực quan hóa + báo cáo

- Heatmap **cụm × thuộc tính** (tần suất) — hình chính cho phần macro-feedback.
- **MDS** trên ma trận Hamming (không dùng t-SNE: MDS nhận trực tiếp ma trận khoảng cách, ổn định hơn với categorical), tô màu theo cụm.
- Confusion matrix `label_true` × cụm (synthetic).
- Bảng cho giảng viên: cụm → tên misconception, số sinh viên, luật tiêu biểu, 1 bài làm minh họa.

**Ánh xạ sang báo cáo:**

| Chương | Nguồn |
|---|---|
| Cơ sở lý thuyết (OAV, K-modes, Hierarchical, ILA, Entropy) | — |
| Dữ liệu | Phase 1–2 |
| Phương pháp | Phase 3–4 |
| Thực nghiệm | Phase 5 (E1–E5) |
| Ứng dụng: macro-feedback | Phase 6 |

**Kết quả (2026-11-19)** — `scripts/p6_figures.py` (matplotlib 3.10.1 thêm vào image; bảng màu theo dataviz skill: thang xanh tuần tự cho heatmap, MDS dạng small multiples vì scatter > 3 màu không đạt ngưỡng CVD):
- `results/figures/heatmap_real_<p>.png` (hình chính), `confusion_syn_<p>.png`, `mds_{real,synthetic}_<p>.png`, `ksweep_real.png`, `ablation_E3.png`.
- `results/tables/macro_feedback.{csv,md}`: cụm → tên (DP5), taxonomy, số SV, số bài, luật ILA tiêu biểu, bài minh họa (medoid). Sửa tên trong `p5_cluster_names.csv` rồi chạy lại script là cập nhật.

### 12.1. Demo giao diện (Phase 7, 2026-11-23)

Chạy: `./demo/start.sh` → http://127.0.0.1:8501 (từ máy khác: `ssh -L 8501:127.0.0.1:8501 ...`); dừng: `./demo/stop.sh`. Chi tiết: `demo/README.md`.

| Thành phần | Vai trò |
|---|---|
| `scripts/p7_build_demo.py` | dựng `data/processed/demo/model_<p>.pkl` (cột, trọng số, mode cụm, luật ILA, kho bản đúng) + `results/demo/dashboard.json` |
| `src/classify.py` | bài mới → runner → OAV (T/O/A + D so với bản đúng gần nhất) → cụm có mode gần nhất (bước gán của K-modes) + luật ILA khớp + láng giềng |
| `scripts/demo_worker.py` + service `sandbox` | worker chạy trong container riêng **`aai-sandbox`** (image `aai-lab:1`, không mạng, root fs chỉ đọc, chỉ mount `src/ scripts/ bench/`, mô hình demo và test của 4 bài ở chế độ `:ro`; ghi được duy nhất `work/queue` + tmpfs `work/demo_jobs`; 1 CPU / 1 GB / 128 PID; `restart: on-failure`). Nhận job bằng cách chuyển sang `queue/run/` → job làm chết worker không bị chạy lại |
| `ui/app.py`, `docker/Dockerfile.ui`, service `ui` trong `compose.yaml` | Streamlit 1.41.1, container `aai-ui`: **không có gcc, không chạy code**, root fs read-only, cap_drop ALL, 0.5 CPU / 512 MB, cổng chỉ `127.0.0.1:8501` |
| `demo/samples/*.c` | 6 bài mẫu tự viết (5 sai, 1 đúng) |

**Rà soát bảo mật (2026-11-23):** bản đầu chạy worker trong `aai-lab` → bài nộp **ghi được vào thư mục dự án** (đã chứng minh bằng file thử, đã xóa) → chuyển sang `aai-sandbox`. Bộ bài nộp độc hại (`work/scratch/adversarial.py`: lặp vô hạn, in vô hạn, ngủ, ăn RAM, ghi file, mở mạng, `#include "/etc/passwd"`/`"/dev/zero"`, fork bomb, tự diệt worker) đều bị chặn hoặc báo lỗi, sandbox tự hồi phục. Còn lại (chấp nhận cho demo): bài nộp đọc được file trong sandbox (code dự án, test công khai) và có thể xóa job trong hàng đợi.

Kiểm thử: `tests/test_classify.py` + AppTest toàn bộ bài mẫu. Bài mẫu tự viết 5/6 đúng cụm (`digits_quen_so_0` → nhầm cụm log10); bài minh họa thật gán lại đúng cụm 16/18 (lệch vì demo không có bản tự sửa của SV → D so với bản gần nhất).

### 12.2. Báo cáo Word (2026-11-23)

`report/BaoCao_BTL_AINangCao_MisconceptionClustering.docx` (38 trang, 20 bảng, 7 hình) — dựng theo file mẫu `BaoCao_BTL_HocMayNangCao_UIT-VSMEC.docx` (giữ bìa + style, định dạng bảng/chú thích/công thức như mẫu). Nguồn: `report/content.py` (nội dung, số liệu lấy từ `results/tables/`), `report/build.py` (dựng 2 lượt để mục lục có số trang).
- Dựng lại: `docker run --rm -v "$PWD":/w -e HOME=/tmp aai-doc:1 python -I report/build.py` (image công cụ `aai-doc:1` = python-docx + LibreOffice, Dockerfile ở `tools/Dockerfile.doc`; không cài gì lên host).
- Hình mới: `results/figures/pipeline.png` (`scripts/p8_report_figs.py`), ảnh giao diện `results/figures/demo/*.png` (Playwright, image `aai-shot:1` từ `tools/Dockerfile.shot`, script `tools/shot.py`, cần demo đang chạy).
- Còn để trống trên bìa: GVHD, học viên thực hiện. Tên học phần ghi “Trí tuệ nhân tạo nâng cao” — cần người dùng xác nhận.

### 12.3. Slide thuyết trình (2026-11-23)

Slides Artifact trên claude.ai: https://claude.ai/artifact/2rjW563aTwaEFE6hjhFCsJ (xem/sửa/tải .pptx). 14 slide chính + 1 tài liệu + 3 phụ lục hỏi đáp; bìa theo mẫu báo cáo; phong cách Swiss + xanh VMU; ghi chú thuyết trình trong từng slide. Bản sao nguồn: `report/slides/`. Skill dùng: `academic-pptx`, `pptx-design-styles` (zip upload claude.ai ở `tools/claude-skills/`).

**Hướng mở rộng (bài báo):** kết hợp embedding mã nguồn (CodeBERT/UniXcoder) với vector OAV (hybrid clustering), dùng LLM đặt tên + giải thích cụm; so sánh OAV-only vs hybrid.

---

## 13. Rủi ro đã biết

| Rủi ro | Dấu hiệu | Xử lý |
|---|---|---|
| Lỗi định dạng output chiếm đa số | phần lớn bài fail toàn bộ test | chuẩn hóa theo DP0 (Bước 1.4) |
| Runner lệch với metadata của dataset | tỷ lệ khớp < 95% | so flag gcc với Makefile dataset; xem nondeterministic |
| Ít bài sai sau lọc | < 30 bài / problem | gộp bài cùng dạng, tăng tỷ trọng synthetic |
| Data leakage AST | ARI ≈ 1.0 trên synthetic | xem E3, giảm trọng số AST |
| tree-sitter đổi API | lỗi `query/captures` | giữ pin, duyệt cây đệ quy |
| Nhiều misconception / bài | cụm lẫn | ghi nhận hạn chế; tùy chọn fuzzy k-modes |
| TIMEOUT oan do container bị giới hạn 1.5 CPU | bài đúng ra TIMEOUT; `test_no_false_timeout_under_load` fail | `os.cpu_count()` trong container vẫn trả 2 → 4 workers trên 1.5 CPU; wall timeout 6 s vẫn dư cho 2 s CPU. Nếu vẫn lệch: hỏi người dùng trước khi giảm `max_workers` hoặc tăng `cpus` |
| Job dự án làm chậm hpstin | load cao, hpstin phản hồi chậm | `cpu_shares: 256` đã ưu tiên hpstin; chạy Phase 1.6 ngoài giờ cao điểm; có thể hạ `cpus` |
| Container hết RAM | process bị OOM-kill, status CRASH bất thường | `mem_limit 3g`; runner giới hạn 256 MB/process × 4 workers ≈ 1 GB |

---

## 14. Bài học từ giai đoạn Colab (không lặp lại)

- `%load_ext autoreload` hỏng trên Python 3.13 của Colab (IPython cũ import module `imp` đã bị xóa từ 3.12). Trên server Python 3.12 với IPython mới thì dùng được; nếu lỗi, dùng `importlib.reload()`.
- Session reset làm mất biến → trên server: job dài viết thành **script trong `scripts/`**, chạy nền trong container (3.6), ghi checkpoint theo từng problem.
- Compile/chạy trên filesystem mạng rất chậm → luôn dùng `work/` trên đĩa local.
