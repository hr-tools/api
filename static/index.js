// if someone requests the same URL multiple times, cache the name
// here instead of on the server
const namecache = {};

function displayError(message) {
    document.getElementById('error-message').innerText = message;
    document.getElementById('error-box').style.display = 'block';
    document.getElementById('merged-image-box').style.display = 'none';
    document.getElementById('merged-image-box-foal').style.display = 'none';
}

async function mergeImage() {
    // basic UX in case the request takes a long time
    const horseurl = document.getElementById('horseurl').value;
    document.getElementById('merged-image-title').innerText = 'Processing...';
    document.getElementById('merged-image').src = '';
    document.getElementById('horseurl').value = null;

    if (!horseurl) {
        displayError('Input box must not be empty.');
        return
    }

    document.getElementById('merged-image-box').style.display = 'block';
    document.getElementById('merged-image-box-foal').style.display = 'none';
    document.getElementById('merged-image-title').innerText = 'Merging...';

    const response = await fetch('/api/merge', {
        method: 'POST',
        body: JSON.stringify({url: horseurl, watermark: useWatermark}),
        headers: {'Content-Type': 'application/json'}
    });
    const data = await response.json();
    if (!response.ok) {
        displayError(data.message);
        return
    } else {
        document.getElementById('error-box').style.display = 'none';
        document.getElementById('merged-image-box').style.display = 'block';
        // it might be hidden if the previous
        // request resulted in an error
    }

    if (response.status == 200) {
        // 200 OK is only returned when the image is already merged
        // this could be more clearly indicated but, eh
        // https://github.com/shayypy/realmerge/blob/main/web.py#L192-L197
        if (namecache[data.original_url] & !data.name) {
            data.name = namecache[data.original_url];
        }
    }

    document.getElementById('merged-image').src = data.horse_url;
    if (!data.name) {
        document.getElementById('merged-image-title').innerText = 'Merged Image';
    } else {
        document.getElementById('merged-image-title').innerText = data.name;
        namecache[data.original_url] = data.name
    }
    if (data.foal_url != undefined) {
        document.getElementById('merged-image-foal').src = data.foal_url;
        document.getElementById('merged-image-box-foal').style.display = 'block';
    }
}
