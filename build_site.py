"""Builds the 다함께돌봄 안내 pages and QR codes.
Pages: index.html (all centers, choose one) and 8.html / 9.html / 10.html (one center).
Each center page shows its flyer (flyers/<n>.jpg|png|pdf when present) and a 신청하기 button that opens
the Google Form with that center already checked (prefilled entry.1460899233).
QR PNG in qr/ points at the Linktree page, whose 8/9/10 buttons open these pages. Rerun after adding or replacing flyers."""
import os, glob, html, urllib.parse
import qrcode
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = 'https://park-hyun-su.github.io/dahamkke-dolbom/'
LINKTREE = 'https://linktr.ee/YeongJong_Together_Care_Center'
FORM = 'https://docs.google.com/forms/d/e/1FAIpQLSfJHSxFiwpyxkl7W1CWkbjg26NQrutEgFMD_qZciQFK3CMH-A/viewform'
ENTRY = 'entry.1460899233'
CENTERS = [  # name = exact option text in the form; address from the form description
    ('8', '다함께 돌봄센터 8호점', '찬들로 142, 커뮤니티센터 지상 1층'),
    ('9', '다함께 돌봄센터 9호점', '영종대로565번길 20, 커뮤니티센터 지상 1층'),
    ('10', '다함께 돌봄센터 10호점', '은하수로 412, 커뮤니티센터 지하 1층'),
]
esc = html.escape


def form_url(name):
    return FORM + '?usp=pp_url&' + urllib.parse.urlencode({ENTRY: name})


def flyers(n):
    fs = sorted(glob.glob(os.path.join(ROOT, 'flyers', f'{n}.*')) + glob.glob(os.path.join(ROOT, 'flyers', f'{n}-*.*')))
    return [os.path.relpath(f, ROOT).replace('\\', '/') for f in fs]


CSS = """
:root{--bg:#f6f7f9;--card:#fff;--fg:#1c1d1f;--sub:#5f6368;--line:#e3e5e8;--btn:#1f6f4a;--btnfg:#fff}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#141516;--card:#1d1f21;--fg:#eceef0;--sub:#a5aab0;--line:#2e3134;--btn:#2f8a5f;--btnfg:#fff}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:17px/1.65 "Pretendard","Apple SD Gothic Neo","Malgun Gothic",system-ui,sans-serif;word-break:keep-all;overflow-wrap:anywhere}
main{max-width:640px;margin:0 auto;padding:28px 16px 64px}
h1{font-size:26px;line-height:1.3;margin:0 0 6px}
.sub{color:var(--sub);font-size:15px;margin:0 0 22px}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px;margin:0 0 16px}
.card h2{font-size:20px;margin:0 0 4px}
.addr{color:var(--sub);font-size:15px;margin:0 0 14px}
.flyer{display:block;width:100%;border-radius:10px;border:1px solid var(--line);margin:0 0 14px;background:var(--card)}
.btn{display:block;text-align:center;background:var(--btn);color:var(--btnfg);text-decoration:none;font-weight:700;font-size:18px;padding:15px 12px;border-radius:12px}
.link{display:block;text-align:center;color:var(--fg);text-decoration:none;font-weight:600;padding:12px;border:1px solid var(--line);border-radius:12px;margin:0 0 10px}
.note{color:var(--sub);font-size:14px;margin:18px 0 0}
a.pdf{display:block;margin:0 0 14px;color:var(--fg)}
"""


def page(title, body):
    return f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title><style>{CSS}</style></head><body><main>{body}</main></body></html>"""


def flyer_html(n, name):
    out = []
    for f in flyers(n):
        if f.lower().endswith('.pdf'):
            out.append(f'<a class="pdf" href="{esc(f)}">{esc(name)} 홍보지 열기 (PDF)</a>')
        else:
            out.append(f'<img class="flyer" src="{esc(f)}" alt="{esc(name)} 홍보지">')
    return ''.join(out)


for n, name, addr in CENTERS:
    body = f"""<h1>영종 {esc(name)}</h1>
<p class="sub">홍보지를 보시고 아래 단추로 신청서를 작성해 주세요.</p>
<section class="card">
{flyer_html(n, name)}
<p class="addr">위치: {esc(addr)}</p>
<a class="btn" href="{esc(form_url(name))}">{esc(n)}호점 신청하기</a>
</section>
<a class="link" href="{LINKTREE}">다른 호점 보기</a>
<p class="note">신청서에는 이용 센터가 「{esc(name)}」으로 미리 선택되어 있습니다.</p>"""
    open(os.path.join(ROOT, f'{n}.html'), 'w', encoding='utf-8').write(page(f'다함께돌봄 {n}호점 신청', body))

cards = ''.join(f"""<section class="card"><h2>{esc(name)}</h2><p class="addr">{esc(addr)}</p>
{flyer_html(n, name)}<a class="btn" href="{n}.html">{esc(n)}호점 안내 보고 신청하기</a></section>""" for n, name, addr in CENTERS)
body = f"""<h1>영종 다함께 돌봄센터 신청 안내</h1>
<p class="sub">이용하실 센터를 골라 홍보지를 보시고 신청해 주세요.</p>{cards}"""
open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(page('다함께돌봄 신청 안내', body))

# ---- QR codes (print size 1200 px, label under the code) ----
os.makedirs(os.path.join(ROOT, 'qr'), exist_ok=True)
font_path = next((p for p in [r'C:\Windows\Fonts\malgunbd.ttf', r'C:\Windows\Fonts\malgun.ttf'] if os.path.exists(p)), None)
# QR only to the Linktree page (user decision 2026-11-08); centers are reached from its buttons
targets = [('linktree', LINKTREE, '영종 다함께 돌봄센터 신청 안내')]
for key, url, label in targets:
    q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=30, border=4)
    q.add_data(url); q.make(fit=True)
    img = q.make_image(fill_color='black', back_color='white').convert('RGB')
    W, H = img.size
    canvas = Image.new('RGB', (W, H + 150), 'white')
    canvas.paste(img, (0, 0))
    d = ImageDraw.Draw(canvas)
    f = ImageFont.truetype(font_path, 56) if font_path else ImageFont.load_default()
    tw = d.textlength(label, font=f)
    d.text(((W - tw) / 2, H + 30), label, fill='black', font=f)
    canvas.save(os.path.join(ROOT, 'qr', f'qr-{key}.png'))
    print(key, url)
