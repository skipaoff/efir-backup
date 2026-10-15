const HANDLE = "@vlad_ai_yasko";

const SCENES = {
  niche: [["Соседи","3 клиники района: одни прячут цены, другие пишут «від»"],["Страхи","«А якщо нарахують ще?», «соромно відкривати рота»"],
          ["Возражения","дорого, разведут на лишнее, боюсь"],["Козыри","цены на сайте, гарантия 6–12 месяцев, микроскоп"]],
  kb: [["Услуги и цены","10 услуг, цена с вилкой и почему"],["Частые вопросы","боль, дети, гарантия, КТ, срочно"],
       ["Запись","свободные окна на 3 дня"],["Предоплата","300 грн, входит в стоимость"]],
  funnel: [["01","Знакомство","кружок и вопрос, что беспокоит"],["02","Потребность","услуга и цена из знаний клиники"],
           ["03","Запись","два свободных времени на выбор"],["04","Оплата","предоплата 300 грн и скриншот"]],
  spin: [["S · Ситуация","«Когда вы последний раз были у стоматолога?»"],["P · Проблема","«Что сейчас беспокоит больше всего?»"],
         ["I · Последствия","«Что будет, если отложить ещё на полгода?»"],["N · Выгода","«Как вам — снова жевать на обе стороны?»"]],
  tone: [["Дорого","Имплант под ключ 17 500 — цена зафиксирована, в неё входят имплант, формирователь и коронка."],
         ["Разведёте на лишнее?","План лечения и сумму называем до начала — сюрпризов нет."],
         ["Боюсь","Работаем под анестезией, врач работает мягко и объясняет каждый шаг."]],
  tg: ["рабочий аккаунт Telegram, не бот","вход по коду подтверждения","голосовые клиента расшифровываются",
       "помнит весь разговор, повторять не нужно","время записи — только из расписания","реквизиты и инструкции не выдать и не подменить"],
  checks: ["10 сценариев: цена, острая боль, «дорого», запись","5 попыток взлома: промпт, ключи, чужая карта","довёл до записи и оплаты по скриншоту"]
};

const LAB = {niche:"разбор ниши", kb:"знания продавца", funnel:"воронка продаж", spin:"вопросы по SPIN",
  tone:"ответы на возражения", profile:"профиль и кружок", tg:"подключение", pay:"приём оплаты", checks:"что проверил"};

const kbList = arr => '<div class="kb">'+arr.map(k=>'<div class="it"><b>'+k[0]+'</b><span>'+k[1]+'</span></div>').join('')+'</div>';
const checkList = arr => '<ul class="rules yes">'+arr.map(c=>'<li class="it">'+c+'</li>').join('')+'</ul>';

const BUILD = {
  niche:   () => kbList(SCENES.niche),
  kb:      () => kbList(SCENES.kb),
  funnel:  () => '<div class="flow">'+SCENES.funnel.map(f=>'<div class="node it'+(f[0]==="04"?" branch":"")+'"><em>'+f[0]+'</em><div><b>'+f[1]+'</b><div class="t">'+f[2]+'</div></div></div>').join('')+'</div>',
  spin:    () => kbList(SCENES.spin),
  tone:    () => '<div class="qa">'+SCENES.tone.map(q=>'<div class="it"><div class="q">— '+q[0]+'</div><div class="a"><b>продавец:</b> '+q[1]+'</div></div>').join('')+'</div>',
  profile: () => '<div class="person">'+
                 '<div class="photo circ it" data-at=".2"></div>'+
                 '<div class="traits">'+
                   '<div class="tr it" data-at=".35"><b>Имя</b><span>Стоматологія Comfort</span></div>'+
                   '<div class="tr it" data-at=".5"><b>Ник</b><span>'+HANDLE+'</span></div>'+
                   '<div class="tr it" data-at=".65"><b>Кружок</b><span>10 секунд: «Здравствуйте! Я администратор стоматологии Комфорт…»</span></div>'+
                   '<div class="tr it" data-at=".8"><b>Роль</b><span>честно говорит, что он AI-администратор</span></div>'+
                 '</div></div>',
  tg:      () => checkList(SCENES.tg),
  pay:     () => '<div class="paychk">'+
                 '<div class="paycard it" data-at=".1"><span class="ok">✓ Успішно</span><b>300 ₴</b><span>Стоматологія Comfort</span><span class="dt">сьогодні, 14:02</span></div>'+
                 '<ul class="rules yes">'+
                   '<li class="it" data-at=".3">реквизиты клиники выдаются только после записи</li>'+
                   '<li class="it" data-at=".46">сумма 300 ₴ совпадает с предоплатой</li>'+
                   '<li class="it" data-at=".6">получатель — Стоматологія Comfort</li>'+
                   '<li class="it" data-at=".74">статус платежа — «Успішно»</li>'+
                   '<li class="it strong" data-at=".88">этап клиента: оплачено, время закреплено</li>'+
                 '</ul></div>',
  checks:  () => checkList(SCENES.checks)
};

const SAY = [
  [.04,"bot", "circle:"],
  [.16,"me",  "Сколько стоит поставить имплант?"],
  [.3, "bot", "Имплант под ключ — 17 500 грн: имплант, формирователь десны и коронка. Консультация бесплатная. Записать вас?"],
  [.46,"me",  "Да, завтра после обеда. Я Игорь"],
  [.6, "bot", "Игорь, записал вас на завтра в 14:30, врач Карпук Андрій. Предоплата 300 грн закрепит время — пришлите скриншот."],
  [.76,"me",  "pay:"],
  [.9, "bot", "Оплата пришла, спасибо! Ждём вас завтра в 14:30, пр. Червоної Калини 67."]
];
const said = new Set();

const STATUS = {niche:"изучаем нишу", kb:"загружаем знания", funnel:"строим воронку", spin:"учим задавать вопросы",
  tone:"настраиваем тон", profile:"записываем кружок", tg:"подключаем Telegram", pay:"подключаем оплату", checks:"проверка перепиской"};

const SETUP = [
  ["niche",   "ниша: 3 соседа, 5 возражений"],
  ["kb",      "знания: услуги, вопросы, запись, оплата"],
  ["funnel",  "воронка: от знакомства до оплаты"],
  ["spin",    "SPIN-вопросы на месте"],
  ["tone",    "тон: на «вы», коротко, без давления"],
  ["profile", "аватар и кружок-приветствие"],
  ["tg",      "Telegram подключён"],
  ["pay",     "оплата: 300 грн, проверка по скриншоту"]
];
const ORDER = SETUP.map(s => s[0]).concat(["checks"]);

function showProfile(){
  el("pAv").classList.add("on");
  el("pName").textContent = "Стоматологія Comfort";
  el("pHandle").textContent = HANDLE;
}

window.STAGE = {
  enter(scene){
    el("pStatus").textContent = STATUS[scene] || "";
    if(ORDER.indexOf(scene) >= ORDER.indexOf("profile")) showProfile();
    if(scene === "checks"){ el("chat").className = "chat"; return; }
    el("chat").className = "chat start";
    const upto = SETUP.findIndex(s => s[0] === scene);
    el("chat").innerHTML = '<div class="setup">' +
      SETUP.slice(0, upto + 1).map((s, i) =>
        '<div class="' + (i === upto ? "now" : "") + '">' + s[1] + '</div>').join('') +
      '</div>';
  },
  tick(scene, frac, finished){
    if(scene !== "checks" && !finished) return;
    SAY.forEach(([at, who, text], i)=>{
      if(said.has(i) || (!finished && frac < at)) return;
      said.add(i);
      const setup = el("chat").querySelector(".setup");
      if(setup){ setup.remove(); el("chat").className = "chat"; }
      const d = document.createElement("div");
      if(text === "circle:"){
        d.className = "msg circle " + who;
        d.innerHTML = '<video src="__CIRCLE__" muted autoplay loop playsinline></video>';
      } else if(text === "pay:"){
        d.className = "msg pay " + who;
        d.innerHTML = '<span class="ok">✓ Успішно</span><b>300 ₴</b><span>Стоматологія Comfort</span>';
      } else if(text.indexOf("voice:") === 0){
        d.className = "msg voice " + who;
        d.innerHTML = '<i></i><i></i><i></i><i></i><i></i>' + text.slice(6);
      } else {
        d.className = "msg " + who;
        d.textContent = text;
      }
      el("chat").appendChild(d);
    });
    if(finished){
      showProfile();
      el("pStatus").textContent = "онлайн, отвечает сам";
      el("pStatus").classList.add("live");
    }
  }
};
