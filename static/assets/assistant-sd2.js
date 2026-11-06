(() => {
  const page = document.currentScript?.dataset.page || 'home';
  const questions = {
    home: ['Как выбрать бетон?', 'Куда доставляете?'],
    beton: ['Какую марку выбрать?', 'Условия доставки'],
    dostavka: ['Нужен бетононасос', 'Доставка за пределы КМВ'],
    zhbi: ['Подобрать ЖБИ', 'Условия отгрузки'],
    asfalt: ['Какие смеси есть?', 'Как заказать асфальт?'],
    karer: ['Какие фракции есть?', 'Условия самовывоза'],
    laboratoriya: ['Какие испытания проводите?', 'Проверить бетон'],
    obekty: ['Примеры поставок', 'Поставка на мой объект'],
    kontakty: ['Как связаться с заводом?', 'Как доехать?'],
  };
  const items = questions[page];
  const root = document.querySelector('.gg-assistant');
  const input = root?.querySelector('.gg-assistant__form .gg-assistant__input');
  const actions = root?.querySelector('.gg-assistant__actions');
  if (!items || !input || !actions) return;

  const quick = document.createElement('div');
  quick.className = 'gg-assistant__quick';
  quick.setAttribute('role', 'group');
  quick.setAttribute('aria-label', 'Быстрые вопросы');
  for (const question of items) {
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = question;
    button.addEventListener('click', () => {
      input.value = question;
      input.focus();
    });
    quick.append(button);
  }
  actions.before(quick);
})();
