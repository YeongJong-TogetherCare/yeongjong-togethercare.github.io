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
CAPACITY = {'8': '정원 20명', '9': '정원 35명', '10': '정원 20명'}  # from the flyer (flyers/main.png, 2026-11-23 PDF 판)
PHONE = {'8': '032-713-4491', '9': '032-713-4492', '10': '032-713-4493'}  # from the flyer (2026-11-19 판)
APT = {'8': '제일풍경채디오션', '9': '오션파크모아엘가그랑데', '10': '영종센트럴푸르지오자이'}  # apartment complex, given by the user 2026-11-20
EMAIL = {'8': 'wow0735@gmail.com', '9': 'kaku837@gmail.com', '10': 'yjdd100@gmail.com'}  # given by the user 2026-11-19
def tel(n):
    out = '<a href="tel:' + PHONE[n].replace(') ', '-').replace(')', '-') + '">☎ ' + esc(PHONE[n]) + '</a>'
    if n in EMAIL:
        out += '<br><a href="mailto:' + esc(EMAIL[n]) + '">✉ ' + esc(EMAIL[n]) + '</a>'
    return out
esc = html.escape


# one Google Form per center (given by the user 2026-11-08 22:45, replaced 2026-11-19); each form has no center question
CENTER_FORMS = {
    '다함께 돌봄센터 8호점': 'https://forms.gle/8TzuqprSrnAP6JqP9',
    '다함께 돌봄센터 9호점': 'https://forms.gle/MnfP18Pq2U9TugH49',
    '다함께 돌봄센터 10호점': 'https://forms.gle/qVnwfxJFWbLgkrmD9',
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
<p class="addr">단지: {esc(APT[n])}<br>위치: {esc(addr)} ({esc(CAPACITY[n])})<br>{tel(n)}</p>
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
    flyers/zoom/main.png (2480 px, rendered from the 2026-11-23 poster PDF) opens in the zoom viewer."""
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


# readable text version of the poster table. Since 2026-11-20 14:05 the poster is KakaoTalk_20261120_135022229.png (1055x1491) from the user's
# desktop, used unchanged for flyers/main.png and flyers/zoom/main.png (its QR decodes to SITE, checked with OpenCV).
# The hwpx in flyers/원본 is an older poster. Wording copied from the poster; do not edit content here.
POSTER_INFO = [
    ('모집 대상', ['돌봄이 필요한 만 6세 ~ 12세 아동', '(만 6세이나 입학 전 아동 포함)']),
    ('우선 순위', ['맞벌이가정, 한부모가정, 다자녀가정, 초등 저학년, 부모의 출퇴근 거리가 긴 경우', '선발기준: 정원의 70%는 단지내 아동으로 우선 배정합니다.']),
    ('접수 기간', ['8·9호점: 2026.11.23(월) 10시 ~ 11.27(금) 17시', '10호점: 2026.11.25(수) 10시 ~ 11.27(금) 17시', 'QR 우선접수: 아래 센터 위치에서 다닐 호점의 「신청하고 싶어요」를 눌러 주세요.']),
    ('이용 시간', ['학기 중 13:00 ~ 20:00, 방학 중 09:00 ~ 18:00', '주말·공휴일 제외']),
    ('이용 요금', ['정기돌봄 월 70,000원 / 일시돌봄 일 5,000원', '(간식비 포함) / 방학기간 중식 무상 지원']),
    ('프로그램', ['기본프로그램: 출결확인, 일상생활 지도, 간식제공', '활동프로그램: 독서지도, 신체활동, 음악, 미술 등 영종특화프로그램']),
    ('입소 서류', ['8·9호점: 11월 23일(월) 오전 10시부터 서류 접수', '10호점: 11월 25일(수) 오전 10시부터 서류 접수', 'QR 신청 아동은 입소 우선순위 및 선정 기준에 따라 검토 후 순차적으로 개별 연락드립니다.', '※ 입소 증빙서류 미제출 시 입소가 취소될 수 있습니다.']),
    ('문의', ['현재 센터 개소 준비로 전화 상담이 어려운 점 양해 부탁드립니다.', '문의사항은 센터 방문 시 안내해 드리겠습니다.']),
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

# ---- documents shown as pictures like the poster (user 2026-11-20: 한글 파일 대신 이미지로) ----
# flyers/guide.png = page copy (1240 px); flyers/zoom/guide.png = 300 dpi render by Hangul COM (CreatePageImage) of
# 영종구_다함께돌봄_신청서류안내_(큐알).hwp (user's desktop 2026-11-25 11:21, the last version; source kept in flyers/원본/).
# That page holds 대상자 우선순위 and 제출서류 only; the 선정기준표 of earlier versions was dropped, so the caption no longer mentions it.
# It replaced the two pictures (score.png, documents.png) used on 2026-11-20 morning.
DOC_IMAGES = [
    ('guide.png', '신청서류 안내', '대상자 우선순위 · 제출서류',
     '대상자 우선순위와 필요한 서류를 확인하고, 아래 「입소 서류」 기간에 센터로 직접 방문해 제출해 주세요.'),
]
docs_html = ''.join(
    f'<div class="docimg"><h3>{esc(step)} <span>{esc(title)}</span></h3><p class="dnote">{esc(note)}</p>'
    f'<button type="button" class="flyerbtn" data-zoom="flyers/zoom/{esc(f)}" aria-label="{esc(title)} 크게 보기">'
    f'<img class="flyer" src="flyers/{esc(f)}" alt="{esc(title)}" loading="lazy"></button>'
    '<p class="zoomhint">그림을 누르면 크게 볼 수 있어요</p></div>'
    for f, step, title, note in DOC_IMAGES)
LAND_CSS += """
.docimg h3{font-size:17px;margin:0 0 2px}
.docimg h3 span{font-weight:600;color:var(--sub)}
.dnote{color:var(--sub);font-size:14px;margin:0 0 10px}
"""

# center card: one label/value row per line so the lines line up in every card; address split into road / building
LAND_CSS += """
.hero h1{white-space:nowrap;font-size:clamp(18px,6.2vw,27px)}
.center{gap:10px}
.center .rows{display:grid;grid-template-columns:auto 1fr;column-gap:8px;row-gap:2px;margin:4px 0 0;font-size:clamp(13px,3.9vw,15px);line-height:1.5}
.center .rows dt{color:var(--sub);font-weight:600}
.center .rows dd{margin:0;white-space:nowrap;color:var(--sub)}
.center .rows dd a{color:var(--fg);font-weight:600;text-decoration:none}
.apply{width:auto;min-width:84px;white-space:nowrap;text-align:center;font-size:13px}
"""


def center_rows(n, addr):
    road, _, bld = addr.partition(', ')
    # no phone row here: user asked 2026-11-23 to remove it (the poster says phone consultation is not available yet)
    rows = [('단지', esc(APT[n])), ('주소', esc(road) + '<br>' + esc(bld)), ('정원', esc(CAPACITY[n].replace('정원 ', '')))]
    if n in EMAIL:
        rows.append(('메일', f'<a href="mailto:{esc(EMAIL[n])}">{esc(EMAIL[n])}</a>'))
    return '<dl class="rows">' + ''.join(f'<dt>{k}</dt><dd>{v}</dd>' for k, v in rows) + '</dl>'


centers_html = ''.join(f"""<div class="center"><div class="info"><h3>{esc(n)}호점</h3>{center_rows(n, addr)}</div>
<a class="apply c{n}" href="{esc(form_url(name))}"><span class="ico">{ICON}</span>신청하고 싶어요</a></div>""" for n, name, addr in CENTERS)
land = f"""<div class="hero"><h1>영종구 다함께돌봄센터</h1></div>
{main_flyers()}
<h2 class="sec">서류 확인</h2>
{docs_html}
<h2 class="sec">모집 안내</h2>
{info_html}
<h2 class="sec">센터 위치</h2>
{centers_html}
<p class="note">누르면 그 호점의 구글 신청서가 열립니다. 칸을 채우고 「제출」을 눌러 주세요.</p>"""
open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(
    f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>영종구 다함께돌봄센터</title><style>{LAND_CSS}{ZOOM_CSS}</style></head><body><main>{land}</main>{ZOOM_HTML}{ZOOM_JS}</body></html>""")

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
