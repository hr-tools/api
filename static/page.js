const e = React.createElement;
const container = document.querySelector('#container');
let currentTab = null

const toolIds = {
    merge: {title: 'Realmerge', tagline: 'Generate transparent PNGs of your horses in seconds.', link: '/merge'},
    predictor: {title: 'Realvision', tagline: 'Preview exact or close estimates of your foal as an adult.', link: '/vision'},
    extension: {title: 'Browser Extension', tagline: 'Use Realtools without leaving Horse Reality.', link: '/extension', openText: 'Download'}
}

class Tab extends React.Component {
    constructor(props) {
        super(props);
        this.state = {selected: props.selected || false};
        this.tool = toolIds[props.id];
    }

    select() {
        if (currentTab == this) {return}
        if (currentTab) {currentTab.setState({selected: false})}
        this.setState({selected: true});
        currentTab = this;
    }

    showContent() {
        const tabContentContainer = document.querySelector('#tab-content');

        const content = e(React.Fragment, {
            children: [
                e('h1', {key: `tool-title-${this.props.id}`}, this.tool.title),
                e('p', {key: `tool-tagline-${this.props.id}`, style: {color: '#CECECE'}}, this.tool.tagline),
                e(
                    'a', {
                        href: this.tool.link,
                        target: '_self',
                        key: `tool-goto-button-link-${this.props.id}`
                    },
                    e(
                        'button', {
                            key: `tool-goto-button-${this.props.id}`,
                            style: {marginTop: '30px'}
                        },
                        this.tool.openText || `Open ${this.tool.title}`
                    )
                )
            ]
        });

        ReactDOM.render(content, tabContentContainer);
        tabContentContainer.style.display = 'block';
    }

    componentDidUpdate() {
        if (this.state.selected) {
            this.showContent()
        }
    }

    render() {
        let className = 'tab';
        if (this.state.selected) {className += ' selected'};
        return e(
            'button', {
                id: `tab-button-${this.props.id}`,
                className: className,
                onClick: () => {this.select()}
            },
            this.tool.title
        )
    }
}

class MainContent extends React.Component {
    render() {
        const allTabs = [];
        Object.keys(toolIds).forEach((toolId) => {
            allTabs.push(e(Tab, {key: toolId, id: toolId}));
        });
        return e(
            'div', {className: 'primary-shaft'},
            // introduction section
            e(
                'div', {style: {display: 'flex', marginBottom: '100px'}},
                e('div', {style: {width: '100%', maxWidth: '550px'}},
                    e('h1', {}, 'Realtools'),
                    e('p', {style: {color: '#CECECE'}}, 'This is the hub page for Realtools - a collection of Horse Reality webtools. Click on a tab below to see info about that specific tool.')
                ),
                e('div', {className: 'home-right-sidebar'},
                    e('img', {src: 'static/logo_128.png', className: 'home-logo'})
                )
            ),
            // tabs
            e(
                'div', {className: 'home-tabs'},
                e(React.Fragment, {children: allTabs})
            ),
            // tab content
            e('div', {id: 'tab-content', style: {display: 'none'}})
        )
    }
}

function loadMain() {
    ReactDOM.render(e(MainContent), container)
}

loadMain();
