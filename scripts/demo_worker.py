"""Worker demo (chạy trong aai-lab, không mạng): xử lý hàng đợi work/queue/in/*.json → work/queue/out/<id>.json.

Giao diện (container aai-ui) chỉ ghi file job; mọi compile/chạy code đi qua src/runner.py ở đây.
  docker exec -d aai-lab bash -c 'python -W ignore scripts/demo_worker.py > work/logs/demo_worker.log 2>&1'
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
IN, OUT, JOBS = Q / 'in', Q / 'out', config.WORK / 'demo_jobs'
for d in (IN, OUT, JOBS):
    d.mkdir(parents=True, exist_ok=True)
for p in config.PROBLEMS:                       # nạp sẵn mô hình
    classify.model(p)
print('worker sẵn sàng', flush=True)


def write_out(jid, obj):
    tmp = OUT / f'{jid}.tmp'
    tmp.write_text(json.dumps(obj, ensure_ascii=False))
    os.replace(tmp, OUT / f'{jid}.json')


while True:
    jobs = sorted(IN.glob('*.json'), key=lambda f: f.stat().st_mtime)
    if not jobs:
        time.sleep(0.5)
        continue
    f = jobs[0]
    jid = f.stem
    t0 = time.time()
    try:
        if not re.fullmatch(r'[\w-]{1,64}', jid):
            raise ValueError('job id không hợp lệ')
        job = json.loads(f.read_text())
        res = classify.classify(str(job['problem']), str(job['code']), JOBS / jid)
    except Exception as e:                      # lỗi của job không làm chết worker
        res = dict(status='error', message=str(e), trace=traceback.format_exc()[-1500:])
    res['elapsed'] = round(time.time() - t0, 2)
    if re.fullmatch(r'[\w-]{1,64}', jid):
        write_out(jid, res)
        shutil.rmtree(JOBS / jid, ignore_errors=True)
    f.unlink(missing_ok=True)
    print(f'{jid}: {res["status"]} {res["elapsed"]}s', flush=True)
