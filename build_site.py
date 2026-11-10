"""Builds the 다함께돌봄 안내 pages and QR codes.
Pages: index.html (all centers, choose one) and 8.html / 9.html / 10.html (one center).
Each center page shows its flyer (flyers/<n>.jpg|png|pdf when present) and a 신청하기 button that opens
the Google Form with that center already checked (prefilled entry.1460899233).
QR PNG in qr/ points at the Linktree page, whose 8/9/10 buttons open these pages. Rerun after adding or replacing flyers."""
import os, glob, html, urllib.parse
import qrcode
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = 'https://yeongjong-togethercare.github.io/'
LINKTREE = 'https://linktr.ee/YeongJong_Together_Care_Center'
FORM = 'https://docs.google.com/forms/d/e/1FAIpQLSfJHSxFiwpyxkl7W1CWkbjg26NQrutEgFMD_qZciQFK3CMH-A/viewform'
ENTRY = 'entry.1460899233'
CENTERS = [  # name = exact option text in the form; address from the form description / flyer
    ('8', '다함께 돌봄센터 8호점', '찬들로 142, 커뮤니티센터 지상 1층'),
    ('9', '다함께 돌봄센터 9호점', '영종대로565번길 20, 커뮤니티센터 지상 1층'),
    ('10', '다함께 돌봄센터 10호점', '은하수로 412, 커뮤니티센터 지하 1층'),
]
CAPACITY = {'8': '정원 20명', '9': '정원 35명', '10': '정원 20명'}  # from the flyer (flyers/main.png, 2026-11-10 판)
PHONE = {'8': '032) 752-1412', '9': '032) 752-2412', '10': '032) 751-3412'}  # from the flyer (2026-11-10 판)
def tel(n):
    return '<a href="tel:' + PHONE[n].replace(') ', '-').replace(')', '-') + '">☎ ' + esc(PHONE[n]) + '</a>'
esc = html.escape


# one Google Form per center (given by the user 2026-11-08 22:45); each form has no center question
CENTER_FORMS = {
    '다함께 돌봄센터 8호점': 'https://forms.gle/E5fAy72eKyufHbdG8',
    '다함께 돌봄센터 9호점': 'https://forms.gle/rEWt49MLSrKaP9ddA',
    '다함께 돌봄센터 10호점': 'https://forms.gle/4vLJVJH1ge7mgqMZ7',
}


def form_url(name):
    return CENTER_FORMS[name]


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
<p class="addr">위치: {esc(addr)} ({esc(CAPACITY[n])})<br>{tel(n)}</p>
<a class="btn" href="{esc(form_url(name))}">{esc(n)}호점 신청하기</a>
</section>
<a class="link" href="{LINKTREE}">다른 호점 보기</a>
<p class="note">「{esc(name)}」 전용 신청서가 열립니다.</p>"""
    open(os.path.join(ROOT, f'{n}.html'), 'w', encoding='utf-8').write(page(f'다함께돌봄 {n}호점 신청', body))

# ---- landing page (QR target): flyer -> center locations -> "신청하고 싶어요" icon -> prefilled form ----
LAND_CSS = """
:root{--bg:#fffaf0;--card:#ffffff;--fg:#2b2620;--sub:#6b6156;--line:#f0e3cc;
 --c8:#f4a340;--c9:#5bb36a;--c10:#7a8cf0;--btnfg:#ffffff}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#1d1a16;--card:#27231e;--fg:#f3ece2;--sub:#bdb2a3;--line:#3a332a}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:17px/1.65 "Pretendard","Apple SD Gothic Neo","Malgun Gothic",system-ui,sans-serif;word-break:keep-all;overflow-wrap:anywhere}
main{max-width:640px;margin:0 auto;padding:24px 16px 56px}
.hero{text-align:center;margin:4px 0 18px}
.hero h1{font-size:27px;line-height:1.3;margin:0 0 6px}
.hero p{margin:0;color:var(--sub);font-size:15px}
.flyer{display:block;width:100%;border-radius:18px;border:1px solid var(--line);margin:0 0 22px;background:var(--card)}
.pdf{display:block;text-align:center;margin:0 0 22px;color:var(--fg);font-weight:600}
h2.sec{font-size:19px;margin:6px 0 12px}
.center{display:flex;gap:14px;align-items:center;background:var(--card);border:1px solid var(--line);border-radius:18px;padding:16px;margin:0 0 14px}
.center .info{flex:1;min-width:0}
.center h3{margin:0 0 2px;font-size:19px}
.center .addr{margin:0;color:var(--sub);font-size:15px}
.addr a{color:var(--fg);font-weight:600;text-decoration:none}
.apply{flex:none;display:flex;flex-direction:column;align-items:center;gap:6px;text-decoration:none;color:var(--fg);font-weight:700;font-size:14px;width:96px}
.apply .ico{width:72px;height:72px;border-radius:50%;display:grid;place-items:center;color:var(--btnfg);box-shadow:0 4px 0 rgba(0,0,0,.12)}
.apply svg{width:38px;height:38px}
.c8 .ico{background:var(--c8)} .c9 .ico{background:var(--c9)} .c10 .ico{background:var(--c10)}
.note{color:var(--sub);font-size:14px;margin:16px 0 0;text-align:center}
"""
ICON = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
        'stroke-linejoin="round" aria-hidden="true"><path d="M9 11V5.5a1.5 1.5 0 0 1 3 0V10"/><path d="M12 10V4.5a1.5 1.5 0 0 1 3 0V10"/>'
        '<path d="M15 10V6.5a1.5 1.5 0 0 1 3 0V14a6 6 0 0 1-6 6h-1a6 6 0 0 1-5-2.7L3.6 14a1.5 1.5 0 0 1 2.5-1.7L9 15"/></svg>')


def main_flyers():
    fs = sorted(glob.glob(os.path.join(ROOT, 'flyers', 'main*.*')))
    out = []
    for f in fs:
        r = os.path.relpath(f, ROOT).replace('\\', '/')
        out.append(f'<a class="pdf" href="{esc(r)}">홍보 전단지 열기 (PDF)</a>' if r.lower().endswith('.pdf')
                   else f'<img class="flyer" src="{esc(r)}" alt="영종 다함께 돌봄센터 홍보 전단지">')
    return ''.join(out)


# readable text version of the poster table (the poster image the centre supplied is only 398x540 px,
# so its table text is blurry on phones). Wording copied from the poster; do not edit content here.
POSTER_INFO = [
    ('모집 대상', ['돌봄이 필요한 만 6세 ~ 12세 아동', '(만 6세이나 입학 전 아동 포함)']),
    ('접수 방법', ['2026.11.12일부터 10시부터 전화 및 방문접수 (평일 10시 ~ 18시)']),
    ('우선 순위', ['맞벌이가정, 한부모가정, 다자녀가정, 초등 저학년, 다문화 가정', '선발기준: 정원의 10%는 단지내 아동으로 우선 배정합니다.', '정원 마감 전까지 선착순 접수 마감합니다.']),
    ('이용 요금', ['정기돌봄 월 70,000원 / 일시돌봄 일 5,000원', '(간식비 포함) / 방학기간 중식 무상 지원']),
    ('이용 시간', ['학기 중: 13시 ~ 20시', '방학 중: 09시 ~ 18시', '(주말 공휴일 제외)']),
    ('프로그램', ['기본프로그램: 출결확인, 일상생활 지도, 간식제공', '활동프로그램: 독서지도, 신체활동, 음악, 미술 등 영종특화프로그램']),
]
info_html = '<div class="infobox">' + ''.join(
    f'<div class="row"><div class="k">{esc(k)}</div><div class="v">' + ''.join(f'<p>{esc(x)}</p>' for x in vs) + '</div></div>'
    for k, vs in POSTER_INFO) + '</div>'
LAND_CSS += """
.infobox{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:6px 16px;margin:0 0 22px}
.infobox .row{display:flex;gap:12px;padding:10px 0;border-bottom:1px solid var(--line)}
.infobox .row:last-child{border-bottom:none}
.infobox .k{flex:none;width:72px;font-weight:700;font-size:15px}
.infobox .v{flex:1;min-width:0;font-size:15px}
.infobox .v p{margin:0}
"""

centers_html = ''.join(f"""<div class="center"><div class="info"><h3>{esc(n)}호점</h3><p class="addr">{esc(addr)}<br>{esc(CAPACITY[n])}<br>{tel(n)}</p></div>
<a class="apply c{n}" href="{esc(form_url(name))}"><span class="ico">{ICON}</span>신청하고 싶어요</a></div>""" for n, name, addr in CENTERS)
land = f"""<div class="hero"><h1>영종 다함께 돌봄센터<br>돌봄 신청</h1></div>
{main_flyers()}
<h2 class="sec">모집 안내</h2>
{info_html}
<h2 class="sec">센터 위치</h2>
{centers_html}
<p class="note">누르면 그 호점의 구글 신청서가 열립니다. 칸을 채우고 「제출」을 눌러 주세요.</p>"""
open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(
    f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>영종 다함께 돌봄센터 신청</title><style>{LAND_CSS}</style></head><body><main>{land}</main></body></html>""")

# ---- QR codes (print size 1200 px, label under the code) ----
os.makedirs(os.path.join(ROOT, 'qr'), exist_ok=True)
font_path = next((p for p in [r'C:\Windows\Fonts\malgunbd.ttf', r'C:\Windows\Fonts\malgun.ttf'] if os.path.exists(p)), None)
# QR straight to the landing page (user decision 2026-11-08 22:00): flyer -> locations -> icon -> form
targets = [('main', SITE, '영종 다함께 돌봄센터 돌봄 신청')]
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
