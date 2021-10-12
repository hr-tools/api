import supportText from '/static/support.js';
import {copyright}  from '/static/symbols.js';
import {getUseWatermark, setCookie} from '/static/cookies.js';

const e = React.createElement;

export function spawnModal(modal) {
    const modalContainer = document.querySelector('#modal-container');
    ReactDOM.render(modal, modalContainer)
}

export class Modal extends React.Component {
    render() {
        return e('div', {className: 'modal-background', id: 'modal-background', onClick: (event) => {
            if (event.target.id == 'modal-background') {
                ReactDOM.unmountComponentAtNode(event.target.parentNode)
            }
        }},
            e('div', {className: 'box modal'},
                e('h1', {}, this.props.name),
                ...this.props.children
            )
        )
    }
}

class WatermarkCheckBox extends React.Component {
    constructor(props) {
        super(props);
        this.state = {checked: getUseWatermark()}
    }

    componentDidUpdate() {
        setCookie({name: 'realtools-watermark', value: this.state.checked});
    }

    render() {
        return e(
            'input', {
                type: 'checkbox',
                defaultChecked: this.state.checked,
                onClick: () => {
                    this.setState({checked: !this.state.checked})
                }
            }
        )
    }
}

const settingsModal = e(Modal, {
    name: 'Settings',
    children: [
        //e('h3', null, 'Attribution'),
        e('label', {key: 'settings-watermark'},
            e(WatermarkCheckBox), 'Horse Reality watermark'
        )
    ]
});

const creditsModal = e(Modal, {
    name: 'Credits',
    children: [
        e('p', null, `All horse artwork ${copyright} `, e('a', {href: 'https://www.deloryan.com'}, 'Deloryan B.V.')),
        e('p', null, `Some icons ${copyright} `, e('a', {href: 'https://fonts.google.com/icons?selected=Material+Icons+Outlined'}, 'Google')),
        e('p', null, `Realtools ${copyright} `, e('a', {href: 'https://shay.cat'}, 'shay')),
        e('br'),
        e('p', {dangerouslySetInnerHTML: {__html: supportText}})
    ]
});

function copyTextToClipboard(text) {
    const input = document.createElement("textarea");

    input.value = text;

    input.style.position = "fixed";
    input.style.opacity = "0";

    const root = document.body;
    root.append(input);

    input.focus();
    input.select();

    document.execCommand("copy");
  
    input.remove();
}

const shareModal = e(Modal, {
    name: 'Share',
    children: [
        e('div', {id: 'share-url-container'}),
        e('button', {
            onClick: () => {
                copyTextToClipboard(document.querySelector('#share-url').href);
                document.querySelector('#share-url-copy-button').innerText = 'Copied';
                setTimeout(() => {
                    document.querySelector('#share-url-copy-button').innerText = 'Copy';
                }, 3000);
            },
            style: {margin: 'auto', marginTop: '15px'},
            id: 'share-url-copy-button'
        }, 'Copy')
    ]
})

export const modals = {
    settings: settingsModal,
    credits: creditsModal,
    share: shareModal
}