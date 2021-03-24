class nanny {
  constructor(steps) {
    this.steps = steps;
    this.current_step = -1;
  }

  start() {
    if (!this.steps || !this.steps.length) return;
    this.current_step = -1;
    this.next();
  };

  finish() {
    return true;
  };

  abort() {
    this.current_step = -1;
  };

  async next() {
    this.current_step += 1;
    const i = this.current_step;
    const s = this.steps[i];

    if (this.marker) this.marker.remove();

    if (!s) { this.finish(); return; }

    const m = s.mark;
    const l = s.listen;

    await s.init.call(s, this);

    const x = _ => {
      if (this.marker) this.marker.remove();
      this.next();
    };

    if (m) {
      let me = m.el ? m.el(s) : s.el;
      this.marker = nanny.pick_element(me, m);
    }

    if (l) {
      let we = l.el ? l.el(s) : s.el;

      let o;
      we.addEventListener(l.action, o = function() {
        (typeof l.f === 'function') ? l.f.call(s,x) : x.call(s,this);
        we.removeEventListener(l.action, o);
      });
    }

    if (typeof s.run === 'function') s.run.call(s,x);
  };

  static pick_element(el, opts) {
    if (!(el instanceof Element)) throw DOMError, `nanny.pick_element: No such element. Got '${el}.'`;

    const elbox = el.getBoundingClientRect();

    const marker = document.createElement('aside');
    marker.className = 'nanny-marker';
    marker.style = `
position: absolute;
display: flex;
`;

    const caret = document.createElement('span');
    caret.className = 'nanny-caret';
    caret.style = `
display: block;
position: absolute;
left: 0;
top: 0;
border-style: inset;
border-color: transparent;
border-radius: 2px;
pointer-events: none;
`;

    const main = document.createElement('main');

    if (opts.title) {
      const header = document.createElement('header');

      if (opts.title instanceof Element)
        header.append(opts.title)
      else
        header.innerHTML = opts.title;

      main.append(header);
    }

    if (opts.message) {
      const content = document.createElement('content');;

      if (opts.message instanceof Element)
        content.append(opts.message);
      else
        content.innerHTML = opts.message;

      main.append(content);
    }

    const close_button = document.createElement('div');
    close_button.className = 'nanny-close-button';
    close_button.style = `cursor: pointer;`;
    close_button.onclick = _ => {
      if (marker) marker.remove();
      if (this instanceof nanny) this.abort();
    }

    close_button.style.display = (opts.close === false) ? 'none' : 'block';

    marker.append(caret, main, close_button);

    document.body.append(marker);

    let x = elbox.x;
    let y = elbox.y;

    function halign() {
      switch (opts.align) {
      case "start":
        x += 0;
        break;

      case "end":
        x += elbox.width - marker.clientWidth;
        break;

      case "middle":
      default:
        x += (elbox.width / 2) - (marker.clientWidth / 2);
        break;
      }
    };

    function valign() {
      switch (opts.align) {
      case "start":
        y -= marker.clientHeight / 2;
        break;

      case "end":
        y += elbox.height - (marker.clientHeight / 2);
        break;

      case "middle":
      default:
        y = elbox.y + (elbox.height / 2) - (marker.clientHeight / 2);
        break;
      }
    };

    const bc = "rgba(0,0,0,1)";
    let cs, f;

    switch (opts.position) {
    case "N":
    case "north": {
      halign();
      cs = (marker.clientWidth / 2);
      f = 1/4;

      caret.style['border-width'] = cs + "px";
      caret.style['border-top-color'] = bc;
      caret.style['transform'] = `scale(1, ${f})`;
      caret.style['top'] = marker.clientHeight - ((marker.clientWidth * (3/8)) + 0.5) + "px";

      y -= marker.clientHeight + (cs * f);

      break;
    }

    case "E":
    case "east": {
      valign();
      cs = (marker.clientHeight / 2);
      f = 1/2;

      caret.style['border-width'] = cs + "px";
      caret.style['border-right-color'] = bc;
      caret.style['transform'] = `scale(${f}, 1)`;
      caret.style['left'] = -((marker.clientHeight * (3/4)) - 0.5) + "px";

      x += elbox.width + (cs * f);

      break;
    }

    case "S":
    case "south": {
      halign();
      cs = (marker.clientWidth / 2);
      f = 1/4;

      caret.style['border-width'] = cs + "px";
      caret.style['border-bottom-color'] = bc;
      caret.style['transform'] = `scale(1, ${f})`;
      caret.style['top'] = -((marker.clientWidth * (5/8)) - 0.25) + "px";

      y += elbox.height + (cs * f);

      break;
    }

    case "W":
    case "west": {
      valign();
      cs = (marker.clientHeight / 2);
      f = 1/2;

      caret.style['border-width'] = cs + "px";
      caret.style['border-left-color'] = bc;
      caret.style['transform'] = `scale(${f}, 1)`;
      caret.style['left'] = marker.clientWidth - ((marker.clientHeight * (1/4)) + 0.5) + "px";

      x -= marker.clientWidth + (cs * f);

      marker.prepend(close_button);

      break;
    }

    case "C":
    case "CENTER": {
      caret.style['display'] = 'none';
      opts.align = 'middle';

      valign();
      halign();

      break;
    }

    default:
      break;
    }

    marker.style.left = x + "px"
    marker.style.top = y + "px"

    return marker;
  };
}

window.nanny = nanny;
