import run, {raster_to_tiff} from "./analysis";
import analyse from "./summary";
import * as plot from "./plot";
import {api_post} from "./api";
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

function gcd(x, y) {
	if (y === 0) {
		return x
	}
	return gcd(y, x % y);
}

function _calculateRatio(x, y) {
	let gcdValue = gcd(x, y);
	return [x/gcdValue, y/gcdValue];
}


export async function downloadReport(sourceWidth = null, sourceHeight = null, destinationWidth = null, destinationHeight = null) {

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
	} catch (e) {
		await delay(1);
	}

	let mapCanvas = document.getElementsByClassName('mapboxgl-canvas')[0];
	let ratio = null;

	if (destinationWidth !== null && destinationHeight !== null) {
		ratio = _calculateRatio(destinationWidth, destinationHeight)
	}

	let width = sourceWidth || mapCanvas.clientWidth;
	let height = sourceHeight || mapCanvas.clientHeight;

	// Height never changes, so we calculate source size based on height
	if (ratio) {
		width = height / ratio[1] * ratio[0]
	}

	if (!destinationWidth) destinationWidth = width
	if (!destinationHeight) destinationHeight = height

	const canvas = document.getElementById('output-clone');
	const ctx = canvas.getContext("2d");


	canvas.width = destinationWidth;
	canvas.height = destinationHeight;
	// ctx.drawImage(image, sourceX, sourceY, sourceWidth, sourceHeight,
	// destinationX, destinationY, destinationWidth, destinationHeight);
	ctx.drawImage(mapCanvas,
		(mapCanvas.width / 2) - (width / 2), 0,
		width, height,
		0,0,
		destinationWidth, destinationHeight
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

	const api_post_response = await api_post(url, fd);
	if (api_post_response.status === 200) {
		let filename = `${USE_CASE_NAME}-${PRESET_NAME}-${GEO_NAME}.pdf`

		// The actual download
		let blob = new Blob([api_post_response.response], {type: 'application/pdf'});
		let link = document.createElement('a');
		link.href = window.URL.createObjectURL(blob);
		link.download = filename;

		document.body.appendChild(link);

		link.click();

		document.body.removeChild(link);

		button.disabled = false;
		buttonText.innerHTML = 'Clean Cooking Access Report'
	}
}
