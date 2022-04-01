let href = '';
let boundaryUUID = '';
let allLayerIds = null;
let rasterGenerated = false;
const countrySelect = document.getElementById('countrySelect');
const provinceSelect = document.getElementById('provinceSelect');
const districtSelect = document.getElementById('districtSelect');
const municipalSelect = document.getElementById('municipalSelect');
const subregionSelect = document.getElementById('subregionSelect');
const discoverBtn = document.getElementById('btn-discover');
const subregionPropertySelect = document.getElementById('subregionPropertySelect');
const exploreBtn = document.getElementById('btn-explorer');
const loadingSpinner1 = document.getElementById('loading-spinner-1');
let provinceLayer = '';
let districtLayer = '';
let municipalLayer = '';
let currentSubregionValue = '';
let currentSubregionSelector = '';

const selectCountry = (countryData) => {
  discoverBtn.disabled = false;
  //statusBtn.querySelector('.text').innerHTML = 'Downloading Country Boundary Layer';
  loadingSpinner1.style.display = "block";
  href = `/use-case/?geoId=${countryData.value}&subRegion=Country:All`;
  showTileLayer(countryData.dataset.layerName);
  zoomToBoundingBox(countryData.dataset.bbox);
  const subregion = subregionSelect.options;
  for (let index = 1; index < subregion.length + 1; index++) {
    try {
        if (selectedGeo) {
          subregion[index].disabled = selectedGeo.dataset[subregion[index].value] == '';
        } else {
          subregion[index].disabled = true;
        }
    } catch (e) {
    }
  }
}

const clipSelectedLayerPromise = (boundary, layerId) => {
  return new Promise((resolve, reject) => {
    const url = '/api/clip-layer-by-region/';
    fetch(url, {
      method: 'POST',
      credentials: "same-origin",
      headers: {
        'X-CSRFToken': csrfToken,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        boundary: boundary,
        layer_id: layerId
      })
    }).then((response) => response.json()).then(async data => {
      if (data['status'] === 'pending') {
        await delay(2);
        if (currentTry === 100) {
            reject('Error clipping layer ' + layerId)
        } else {
            resolve(clipSelectedLayerPromise(boundary, layerId, drawToMap, currentTry+=1));
        }
      } else if (data['status'] === 'success') {
        const output = data.output;
        resolve("FINISH")
      } else {
        reject('Error clipping layer')
      }
    }).catch((error) => reject(error))
  })
}

(function () {

  const clearAndDisableSelect = (element) => {
    element.innerHTML = '';
    let opt = document.createElement('option');
    opt.value = 'All';
    opt.innerHTML = 'All';
    element.appendChild(opt);
    element.disabled = true;
  }

  const generateRasterMask = (subRegionSelector = '', subRegionValue = '') => {
    let url = '/api/geography-raster-mask/';
    const geoId = selectedGeo.value;
    if (!subRegionSelector) {
      subRegionSelector = selectedGeo.dataset[subregionSelect.value];
    }
    if (!subRegionValue) {
      subRegionValue = subregionPropertySelect.value;
    }

    currentSubregionValue = subRegionValue;
    currentSubregionSelector = subRegionSelector;

    loadingSpinner1.style.display = "block";
    discoverBtn.disabled = true;
    exploreBtn.disabled = true;

    return new Promise( (resolve, reject) => fetch(url, {
        method: 'POST',
        credentials: "same-origin",
        headers: {
          'X-CSRFToken': csrfToken,
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          geo_id: parseInt(geoId),
          subregion_selector: subRegionSelector,
          subregion_value: subRegionValue
        })
      }).then((response) => response.json()).then(async data => {
        allLayerIds = data.AllLayerIds;
        boundaryUUID = data.File.replace('.tif', '');
        href = `/use-case/?boundary=${boundaryUUID}&geoId=${geoId}&subRegion=${subRegionSelector}:${subRegionValue}`;
        await showGeoJSONLayer(data.RasterPath.replace('.tif', '.json'), true, 'subregion');
        rasterGenerated = true;
        discoverBtn.disabled = false;
        exploreBtn.disabled = false;
        loadingSpinner1.style.display = "none";
        resolve(data)
      }).catch((error) => {
        alert("Unable to generate raster, please choose other subregion...")
        console.error(error)
        //statusBtn.disabled = false;
        rasterGenerated = false;
        loadingSpinner1.style.display = "none";
        reject(error)
    }));
  }

  const getSubregionPropertyList = (geoId, selector, selectorValue = '') => {
    let url = `/api/subregion-list/${geoId}/${selector}/`;
    if (selectorValue) {
      url += `${selectorValue}/`;
    }
    return new Promise((resolve, reject) => fetch(url).then(response => response.json()).then(
        data => resolve(data)
    ).catch((error) => reject(error)))
  }

  const fetchSubregionData = (selectorType, selectorElement, selectorValue = '') => {
    getSubregionPropertyList(selectedGeo.value, selectorType, selectorValue).then(
        data => {
          // loadingSpinner1.style.display = "none";
          const subregionListData = data.subregion_list;
          if (subregionListData) {
            clearAndDisableSelect(selectorElement);
            selectorElement.disabled = false;
            for (let i = 0; i < subregionListData.length; i++) {
              let opt = document.createElement('option');
              opt.value = subregionListData[i];
              opt.innerHTML = subregionListData[i];
              selectorElement.appendChild(opt);
            }
          }
        }
    ).catch(
        error => {
          loadingSpinner1.style.display = "none";
          console.error(error)
        }
    )
  }

  const getAllProvinces = () => {
    fetchSubregionData(selectedGeo.dataset.province, provinceSelect);
  }

  provinceSelect.onchange = (e) => {
    let provinceValue = e.target.value;
    clearAndDisableSelect(municipalSelect);
    if (provinceValue === 'All') {
      clearAndDisableSelect(districtSelect);
      MAPBOX.removeLayer('subregion-layer');
      MAPBOX.removeSource('subregion-source');
      zoomToBoundingBox(selectedGeo.dataset.bbox);
    } else {
      generateRasterMask(selectedGeo.dataset.province, provinceValue).then(data => {
        provinceLayer = data.RasterPath.replace('.tif', '.json');
        fetchSubregionData(selectedGeo.dataset.province, districtSelect, provinceValue);
      })
    }
  }

  districtSelect.onchange = (e) => {
    let districtValue = e.target.value;
    if (districtValue === 'All') {
      clearAndDisableSelect(municipalSelect);
      currentSubregionSelector = selectedGeo.dataset.province;
      currentSubregionValue = provinceSelect.value;
      showGeoJSONLayer(provinceLayer, true, 'subregion');
    } else {
      generateRasterMask(selectedGeo.dataset.district, districtValue).then(data => {
        districtLayer = data.RasterPath.replace('.tif', '.json');
        fetchSubregionData(selectedGeo.dataset.district, municipalSelect, districtValue);
      })
    }
  }

  municipalSelect.onchange = (e) => {
    let municipalValue = e.target.value;
    if (municipalValue === 'All') {
      currentSubregionSelector = selectedGeo.dataset.district;
      currentSubregionValue = districtSelect.value;
      showGeoJSONLayer(districtLayer, true, 'subregion');
    } else {
      generateRasterMask(selectedGeo.dataset.municipal, municipalValue);
    }
  }

  setTimeout(() => {
    if (countrySelect) {
      countrySelect.selectedIndex = 0;
    }
    if (provinceSelect) {
      provinceSelect.selectedIndex = 0;
    }
    // Get all provinces
    getAllProvinces();
  }, 100)

  if (countrySelect) {
    countrySelect.onchange = (e) => {
      if (e.target.value !== '-') {
        selectedGeo = e.target.options[e.target.selectedIndex];
        discoverBtn.disabled = false;
        //statusBtn.querySelector('.text').innerHTML = 'Downloading Country Boundary Layer';
        loadingSpinner1.style.display = "block";
        href = `/use-case/?geoId=${selectedGeo.value}&subRegion=Country:All`;
        zoomToBoundingBox(selectedGeo.dataset.bbox);
        showTileLayer(selectedGeo.dataset.layerName);
      } else {
        selectedGeo = null;
        discoverBtn.disabled = true;
        subregionSelect.value = '-';
        subregionPropertySelect.innerHTML = "";
      }
      const subregion = subregionSelect.options;
      for (let index = 1; index < subregion.length + 1; index++) {
        try {
            if (selectedGeo) {
              subregion[index].disabled = selectedGeo.dataset[subregion[index].value] == '';
            } else {
              subregion[index].disabled = true;
            }
        } catch (e) {
        }
      }
    }
  }

  discoverBtn.onclick = (e) => {
    e.preventDefault();
    const geoId = selectedGeo.value;
    if (!rasterGenerated) {
      discoverBtn.querySelector('.text').innerHTML = 'Generating raster';
      discoverBtn.disabled = true;
    } else {
      rasterGenerated = true;
    }
    if (!href) {
      generateRasterMask().then(data => {
         boundaryUUID = data.File.replace('.tif', '');
         window.location.href = `/use-case/?boundary=${boundaryUUID}&geoId=${geoId}&subRegion=${currentSubregionSelector}:${currentSubregionValue}`;
      })
    } else {
      if (currentSubregionSelector &&  currentSubregionValue) {
        window.location.href = `/use-case/?boundary=${boundaryUUID}&geoId=${geoId}&subRegion=${currentSubregionSelector}:${currentSubregionValue}`;
      } else {
        window.location.href = href;
      }
    }
  }

  exploreBtn.onclick = (e) => {
    e.preventDefault();
    const tasks = [];
    const geoId = selectedGeo.value;
    if (!allLayerIds) {
      window.location.href = '/tool/?geoId=' + geoId;
    }
    exploreBtn.querySelector('.text').innerHTML = 'Clipping layers...';
    exploreBtn.disabled = true;
    for (let j = 0; j < allLayerIds.length; j++) {
      tasks.push(clipSelectedLayerPromise(boundaryUUID, allLayerIds[j]));
    }

    Promise.allSettled(tasks).then(function (results) {
      results.forEach((result) => console.log(result))
      exploreBtn.querySelector('.text').innerHTML = 'Go to Explorer Tool';
      exploreBtn.disabled = false;
      window.location.href = '/tool/?boundary=' + boundaryUUID + '&geoId=' + geoId;
    });
  }

})();
