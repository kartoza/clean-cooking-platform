let selectedGeo = null;

const getSubregionPropertyList = (geoId, selector) => {
  let url = `/api/subregion-list/${geoId}/${selector}/`;
  return new Promise((resolve, reject) => fetch(url).then(response => response.json()).then(
      data => resolve(data)
  ).catch((error) => reject(error)))
}

(function () {
  document.getElementById('countrySelect').onchange = (e) => {
    const subregionSelect = document.getElementById('subregionSelect');
    const discoverBtn = document.getElementById('btn-discover');
    if (e.target.value !== '-') {
      selectedGeo = e.target.options[e.target.selectedIndex];
      discoverBtn.disabled = false;
    } else {
      selectedGeo = null;
      discoverBtn.disabled = true;
      subregionSelect.value = '-';
      document.getElementById('subregionPropertySelect').innerHTML = "";
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

  document.getElementById('subregionSelect').onchange = (e) => {
    const selectedSubRegion = e.target.options[e.target.selectedIndex];
    if (!selectedGeo) return false;

    const subRegionSelector = selectedGeo.dataset[selectedSubRegion.value];
    const subregionPropertySelect = document.getElementById('subregionPropertySelect');

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
})();
