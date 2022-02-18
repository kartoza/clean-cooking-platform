class modal {
  constructor(id, o) {
    let d = document.createElement('dialog');
    d.id = id;
    d.className = 'modal';
    d.style = `
position: fixed;
top: 0;
left: 0;
display: none;
border: none;
margin: 0;
width: 100%;
height: 100%;
z-index: 1000;
background-color: rgba(0,0,0,0.4);
overflow-y: scroll;
padding: 0;
`;

    let m = document.createElement('main');
    m.style = `
margin: auto;
margin-bottom: 20px;
width: -moz-fit-content;
`;
    d.append(m);

    let h = document.createElement('header');
    h.style = `padding: 1em; position: relative;`;
    m.prepend(h);

    let c = document.createElement('content');
    c.style = `padding-right: 2em; padding-left: 2em; padding-bottom: 0.5em;`;
    m.append(c);

    let f = document.createElement('footer');
    f.style = `padding: 1em;`;
    m.append(f);

    this.dialog = d;
    this.main = m;
    this.header = h;
    this.content = c;
    this.footer = f;

    this.check = o.check;
    this.destroy = o.destroy || false;

    this.click_listener = e => {
      e.stopImmediatePropagation();
      if (e.target !== this.dialog) return;

      if (this.destroy) this.remove();
      else this.hide();

      return true;
    };

    this.esc_listener = e => {
      if (e.key === "Escape") {
        let t = document.elementFromPoint(5,5);

        if (!(t === this.dialog || t === this.dialog)) return false;

        if (this.destroy) this.remove();
        else this.hide();

        return true;
      }
    };

    this.set(o);
    document.body.append(d);

    return this;
  }

  set(o) {
    this.set_el(this.header, maybe(o, 'header'));
    this.set_el(this.content, maybe(o, 'content'));
    this.set_el(this.footer, maybe(o, 'footer'));

    // Update header to add X button
    this.header.style.display = 'flex';
    let x = document.createElement('div');
    x.style.marginLeft = 'auto';
    x.classList.add('hover-button');
    x.innerHTML = '✕';
    let that = this;
    x.addEventListener('click', function (event) {
      that.hide();
    })
    this.header.append(x);

    return this;
  }

  set_el(el, t) {
    if (t) {
      while (el.lastChild) el.removeChild(el.lastChild);

      if (t instanceof HTMLElement) el.appendChild(t);
      else if (typeof t === 'string') el.innerHTML = t;
    }

    el.style.display = (!t || el.innerHTML === "") ? "none" : "block";
  }

  show(callback) {
    this.dialog.style['display'] = 'block';
    document.addEventListener('keydown', this.esc_listener);

    this.dialog.addEventListener('click', this.click_listener);

    document.addEventListener('keydown', this.esc_listener);

    document.body.append(this.dialog);

    if (typeof callback === 'function') callback(this);

    return this.dialog;
  }

  hide(callback) {
    if (typeof this.check === 'function' && !this.check()) return false;

    this.dialog.style['display'] = 'none';

    document.removeEventListener('keydown', this.esc_listener);

    if (typeof callback === 'function') callback(this);
    return true;
  }

  _empty_close() {
    let d = this.dialog;

    while (d.lastChild) d.removeChild(d.lastChild);
    d.remove();
  }

  remove(callback, force = false) {
    if (force) {
      this._empty_close();
      return true;
    }

    if (!this.hide()) return false;

    this._empty_close();

    if (typeof callback === 'function') callback(this);
    return true;
  }
}

window.modal = modal;
