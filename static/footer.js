import {spawnModal} from '/static/modal.js';

const e = React.createElement;

class Footer extends React.Component {
    render() {
        return e('div', {className: 'footer'},
            e('a', {href: '/'}, e('img', {src: '/static/logo_128.png'})),
            e('div', {className: 'right'},
                e('img', {
                    className: 'settings',
                    src: '/static/icons/settings_white.svg',
                    onClick: () => {spawnModal(this.props.settingsModal)}
                }),
                e('button', {className: 'credits', onClick: () => {spawnModal(this.props.creditsModal)}}, 'Credits')
            )
        )
    }
}

export default Footer
