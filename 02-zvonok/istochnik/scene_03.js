const SCENES = {
  facts: ["77 цен в прайсе", "9 страниц услуг", "2 врача, 16 лет практики", "щодня 9:00–20:00", "пр. Червоної Калини, 67", "гарантія 6–12 місяців", "консультація безкоштовна"],
  kb: [["Кто мы","Троєщина, 2 врача, лечение под микроскопом"],["Услуги","9 направлений, как на сайте"],["Цены","77 цен из прайса клиники"],["Как отвечать","коротко, без диагнозов"]],
  flow: [["01","Понять запрос","что болит и зачем пришёл"],["02","Ответить по базе","только то, что есть в файлах"],
         ["03","Развилка","хочет записаться → в Telegram; просто смотрит → прощаемся"]],
  rules: ["не ставит диагноз по видео","не обещает результат лечения","не называет цен, которых нет в файле","не спорит и не давит"],
  qa: [["Скільки коштує імплант?","Імплант під ключ — 17 500 грн: імплант, формувач і коронка. Консультація безкоштовна."],
       ["Працюєте у вихідні?","Так, щодня з 9:00 до 20:00, без вихідних. Записати вас на консультацію?"],
       ["Це точно не боляче?","Лікування під знеболенням, лікар пояснює кожен крок. Можу записати на консультацію."]]
};

const chips = () => '<div class="chips">'+SCENES.facts.map(f=>'<span class="chip it">'+f+'</span>').join('')+'</div>';
const kb = () => '<div class="kb">'+SCENES.kb.map(k=>'<div class="it"><b>'+k[0]+'</b><span>'+k[1]+'</span></div>').join('')+'</div>';
const flow = () => '<div class="flow">'+SCENES.flow.map(f=>'<div class="node it'+(f[0]==="03"?" branch":"")+'"><em>'+f[0]+'</em><div><b>'+f[1]+'</b><div class="t">'+f[2]+'</div></div></div>').join('')+'</div>';
const rules = () => '<ul class="rules">'+SCENES.rules.map(r=>'<li class="it">'+r+'</li>').join('')+'</ul>';
const install = () => '<ul class="rules yes">'+["кнопка живёт на всех страницах","звонки разрешены только с домена клиники","на телефоне открывается на весь экран"]
  .map(r=>'<li class="it">'+r+'</li>').join('')+'</ul>';
const qa = () => '<div class="qa">'+SCENES.qa.map(q=>'<div class="it"><div class="q">— '+q[0]+'</div><div class="a"><b>консультант:</b> '+q[1]+'</div></div>').join('')+'</div>';
function faces(){
  const bars = Array.from({length:13},(_,i)=>'<i style="animation-delay:'+(i*.07)+'s"></i>').join('');
  return '<div class="person">'+
    '<div class="photo it" data-at=".18"></div>'+
    '<div class="traits">'+
      '<div class="tr it" data-at=".34"><b>Лицо</b><span>фото ведущего, без мультяшности</span></div>'+
      '<div class="tr it" data-at=".52"><b>Голос</b><span>украинский, спокойный, не диктор</span></div>'+
      '<div class="tr it" data-at=".70"><b>Манера</b><span>отвечает сразу, без пауз и заученных фраз</span></div>'+
    '</div>'+
    '<div class="wave it" data-at=".70">'+bars+'</div></div>';
}

const LAB = {facts:"что нашёл на сайте", kb:"память консультанта", flow:"ход разговора",
  rules:"чего не делает", faces:"лицо и голос", install:"кнопка на сайте", qa:"проверка вопросами"};
const BUILD = {facts:chips, kb:kb, flow:flow, rules:rules, faces:faces, install:install, qa:qa};


window.STAGE = {
  enter(scene){ el("scan").classList.toggle("on", scene === "facts"); }
};
