function _request(method, url, data=null) {
    return new Promise(function (resolve, reject) {
        let xhr = new XMLHttpRequest();
        xhr.open(method, url);
        xhr.onload = function () {
            if (this.status >= 200 && this.status < 300) {
                resolve({
                    status: this.status,
                    response: xhr.response
                });
            } else {
                reject({
                    status: this.status,
                    statusText: xhr.statusText
                });
            }
        };
        xhr.onerror = function () {
            reject({
                status: this.status,
                statusText: xhr.statusText
            });
        };
        if (data) {
            xhr.send(data);
        } else {
            xhr.send();
        }
    });
}

function _get(url) {
    return _request('GET', url)
}

export async function api_post(url, post_data) {
    return await _request('POST', url, post_data);
}


export default async function api_get(url) {
    const response = await _get(url)
    return JSON.parse(response.response)
}