import Footer from '/static/footer.js';
import {modals, spawnModal} from '/static/modal.js';
import {emoji} from '/static/symbols.js';
import {getUseWatermark} from '/static/cookies.js';
import {base64Decode} from '/static/base64.js';

const e = React.createElement;
const container = document.querySelector('#container');

let layerBoxes = [];
const checkTable = {};
let layerOrderManagement = [];
let checkboxCache = null;

class MainContent extends React.Component {
    render() {
        return e('div', {className: 'primary-shaft app', id: 'primary-shaft'},
            e('h1', {className: 'tool-page-title'}, 'Realmerge Multi'),
            e('div', {className: 'box'},
                e('input', {
                    className: 'horse-url',
                    id: 'horse-url',
                    placeholder: 'https://horsereality.com/horses/...',
                    required: true
                }),
                e('button', {onClick: () => {getLayers()}}, `${emoji.horse} Add`),
                e('div', {className: 'options-container'},
                    e('h3', null, 'Options'),
                    e(
                        'label', null,
                        e('input', {id: 'use-foal', defaultChecked: false, type: 'checkbox'}),
                        'Use foal instead of mare'
                    )
                )
            ),
            e('div', {className: 'box-holder', id: 'columns-container'}),
            e('div', {className: 'box', id: 'preview-container', style: {display: 'none'}}),
            e('div', {className: 'box', id: 'result-container', style: {display: 'none'}}),
            e(Footer, {page: 'multi', settingsModal: modals.settings, creditsModal: modals.credits})
        )
    }
}

class HorseResult extends React.Component {
    render() {
        return e(
            'div', {className: 'box results', style: {width: '100%', padding: '0'}},
            e('h1', null, this.props.title || 'Result'),
            e('img', {src: this.props.url})
        )
    }
}

class CheckBox extends React.Component {
    constructor(props) {
        super(props);
        this.state = {checked: props.enabled || false};
        checkTable[this.props.key_id] = props.enabled || false;
        if (props.enabled) layerOrderManagement.push(this.props.key_id);
    }

    toggle() {
        const key_id = this.props.key_id;
        checkTable[key_id] = !this.state.checked;
        if (!this.state.checked == true) {
            layerOrderManagement.push(key_id);
        } else {
            layerOrderManagement = layerOrderManagement.filter(function (item) {return item != key_id});
        }
        this.setState({checked: !this.state.checked});
    }

    componentDidUpdate() {
        updatePreview(this.state.checked, this.props.large_url);
    }

    render() {
        return e(
            'input', {
                id: this.props.key_id,
                type: 'checkbox',
                className: 'check-horse-input',
                defaultChecked: this.state.checked,
                onClick: () => {this.toggle()}
            }
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
        const holder = document.querySelector('#columns-container');
        layerBoxes = layerBoxes.filter(function (item) {return item.props.id != id});
        const fragment = e(React.Fragment, {children: layerBoxes});
        ReactDOM.render(fragment, holder);
        // purge from cache
        usedIds = usedIds.filter(function (item) {return item != id})
    }

    render() {
        this.checkboxes = [];
        for (const obj of this.props.layers) {
            const checkbox = e(CheckBox, obj);
            this.checkboxes.push(checkbox);
            this.checkboxes.push(e('label', {htmlFor: obj.key_id}, e('img', {src: obj.small_url, className: 'check-horse'})));
            this.checkboxes.push(e('br'));
        }
        checkboxCache = this.checkboxes;
        let sourceSpan = null;
        if (typeof this.props.source != 'undefined') {
            sourceSpan = e(
                'span', {className: 'source'}, `(from ${this.props.source})`
            )
        }
        return e('div', null,
            e('div', {className: 'preview-titlebar'},
                e('a', 
                    {
                        href: `https://www.horsereality.com/horses/${this.props.id}/`,
                        target: '_blank'
                    },
                    e('h2', null, this.props.name)
                ),
                e('img', 
                    {
                        src: '/static/icons/close_white.svg',
                        onClick: () => {this.close(this.props.id)}
                    }
                ),
                sourceSpan
            ),
            e('div', {className: 'box layer-column', key: this.props.id}, this.checkboxes)
        );
    }
}

const previewTitlebar = e('div', {className: 'preview-titlebar'},
    e('h1', {}, 'Preview'),
    e('button', {onClick: () => merge()}, 'Generate'),
    e('button', {id: 'share-button', onClick: () => {sharePage()}, style: {marginLeft: '0'}}, 'Share')
);
let usedIds = [];
let previewImages = [];

function changePreviewHeight() {
    const previewContainer = document.querySelector('#preview-container');
    const bottomLayer = previewContainer.children[1];
    if (!bottomLayer) {return};
    previewContainer.style.height = bottomLayer.height + 47 + 'px';  // adding 47 for some pseudo-padding
    for (const layer of [...previewContainer.children].slice(2)) {
        layer.style.height = bottomLayer.height + 'px';
        layer.style.width = bottomLayer.width + 'px';
    }
}
window.onresize = changePreviewHeight;

function updatePreview(checked, largeImgUrl) {
    const preview_holder = document.querySelector('#preview-container');
    if (checked == true) {
        previewImages.push(largeImgUrl);
    } else if (checked == false) {
        previewImages = previewImages.filter(function (item) {return item != largeImgUrl})
    } else {
        return
    }
    const imageElements = [];
    for (const url of previewImages) {
        imageElements.push(e('img', {src: url, onLoad: () => changePreviewHeight()}))
    }
    const fragment = e(React.Fragment, {children: [previewTitlebar].concat(imageElements)});
    ReactDOM.render(fragment, preview_holder);

    if (previewImages.length < 1) {
        preview_holder.style.display = 'none';
    } else {
        preview_holder.style.display = 'block';
    }
}

function addBox(data) {
    const holder = document.querySelector('#columns-container');
    const child = e(LayersBox, data);
    layerBoxes.push(child);
    const fragment = e(React.Fragment, {children: layerBoxes})
    ReactDOM.render(fragment, holder);
    return child;
}

async function getLayers() {
    if (layerBoxes.length >= 6) {
        alert('Maximum number of horses per page reached.');
        document.getElementById('horse-url').value = null;
        return
    }
    const horse_url = document.getElementById('horse-url').value;
    document.getElementById('horse-url').value = null;

    if (!horse_url) {
        alert('Input box must not be empty.');
        return
    }

    const response = await fetch('/api/layers', {
        method: 'POST',
        body: JSON.stringify({url: horse_url, use_foal: document.querySelector('#use-foal').checked}),
        headers: {'Content-Type': 'application/json'}
    });
    const data = await response.json();
    if (!response.ok) {
        alert(data.message);
        return
    } else {
        //document.getElementById('error-box').style.display = 'none';
    }
    if (usedIds.indexOf(data.id) >= 0) {
        alert(data.name + ' is already being used on this page.');
        return
    }
    addBox(data);
    usedIds.push(data.id);
}

async function merge() {
    if (previewImages.length < 1) {
        displayError('No layers to merge.');
        return
    } else if (previewImages.length == 1) {
        alert('Only one layer is present.')
        return
    }

    const useWatermark = getUseWatermark();
    const response = await fetch('/api/merge/multiple', {
        method: 'POST',
        body: JSON.stringify({urls: previewImages, watermark: useWatermark}),
        headers: {'Content-Type': 'application/json'}
    });
    const data = await response.json();
    if (!response.ok) {
        displayError(data.message);
        return
    }

    const resultContainer = document.querySelector('#result-container');
    const results = e(HorseResult, data);
    ReactDOM.unmountComponentAtNode(resultContainer);
    ReactDOM.render(results, resultContainer);
    resultContainer.style.display = 'block';
}

function loadMain() {
    ReactDOM.render(e(MainContent), container)
}

async function sharePage() {
    if (!layerBoxes) {
        alert('Nothing to share.');
        return
    }
    const layersData = [];
    for (const obj of layerBoxes) {
        for (const layer of obj.props.layers) {
            layer.enabled = checkTable[layer.key_id] || false;
            if (layerOrderManagement.indexOf(layer.key_id) >= 0) {
                layer.index = layerOrderManagement.indexOf(layer.key_id);
            } else {
                layer.index = null;
            }
        }
        layersData.push(obj.props)
    }
    spawnModal(modals.share);
    const shareUrlContainer = document.querySelector('#share-url-container');
    ReactDOM.unmountComponentAtNode(shareUrlContainer);
    ReactDOM.render(e('p', null, 'Creating share URL...'), shareUrlContainer);

    const response = await fetch('/api/multi-share', {
        method: 'POST',
        body: JSON.stringify({layers_data: layersData}),
        headers: {'Content-Type': 'application/json'}
    });
    const data = await response.json();
    if (!response.ok) {
        shareUrlBox.innerText = data.message;
        return
    }
    const now = new Date().getTime() / 1000;
    const days = ((data.expires - now) / 86400).toPrecision(1);
    ReactDOM.unmountComponentAtNode(shareUrlContainer);
    ReactDOM.render(
        e(React.Fragment, {children: [
            e('p', null, e('a', {id: 'share-url', href: data.url, key: 'share-url'}, data.url)),
            e('p', {key: 'share-url-expires'}, `This link expires in ${days} days.`)
        ]}),
        shareUrlContainer
    )
}

async function loadCheckShare() {
    const queryParams = new URLSearchParams(window.location.search);
    const shareId = queryParams.get('share');
    if (!shareId) return false

    const response = await fetch(`/api/multi-share/${shareId}`, {method: 'GET'});
    const data = await response.json();
    if (!response.ok) {
        alert(data.message);
        return false
    }

    const tempSorting = [];
    for (const layer_data of data) {
        addBox(layer_data);
        usedIds.push(layer_data.id);
        for (const checkbox of checkboxCache) {
            if (checkbox.props.enabled) {
                tempSorting.push(checkbox);
            }
        }
    }
    checkboxCache = null;
    tempSorting.sort((first, second) => {return first.props.index - second.props.index})
    for (const checkbox of tempSorting) {
        updatePreview(checkbox.props.enabled, checkbox.props.large_url);
    }
    return true
}

async function loadCheckShareRaw() {
    const queryParams = new URLSearchParams(window.location.search);
    const shareData = queryParams.get('data');
    if (!shareData) return false

    const layer_data = JSON.parse(base64Decode(shareData));

    addBox(layer_data);
    usedIds.push(layer_data.id);
    const tempSorting = [];
    for (const checkbox of checkboxCache) {
        if (checkbox.props.enabled) {
            tempSorting.push(checkbox);
        }
    }
    checkboxCache = null;
    tempSorting.sort((first, second) => {return first.props.index - second.props.index})
    for (const checkbox of tempSorting) {
        updatePreview(checkbox.props.enabled, checkbox.props.large_url);
    }
    queryParams.delete('data');
    return true
}

loadMain();
loadCheckShare().then((result) => {
    if (result == false) {
        loadCheckShareRaw()
    }
    window.history.pushState({}, document.title, window.location.pathname);
});
