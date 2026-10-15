const SCENES = {
  access: [["Кабинет","Стоматологія Comfort, доступ есть"],["Страница","клиника привязана"],
           ["Оплата","карта подключена"],["Приложение","статус Live"]],
  hooks: [["0–3 с","Влад у зеркала: «почему-то белые зубы…» — цепляет сразу"],
          ["3–15 с","живая история: «ухоженный вид», страх сжечь эмаль"],
          ["15–30 с","клиника «Комфорт» и сама процедура"],
          ["30–39 с","сертификат и название клиники"]],
  aud: ["Троєщина + 5 км","25–40 років","переважно жінки","інтерес: відбілювання","події: весілля, фотосесія","охоплення ~90 000"],
  place: [["Reels","главный показ, вертикальное видео"],["Stories","добираем охват"],
          ["Лента","остаток бюджета"],["₴400 в день","старт завтра в 9:00"]],
  checks: ["ссылка из объявления открывается","модерация объявление приняла","дневной лимит на месте"]
};

const LAB = {access:"доступ к кабинету", hooks:"первые секунды видео", aud:"кому показываем",
  copy:"текст объявления", place:"места показа и деньги", checks:"перед включением"};

const kbList = arr => '<div class="kb">'+arr.map(k=>'<div class="it"><b>'+k[0]+'</b><span>'+k[1]+'</span></div>').join('')+'</div>';
const flowList = arr => '<div class="flow">'+arr.map(f=>'<div class="node it"><em>'+f[0]+'</em><div><b>'+f[1]+'</b></div></div>').join('')+'</div>';

const BUILD = {
  access: () => kbList(SCENES.access),
  hooks:  () => flowList(SCENES.hooks),
  aud:    () => '<div class="chips">'+SCENES.aud.map(a=>'<span class="chip it">'+a+'</span>').join('')+'</div>',
  copy:   () => '<div class="ad">'+
                '<div class="head it" data-at=".12">Білі зуби без шкоди для емалі</div>'+
                '<div class="txt it" data-at=".38">Кабінетне відбілювання MagicSmile у «Комфорт» на Троєщині. '+
                'Професійна гігієна в подарунок, консультація безкоштовна. Працюємо щодня до 20:00.</div>'+
                '<div class="cta it" data-at=".68">Написати в Telegram</div></div>',
  place:  () => kbList(SCENES.place),
  checks: () => '<ul class="rules yes">'+SCENES.checks.map(c=>'<li class="it">'+c+'</li>').join('')+'</ul>'
};

const FIELDS = [
  ["access",   {cabPill:"кабинет подключён", cNote:"кампании пока нет"}],
  ["hooks",    {cNote:"смотрим видео: вертикальное, 39 секунд, с субтитрами"}],
  ["aud",      {cAud:"Троєщина · 25–40", cNote:"аудитория собрана: около 90 000 человек"}],
  ["copy",     {cName:"Comfort · Відбілювання", cNote:"объявление собрано, ещё не включено"}],
  ["place",    {cBud:"₴400 / день", cNote:"Reels и Stories, старт завтра в 9:00"}],
  ["checks",   {cNote:"проверяем перед включением"}]
];

window.STAGE = {
  enter(scene){
    el("creoScan").classList.toggle("on", scene === "hooks");
    const upto = FIELDS.findIndex(f => f[0] === scene);
    FIELDS.slice(0, upto + 1).forEach(([, vals]) => {
      Object.keys(vals).forEach(id => { el(id).textContent = vals[id]; });
    });
  },
  tick(scene, frac, finished){
    if((scene === "checks" && frac > .9) || finished){
      el("cSt").textContent = "активна";
      el("cSt").classList.add("live");
      el("cabPill").textContent = "кампания работает";
      el("cabPill").classList.add("live");
      el("cNote").textContent = "первые цифры по показам появятся через 15–20 минут";
    }
  }
};
