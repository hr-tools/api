import Footer from '/static/footer.js';
import {modals} from '/static/modal.js'

const e = React.createElement;
const container = document.querySelector('#container');


class MainContent extends React.Component {
    render() {
        return e('div', {className: 'primary-shaft app', id: 'primary-shaft'},
            e('h1', {className: 'tool-page-title'}, 'Supported Realvision Breeds'),
            e('div', {className: 'box', style: {textAlign: 'left'}},
                e('h2', {style: {marginTop: '0px', marginBottom: '5px'}}, 'Done'),
                e('ul', null,
                    e('li', null, 'Camargue'),
                    e('li', null, 'Cleveland'),
                    e('li', null, 'Exmoor'),
                    e('li', null, 'Fjord'),
                    e('li', null, 'Haflinger'),
                    e('li', null, 'Norman Cob'),
                    e('li', null, 'Suffolk Punch')
                ),
                e('h2', {style: {marginTop: '0px', marginBottom: '5px'}}, 'Supported (not finished)'),
                e('ul', null,
                    e('li', null, 'Akhal-Teke - ', e('b', null, 'In progress:'), ' colors, white markings & patterns'),
                    e('li', null, 'Arabian - ', e('b', null, 'In progress:'), ' white markings & patterns'),
                    e('li', null, 'Brabant - ', e('b', null, 'In progress:'), ' colors (new variations)'),
                    e('li', null, 'Brumby - ', e('b', null, 'In progress:'), ' colors, white markings & patterns'),
                    e('li', null, 'Friesian - ', e('b', null, 'In progress:'), ' colors (new variations), white markings (new stars)'),
                    e('li', null, 'Icelandic - ', e('b', null, 'In progress:'), ' colors (grays), white markings & patterns'),
                    e('li', null, 'Irish Cob - ', e('b', null, 'In progress:'), ' white markings & patterns'),
                    e('li', null, 'Kladruber - ', e('b', null, 'In progress:'), ' colors, white markings'),
                    e('li', null, 'Knabstrupper - ', e('b', null, 'In progress:'), ' white markings & patterns'),
                    e('li', null, 'Mustang - ', e('b', null, 'In progress:'), ' colors, white markings & patterns'),
                    e('li', null, 'PRE - ', e('b', null, 'In progress:'), ' colors, white markings'),
                    e('li', null, 'Quarter - ', e('b', null, 'In progress:'), ' colors, white markings & patterns'),
                    e('li', null, 'Shire - ', e('b', null, 'In progress:'), ' colors'),
                    e('li', null, 'Thoroughbred - ', e('b', null, 'In progress:'), ' colors, white markings & patterns'),
                    e('li', null, 'Trakehner - ', e('b', null, 'In progress:'), ' colors, white markings & patterns'),
                    e('li', null, 'Welsh Pony - ', e('b', null, 'In progress:'), ' colors, white markings & patterns')
                ),
                e('h2', {style: {marginTop: '0px', marginBottom: '5px'}}, 'Doing (not supported)'),
                e('ul', null,
                    e('li', null, 'Finnhorse'),
                    e('li', null, 'Lusitano'),
                    e('li', null, 'Noriker'),
                ),
                e('h2', {style: {marginTop: '0px', marginBottom: '5px'}}, 'To-do'),
                e('ul', null,
                    e('li', null, 'Oldenburg')
                )
            ),
            e(Footer, {page: 'vision', settingsModal: modals.settings, creditsModal: modals.credits})
        )
    }
}

function loadMain() {
    ReactDOM.render(e(MainContent), container);
}

loadMain();
