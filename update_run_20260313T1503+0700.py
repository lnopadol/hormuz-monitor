import json, datetime, re
from zoneinfo import ZoneInfo

DATA_PATH = '/home/user/workspace/hormuz-monitor/data.json'
INDEX_PATH = '/home/user/workspace/hormuz-monitor/index.html'

# New observation (manual inputs)
timestamp = '2026-03-13T15:03:00+07:00'
display_time = '2026-03-13 15:03 ICT'
hormuz_status = 'Severely Disrupted'
brent = 99.10
wti = 93.57
gold = 5113.60
btc = 72235.89
headline = 'Oil eases but stays elevated; Reuters says Iran tells UN it will not close Hormuz, though shipping remains near-standstill.'

new_entry = {
    'timestamp': timestamp,
    'display_time': display_time,
    'hormuz_status': hormuz_status,
    'brent': brent,
    'wti': wti,
    'gold': gold,
    'btc': btc,
    'headline': headline[:200]
}

# Update data.json
with open(DATA_PATH, 'r', encoding='utf-8') as f:
    data = json.load(f)

data.append(new_entry)

with open(DATA_PATH, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write('\n')

# Update index.html
with open(INDEX_PATH, 'r', encoding='utf-8') as f:
    html = f.read()

# Update last updated span
html = re.sub(r'(<span id="last-updated">)(.*?)(</span>)', r"\1{}\3".format(display_time), html, flags=re.DOTALL)

# Update observation count in subtitle (assumes '(N observations)')
count = len(data)
html = re.sub(r'(\()\d+( observations\))', r"\g<1>{}\g<2>".format(count), html)

# Helper to update status bar values by element id
repls = {
    'hormuz-status': hormuz_status,
    'brent-price': f"{brent:.2f}",
    'wti-price': f"{wti:.2f}",
    'gold-price': f"{gold:.2f}",
    'btc-price': f"{btc:.2f}",
}
for el_id, val in repls.items():
    pattern = rf'(<span id="{re.escape(el_id)}">)(.*?)(</span>)'
    html = re.sub(pattern, lambda m, v=val: m.group(1) + str(v) + m.group(3), html, flags=re.DOTALL)

# Insert new row at top of tbody (after <tbody>)
row = f"<tr><td>{display_time}</td><td>{hormuz_status}</td><td>{brent:.2f}</td><td>{wti:.2f}</td><td>{gold:.2f}</td><td>{btc:.2f}</td><td>{headline}</td></tr>\n"
html = re.sub(r'(<tbody>\s*)', r"\1" + row, html, count=1)

with open(INDEX_PATH, 'w', encoding='utf-8') as f:
    f.write(html)

print('Updated data.json and index.html with new entry; count=', count)
