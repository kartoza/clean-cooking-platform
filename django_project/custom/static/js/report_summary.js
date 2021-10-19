function run_analysis() {
    const it = new Float32Array(boundaries.length).fill(-1);
}


function summary() {
}

function downloadMap() {
    run_analysis();
    this.href = map.getCanvas().toDataURL('image/png')
}