class flash {
  constructor() {
    let el = document.querySelector('aside#flash');
    if (!el) {
      el = document.createElement('aside');
      el.id = 'flash';
      el.style = `
position: fixed;
top: 7px;
left: 7px;
z-index: 9999;`;

      document.body.prepend(el);
    }

    this.el = el;
  }

  push(e) {
    let colors = this.e_colors(e.type);
    let timeout = isFinite(e.timeout) ? e.timeout : this.e_timeout(e.type);
    let item_el = this.e_element(e, colors);

    if (timeout > 0)
      setTimeout(function() { item_el.remove(); }, timeout);

    this.el.prepend(item_el);

    return this;
  }

  clear() {
    this.el.innerHTML = "";

    return this;
  }

  e_element(e, colors) {
    let d = document.createElement('div');
    d.className = "flash-item";
    let html = ''

    if (e.title)
      html += `<strong class="flash-title">${e.title}</strong>`;

    if (e.title && e.message)
      html += '<br>';

    if (e.message)
      html += `<pre class="flash-message">${e.message}</pre>`;

    d.innerHTML = html;
    d.style = `
margin-bottom: 10px;
padding: 10px 20px;
border: 1px solid white;`;

    for (let c in colors)
      d.style[c] = colors[c];

    d.addEventListener('click', _ => d.remove());

    return d;
  }

  e_timeout(type) {
    let t;

    switch (type) {
    case "error":
      t = 0;
      break;

    case "info":
      t = 3000;
      break;

    case "success":
      t = 1000;
      break;

    default:
      t = 5000;
      break;
    };

    return t;
  }

  e_colors(type) {
    let bc, c;

    switch (type) {
    case "error":
      bc = '#E3655A';
      c = 'white';
      break;

    case "info":
      bc = '#AEB3FF';
      c = 'white';
      break;

    case "success":
      bc = '#77B96F';
      c = 'white';
      break;

    default:
      bc = 'gray';
      c = 'white';
    };

    return { "background-color": bc, "color": c };
  }
}

window.flash = flash;
