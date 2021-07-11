const rawCookie = getCookie('realmerge-watermark');
let useWatermark = rawCookie == null || rawCookie == 'true';

function toggleUseWatermark() {
    useWatermark = !useWatermark;
    setCookie({name: 'realmerge-watermark', value: useWatermark})
}

class SettingsModal extends React.Component {
    constructor(props) {super(props)}

    render() {
        return e('div', {className: 'modal-bg'}, //dismissSettings()
        e(
            'div',
            {className: 'box modal'},
            e('div', {className: 'preview-titlebar'},
                e('h3', {}, 'Realmerge Settings'),
                e('button', {onClick: () => dismissSettings()}, 'Close')
            ),
            e('h4', {className: 'settings-section', style: {marginTop: '0px'}}, 'Theme'),
            e('input', {style: {marginLeft: '0'}, name: 'theme-radio-button', type: 'radio', defaultChecked: theme === 'light', id: 'theme-light', onClick: () => useLight()}),
            e('label', {htmlFor: 'theme-light'}, 'Light'),
            e('input', {style: {marginLeft: '15px'}, name: 'theme-radio-button', type: 'radio', defaultChecked: theme === 'dark', id: 'theme-dark', onClick: () => useDark()}),
            e('label', {htmlFor: 'theme-dark'}, 'Dark'),
            e('h4', {className: 'settings-section'}, 'Attribution'),
            e('input', {style: {marginLeft: '0'}, type: 'checkbox', id: 'watermark', defaultChecked: useWatermark, onClick: () => toggleUseWatermark()}),
            e('label', {htmlFor: 'watermark'}, 'Horse Reality watermark'),
            e('p', {className: 'modal-footnote'}, 'Although not required by HR, we recommend keeping this enabled if you plan on sharing merged images.')
        ))
    }
}

function spawnSettings() {
    ReactDOM.render(e(SettingsModal), document.querySelector('#settings-modal-container'))
}
function dismissSettings() {
    ReactDOM.unmountComponentAtNode(document.querySelector('#settings-modal-container'))
}