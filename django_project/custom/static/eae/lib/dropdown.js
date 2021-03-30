class dropdown {
  constructor(array) {
    if (!array.length) return "";

    this.array = array;

    if (!this.array.every(i => undefined !== i.content)) {
      throw "dropdown: array elements do not comply with { action: function, content: Element } form";
    }

    this.root = document.createElement('div');
    this.root.className = 'more-dropdown';

    this.dots = document.createElement('div');
    this.dots.innerHTML = `
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" style="position: relative; top: 2px;">
   <path d="M12 8c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm0 2c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0 6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z"/>
</svg>`;
    this.dots.style = `
fill: gray;
display: block;
width: 24px;`;

    this.root.append(this.dots);

    this.init();

    return this.root;
  };

  create_ul() {
    this.ul = document.createElement('ul');
    this.ul.className = 'more-dropdown-ul';

    const b = this.root.getBoundingClientRect();

    for (let i of this.array) {
      let li = document.createElement('li');
      li.className = 'more-dropdown-li';

      if (i.content instanceof Element)
        li.append(i.content);
      else
        li.innerText = i.content;

      if (typeof i.action === 'function')
        li.onclick = e => i.action(this, e);

      li.style = `
text-align: left;
cursor: pointer;`;

      this.ul.append(li);
    }

    document.body.append(this.ul);

    if (b.left + this.ul.clientWidth > screen.width)
      this.ul.style.right = 0 + "px";
    else
      this.ul.style.left = b.left + "px";

    if (b.top + this.ul.clientHeight > screen.height) {
      this.ul.style.bottom = 0 + "px";
      this.ul.style.top = "auto";
    }
    else
      this.ul.style.top = b.top + "px";
  };

  init() {
    this.blur_listener = e => {
      e.stopPropagation();
      e.preventDefault();

      if (e.target.closest('.more-dropdown') === this.root)
        return true;
      else {
        this.ul.remove();
        document.body.removeEventListener('click', this.blur_listener);
      }

      return false;
    };

    this.dots.onclick = e => {
      this.create_ul();
      setTimeout(_ => document.body.addEventListener('click', this.blur_listener), 50);
    };
  };
}

window.dropdown = dropdown;
