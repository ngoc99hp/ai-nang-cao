"""Worker demo (chạy trong container aai-sandbox, không mạng, root fs chỉ đọc): xử lý hàng đợi work/queue/in/*.json → work/queue/out/<id>.json.

Giao diện (container aai-ui) chỉ ghi file job; mọi compile/chạy code đi qua src/runner.py ở đây.
  docker compose up -d sandbox   (log: docker logs aai-sandbox)
Job: {"problem": "...", "code": "..."}; id = tên file (chữ, số, -, _).
"""
import json
import os
import re
import shutil
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import classify
import config

Q = config.WORK / 'queue'
IN, RUN, OUT, JOBS = Q / 'in', Q / 'run', Q / 'out', config.WORK / 'demo_jobs'
ID = re.compile(r'[0-9a-f]{32}')                # uuid4().hex do giao diện sinh
for d in (IN, RUN, OUT, JOBS):
    d.mkdir(parents=True, exist_ok=True)


def write_out(jid, obj):
    tmp = OUT / f'{jid}.tmp'
    tmp.write_text(json.dumps(obj, ensure_ascii=False))
    os.replace(tmp, OUT / f'{jid}.json')


# Job còn trong run/ = worker đã chết giữa chừng khi chạy nó (vd. bài nộp diệt tiến trình) → không chạy lại
for f in RUN.glob('*.json'):
    if ID.fullmatch(f.stem):
        write_out(f.stem, dict(status='error', elapsed=0,
                               message='Bài nộp làm dừng bộ chấm (ví dụ tự diệt tiến trình) — không chấm được.'))
        print(f'{f.stem}: bỏ qua (làm dừng worker lần trước)', flush=True)
    f.unlink(missing_ok=True)
for p in config.PROBLEMS:                       # nạp sẵn mô hình
    classify.model(p)
print('worker sẵn sàng', flush=True)

last_clean = 0.0
while True:
    if time.time() - last_clean > 60:           # kết quả không ai lấy (giao diện đã hết chờ) → xóa sau 10 phút
        for f in OUT.glob('*'):
            if time.time() - f.stat().st_mtime > 600:
                f.unlink(missing_ok=True)
        last_clean = time.time()
    jobs = sorted(IN.glob('*.json'), key=lambda f: f.stat().st_mtime)
    if not jobs:
        time.sleep(0.5)
        continue
    f = jobs[0]
    jid = f.stem
    if not ID.fullmatch(jid):
        f.unlink(missing_ok=True)
        continue
    claimed = RUN / f.name
    try:
        os.replace(f, claimed)                  # nhận job
    except FileNotFoundError:
        continue
    t0 = time.time()
    try:
        job = json.loads(claimed.read_text())
        res = classify.classify(str(job['problem']), str(job['code']), JOBS / jid)
    except Exception as e:                      # lỗi của job không làm chết worker
        msg = ('Bài nộp tạo quá nhiều tiến trình (fork) — đã bị chặn.' if isinstance(e, BlockingIOError)
               else str(e))
        res = dict(status='error', message=msg, trace=traceback.format_exc()[-1500:])
    res['elapsed'] = round(time.time() - t0, 2)
    write_out(jid, res)
    shutil.rmtree(JOBS / jid, ignore_errors=True)
    claimed.unlink(missing_ok=True)
    print(f'{jid}: {res["status"]} {res["elapsed"]}s', flush=True)
