"""Build weekly.xml (RSS 2.0, one item) for the iMoney weekly market wrap email.
Usage: python3 -I build_weekly.py <market-tracker.json> <out weekly.xml> <wrap.json>
wrap.json: {"title": str, "intro": str, "sections": [{"heading","body"}], "date": "YYYY-MM-DD"}
"""
import json, sys, html, datetime
from email.utils import format_datetime
src, out, wrapf = sys.argv[1:4]
d = json.load(open(src)); w = json.load(open(wrapf))
e = html.escape
def dmy(s):
    s = (s or '')[:10]; p = s.split('-')
    return f"{p[2]}-{p[1]}-{p[0][2:]}" if len(p) == 3 else (s or '—')
def pct(v, sign=True, dp=2):
    if v is None or v == '': return '—'
    v = float(v); return (('+' if sign and v > 0 else '') + f"{v:,.{dp}f}%")
def num(v, dp=0):
    if v is None or v == '': return '—'
    return f"{float(v):,.{dp}f}"
col = lambda v: '#1d7a3e' if v and float(v) > 0 else ('#b42318' if v and float(v) < 0 else '#26303d')
td = 'style="padding:6px 8px;border-bottom:1px solid #e3dccf;font-size:14px"'
tdr = 'style="padding:6px 8px;border-bottom:1px solid #e3dccf;font-size:14px;text-align:right;white-space:nowrap"'
th = 'style="padding:6px 8px;background:#0b2340;color:#fff;font-size:12px;text-align:left"'
rows = ''.join(f'<tr><td {td}>{e(r["index"])}</td><td {tdr}>{num(r["level"])}</td><td {tdr}><span style="color:{col(r["change_pct"])}">{pct(r["change_pct"])}</span></td><td {td}>{dmy(r["as_of"])}</td></tr>' for r in d['indices'])
by = lambda rows, k, v: next((r for r in rows if r.get(k) == v), {})
rba = by(d['cash_rates'], 'bank', 'RBA'); au = by(d['inflation'], 'country', 'Australia')
aud = sorted(d['audusd'], key=lambda r: r['date'])[-1]
au10 = by(d['bond_yields'], 'country', 'Australia'); us10 = by(d['bond_yields'], 'country', 'United States')
key = (f'<p style="font-size:15px;margin:0 0 6px"><b>RBA cash rate</b> {e(rba.get("rate_label","—"))} · <b>Australian CPI</b> {pct(au.get("annual_pct"), False, 1)} ({e(au.get("period",""))}) · '
       f'<b>AUD/USD</b> {num(aud.get("rate"), 4)} · <b>10-yr yields</b> Australia {pct(au10.get("yield_pct"), False)}, US {pct(us10.get("yield_pct"), False)}</p>')
secs = ''.join(f'<h3 style="color:#1540b3;font-size:17px;margin:20px 0 6px">{e(s["heading"])}</h3><p style="font-size:15px;line-height:1.6;margin:0">{e(s["body"])}</p>' for s in w['sections'])
warn = ('<p style="font-size:12px;color:#5f6772;line-height:1.5;margin-top:24px;border-top:1px solid #e3dccf;padding-top:12px"><b>General advice warning.</b> This email is general information and market commentary only. '
        'It does not take into account your objectives, financial situation or needs and is not a recommendation to buy or sell any investment. Before acting on it, consider whether it is appropriate for you and read the relevant '
        'Product Disclosure Statement and Target Market Determination. Past performance is not a reliable indicator of future performance. Figures are from public market reports and official releases and may have changed since. '
        'iMoney Pty Ltd ABN 75 163 810 820 is a Corporate Authorised Representative (No. 000448872) of AD Advisory Services Pty Ltd ABN 68 005 830 802, AFSL 237058. '
        'Andrew Hayes is an Authorised Representative (No. 000263858) of AD Advisory Services Pty Ltd. Our <a href="https://imoneywealth.com/fsg">Financial Services Guide</a>.</p>')
body = (f'<p style="font-size:16px;line-height:1.6">{e(w["intro"])}</p>{secs}'
        f'<h3 style="color:#0b2340;font-size:17px;margin:24px 0 8px">Markets at a glance</h3>{key}'
        f'<table cellpadding="0" cellspacing="0" style="border-collapse:collapse;width:100%;margin-top:8px"><tr><th {th}>Index</th><th {th}>Level</th><th {th}>Day</th><th {th}>Date</th></tr>{rows}</table>'
        f'<p style="margin:20px 0"><a href="https://imoneywealth.com/market-tracker" style="background:#1540b3;color:#fff;padding:10px 16px;border-radius:8px;text-decoration:none;font-weight:600">See the full market tracker</a></p>{warn}')
dt = datetime.datetime.fromisoformat(w['date'] + 'T07:45:00+11:00')
title = w['title']
xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
<title>iMoney weekly market wrap</title>
<link>https://imoneywealth.com/market-tracker</link>
<atom:link href="https://andrewhayes-spec.github.io/imoney-market-data/weekly.xml" rel="self" type="application/rss+xml"/>
<description>A plain-English weekly wrap of what moved markets, from iMoney.</description>
<language>en-au</language>
<lastBuildDate>{format_datetime(dt)}</lastBuildDate>
<item>
<title>{e(title)}</title>
<link>https://imoneywealth.com/market-tracker#{w['date']}</link>
<guid isPermaLink="false">imoney-wrap-{w['date']}</guid>
<pubDate>{format_datetime(dt)}</pubDate>
<author>andrew.hayes@imoneywealth.com (Andrew Hayes, iMoney)</author>
<description>{e(w["intro"])}</description>
<content:encoded><![CDATA[{body}]]></content:encoded>
</item>
</channel>
</rss>
'''
open(out, 'w').write(xml)
print('ok', len(xml))
