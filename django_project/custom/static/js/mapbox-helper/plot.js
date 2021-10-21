NORM_STOPS = d3.range(0, 1.000000001, 0.25);

function ea_colorscale(opts) {
  let s;

  let {intervals, stops, domain} = opts;
  if (!stops || !stops.length)
    stops = ea_default_colorscale.stops;

  if (!domain) domain = NORM_STOPS;

  if (maybe(intervals, 'length')) {
    s = d3.scaleQuantile()
        .domain(domain = intervals)
        .range(stops);
  } else {
    s = d3.scaleLinear()
        .domain(d3.range(domain.min, domain.max + 0.0000001, (domain.max - domain.min) / (stops.length - 1)))
        .range(stops)
        .clamp(true);
  }

  function color_steps(steps, height) {
    const h = height || 5;

    const svg = d3.create("svg")
        .attr('class', 'svg-interval');

    const g = svg.append('g');

    steps.forEach((v, i) => {
      g.append('rect')
          .attr('fill', v)
          .attr('stroke', 'none')
          .attr('x', `${(100 / steps.length) * i}%`)
          .attr('width', `${100 / steps.length}%`)
          .attr('height', h);
    });

    svg
        .attr('width', "100%")
        .attr('height', h);

    return svg.node();
  }

  function rgba(str) {
    let c;

    if (!str) return [0, 0, 0, 255];

    if (str.match(/^#([A-Fa-f0-9]{3}){1,2}$/)) {
      c = str.substring(1).split('');

      if (c.length === 3) c = [c[0], c[0], c[1], c[1], c[2], c[2]];

      c = '0x' + c.join('');

      return [(c >> 16) & 255, (c >> 8) & 255, c & 255, 255];
    } else if ((c = str.match(/^rgba?\(([0-9]{1,3}), ?([0-9]{1,3}), ?([0-9]{1,3}),? ?([0-9]{1,3})?\)$/))) {
      return [+c[1], +c[2], +c[3], +c[4] || 255];
    } else
      throw new Error(`rgba: argument ${str} doesn't match`);
  };

  return {
    domain: domain,
    fn: x => rgba(s(x)),
    stops: stops,
    intervals: intervals,
    svg: color_steps(stops)
  };
}

const ea_default_colorscale = ea_colorscale({
	stops: d3.schemeRdBu[5].reverse(),
	domain: { min: 0, max: 1 },
});

function drawcanvas(opts) {
  const {canvas, data, width, height, nodata, colorscale} = opts;
  const ctx = canvas.getContext("2d");
  const imagedata = ctx.createImageData(width, height);
  const imgd = imagedata.data;

  canvas.width = width;
  canvas.height = height;

  let i, p;
  for (i = p = 0; i < data.length; i += 1, p += 4) {
    if (isNaN(data[i])) {
      continue;
    }
    if (data[i] === nodata) continue;

    const c = colorscale.fn(data[i]);

    if (!c) continue;

    imgd[p] = c[0];
    imgd[p + 1] = c[1];
    imgd[p + 2] = c[2];
    imgd[p + 3] = 255;
  }

  ctx.putImageData(imagedata, 0, 0);

  return canvas;
};

/*
 * outputcanvas
 *
 * @param "raster" []numbers
 * @param "canvas" a canvas element (if null, will default to canvas#output)
 */

function outputcanvas(data, canvas = null) {
  const A = DST.get('boundaries');

  if (!data.length) {
    console.warn("plot.outputcanvas: no raster given. Filling up with a blank (transparent) one...");
    data = new Float32Array(A.raster.data.length).fill(-1);
  }
  ;

  drawcanvas({
    canvas: canvas || qs('canvas#output'),
    data: data,
    width: A.raster.width,
    height: A.raster.height,
    nodata: -1,
    colorscale: ea_analysis_colorscale,
  });
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

