"""
dbr_P_01_build.py
בונה את dbr_P_01_data.csv — טבלה שטוחה: שורה אחת למועמד, 98 עמודות.

מקורות:
  - data/ntm.csv       (נושאים × מועמדים, 12 שורות למועמד)
  - data/sm.csv        (פרמטרים גלובליים, שורה למועמד)

עמודות הפלט:
  6  מזהים         id1..id6
  72 נושאים        sud01..sud12, sud01e..sud12e,
                   suc01..suc12, suc01e..suc12e,
                   sut01..sut12, sut01e..sut12e
  5  גולמיים       zps, zpc, zr1, zr2, zr3
  5  חישובי מועמד  zcca..zcce
  10 חישובי קבוצה  zcrg0..zcrg9
"""

import csv
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(ROOT, 'data')

NTM_PATH = os.path.join(DATA, 'ntm.csv')
SM_PATH  = os.path.join(DATA, 'sm.csv')
OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        '..', 'run', 'dbr_P_01_data.csv')

# ── Column definitions ──────────────────────────────────────────────────────

ID_COLS = ['id1', 'id2', 'id3', 'id4', 'id5', 'id6']

TOPIC_NUMS = [f'{i:02d}' for i in range(1, 13)]

# sud = score, sude = evidence (for each axis × topic)
TOPIC_COLS = []
for prefix in ['sud', 'suc', 'sut']:
    for num in TOPIC_NUMS:
        TOPIC_COLS.append(f'{prefix}{num}')
        TOPIC_COLS.append(f'{prefix}{num}e')

RAW_COLS = ['zps', 'zpc', 'zr1', 'zr2', 'zr3']

COMP_CANDIDATE_COLS = ['zcca', 'zccb', 'zccc', 'zccd', 'zcce']

COMP_GROUP_COLS = [f'zcrg{i}' for i in range(10)]

ALL_COLS = ID_COLS + TOPIC_COLS + RAW_COLS + COMP_CANDIDATE_COLS + COMP_GROUP_COLS

# ── NTM axis mapping ────────────────────────────────────────────────────────
# NTM columns: עמדות_ציון, עמדות_ביטחון, ביצוע_ציון, ביצוע_ביטחון, תדמית_ציון, תדמית_ביטחון
# Map to: sud=עמדות, suc=ביצוע, sut=תדמית

AXIS_MAP = {
    'sud': ('עמדות_ציון', 'עמדות_ביטחון'),
    'suc': ('ביצוע_ציון', 'ביצוע_ביטחון'),
    'sut': ('תדמית_ציון', 'תדמית_ביטחון'),
}

# ── Load NTM ────────────────────────────────────────────────────────────────

def load_ntm():
    """Returns dict: { candidate_name: { 'D01': row_dict, ... } }"""
    db = {}
    with open(NTM_PATH, encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            name = row.get('מועמד', '').strip()
            num = row.get('מספר_נושא', '').strip()
            if not name or not num:
                continue
            code = f'D{int(num):02d}'
            if name not in db:
                db[name] = {}
            db[name][code] = row
    return db

# ── Load SM ─────────────────────────────────────────────────────────────────

def load_sm():
    """Returns dict: { candidate_name: row_dict }"""
    db = {}
    with open(SM_PATH, encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            name = row.get('מועמד', '').strip()
            if name:
                db[name] = row
    return db

# ── Compute candidate-level fields ──────────────────────────────────────────

def compute_zcca(topic_scores):
    """zcca = ממוצע עמדות (average of sud scores that are not empty)"""
    vals = []
    for num in TOPIC_NUMS:
        v = topic_scores.get(f'sud{num}', '')
        if v != '':
            try:
                vals.append(float(v))
            except ValueError:
                pass
    return round(sum(vals) / len(vals), 1) if vals else ''

# ── Build flat row ──────────────────────────────────────────────────────────

def build_row(name, ntm_data, sm_row):
    row = {c: '' for c in ALL_COLS}

    # id1 = candidate name
    row['id1'] = name

    # Topic fields from NTM
    for num in TOPIC_NUMS:
        code = f'D{num}'
        ntm_row = ntm_data.get(code, {})
        for prefix, (score_col, conf_col) in AXIS_MAP.items():
            score_val = ntm_row.get(score_col, '').strip()
            conf_val = ntm_row.get(conf_col, '').strip()
            row[f'{prefix}{num}'] = score_val
            row[f'{prefix}{num}e'] = conf_val

    # Raw SM fields
    if sm_row:
        row['zps'] = sm_row.get('סגנון', '')
        row['zpc'] = sm_row.get('סגנון_ביטחון', '')
        row['zr1'] = sm_row.get('תפקיד_מאבק', '')
        row['zr2'] = sm_row.get('תפקיד_חקיקה', '')
        row['zr3'] = sm_row.get('תפקיד_חיבור', '')

    # Computed candidate fields
    row['zcca'] = compute_zcca(row)

    return row

# ── Main ────────────────────────────────────────────────────────────────────

def main():
    ntm = load_ntm()
    sm = load_sm()

    # All candidate names (union of both sources)
    all_names = sorted(set(list(ntm.keys()) + list(sm.keys())))

    rows = []
    for name in all_names:
        row = build_row(name, ntm.get(name, {}), sm.get(name))
        rows.append(row)

    # Write CSV
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=ALL_COLS)
        writer.writeheader()
        writer.writerows(rows)

    print(f'OK: {OUT_PATH}')
    print(f'   {len(rows)} candidates, {len(ALL_COLS)} columns')

if __name__ == '__main__':
    main()
