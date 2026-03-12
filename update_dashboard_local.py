import json, argparse, re
from pathlib import Path

DATA_PATH = Path('/home/user/workspace/hormuz-monitor/data.json')
HTML_PATH = Path('/home/user/workspace/hormuz-monitor/index.html')

def fmt_price(x):
    if x is None:
        return None
    return float(x)

def fmt_price_html(x, kind='plain'):
    if x is None:
        return '-' if kind == 'table' else '—'
    # table format includes $ and rounding to nearest integer for gold/btc in current HTML
    return x

def format_row_time(display_time: str):
    # display_time: '2026-03-12 19:02 ICT' -> 'Mar 12 19:02'
    parts = display_time.split(' ')
    y,m,d = parts[0].split('-')
    hhmm = parts[1]
    month_names = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    return f"{month_names[int(m)-1]} {int(d)} {hhmm}"

def tag_class(status: str):
    if status == 'Effectively Closed':
        return 'tag tag-closed'
    if status == 'Open':
        return 'tag tag-open'
    return 'tag tag-disrupted'

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--timestamp', required=True)
    ap.add_argument('--display_time', required=True)
    ap.add_argument('--hormuz_status', required=True)
    ap.add_argument('--brent', type=float)
    ap.add_argument('--wti', type=float)
    ap.add_argument('--gold', type=float)
    ap.add_argument('--btc', type=float)
    ap.add_argument('--headline', required=True)
    args = ap.parse_args()

    data = json.loads(DATA_PATH.read_text())
    new_entry = {
        'timestamp': args.timestamp,
        'display_time': args.display_time,
        'hormuz_status': args.hormuz_status,
        'brent': args.brent if args.brent is not None else None,
        'wti': args.wti if args.wti is not None else None,
        'gold': args.gold if args.gold is not None else None,
        'btc': args.btc if args.btc is not None else None,
        'headline': args.headline[:200]
    }
    data.append(new_entry)
    DATA_PATH.write_text(json.dumps(data, indent=2))

    html = HTML_PATH.read_text()

    # Update last updated span (id="last-updated")
    html = re.sub(r'(<span id="last-updated">)(.*?)(</span>)', rf"\\1{args.display_time}\\3", html)

    # Update observation count text like "| 20 recorded observations"
    html = re.sub(r'\|\s*(\d+)\s*recorded observations', f"| {len(data)} recorded observations", html)

    # Update status bar values (ids cur-*)
    def sub_span(id_, value):
        nonlocal html
        html = re.sub(rf'(<span[^>]*id="{id_}"[^>]*>)(.*?)(</span>)', rf"\\1{value}\\3", html)

    sub_span('cur-hormuz', args.hormuz_status)
    sub_span('cur-brent', f"{args.brent:.2f}" if args.brent is not None else '-')
    sub_span('cur-wti', f"{args.wti:.2f}" if args.wti is not None else '-')
    sub_span('cur-gold', f"{args.gold:.2f}" if args.gold is not None else '-')
    sub_span('cur-btc', f"{args.btc:,.0f}" if args.btc is not None else '-')

    # Insert new row right after <tbody id="log-body"> tag
    time_cell = format_row_time(args.display_time)
    tag = f"<span class=\"{tag_class(args.hormuz_status)}\">{args.hormuz_status}</span>"

    def money(v, decimals=2):
        return '-' if v is None else f"${v:.{decimals}f}"

    brent_cell = money(args.brent, 2)
    wti_cell = money(args.wti, 2)
    gold_cell = '-' if args.gold is None else f"${args.gold:,.0f}"
    btc_cell = '-' if args.btc is None else f"${args.btc:,.0f}"

    row = (
        f"<tr><td>{time_cell}</td><td>{tag}</td><td>{brent_cell}</td><td>{wti_cell}</td>"
        f"<td>{gold_cell}</td><td>{btc_cell}</td><td class=\"headline\">{args.headline[:200]}</td></tr>\n"
    )

    marker = '<tbody id="log-body">'
    idx = html.find(marker)
    if idx == -1:
        raise SystemExit('No log-body tbody found')
    insert_at = idx + len(marker)
    html = html[:insert_at] + row + html[insert_at:]

    HTML_PATH.write_text(html)

if __name__ == '__main__':
    main()
