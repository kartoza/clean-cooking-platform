import {init, getDatasets} from '/static/eae/tool/summary_report_page.js';

window.getDatasets = getDatasets;

document.addEventListener("DOMContentLoaded", function(event) {
    init();
});
