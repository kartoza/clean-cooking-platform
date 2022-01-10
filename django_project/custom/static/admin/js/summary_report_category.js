
$(document).ready(function(){
  const $analysisDropdown = $('#id_analysis');
  const $vectorLayer = $('.vector_layer');
  const $supplyLayer = $('.supply_layer');

  $vectorLayer.hide();
  $supplyLayer.hide();

  $analysisDropdown.change(e => {
    let selectedAnalysis = e.target.value;
    if (selectedAnalysis === 'supply' || selectedAnalysis === 'ccp') {
      $vectorLayer.show();
    } else {
      $vectorLayer.hide();
    }

    if (selectedAnalysis === 'ani') {
      $supplyLayer.show();
    } else {
      $supplyLayer.hide();
    }
  })

  $analysisDropdown.change();
})