class selectlist {
  constructor(id, dict, opts = {}) {
    this.dict = dict;
    this.id = id;
    this.opts = opts;

    this.input = document.createElement('input');
    this.input.id = 'selectlist-input-' + this.id;
    this.input.className = 'selectlist-input';
    this.input.setAttribute('type', 'text');
    this.input.setAttribute('autocomplete', 'off');

    const chrome = /Google Inc/.test(navigator.vendor);
    const safari = /Apple Computer/.test(navigator.vendor);
    const firefox = typeof InstallTrigger !== 'undefined';

    const style = document.createElement('style');
    style.innerHTML = `
.selectlist-dropdown {
  position: absolute;
  display: none;
  width: 100%;
  max-height: 300px;
  overflow-x: hidden;
  overflow-y: scroll;
  z-index: 9999;
  padding: 8px 0;
  border-radius: 5px;
  background-color: white;
  box-shadow: 0 3px 5px 0 rgba(0,0,0,0.2);
}

.selectlist-dropdown-element {
  padding: 7px 15px;
  font-size: 0.9em;
  color: black;
  text-align: left;
}

.selectlist-dropdown-element:hover:active {
  background-color: #cecece
}

.selectlist-dropdown-element:hover,
.selectlist-dropdown-element[active] {
  background-color: #e7e9ec;
}`;

    document.head.append(style);

    return (safari || firefox || opts.polyfill) ?
      this.polyfill() :
      this.datalist();
  };

  input_change(e) {
    this.current_value = this.input.value;

    if (typeof this.opts.change === 'function')
      this.opts.change.apply(this.input, e);
  };

  datalist() {
    const dl = document.createElement('datalist');
    dl.id = 'selectlist-datalist-' + this.id;

    document.body.append(dl);

    this.input.setAttribute('list', 'selectlist-datalist-' + this.id);

    for (let x in this.dict) {
      let o = document.createElement('option');
      o.setAttribute('value', x);
      o.innerText = this.dict[x];

      dl.append(o);
    }

    this.datalist_events();
    this.input = this.input;
    this.el = this.input;

    return this;
  };

  datalist_events() {
    this.current_value = this.input.value;

    this.input.addEventListener('click', e => {
      if (typeof this.opts.click === 'function') this.opts.click.apply(this.input, e);
      else null;
    });

    this.input.addEventListener('change', e => this.input_change());

    this.input.addEventListener('focus', e => {
      this.current_value = this.input.value;

      if (typeof this.opts.focus === 'function')
        this.opts.focus.apply(this.input, e);
      else
        this.input.value = '';
    });

    this.input.addEventListener('blur', e => {
      if (typeof this.opts.blur === 'function')
        this.opts.blur.apply(this.input, e);

      if (this.input.value === "") this.input.value = this.current_value;
    });
  };

  polyfill() {
    this.container = document.createElement('div');
    this.container.style = `position: relative; margin: 0; padding: 0;`;
    this.container.className = 'selectlist-container';

    this.dropdown = document.createElement('div');
    this.dropdown.id = 'selectlist-dropdown-' + this.id;
    this.dropdown.className = 'selectlist-dropdown';

    for (let x in this.dict) {
      let o = document.createElement('div');
      o.className = 'selectlist-dropdown-element';
      o.setAttribute('bind-value', x);
      o.innerText = this.dict[x];
      o.onclick = e => {
        this.input.value = x;
        this.input.dispatchEvent(new Event('change'));

        return false;
      };

      this.dropdown.append(o);
    }

    this.el = this.container;
    this.container.append(this.input, this.dropdown);

    this.blur_listener = e => {
      e.stopPropagation();
      e.preventDefault();

      if (e.target.closest('.selectlist-dropdown') === this.dropdown
          || e.target === this.input) return;

      this.dropdown.style.display = 'none';

      return false;
    };

    this.options = this.container.querySelectorAll('.selectlist-dropdown-element');

    this.polyfill_events();

    return this;
  };

  polyfill_show() {
    const r = this.input.getBoundingClientRect();

    this.polyfill_unsetactive();

    this.dropdown.style.display = 'block';
    this.dropdown.style.width = r.width + "px";
    this.dropdown.style.top = r.height + 10 + "px";
    this.dropdown.style.left = window.getComputedStyle(this.input)['margin-left'];

    document.body.addEventListener('click', this.blur_listener);
  };

  polyfill_setactive() {
    if (!this.active) return;

    this.active.setAttribute('active', '');
    this.active.scrollIntoView({ block: "center" });
  };

  polyfill_unsetactive() {
    if (this.active) this.active.removeAttribute('active');
  };

  polyfill_hide() {
    document.body.removeEventListener('click', this.blur_listener);
    this.dropdown.style.display = 'none';
  };

  polyfill_next() {
    if (!this.active)
      this.active = this.dropdown.firstChild;
    else {
      this.polyfill_unsetactive();
      this.active = this.active.nextElementSibling || this.dropdown.firstChild;
    }

    if (this.active) {
      this.active.setAttribute('active', '');
      this.active.scrollIntoView({ block: "center" });
    }
  };

  polyfill_prev() {
    if (!this.active)
      this.active = this.dropdown.lastChild;
    else {
      this.polyfill_unsetactive();
      this.active = this.active.previousElementSibling || this.dropdown.lastChild;
    }

    this.polyfill_setactive();
  };

  polyfill_events() {
    /*
     *  We cannot use the blur event. it happens to fast and breaks stuff.
     */
    this.input.addEventListener('focus', _ => this.polyfill_show());

    this.input.addEventListener('change', e => {
      this.input_change(e);
      this.polyfill_hide();
    });

    this.input.addEventListener('keydown', e => {
      switch (e.key) {
      case 'ArrowDown':
        this.polyfill_next();
        return;

      case 'ArrowUp':
        this.polyfill_prev();
        return;

      case 'Enter': // buggy
        e.preventDefault();
        e.stopPropagation();

        if (this.active) {
          const nv = this.active.getAttribute('bind-value');
          if (nv === this.input.value) return false;

          this.input.value = this.active.getAttribute('bind-value');
          this.polyfill_hide();
          this.input.dispatchEvent(new Event('change'));
        }

        return false;
      }
    });

    this.input.addEventListener('keyup', e => {
      switch (e.key) {
      case 'ArrowDown':
      case 'ArrowUp':
        return;

      case 'Enter':
        return;

      case 'Escape':
        this.polyfill_hide();
        return;

      case 'ArrowRight':
        if (this.active) this.input.value = this.active.getAttribute('bind-value');
        return;

      default:
        break;
      };

      const r = new RegExp(e.target.value, 'i');

      const c = [];
      for (let i = 0; i < this.options.length; i += 1) {
        let o = this.options[i];
        if (o.getAttribute('bind-value').match(r)) c.push(o);
      }

      this.dropdown.innerHTML = '';
      this.dropdown.append(...c);

      this.polyfill_unsetactive();
      this.polyfill_show();

      this.active = c[0];
      this.polyfill_setactive();
    });
  };
}

window.selectlist = selectlist;
