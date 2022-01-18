let href = '';
let boundaryUUID = '';
let allLayerIds = null;
let rasterGenerated = false;
const countrySelect = document.getElementById('countrySelect');
const subregionSelect = document.getElementById('subregionSelect');
const discoverBtn = document.getElementById('btn-discover');
const subregionPropertySelect = document.getElementById('subregionPropertySelect');
const exploreBtn = document.getElementById('btn-explorer');
const loadingSpinner1 = document.getElementById('loading-spinner-1');

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

  const getSubregionPropertyList = (geoId, selector) => {
    let url = `/api/subregion-list/${geoId}/${selector}/`;
    return new Promise((resolve, reject) => fetch(url).then(response => response.json()).then(
        data => resolve(data)
    ).catch((error) => reject(error)))
  }

  setTimeout(() => {
    if (countrySelect) {
      countrySelect.selectedIndex = 0;
    }
    subregionSelect.selectedIndex = 0;
    if (subregionPropertySelect) {
      subregionPropertySelect.selectedIndex = 0;
    }
  }, 100)

  const generateRasterMask = () => {
    let url = '/api/geography-raster-mask/';
    const geoId = selectedGeo.value;
    const subRegionSelector = selectedGeo.dataset[subregionSelect.value];
    const subRegionValue = subregionPropertySelect.value;
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
      }).then((response) => response.json()).then(data => {
        resolve(data)
      }).catch((error) => reject(error)));
  }

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

  subregionSelect.onchange = (e) => {
    const selectedSubRegion = e.target.options[e.target.selectedIndex];
    if (!selectedGeo) return false;

    const subRegionSelector = selectedGeo.dataset[selectedSubRegion.value];

    if (selectedSubRegion.value === '-') {
      let x = document.querySelectorAll(".subregion-elm");
      let i;
      for (i = 0; i < x.length; i++) {
        x[i].style.display = "none";
      }
      return
    } else {
      loadingSpinner1.style.display = "block";
    }

    //statusBtn.querySelector('.text').innerHTML = 'Generate Sub Region Boundary';
    //statusBtn.disabled = false;

    let loadingOption = document.createElement('option');
    subregionPropertySelect.innerHTML = '';
    loadingOption.innerHTML = 'loading...';
    subregionPropertySelect.appendChild(loadingOption);
    subregionPropertySelect.disabled = true;

    getSubregionPropertyList(selectedGeo.value, subRegionSelector).then(
        data => {
          let x = document.querySelectorAll(".subregion-elm");
          let i;
          for (i = 0; i < x.length; i++) {
            x[i].style.display = "flex";
          }
          loadingSpinner1.style.display = "none";
          const subregionListData = data.subregion_list;
          document.getElementById('subregionPropertyLabel').innerHTML = selectedSubRegion.innerHTML;
          subregionPropertySelect.innerHTML = '';
          subregionPropertySelect.disabled = false;
          if (subregionListData) {
            let opt = document.createElement('option');
            opt.value = '-';
            opt.innerHTML = 'All';
            subregionPropertySelect.appendChild(opt);

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
          loadingSpinner1.style.display = "none";
          subregionPropertySelect.innerHTML = "";
          subregionPropertySelect.disabled = false;
        }
    )
  }

  subregionPropertySelect.onchange = (e) => {
    const selectedData = e.target.options[e.target.selectedIndex];
    const geoId = selectedGeo.value;
    const subRegionSelector = selectedGeo.dataset[subregionSelect.value];
    const subRegionValue = subregionPropertySelect.value;
    if (selectedData.value === '-') {
      return false
    }
    loadingSpinner1.style.display = "block";
    generateRasterMask().then(data => {
      allLayerIds = data.AllLayerIds;
      boundaryUUID = data.File.replace('.tif', '');
      href = `/use-case/?boundary=${boundaryUUID}&geoId=${geoId}&subRegion=${subRegionSelector}:${subRegionValue}`;
      showGeoJSONLayer(data.RasterPath.replace('.tif', '.json'), true, 'subregion');
      rasterGenerated = true;
      loadingSpinner1.style.display = "none";
    }).catch(error => {
      alert("Unable to generate raster, please choose other subregion...")
      //statusBtn.disabled = false;
      rasterGenerated = false;
      loadingSpinner1.style.display = "none";
    })
  }

  discoverBtn.onclick = (e) => {
    e.preventDefault();
    const geoId = selectedGeo.value;
    const subRegionSelector = selectedGeo.dataset[subregionSelect.value];
    const subRegionValue = subregionPropertySelect.value;
    if (subRegionSelector && subRegionValue !== '-') {
      discoverBtn.querySelector('.text').innerHTML = 'Generating raster';
      discoverBtn.disabled = true;
    } else {
      rasterGenerated = true;
    }
    if (!rasterGenerated && subRegionValue) {
      generateRasterMask().then(data => {
         boundaryUUID = data.File.replace('.tif', '');
         window.location.href = `/use-case/?boundary=${boundaryUUID}&geoId=${geoId}&subRegion=${subRegionSelector}:${subRegionValue}`;
      })
    } else {
      window.location.href = href;
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
