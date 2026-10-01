"""
DF06 Kelompok 6 — Generate baseline CSV log
Hitung SHA-256 semua baseline dan simpan ke CSV.
"""
import hashlib, csv
from pathlib import Path
from datetime import datetime

baseline_dir = Path(r'E:\UNIVERSITAS PENDIDIKAN INDONESIA\SEMESTER 5\DIGITAL FORENSICS\DF06_KELOMPOK6\01_BASELINE')
files = sorted(baseline_dir.glob('*.jpg'))

rows = []
for p in files:
    sha = hashlib.sha256(p.read_bytes()).hexdigest()
    rows.append({
        'filename': p.name,
        'size_bytes': p.stat().st_size,
        'sha256': sha,
        'format': 'JPEG',
        'resolution': '640x480',
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M WIB'),
        'status': 'baseline'
    })

out_csv = Path(r'E:\UNIVERSITAS PENDIDIKAN INDONESIA\SEMESTER 5\DIGITAL FORENSICS\DF06_KELOMPOK6\06_RAW_RESULTS\baseline_generate_log.csv')
with open(out_csv, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

print(f'CSV saved: {out_csv}')
print(f'Total rows: {len(rows)}')
total_size = sum(r['size_bytes'] for r in rows)
print(f'Total size: {total_size:,} bytes')
print()
print('Sample:')
for r in rows[:3]:
    print(f"  {r['filename']}  {r['size_bytes']:>8,} bytes  {r['sha256'][:24]}...")
print(f"  ...")
print(f"  {rows[-1]['filename']}  {rows[-1]['size_bytes']:>8,} bytes  {rows[-1]['sha256'][:24]}...")
