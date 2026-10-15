# -*- coding: utf-8 -*-
"""Собирает студию агента: девять специалистов живут на общей сцене.

Фон это картинка студии, персонажи вырезаны по фигуре и стоят каждый у своей
зоны. Активный работает своей анимацией, остальные ждут и изредка
переминаются. Когда этап закончен, светящаяся папка уезжает к следующему.

Кадры: assets/hod/<роль>/*.webp это ходьба, assets/rabota/<роль>/*.webp это
работа. Всё вшивается в страницу целиком: артефакт не пускает внешние адреса.

Запуск:  python .claude/skills/site-agent/scena.py

Changes when: меняется состав команды, хореография или фон студии.

Anti-goal: не рисует прогресса, которого не было. Это сцена, а не отчёт.
"""
import base64
import glob
import io
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
OUT = os.path.join(ROOT, "build", "Студия.html")

# роль, имя, зона студии, что делает, где стоит по ширине сцены
CREW = [
    ("issledovatel", "Исследователь", "библиотека",  "читаю сайт клиники",     22.0, 1),
    ("analitik",     "Аналитик",      "стена идей",  "сравниваю конкурентов",  38.0, 1),
    ("marketolog",   "Маркетолог",    "лаунж",       "разбираю клиента",       79.0, 0),
    ("strateg",      "Стратег",       "антресоль",   "смотрю, кто дозрел",     53.0, 0),
    ("kopirayter",   "Копирайтер",    "стол у окна", "пишу тексты",            46.0, 2),
    ("arhitektor",   "Архитектор",    "чертёжная",   "проектирую страницы",    33.0, 2),
    ("konversia",    "Конверсия",     "печатная",    "считаю, кто запишется",  60.0, 1),
    ("videograf",    "Видеограф",     "монтажная",   "снимаю видео",           75.0, 1),
    ("razrabotchik", "Разработчик",   "верстак",     "собираю сайт",           92.0, 1),
]


def uri(path, mime="image/webp"):
    full = path if os.path.isabs(path) else os.path.join(ROOT, path)
    if not os.path.exists(full):
        return ""
    return "data:%s;base64,%s" % (mime, base64.b64encode(io.open(full, "rb").read()).decode("ascii"))


def frames(kind, role):
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, "assets", kind, role, "*.webp"))):
        u = uri(f)
        if u:
            out.append(u)
    return out


CSS = """
:root{
  --void:#05070b; --panel:#0c121b; --line:#1b2634;
  --ink:#e8f0f7; --mid:#93a6bb; --dim:#5d7085; --neon:#3ce0c0; --blue:#6f9cff;
}
*{box-sizing:border-box}
body{margin:0;background:var(--void);color:var(--ink);
     font:16px/1.6 Manrope,system-ui,-apple-system,'Segoe UI',sans-serif;-webkit-font-smoothing:antialiased}
.wrap{max-width:1180px;margin:0 auto;padding:24px 16px 60px}
h1{font-family:Unbounded,Manrope,system-ui,sans-serif;font-size:clamp(19px,3vw,26px);
   margin:0 0 6px;font-weight:600;letter-spacing:-.02em}
.sub{color:var(--mid);margin:0 0 18px;font-size:14.5px;max-width:66ch}
.lab{font-family:'JetBrains Mono',ui-monospace,monospace;font-size:10.5px;letter-spacing:.16em;
     text-transform:uppercase;color:var(--dim)}

.studio{position:relative;width:100%;aspect-ratio:2200/944;border:1px solid var(--line);
        border-radius:18px;overflow:hidden;background-size:cover;background-position:center bottom}
.studio::after{content:"";position:absolute;inset:0;pointer-events:none;
  background:linear-gradient(180deg,rgba(5,7,11,.35),transparent 26%,transparent 72%,rgba(5,7,11,.45))}

/* персонаж на полу студии. три плана глубины: дальний мельче и выше */
.guy{position:absolute;transform:translateX(-50%);transition:left linear}
.guy img{width:100%;display:block;filter:drop-shadow(0 5px 9px rgba(0,0,0,.75))}
.guy[data-dir="left"] img{transform:scaleX(-1)}

.guy[data-lane="0"]{bottom:57.5%;width:6.2%;z-index:2}
.guy[data-lane="1"]{bottom:17.5%;width:7.8%;z-index:3}
.guy[data-lane="2"]{bottom:4%;width:9.8%;z-index:4}
.guy[data-lane="0"] img{filter:drop-shadow(0 4px 7px rgba(0,0,0,.7)) brightness(.72) saturate(.8)}
.guy[data-lane="1"] img{filter:drop-shadow(0 5px 8px rgba(0,0,0,.72)) brightness(.88)}

.guy[data-act="work"][data-lane="0"]{width:8.6%}
.guy[data-act="work"][data-lane="1"]{width:10.8%}
.guy[data-act="work"][data-lane="2"]{width:13.4%}

.guy .glow{position:absolute;left:50%;bottom:-2%;transform:translateX(-50%);width:66%;height:8px;
           border-radius:50%;background:rgba(60,224,192,.12);filter:blur(6px);transition:.4s}
.guy[data-act="work"] .glow{background:rgba(60,224,192,.6);width:86%;height:12px}
.guy[data-act="idle"] img{animation:sway 4.5s ease-in-out infinite}
@keyframes sway{0%,100%{transform:translateY(0)}50%{transform:translateY(-2px)}}
.guy[data-dir="left"][data-act="idle"] img{animation:swayL 4.5s ease-in-out infinite}
@keyframes swayL{0%,100%{transform:scaleX(-1) translateY(0)}50%{transform:scaleX(-1) translateY(-2px)}}

/* подпись под тем, кто работает */
.tag{position:absolute;left:50%;bottom:-16%;transform:translateX(-50%);white-space:nowrap;
     font-family:'JetBrains Mono',ui-monospace,monospace;font-size:9.5px;letter-spacing:.08em;
     text-transform:uppercase;color:#48607a;transition:.35s}
.guy[data-act="work"] .tag{color:var(--neon);bottom:-13%}
.guy[data-lane="0"] .tag,.guy[data-lane="0"] .say{font-size:8.5px}
.guy[data-act="idle"] .tag{opacity:.55}

/* реплика над головой */
.say{position:absolute;left:50%;bottom:104%;transform:translateX(-50%) translateY(6px);white-space:nowrap;
     background:rgba(8,13,20,.96);border:1px solid rgba(60,224,192,.45);color:var(--ink);
     border-radius:11px;padding:5px 11px;font-size:12.5px;opacity:0;transition:.3s;
     pointer-events:none;z-index:6}
.guy[data-act="work"] .say{opacity:1;transform:translateX(-50%) translateY(0)}

.spark{position:absolute;width:3px;height:3px;border-radius:50%;background:var(--neon);
       opacity:0;pointer-events:none;z-index:2}
@keyframes fly{0%{opacity:0;transform:translate(0,0) scale(.6)}
               20%{opacity:1}
               100%{opacity:0;transform:translate(var(--dx),-70px) scale(.2)}}

.baton{position:absolute;bottom:16%;width:15px;height:12px;border-radius:2px;z-index:5;opacity:0;
       background:linear-gradient(150deg,var(--neon),var(--blue));
       box-shadow:0 0 14px rgba(60,224,192,.85);transform:translateX(-50%)}

.pop{position:absolute;width:11%;aspect-ratio:1;border-radius:50%;pointer-events:none;z-index:2;
     background:radial-gradient(circle,rgba(60,224,192,.5),transparent 62%);
     transform:translate(-50%,50%);animation:pop .85s ease-out forwards}
@keyframes pop{0%{opacity:.9;transform:translate(-50%,50%) scale(.4)}
               100%{opacity:0;transform:translate(-50%,50%) scale(1.8)}}

.bar{margin-top:14px;display:flex;flex-wrap:wrap;gap:10px 16px;align-items:center;
     border:1px solid var(--line);border-radius:14px;background:var(--panel);padding:13px 16px}
.dot{width:8px;height:8px;border-radius:50%;background:var(--neon);flex:0 0 8px;animation:blink 1.6s infinite}
@keyframes blink{50%{opacity:.25}}
.bar b{font-weight:600;font-size:15px}
.bar span{color:var(--mid);font-size:14px}
.hint{margin-top:12px;color:var(--dim);font-size:13.5px;max-width:72ch}
@media (max-width:640px){
  .studio{border-radius:13px}
  .guy{width:12%}
  .guy[data-act="work"]{width:16%}
  .tag{display:none}
  .say{font-size:10px;padding:4px 8px}
}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
"""

JS = """
(function(){
  var studio = document.getElementById('studio');
  var what = document.getElementById('what');
  var who = document.getElementById('who');
  var baton = document.getElementById('baton');
  var CREW = window.__CREW__;
  var guys = CREW.map(function(c, k){ return document.getElementById('guy' + k); });
  var active = 0;
  var state = CREW.map(function(c){ return {x: c.at, timer: null, busy: false}; });

  CREW.forEach(function(c){
    c.walk.concat(c.work).forEach(function(src){ var im = new Image(); im.src = src; });
  });

  function im(k){ return guys[k].querySelector('img'); }
  function stopAnim(k){ if(state[k].timer){ clearInterval(state[k].timer); state[k].timer = null; } }

  function animate(k, list, ms){
    stopAnim(k);
    var f = 0, el = im(k);
    el.src = list[0];
    state[k].timer = setInterval(function(){
      f = (f + 1) % list.length;
      el.src = list[f];
    }, ms);
  }

  function stand(k){
    stopAnim(k);
    var c = CREW[k];
    im(k).src = c.walk.length > 2 ? c.walk[2] : c.walk[0];
    guys[k].setAttribute('data-act', 'idle');
  }

  /* шаг за шагом до точки: скорость постоянная, поэтому длинный путь идёт дольше */
  function walkTo(k, x, done){
    var c = CREW[k], g = guys[k], from = state[k].x;
    var dist = Math.abs(x - from);
    if(dist < 0.6){ state[k].x = x; stand(k); done && done(); return; }
    var speed = 5.2 + c.lane * 1.6;           /* ближний план идёт быстрее: он крупнее */
    var ms = Math.max(500, (dist / speed) * 1000);
    g.setAttribute('data-dir', x < from ? 'left' : 'right');
    g.setAttribute('data-act', 'walk');
    animate(k, c.walk, 115);
    g.style.transitionDuration = ms + 'ms';
    g.style.left = x + '%';
    state[k].x = x;
    setTimeout(function(){ stand(k); done && done(); }, ms + 40);
  }

  /* своя жизнь: гуляет рядом со своим местом, стоит, снова идёт */
  function live(k){
    if(state[k].busy) return;
    var c = CREW[k];
    var span = 7 + Math.random() * 13;
    var x = c.at + (Math.random() < 0.5 ? -span : span);
    var edge = c.lane === 0 ? [40, 93] : [5, 96];
    x = Math.max(edge[0], Math.min(edge[1], x));
    walkTo(k, x, function(){
      setTimeout(function(){
        if(state[k].busy) return;
        walkTo(k, c.at + (Math.random() * 4 - 2), function(){
          setTimeout(function(){ live(k); }, 1800 + Math.random() * 5200);
        });
      }, 1400 + Math.random() * 3600);
    });
  }

  function sparks(k){
    var x = state[k].x, lane = CREW[k].lane;
    var bottom = [60, 20, 7][lane];
    for(var n = 0; n < 6; n++){
      (function(n){
        setTimeout(function(){
          var s = document.createElement('i');
          s.className = 'spark';
          s.style.left = (x + (Math.random() * 6 - 3)) + '%';
          s.style.bottom = bottom + '%';
          s.style.setProperty('--dx', (Math.random() * 34 - 17) + 'px');
          s.style.animation = 'fly 1.2s ease-out forwards';
          studio.appendChild(s);
          setTimeout(function(){ s.remove(); }, 1300);
        }, n * 210);
      })(n);
    }
  }

  function pop(k){
    var p = document.createElement('div');
    p.className = 'pop';
    p.style.left = state[k].x + '%';
    p.style.bottom = [58, 18, 5][CREW[k].lane] + '%';
    studio.appendChild(p);
    setTimeout(function(){ p.remove(); }, 900);
  }

  function pass(from, to, done){
    var yFrom = [60, 20, 7][CREW[from].lane], yTo = [60, 20, 7][CREW[to].lane];
    baton.style.transition = 'none';
    baton.style.left = state[from].x + '%';
    baton.style.bottom = yFrom + '%';
    baton.style.opacity = '1';
    setTimeout(function(){
      baton.style.transition = 'left 1.1s ease-in-out, bottom 1.1s ease-in-out';
      baton.style.left = state[to].x + '%';
      baton.style.bottom = yTo + '%';
      setTimeout(function(){ baton.style.opacity = '0'; done && done(); }, 1100);
    }, 40);
  }

  /* очередь этапов: активный бросает прогулку, идёт на место и работает */
  function step(){
    var k = active, c = CREW[k], next = (k + 1) % CREW.length;
    state[k].busy = true;
    who.textContent = c.name;
    what.textContent = 'иду на место';

    walkTo(k, c.at, function(){
      guys[k].setAttribute('data-dir', 'right');
      guys[k].setAttribute('data-act', 'work');
      what.textContent = c.doing;
      animate(k, c.work, 190);
      sparks(k);
      setTimeout(function(){ sparks(k); }, 1500);

      setTimeout(function(){
        stand(k);
        pop(k);
        what.textContent = 'готово, передаю дальше';
        pass(k, next, function(){
          state[k].busy = false;
          setTimeout(function(){ live(k); }, 2000 + Math.random() * 3000);
          active = next;
          step();
        });
      }, 3800);
    });
  }

  guys.forEach(function(g, k){
    stand(k);
    setTimeout(function(){ live(k); }, 400 + Math.random() * 4000);
  });
  setTimeout(step, 900);
})();
"""


def build():
    bg = uri("assets/studio.webp")
    people = []
    data = []
    for k, (role, name, zone, doing, at, lane) in enumerate(CREW):
        walk = frames("hod", role)
        work = frames("rabota", role)
        if not walk:
            continue
        people.append(
            '<div class="guy" id="guy%d" data-act="idle" data-idle="1" data-dir="right" '
            'data-lane="%d" style="left:%s%%">'
            '<span class="say">%s</span>'
            '<img alt="%s">'
            '<span class="glow"></span>'
            '<span class="tag">%s</span>'
            '</div>' % (k, lane, at, doing, name, zone))
        data.append('{name:"%s",doing:"%s",at:%s,lane:%d,walk:[%s],work:[%s]}' % (
            name, doing, at, lane,
            ",".join('"%s"' % w for w in walk),
            ",".join('"%s"' % w for w in (work or walk))))

    return """<title>Студия агента</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Unbounded:wght@500;600&family=Manrope:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap">
<style>%s</style>
<div class="wrap">
  <span class="lab">команда агента за работой</span>
  <h1>Студия агента</h1>
  <p class="sub">Девять специалистов на своих местах. Тот, чей сейчас этап, работает: руки двигаются, вверх летят искры, над головой видно, чем он занят. Закончил, и светящаяся папка уезжает к следующему.</p>

  <div class="studio" id="studio" style="background-image:url(%s)">
    <div class="baton" id="baton"></div>
    %s
  </div>

  <div class="bar">
    <span class="dot"></span><b id="who">Исследователь</b><span id="what">читаю сайт клиники</span>
  </div>
  <p class="hint">Каждому нарисованы свои кадры: походка со своим инструментом и своё действие на рабочем месте. Персонажи вырезаны по фигуре, никаких квадратов.</p>
</div>
<script>window.__CREW__ = [%s];</script>
<script>%s</script>
""" % (CSS, bg, "\n    ".join(people), ",".join(data), JS)


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    io.open(OUT, "w", encoding="utf-8").write(build())
    size = os.path.getsize(OUT) / 1048576.0
    print("студия собрана: %s (%.2f МБ)" % (OUT, size))
    if size > 15:
        print("ВНИМАНИЕ: артефакт не берёт больше 16 МБ")


if __name__ == "__main__":
    main()
