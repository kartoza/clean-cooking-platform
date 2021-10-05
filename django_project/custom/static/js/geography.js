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

  countrySelect.onchange = (e) => {
    if (e.target.value !== '-') {
      selectedGeo = e.target.options[e.target.selectedIndex];
      discoverBtn.disabled = false;
      statusBtn.querySelector('.text').innerHTML = 'Downloading Country Boundary Layer';
      loadingSpinner1.style.display = "block";
      href = `/use-case/?geoId=${selectedGeo.value}&subRegion=Country:All`;
      showGeoJSONLayer('/proxy_cca/' + selectedGeo.dataset.geojson);
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

    getSubregionPropertyList(selectedGeo.value, subRegionSelector).then(
        data => {
          const subregionListData = data.subregion_list;
          subregionPropertySelect.innerHTML = "";
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
        error => console.error(error)
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
      fetch('/api/geography-raster-mask/', {
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
        const boundaryUUID = data.File;
        window.location.href = `/use-case/?boundary=${boundaryUUID}&geoId=${geoId}&subRegion=${subRegionSelector}:${subRegionValue}`;
      });
    } else {
      window.location.href = href;
    }
  }

  statusBtn.onclick = (e) => {
    const geoId = selectedGeo.value;
    const subRegionSelector = selectedGeo.dataset[subregionSelect.value];
    const subRegionValue = subregionPropertySelect.value;
    loadingSpinner1.style.display = "block";
    statusBtn.querySelector('.text').innerHTML = 'Generating raster';
    statusBtn.disabled = true;
    fetch('/api/geography-raster-mask/', {
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
      const boundaryUUID = data.File;
      href = `/use-case/?boundary=${boundaryUUID}&geoId=${geoId}&subRegion=${subRegionSelector}:${subRegionValue}`;
      showGeoTiffLayer(data.RasterPath);
      loadingSpinner1.style.display = "none";
      statusBtn.querySelector('.text').innerHTML = 'Generate Sub Region Boundary';
      statusBtn.disabled = false;
      rasterGenerated = true;
    });
  }
})();
