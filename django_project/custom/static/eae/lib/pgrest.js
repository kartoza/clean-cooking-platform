class pgrest {
  constructor(api, flash) {
    this.api = api;
    this.flash = flash || { push: x => console.log(x), clear: _ => null };
    this.token = localStorage.getItem('token');
  };

  async parse(response, options = {}) {
    let body;

    try {
      switch (options.expect) {
      case 'csv':
      case 'text':
        body = await response.text();
        break;

      case 'blob':
        body = await response.blob();
        break;

      case 'json':
      default:
        body = await response.json();
        break;
      }
    }
    catch(err) {
      return { "message": "pgrst#parse: failed to parse response!" };
    }

    if (!response.ok) {
      let title, message;
      let type = 'error';

      switch (response.status) {
      case 0: {
        title = "Connection error";
        message = "You (and/or the server) are offline.";
        this.flash.push({ type: type, title: title, message, message });
        break;
      }

      case 401: {
        localStorage.removeItem('token');

        if (body.message === 'JWT expired') {
          type = null
          title = "Session expired";
          message = "Log in on the other tab.";

          setTimeout(_ => window.open('/?login&popup=true'), 1000);

          window.dt_token_interval = setInterval(function() {
            if (!localStorage.getItem('token'))
              console.log("Waiting for token");

            else {
              clearInterval(window.dt_token_interval);
              window.location.reload();
            }
          }, 1000);

          this.flash.push({ type: type, title: title, message, message });
        }

        else {
          window.location = '/?login';
          return;
        }
        break;
      }

      case 500: {
        title = "Server crash!";
        message = "NOT GOOD. File a bug report.";
        this.flash.push({ type: type, title: title, message, message });
        break;
      }

      case 502: {
        title = "Server is not running!";
        message = "NOT GOOD. Contact an admin.";
        this.flash.push({ type: type, title: title, message, message });
        break;
      }

      default: {
        title = `${response.status}: ${response.statusText}`;
        message = body.message;
        this.flash.push({ type: type, title: title, message, message });

        break;
      }
      }

      throw new Error('pgrest: FAILED request');
    }

    return body;
  };

  req(method, options) {
    const {contenttype, payload, one, expect} = options;

    const r = {
      "method": method,
      "headers": {
        "Authorization": this.token ? `Bearer ${this.token}` : undefined,
        "Content-Type": (contenttype || 'application/json'),
      }
    }

    if (one) r.headers['Accept'] = "application/vnd.pgrst.object+json";

    if (expect === 'csv') r.headers['Accept'] = "text/csv";

    for (let k in r.headers)
      if (undefined === r.headers[k]) delete r.headers[k];

    return r;
  }

  go(request, table, params = {}, options = {}) {
    const url = new URL(this.api + "/" + table);

    for (let k in params) {
      let v = params[k];
      if (v instanceof Array) v = params[k].join(',');

      url.searchParams.set(k,v);
    }

    return fetch(url, request)
      .catch(err => {
        this.flash.push({
          type: 'error',
          title: err.message,
          message: url.toString().substring(0,128) + " ..."
        });

        throw err;
      })
      .then(r => this.parse(r, options));
  };

  get(table, params = {}, options = {}) {
    const req = this.req('GET', options);
    return this.go.call(this, req, ...arguments);
  };

  post(table, params = {}, options = {}) {
    const req = this.req('POST', options);

    req.headers["Prefer"] = "return=representation";
    if (req.headers['Content-Type'] === 'multipart/form-data')
      delete req.headers['Content-Type'] // OMFG...

    if (options.payload) {
      req.body = (req.headers['Content-Type'] === 'application/json') ?
        JSON.stringify(options.payload) :
        options.payload
    }

    return this.go.call(this, req, ...arguments);
  };

  patch(table, params = {}, options = {}) {
    const req = this.req('PATCH', options);
    req.headers["Prefer"] = "return=representation";

    if (options.payload) {
      req.body = (req.headers['Content-Type'] === 'application/json') ?
        JSON.stringify(options.payload) :
        options.payload
    }

    return this.go.call(this, req, ...arguments);
  };

  delete(table, params = {}, options = {}) {
    const req = this.req('DELETE', options);
    req.headers["Prefer"] = "return=representation";

    return this.go.call(this, req, ...arguments);
  };
}

window.pgrest = pgrest;
