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
CAPACITY = {'8': '정원 20명', '9': '정원 35명', '10': '정원 20명'}  # from the flyer (flyers/main.png, 2026-11-10 343x479 판)
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
    """Poster on the landing page. flyers/main.png is the on-page copy (1240 px wide);
    flyers/zoom/main.png (2480 px, rendered from flyers/원본/*-현재판.hwpx) opens in the zoom viewer."""
    fs = sorted(glob.glob(os.path.join(ROOT, 'flyers', 'main*.*')))
    out = []
    for f in fs:
        r = os.path.relpath(f, ROOT).replace('\\', '/')
        if r.lower().endswith('.pdf'):
            out.append(f'<a class="pdf" href="{esc(r)}">홍보 전단지 열기 (PDF)</a>')
            continue
        big = os.path.join(ROOT, 'flyers', 'zoom', os.path.basename(f))
        zr = os.path.relpath(big, ROOT).replace('\\', '/') if os.path.exists(big) else r
        out.append(f'<button type="button" class="flyerbtn" data-zoom="{esc(zr)}" aria-label="홍보 전단지 크게 보기">'
                   f'<img class="flyer" src="{esc(r)}" alt="영종 다함께 돌봄센터 홍보 전단지"></button>'
                   '<p class="zoomhint">포스터를 누르면 크게 볼 수 있어요</p>')
    return ''.join(out)


# ---- zoom viewer: black full screen, pinch / double tap / wheel / +- buttons, back button closes ----
ZOOM_CSS = """
.flyerbtn{display:block;width:100%;padding:0;border:0;background:none;cursor:zoom-in;margin:0 0 6px}
.flyerbtn .flyer{margin:0}
.zoomhint{text-align:center;color:var(--sub);font-size:14px;margin:0 0 22px}
#zv{position:fixed;inset:0;z-index:50;background:#000;display:none;touch-action:none;overflow:hidden;user-select:none;-webkit-user-select:none}
#zv.on{display:block}
#zv img{position:absolute;left:0;top:0;transform-origin:0 0;max-width:none;-webkit-user-drag:none}
#zv .bar{position:absolute;left:0;right:0;bottom:0;display:flex;justify-content:center;gap:12px;padding:12px 16px calc(12px + env(safe-area-inset-bottom))}
#zv button{font:700 17px/1 "Pretendard","Apple SD Gothic Neo","Malgun Gothic",system-ui,sans-serif;color:#fff;background:#000;border:2px solid #fff;border-radius:999px;min-width:56px;height:48px;padding:0 18px}
#zv .close{position:absolute;top:calc(12px + env(safe-area-inset-top));right:12px}
"""
ZOOM_HTML = """<div id="zv" role="dialog" aria-modal="true" aria-label="홍보 전단지 크게 보기"><img alt="영종 다함께 돌봄센터 홍보 전단지 (크게)">
<button type="button" class="close">닫기</button>
<div class="bar"><button type="button" class="out" aria-label="작게">－</button><button type="button" class="fit">전체</button><button type="button" class="in" aria-label="크게">＋</button></div></div>"""
ZOOM_JS = r"""<script>
(function(){
var zv=document.getElementById('zv'),im=zv.querySelector('img');
var s=1,tx=0,ty=0,bw=0,bh=0,maxS=6,pts={},pinch=null,drag=null,lastTap=0,open=false;
function vw(){return zv.clientWidth} function vh(){return zv.clientHeight}
function apply(){
  var W=bw*s,H=bh*s;
  if(W<=vw()) tx=(vw()-W)/2; else tx=Math.min(0,Math.max(vw()-W,tx));
  if(H<=vh()) ty=(vh()-H)/2; else ty=Math.min(0,Math.max(vh()-H,ty));
  im.style.transform='translate('+tx+'px,'+ty+'px) scale('+s+')';
}
function fit(){
  var nw=im.naturalWidth||1,nh=im.naturalHeight||1,k=Math.min(vw()/nw,vh()/nh);
  bw=nw*k;bh=nh*k;im.style.width=bw+'px';im.style.height=bh+'px';
  maxS=Math.max(3,nw/(bw*(window.devicePixelRatio||1))*2);s=1;tx=0;ty=0;apply();
}
function zoomAt(px,py,k){
  var ns=Math.min(maxS,Math.max(1,s*k));k=ns/s;
  tx=px-(px-tx)*k;ty=py-(py-ty)*k;s=ns;apply();
}
var hiDone={};
function show(src,small){
  open=true;zv.classList.add('on');document.body.style.overflow='hidden';
  if(hiDone[src]){if(im.getAttribute('src')!==src){im.onload=fit;im.src=src;}else fit();}
  else{
    // show the already-loaded page copy at once, swap in the sharp copy when it arrives (same aspect ratio)
    im.onload=function(){im.onload=null;fit();};im.src=small;
    var h=new Image();h.onload=function(){hiDone[src]=1;im.src=src;
      maxS=Math.max(3,h.naturalWidth/(bw*(window.devicePixelRatio||1))*2);};h.src=src;
  }
  try{history.pushState({zv:1},'')}catch(e){}
}
function hide(fromPop){
  if(!open)return;open=false;zv.classList.remove('on');document.body.style.overflow='';pts={};pinch=null;drag=null;
  if(!fromPop){try{if(history.state&&history.state.zv)history.back()}catch(e){}}
}
document.querySelectorAll('.flyerbtn').forEach(function(b){b.addEventListener('click',function(){show(b.getAttribute('data-zoom'),b.querySelector('img').currentSrc||b.querySelector('img').src)})});
zv.querySelector('.close').addEventListener('click',function(){hide(false)});
zv.querySelector('.in').addEventListener('click',function(){zoomAt(vw()/2,vh()/2,1.6)});
zv.querySelector('.out').addEventListener('click',function(){zoomAt(vw()/2,vh()/2,1/1.6)});
zv.querySelector('.fit').addEventListener('click',fit);
window.addEventListener('popstate',function(){hide(true)});
window.addEventListener('resize',function(){if(open)fit()});
document.addEventListener('keydown',function(e){if(open&&e.key==='Escape')hide(false)});
zv.addEventListener('wheel',function(e){e.preventDefault();var r=zv.getBoundingClientRect();zoomAt(e.clientX-r.left,e.clientY-r.top,e.deltaY<0?1.15:1/1.15)},{passive:false});
function onBar(e){return e.target.closest('button')}
zv.addEventListener('pointerdown',function(e){
  if(onBar(e))return;zv.setPointerCapture(e.pointerId);pts[e.pointerId]={x:e.clientX,y:e.clientY};
  var ids=Object.keys(pts);
  if(ids.length===2){var a=pts[ids[0]],b=pts[ids[1]];pinch={d:Math.hypot(a.x-b.x,a.y-b.y),s:s};drag=null;}
  else if(ids.length===1){drag={x:e.clientX,y:e.clientY,tx:tx,ty:ty,moved:false};}
});
zv.addEventListener('pointermove',function(e){
  if(!pts[e.pointerId])return;pts[e.pointerId]={x:e.clientX,y:e.clientY};
  var ids=Object.keys(pts),r=zv.getBoundingClientRect();
  if(pinch&&ids.length>=2){
    var a=pts[ids[0]],b=pts[ids[1]],d=Math.hypot(a.x-b.x,a.y-b.y);
    zoomAt((a.x+b.x)/2-r.left,(a.y+b.y)/2-r.top,(pinch.s*d/pinch.d)/s);
  }else if(drag){
    var dx=e.clientX-drag.x,dy=e.clientY-drag.y;if(Math.abs(dx)+Math.abs(dy)>6)drag.moved=true;
    tx=drag.tx+dx;ty=drag.ty+dy;apply();
  }
});
function up(e){
  if(!pts[e.pointerId])return;delete pts[e.pointerId];
  var ids=Object.keys(pts);
  if(ids.length<2)pinch=null;
  if(ids.length===1){var p=pts[ids[0]];drag={x:p.x,y:p.y,tx:tx,ty:ty,moved:true};return;}
  if(ids.length===0&&drag&&!drag.moved&&e.type==='pointerup'){
    var now=Date.now(),r=zv.getBoundingClientRect();
    if(now-lastTap<320){lastTap=0;if(s>1.05)fit();else zoomAt(e.clientX-r.left,e.clientY-r.top,3);}
    else lastTap=now;
  }
  if(ids.length===0)drag=null;
}
zv.addEventListener('pointerup',up);zv.addEventListener('pointercancel',up);
})();
</script>"""


# readable text version of the poster table. The poster image the centre supplied is only 343x479 px;
# since 2026-11-11 the site shows a sharp re-render of the same hwpx instead (flyers/zoom/main.png),
# but keep this text list too. Wording copied from the poster; do not edit content here.
POSTER_INFO = [
    ('모집 대상', ['돌봄이 필요한 만 6세 ~ 12세 아동', '(만 6세이나 입학 전 아동 포함)']),
    ('접수 방법', ['2026.11.12일부터 10시부터 전화 및 방문접수 (평일 10시 ~ 18시)']),
    ('우선 순위', ['맞벌이가정, 한부모가정, 다자녀가정, 초등 저학년, 다문화 가정', '선발기준: 정원의 70%는 단지내 아동으로 우선 배정합니다.', '정원 마감 전까지 선착순 접수 마감합니다.']),
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
<title>영종 다함께 돌봄센터 신청</title><style>{LAND_CSS}{ZOOM_CSS}</style></head><body><main>{land}</main>{ZOOM_HTML}{ZOOM_JS}</body></html>""")

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
