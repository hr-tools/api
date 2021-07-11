let layerBoxes = [];
class CheckBox extends React.Component {
    constructor(props) {
        super(props);
        this.state = {checked: false};
    }

    toggle() {
        this.setState({checked: !this.state.checked});
    }

    componentDidUpdate() {
        updatePreview(this.state.checked, this.props.large_url);
    }

    render() {
        return e(
            'input',
            {id: this.props.key_id, type: 'checkbox', defaultChecked: this.state.checked, onClick: () => this.toggle()}
        )
    }
}
class LayersBox extends React.Component {
    constructor(props) {
        super(props);
        this.checkboxes = [];
    }

    close(id) {
        // uncheck boxes
        for (const obj of this.props.layers) {
            updatePreview(false, obj.large_url)
        }
        // remove display
        const holder = document.querySelector('#box-holder');
        layerBoxes = layerBoxes.filter(function (item) {return item.props.id != id});
        const fragment = e(React.Fragment, {children: layerBoxes});
        ReactDOM.render(fragment, holder);
        // purge from cache
        usedIds = usedIds.filter(function (item) {return item != id})
    }

    render() {
        for (const obj of this.props.layers) {
            const checkbox = e(CheckBox, obj);
            this.checkboxes.push(checkbox);
            this.checkboxes.push(e('label', {htmlFor: obj.key_id}, e('img', {src: obj.small_url, className: 'check-horse'})));
            this.checkboxes.push(e('br'));
        }
        return e(
            'div',
            {className: 'box layer-column', key: this.props.id},
            e('div', {className: 'preview-titlebar'},
                e('h3', {}, this.props.name),
                e('button', {onClick: () => this.close(this.props.id)}, 'Close')
            ),
            this.checkboxes
        );
    }
}
const previewTitlebar = e('div', {className: 'preview-titlebar'},
    e('h3', {}, 'Preview'),
    e('button', {onClick: () => mergeImage()}, 'Generate'),
    //e('button', {onClick: () => sharePage()}, 'Share')  // soon!
);
let usedIds = [];
let previewImages = [];

function displayError(message) {
    document.getElementById('error-message').innerText = message;
    document.getElementById('error-box').style.display = 'block';
    document.getElementById('merged-image-box').style.display = 'none';
}

function updatePreview(checked, largeImgUrl) {
    const preview_holder = document.querySelector('#preview-box');
    if (checked == true) {
        previewImages.push(largeImgUrl);
    } else if (checked == false) {
        previewImages = previewImages.filter(function (item) {return item != largeImgUrl})
    } else {
        return
    }
    const imageElements = [];
    for (const url of previewImages) {
        imageElements.push(e('img', {src: url}))
    }
    const fragment = e(React.Fragment, {children: [previewTitlebar].concat(imageElements)});
    ReactDOM.render(fragment, preview_holder);

    if (previewImages.length < 1) {
        preview_holder.style.display = 'none';
    } else {
        preview_holder.style.display = 'block';
    }
    setTimeout(()=>{changePreviewHeight()}, 60)
}

function addBox(data) {
    const holder = document.querySelector('#box-holder');
    const child = e(LayersBox, data);
    layerBoxes.push(child);
    const fragment = e(React.Fragment, {children: layerBoxes})
    ReactDOM.render(fragment, holder);
}

async function getLayers() {
    if (layerBoxes.length >= 6) {
        displayError('Maximum number of horses per page reached.');
        document.getElementById('horseurl').value = null;
        return
    }
    const horseurl = document.getElementById('horseurl').value;
    document.getElementById('horseurl').value = null;

    if (!horseurl) {
        displayError('Input box must not be empty.');
        return
    }

    const response = await fetch('/api/layers', {
        method: 'POST',
        body: JSON.stringify({url: horseurl, use_foal: document.getElementById('use-foal').state}),
        headers: {'Content-Type': 'application/json'}
    });
    const data = await response.json();
    if (!response.ok) {
        displayError(data.message);
        return
    } else {
        document.getElementById('error-box').style.display = 'none';
    }
    if (usedIds.indexOf(data.id) >= 0) {
        displayError(data.name + ' is already being used on this page.');
        return
    }
    addBox(data);
    usedIds.push(data.id)
}

function showMerged(url) {
    document.getElementById('merged-image-title').innerText = 'Merged Image'
    document.getElementById('merged-image').src = url;
    document.getElementById('merged-image-box').style.display = 'block';
}

async function mergeImage() {
    document.getElementById('merged-image-title').innerText = 'Processing...';
    document.getElementById('merged-image').src = '';

    if (previewImages.length < 1) {
        displayError('No layers to merge.');
        return
    } else if (previewImages.length == 1) {
        showMerged(previewImages[0]);
        return
    }

    document.getElementById('merged-image-title').innerText = 'Merging...';
    document.getElementById('merged-image-box').style.display = 'block';

    const response = await fetch('/api/merge/multiple', {
        method: 'POST',
        body: JSON.stringify({urls: previewImages, watermark: useWatermark}),
        headers: {'Content-Type': 'application/json'}
    });
    const data = await response.json();
    if (!response.ok) {
        displayError(data.message);
        return
    } else {
        document.getElementById('error-box').style.display = 'none';
    }
    showMerged(data.url);
}
