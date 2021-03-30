UUID_REGEXP = "^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$";

Whatever = new Promise((resolve, reject) => resolve());

function qs(str, el) {
  if (!el) el = document;
  else if (!(el instanceof Node))
    throw Error(`qs: Expected a Node. got ${el}.`);

  return (el.shadowRoot) ?
    el.shadowRoot.querySelector(str) :
    el.querySelector(str);
};

function qsa(str, el, array = false) {
  if (!el) el = document;
  else if (!(el instanceof Node))
    throw Error(`qs: Expected a Node. got ${el}.`);

  const r = (el.shadowRoot) ?
    el.shadowRoot.querySelectorAll(str) :
        el.querySelectorAll(str);

  if (array) {
    const a = [];
    for (let i = r.length; i--; a.unshift(r[i]));
    return a;
  }

  return r;
};

function ce(str, content, attrs = {}) {
  const el = document.createElement(str);
  for (let o in attrs)
    if (attrs.hasOwnProperty(o) && attrs[o] !== undefined) el.setAttribute(o, attrs[o]);

  if (content instanceof Element) el.append(content);
  else if (typeof content === 'string') el.innerHTML = content;
  else if (Array.isArray(content) && content.every(x => x instanceof Element)) el.append(...content);

  return el;
};

function shadow_tmpl(el) {
  if (typeof el === 'string') el = qs(el);

  if (!el) throw Error(`shadow_tmpl: Expected 'el' to be a DOM Element.`);

  return el.content.cloneNode(true);
};

function tmpl(el, data = null) {
  const _el = el;
  if (typeof el === 'string') el = qs(el);

  if (!el) throw Error(`tmpl: Expected 'el' to be a DOM Element: ${_el}`);

  const r = el.content.cloneNode(true);

  if (!data) return r.firstElementChild;

  for (let e of r.querySelectorAll('[bind]')) {
    let v = e.getAttribute('bind');
    if (undefined === data[v]) continue;

    if (data[v] instanceof Element)
      e.append(data[v]);
    else
      e.innerHTML = tmpl_format(e, data[v]);
  }

  for (let e of r.querySelectorAll('[bind-cond]')) {
    let v = e.getAttribute('bind-cond');

    if (null === data[v] ||
        false === data[v] ||
        undefined === data[v]) e.remove();
  }

  for (let e of r.querySelectorAll('[bind-unless]')) {
    let v = e.getAttribute('bind-unless');

    if (data[v]) e.remove();
  }

  for (let e of r.querySelectorAll('[bind-attr]')) {
    let v = e.getAttribute('bind-value');
    if (undefined === data[v]) continue;

    let n, a, t;
    a = e.getAttribute('bind-attr');
    t = tmpl_format(e, data[v]);

    if (!data[v] && (n = e.getAttribute('bind-not')))
      t = n;

    e.setAttribute(a, t);
  }

  for (let e of r.querySelectorAll('[bind-lambda]')) {
    let v = e.getAttribute('bind-value');
    if (undefined === data[v]) continue;

    let n, f, t;
    f = e.getAttribute('bind-lambda');

    t = tmpl_format(e, eval(`${f}(data['${v}'])`)); // yes, I did it!

    if (!data[v] && (n = e.getAttribute('bind-not')))
      t = n;

    if (t instanceof Element)
      e.append(t);
    else
      e.innerHTML = t;
  }

  return r.firstElementChild;
};

function tmpl_format(el, data = null) {
  let f, t;

  t = data;

  if (f = el.getAttribute('bind-format'))
    t = f.replace('{0}', data);

  return t;
};

function elem(str, p) {
  var d = document.createElement(p ? p : 'div');
  d.innerHTML = str;

  return p ? d : d.firstElementChild;
};

function elem_empty(e) {
  if (e instanceof Node)
    while (e.lastChild) e.removeChild(e.lastChild);
  else
    throw "Argument: argument is not a Node";
};

function attach(el) {
  const shadow = this.attachShadow({ mode: 'open' });
  shadow.append(el);

  return shadow;
};

function is_tree(t) {
  return (t[0] instanceof Element) &&
    (!t[1] || t[1] instanceof Array)
};

function el_tree(t) {
  const head = t[0];
  const tail = t[1];

  if (t instanceof Element) return t;

  if (!(head instanceof Element))
    throw 'el_tree: head is not a Element.';

  if (tail instanceof NodeList) {
    head.append(...tail);
    return head;
  }

  else if (tail instanceof Array) {
    if (tail.every(e => e instanceof Element)) // allows [p, [c1, c2, c3]]
      head.append(...tail);

    else if (is_tree(tail))        // allows [p, [c, []]]
      head.append(el_tree(tail));  //            ^---- a tree, not array of trees (the default)

    else                           // asume array of trees. [p, [[c1, []], [c2, []]]]
      tail.forEach(e => head.append(el_tree(e)));
  }

  else if (!t[1]) { }

  else {
    throw `el_tree: don't know what to do with ${typeof t[1]}, ${t[1]}`;
  }

  return t[0];
};

function slot(name, content) {
  let el = document.createElement('span');
  el.setAttribute('slot', name);

  if (content instanceof Element)
    el.append(content);
  else if (typeof content === 'object')
    throw Error(`slot: Expected an Element or something stringy. Got an ${content}`);
  else
    el.innerHTML = content;

  return el;
};

function slot_populate(data, extra = {}) {
  for (let k in data) {
    if (typeof data[k] === 'object') continue;
    let s = qs(`slot[name=${k}]`, this);
    if (s) this.append(slot(k, data[k]));
  }

  if (typeof extra !== 'object') return;

  for (let k in extra) {
    if (!extra[k]) continue;
    // this.append(slot(k, extra[k]));
    qs(`[name=${k}]`, this).append(slot(k, extra[k]));
  }
};

function log() {
  return console.log.apply(console, arguments);
};

function debug() {
  return console.trace.apply(console, arguments);
};

function warn() {
  return console.warn.apply(console, arguments);
};

function delay(s) {
  if (typeof s !== 'number') throw "ArgumentError: delay expects an number";
  return new Promise(_ => setTimeout(_, s * 1000));
};

function until(fn, maxtries = 100) {
  if (typeof fn !== 'function') throw "ArgumentError: waitfor expects a function";

  return new Promise((resolve, reject) => {
    let tries = 0;

    let interval = setInterval(function() {
      let result;

      try {
        result = fn();
        tries += 1;
      }
      catch (err) {
        result = null;
      }

      if (result) {
        clearInterval(interval);
        resolve();

        return true;
      }

      else if (tries >= maxtries) {
        console.warn(`until: gave up after ${tries} tries.`);
        clearInterval(interval);
        reject();

        return true;
      }
    }, 70);
  });
};

function maybe(o, ...path) {
  return (!o || !path.length) ? o :
    maybe(o[path[0]], ...path.slice(1));
};

function coalesce() {
  if (!arguments.length) return undefined;

  const a = arguments[0];

  return (null === a || undefined === a) ?
    coalesce(...Array.prototype.slice.call(arguments, 1)) : a;
};

function date_valid(d) {
  return d instanceof Date && !isNaN(d);
};

function has(object, attr) {
  return !(!object.hasOwnProperty(attr)
           || undefined === object[attr]
           || null === object[attr]);
};

function load_script(src, callback) {
  let script = document.createElement('script');
  script.async = true;
  script.src = src;

  if (typeof callback === 'function')
    script.onload = _ => callback(src);

  document.head.appendChild(script);
};

async function fake_blob_download(stream, filename, datatype = "application/octet-stream;charset=utf-8") {
  const url = URL.createObjectURL(new Blob([stream], { type: datatype }));

  await fake_download(url, filename);

  if (url instanceof URL) window.URL.revokeObjectURL(url);
};

async function fake_download(url, filename) {
  const a = document.createElement('a');
  a.href = url;
  a.target = "_blank";
  a.download = filename ? filename : '';
  a.style.display = 'none';

  document.body.appendChild(a);

  await delay(0.1);
  a.click();

  a.remove();
};
