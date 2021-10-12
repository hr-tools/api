import {modals, spawnModal} from '/static/modal.js';

const e = React.createElement;

export const basicShare = (horse_id, tld, path) => {
    const url = `${window.location.origin}/${path}?share=${horse_id}&tld=${tld}`;

    spawnModal(modals.share);
    const shareUrlContainer = document.querySelector('#share-url-container');
    ReactDOM.unmountComponentAtNode(shareUrlContainer);
    ReactDOM.render(
        e(React.Fragment, {children: [
            e('p', null, e('a', {id: 'share-url', href: url, key: 'share-url'}, url))
        ]}),
        shareUrlContainer
    )
}
