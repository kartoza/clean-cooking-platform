let selectedGeo = null;
let href = '';
let rasterGenerated = false;

const getSubregionPropertyList = (geoId, selector) => {
  let url = `/api/subregion-list/${geoId}/${selector}/`;
  return new Promise((resolve, reject) => fetch(url).then(response => response.json()).then(
      data => resolve(data)
  ).catch((error) => reject(error)))
}

(function () {
  const countrySelect = document.getElementById('countrySelect');
  const subregionSelect = document.getElementById('subregionSelect');
  const discoverBtn = document.getElementById('btn-discover');
  const subregionPropertySelect = document.getElementById('subregionPropertySelect');
  const statusBtn = document.getElementById('btn-status');
  const loadingSpinner1 = document.getElementById('loading-spinner-1');

  const generateRasterMask = () => {
    let url = '/api/geography-raster-mask/';
    const geoId = selectedGeo.value;
    const subRegionSelector = selectedGeo.dataset[subregionSelect.value];
    const subRegionValue = subregionPropertySelect.value;
    return new Promise( (resolve, reject) => fetch(url, {
        method: 'POST',
        credentials: "same-origin",
        headers: {
          'X-CSRFToken': getCookie("csrftoken"),
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          geo_id: parseInt(geoId),
          subregion_selector: subRegionSelector,
          subregion_value: subRegionValue
        })
      }).then((response) => response.json()).then(data => {
        resolve(data)
      }).catch((error) => reject(error)));
  }

  countrySelect.onchange = (e) => {
    if (e.target.value !== '-') {
      selectedGeo = e.target.options[e.target.selectedIndex];
      discoverBtn.disabled = false;
      statusBtn.querySelector('.text').innerHTML = 'Downloading Country Boundary Layer';
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

  subregionSelect.onchange = (e) => {
    const selectedSubRegion = e.target.options[e.target.selectedIndex];
    if (!selectedGeo) return false;

    const subRegionSelector = selectedGeo.dataset[selectedSubRegion.value];
    statusBtn.querySelector('.text').innerHTML = 'Generate Sub Region Boundary';
    statusBtn.disabled = false;

    let loadingOption = document.createElement('option');
    subregionPropertySelect.innerHTML = '';
    loadingOption.innerHTML = 'loading...';
    subregionPropertySelect.appendChild(loadingOption);
    subregionPropertySelect.disabled = true;

    getSubregionPropertyList(selectedGeo.value, subRegionSelector).then(
        data => {
          const subregionListData = data.subregion_list;
          subregionPropertySelect.innerHTML = '';
          subregionPropertySelect.disabled = false;
          if (subregionListData) {
            for (let i = 0; i < subregionListData.length; i++) {
              let opt = document.createElement('option');
              opt.value = subregionListData[i];
              opt.innerHTML = subregionListData[i];
              subregionPropertySelect.appendChild(opt);
            }
          }
        }
    ).catch(
        error => {
          console.error(error)
          subregionPropertySelect.innerHTML = "";
          subregionPropertySelect.disabled = false;
        }
    )
  }

  discoverBtn.onclick = (e) => {
    e.preventDefault();
    const geoId = selectedGeo.value;
    const subRegionSelector = selectedGeo.dataset[subregionSelect.value];
    const subRegionValue = subregionPropertySelect.value;
    const loading = document.getElementById('loading-spinner');
    loading.style.display = "block";
    discoverBtn.querySelector('.text').innerHTML = 'Generating raster';
    discoverBtn.disabled = true;
    if (!rasterGenerated && subRegionValue) {
      generateRasterMask().then(data => {
         const boundaryUUID = data.File.replace('.tif', '');
         window.location.href = `/use-case/?boundary=${boundaryUUID}&geoId=${geoId}&subRegion=${subRegionSelector}:${subRegionValue}`;
      })
    } else {
      window.location.href = href;
    }
  }

  statusBtn.onclick = (e) => {
    e.preventDefault();
    const geoId = selectedGeo.value;
    const subRegionSelector = selectedGeo.dataset[subregionSelect.value];
    const subRegionValue = subregionPropertySelect.value;
    loadingSpinner1.style.display = "block";
    statusBtn.querySelector('.text').innerHTML = 'Generating raster';
    statusBtn.disabled = true;
    generateRasterMask().then(data => {
      const boundaryUUID = data.File.replace('.tif', '');
      href = `/use-case/?boundary=${boundaryUUID}&geoId=${geoId}&subRegion=${subRegionSelector}:${subRegionValue}`;
      showGeoJSONLayer(data.RasterPath.replace('.tif', '.json'), true, 'subregion');
      loadingSpinner1.style.display = "none";
      statusBtn.querySelector('.text').innerHTML = 'Generate Sub Region Boundary';
      statusBtn.disabled = false;
      rasterGenerated = true;
    }).catch(error => {
      alert("Unable to generate raster, please choose other subregion...")
      statusBtn.querySelector('.text').innerHTML = 'Generate Sub Region Boundary';
      loadingSpinner1.style.display = "none";
      statusBtn.disabled = false;
      rasterGenerated = false;
    })
  }
})();
