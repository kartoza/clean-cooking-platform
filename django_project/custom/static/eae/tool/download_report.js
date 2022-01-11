import run, {raster_to_tiff} from "./analysis";
import analyse from "./summary";
import * as plot from "./plot";
let raster_data = {};

function isCanvasBlank(canvas) {
  return !canvas.getContext('2d')
    .getImageData(0, 0, canvas.width, canvas.height).data
    .some(channel => channel !== 0);
}

async function run_analysis (output, id = "") {
	const key = `${output}${id}`;
	let raster;
	if (raster_data.hasOwnProperty(key) && raster_data[key].length > 0) {
		raster = raster_data[key]
	} else {
		raster = await run(output, true);
		raster_data[key] = raster;
	}
	const data = await analyse(raster);
	plot.outputcanvas(raster, qs(`canvas#${output}-output`));
	return data;
}


export async function downloadReport(mapImageWidth = null, mapImageHeight = null) {

	let buttonText = document.getElementById('report-btn-text');
	let button = document.getElementById('summary-button');

	button.disabled = true;
	buttonText.innerHTML = 'Generating...'

	let url = '/generate-report-pdf/';
	let request = new XMLHttpRequest();
	let fd = new FormData();

	MAPBOX.fitBounds(BBOX, {padding: 100, duration: 0});

	try {
		document.getElementById('view-inputs').click()
		await delay(2);
	} catch (e) {}

	let mapCanvas = document.getElementsByClassName('mapboxgl-canvas')[0];

	let width = mapImageWidth ? mapImageWidth : mapCanvas.clientWidth;
	let height = mapImageHeight ? mapImageHeight : mapCanvas.clientHeight;

	const canvas = document.getElementById('output-clone');
	const ctx = canvas.getContext("2d");

	canvas.width = width;
	canvas.height = height;
	ctx.drawImage(mapCanvas,
		(mapCanvas.width / 2) - (width / 2),0,
		width, height,
		0,0,
		width, height
	);
	let mapImage = canvas.toDataURL('image/png', 1.0);

	try {
		document.getElementById('view-outputs').click()
	} catch (e) {}

	let totalPopulation = null;

	let analysisType = ANALYSIS_TYPE;
	let presetId = PRESET_ID;
	let useCaseId = USE_CASE_ID;

	if (analysisType.includes('ccp') || analysisType.includes('supply_demand')) {
		window.demandData = await run_analysis("demand", presetId);
	}
	if (analysisType.includes('ani')) {
		window.aniData = await run_analysis("ani", presetId);
	}
	if (analysisType.includes('supply') || analysisType.includes('supply_demand')) {
		window.supplyData = await run_analysis("supply", presetId);
	}

	if (window.demandData && !isCanvasBlank(document.getElementById('demand-output'))) {
		let demandImage = document.getElementById('demand-output').toDataURL('image/png', 1.0);
		let demandRaster = await raster_to_tiff('demand', raster_data['demand' + presetId]);
		fd.append('demandImage', demandImage);
		fd.append('demandTiff', new Blob([demandRaster], {
			type: 'application/octet-stream;charset=utf-8' }),
			`demand_${boundary}_${geoId}_${subRegion}.tiff`);
		try {
			fd.append('demandDataHighPercentage', (window.demandData['population-density']['distribution'][4] * 100).toFixed(2))
			totalPopulation = Math.round(window.demandData['population-density']['total']);
		} catch (e) {}
	}

	if (window.supplyData && !isCanvasBlank(document.getElementById('supply-output'))) {
		let supplyImage = document.getElementById('supply-output').toDataURL('image/png', 1.0);
		let supplyRaster = await raster_to_tiff('supply', raster_data['supply' + presetId]);
		fd.append('supplyTiff', new Blob([supplyRaster], {
			type: 'application/octet-stream;charset=utf-8' }),
			`supply_${boundary}_${geoId}_${subRegion}.tiff`);
		fd.append('supplyImage', supplyImage);

		try {
			fd.append('supplyDataHighPercentage', (
				window.supplyData['population-density']['distribution'][4] * 100).toFixed(2))
			if (!totalPopulation) {
				fd.append('totalPopulation', Math.round(window.supplyData['population-density']['total']))
			}
		} catch (e) {}
	}

	if (window.aniData && !isCanvasBlank(document.getElementById('ani-output'))) {
		let aniImage = document.getElementById('ani-output').toDataURL('image/png', 1.0);
		let aniRaster = await raster_to_tiff('ani', raster_data['ani' + presetId]);
		fd.append('aniTiff', new Blob([aniRaster], {
			type: 'application/octet-stream;charset=utf-8' }),
			`ani_${boundary}_${geoId}_${subRegion}.tiff`);
		fd.append('aniImage', aniImage);

		try {
			fd.append('aniDataMedToHigh',
				window.aniData['population-density']['amounts'].slice(-3).reduce((acc, val) => acc + val).toFixed(0))
			if (!totalPopulation) {
				fd.append('totalPopulation', Math.round(window.aniData['population-density']['total']))
			}
		} catch (e) {}
	}


	fd.append('totalPopulation', totalPopulation | 0)
	fd.append('geoId', geoId);
	fd.append('subRegion', subRegion);
	fd.append('mapImage', mapImage);
	fd.append('useCaseId', useCaseId);
	fd.append('scenarioId', presetId);
	fd.append('boundary', boundary);

	request.open('POST', url, true);
	request.setRequestHeader('X-CSRFToken', csrfToken);
	request.responseType = 'blob';

	request.onload = function () {
		// Only handle status code 200
		if (request.status === 200) {

			let filename = `${USE_CASE_NAME}-${PRESET_NAME}-${GEO_NAME}.pdf`

			// The actual download
			let blob = new Blob([request.response], {type: 'application/pdf'});
			let link = document.createElement('a');
			link.href = window.URL.createObjectURL(blob);
			link.download = filename;

			document.body.appendChild(link);

			link.click();

			document.body.removeChild(link);

			button.disabled = false;
			buttonText.innerHTML = 'Clean Cooking Access Report'
		}
	};

	request.send(fd);
}
