import {modals, spawnModal} from '/static/modal.js';

const e = React.createElement;

const availableGenes = ['extension', 'agouti', 'frame', 'splash_white', 'tobiano', 'roan', 'rabicano', 'sabino2'];

export const basicShare = (horse_id, tld, path) => {
    let url = `${window.location.origin}/${path}?share=${horse_id}`;
    if (tld != 'com') {
        url += `&tld=${tld}`
    }

    if (path == 'vision') {
        for (const geneName of availableGenes) {
            const selectElement = document.querySelector(`#genes-${geneName}`);
            const option = selectElement.selectedOptions[0].value;
            if (option) {
                url += `&${geneName}=${option}`
            }
        }
    }

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
