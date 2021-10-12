import Footer from '/static/footer.js';
import {modals} from '/static/modal.js';

const e = React.createElement;
const container = document.querySelector('#container');

class MainContent extends React.Component {
    render() {
        return e(
            'div', {className: 'primary-shaft'},
            e(
                'div', {style: {display: 'flex'}},
                e('div', {style: {width: '100%', maxWidth: '550px'}},
                    e('h1', null, 'Realtools for Chrome'),
                    e('p', {style: {color: '#CECECE'}}, 'Hello. Our extension was recently removed from the Chrome Web Store for reasons that were not clearly communicated to us by Google.'),
                    e('br'),
                    e('a', {href: '/firefox'}, e('button', {class: 'secondary'}, 'I\'m using Firefox, not Chrome!'))
                ),
                e('div', {className: 'home-right-sidebar'},
                    e('img', {src: 'static/logo_128.png', className: 'home-logo'})
                )
            ),
            e(
                'div', {style: {marginBottom: '100px'}},
                e('div', {style: {width: '100%'}},
                    e('h2', {style: {fontSize: '2em', marginBottom: '10px'}}, 'Here\'s how to use it anyway'),
                    e('p', {style: {color: '#CECECE', fontSize: '20px'}}, e('b', null, 'Note:'), ' this method does not automatically receive updates, so you should probably ', e('a', {href: 'https://discord.com/invite/TFgqyWF9bn', target: '_blank'}, 'join our Discord server'), ' for news.'),
                    e(
                        'ol', {style: {color: '#CECECE', fontSize: '20px'}},
                        e('li', null, 'Download and extract ', e('a', {href: '/static/ext-chrome/latest.zip'}, 'this ZIP file'), ' anywhere on your computer (don\'t delete the folder)'),
                        e('li', null, 'Visit ', e('a', {href: 'chrome://extensions', target: '_blank'}, 'chrome://extensions'), ' in your browser'),
                        e('li', null, 'Enable "Developer mode" in the top right corner'),
                        e('li', null, 'Click "Load unpacked" and select the folder that you extracted'),
                    ),
                    e('p', {style: {color: '#CECECE', fontSize: '20px'}}, 'Congratulations! You now have your very own copy of Realtools for Chrome loaded in your browser.')
                ),
            ),
            e(Footer, {page: 'chrome', settingsModal: modals.settings, creditsModal: modals.credits})
        )
    }
}

function loadMain() {
    ReactDOM.render(e(MainContent), container)
}

loadMain();
