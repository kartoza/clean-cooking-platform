(function() {
  new cookieNoticeJS({
    'messageLocales': {
      'en': "This website uses cookies to provide you with an improved user experience. By continuing to browse this site, you consent to the use of cookies and similar technologies. For further details please visit our"
    },
    'buttonLocales': {
      'en': "OK"
    },
    'learnMoreLinkText':{
      'en': 'privacy policy.'
    },
    'learnMoreLinkEnabled': true,
    'learnMoreLinkHref': '/privacy-policy',
    'cookieNoticePosition': 'bottom',
    'expiresIn': 30,
    'buttonBgColor': '#f0ab00',
    'buttonTextColor': '#131313',
    'noticeBgColor': '#000000',
    'noticeTextColor': '#ffffff',
    'linkColor': '#e3810a',
    'linkTarget': '_blank',
    'debug': false
  });

  function add() {
    const script = document.createElement('script');
    script.async = true;
    script.src = "https://www.googletagmanager.com/gtag/js?id=UA-67196006-4";
    script.onload = _ => {
      const s = document.createElement('script');
      s.innerHTML = `
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());
gtag('config', 'UA-67196006-4');
`;
      document.head.appendChild(s);
    };
    document.head.appendChild(script);
  };

  let c = document.cookie.match(/cookie_notice=(\d)/);
  if (!c) document.querySelector('span[data-test-action="dismiss-cookie-notice"]').addEventListener('click', e => add());
  else if (c[1] === "1") add();

  const el = document.querySelector('#cookieNotice');
  setTimeout(_ => el ? el.remove() : null, 60*1000);
})();
