import Footer from '/static/footer.js';
import {modals} from '/static/modal.js';
import {emoji} from '/static/symbols.js';
import {getUseWatermark} from '/static/cookies.js';
import {basicShare} from '/static/share.js';

const e = React.createElement;
const container = document.querySelector('#container');

class MainContent extends React.Component {
    render() {
        return e('div', {className: 'primary-shaft app', id: 'primary-shaft'},
            e('h1', {className: 'tool-page-title'}, 'Realmerge'),
            e(
                'a', {href: '/merge/multi'},
                e(
                    'button', {className: 'secondary', style: {
                        float: 'right',
                        marginTop: '-60px',
                        marginRight: '0px',
                        borderRadius: '10px',
                    }},
                    `${emoji.palette} Multi Mode`
                )
            ),
            e('div', {className: 'box'},
                e('input', {
                    className: 'horse-url',
                    id: 'horse-url',
                    placeholder: 'https://horsereality.com/horses/...',
                    required: true
                }),
                e('button', {onClick: () => {merge()}}, `${emoji.horse} Generate`),
                e('div', {className: 'options-container'},
                    e('h3', null, 'Options'),
                    e(
                        'label', null,
                        e('input', {id: 'remove-whites', defaultChecked: false, type: 'checkbox'}),
                        'Remove white layers'
                    )
                )
            ),
            e('div', {id: 'result-container'}),
            e(Footer, {page: 'merge', settingsModal: modals.settings, creditsModal: modals.credits})
        )
    }
}

class HorseResults extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        const results = [];
        if (this.props.horse_url) {
            results.push(e(
                'div', {className: 'box results', style: {width: '100%', marginRight: (this.props.foal_url ? '20px' : '0')}},
                e('div', {className: 'preview-titlebar'},
                    e('a', {href: `https://www.horsereality.${this.props.tld}/horses/${this.props.horse_id}/`}, e('h1', null, this.props.name)),
                    e('button',
                        {style: {marginLeft: '15px'}, onClick: () => {basicShare(this.props.horse_id, this.props.tld, 'merge')}},
                        'Share'
                    )
                ),
                e('img', {src: this.props.horse_url})
            ))
        }
        if (this.props.foal_url) {
            results.push(e(
                'div', {className: 'box results', style: {marginLeft: 'auto', marginTop: '0'}},
                e('h1', null, 'Foal'),
                e('img', {src: this.props.foal_url})
            ))
        }

        return e(React.Fragment, {children: results})
    }
}

async function merge() {
    const horse_url_input = document.querySelector('#horse-url');
    const horse_url = horse_url_input.value;
    if (!horse_url) {
        alert('Input box must not be empty.')
        return
    }
    horse_url_input.value = null;

    // fetch merged image
    const useWatermark = getUseWatermark();
    const removeWhites = document.querySelector('#remove-whites').checked;
    const response = await fetch('/api/merge', {
        method: 'POST',
        body: JSON.stringify({url: horse_url, watermark: useWatermark, use_whites: !removeWhites}),
        headers: {'Content-Type': 'application/json'}
    });
    const data = await response.json();
    if (!response.ok) {
        alert(data.message);
        return
    }

    // display the horse
    const resultContainer = document.querySelector('#result-container');
    const results = e(HorseResults, data);
    ReactDOM.unmountComponentAtNode(resultContainer);
    ReactDOM.render(results, resultContainer);
}

function loadMain() {
    ReactDOM.render(e(MainContent), container)
}

async function loadCheckShare() {
    const queryParams = new URLSearchParams(window.location.search);
    const shareId = queryParams.get('share');
    const tld = queryParams.get('tld');
    if (!shareId) return false
    if (['com', 'nl'].indexOf(tld) == -1) return false

    const url = `https://www.horsereality.${tld}/horses/${shareId}/`
    document.querySelector('#horse-url').value = url;
    await merge()
}

loadMain();
loadCheckShare();
