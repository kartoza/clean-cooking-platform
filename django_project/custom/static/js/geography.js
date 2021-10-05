let selectedGeo = null;

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

  countrySelect.onchange = (e) => {
    if (e.target.value !== '-') {
      selectedGeo = e.target.options[e.target.selectedIndex];
      discoverBtn.disabled = false;
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
      window.location.href = '/presets/?boundary=' + boundaryUUID;
    });
  }
})();
