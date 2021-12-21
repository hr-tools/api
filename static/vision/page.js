import Footer from '/static/footer.js';
import {Modal, modals, spawnModal} from '/static/modal.js';
import {showError} from '/static/errors.js';
import {emoji} from '/static/symbols.js';
import {getCookie, setCookie, getUseWatermark} from '/static/cookies.js';
import {base64UrlEncode} from '/static/base64.js';
import {basicShare} from '/static/share.js';

const e = React.createElement;
const container = document.querySelector('#container');

const disclaimersModal = e(Modal, {
    name: 'Disclaimers',
    children: [
        e('p', {className: 'disclaimer'}, e('a', {href: '/vision/breeds'}, 'Click here for a list of breeds that Realvision supports.')),
        e('br'),
        e('p', {className: 'disclaimer'}, 'Base color selections are for eliminating inaccurate color predictions caused by duplicate image codes. We suggest using these fields if your horse is heavily diluted.'),
        e('br'),
        e('p', {className: 'disclaimer'}, 'If your foal is predicted with a ± (plus-minus sign) in its color name and genotype, it means that this color shares image codes with a different genotype, and could be used for a horse with or without a certain gene. E.g., Smoky Cream ± Silver = your horse will look exactly like a smoky cream with or without silver.'),
        e('br'),
        e('p', {className: 'disclaimer'}, 'Realvision can predict rabicano and roan on untested foals by referencing white pattern codes that are changed due to the presence of the gene. However, these genes cannot be seen on foals. This means that the rabicano and roan selection boxes must be used for an accurate prediction if your foal has no white markings/patterns.'),
        e('br'),
        e('p', {className: 'disclaimer'}, 'If your foal cannot be predicted or is predicted without white markings/patterns, this means that its layers do not currently exist in our database (it will, of course, grow with its white markings/patterns!) If this happens, please send the foal\'s link to bjömun#6758 on Discord or ', e('a', {href: 'https://v2.horsereality.com/user/2965'}, 'Bjomun'), ' on Horse Reality.')
    ]
});

const users = {
    aBREEviate: 'https://v2.horsereality.com/user/86694',
    Aca: 'https://v2.horsereality.com/user/70318',
    Allendria: 'https://v2.horsereality.com/user/104787',
    ArufaurufuChan: 'https://v2.horsereality.com/user/104991',
    Casper: 'https://v2.horsereality.com/user/2743',
    DarkCornelius: 'https://v2.horsereality.com/user/30403',
    Dreepy: 'https://v2.horsereality.com/user/49048',
    '--Equestrian--': 'https://v2.horsereality.com/user/45061',
    Falida: 'https://v2.horsereality.com/user/18825',
    Foam: 'https://v2.horsereality.com/user/12669',
    JessaB: 'https://v2.horsereality.com/user/38272',
    Karmaleon: 'https://v2.horsereality.com/user/8740',
    'Kit-Kat': 'https://v2.horsereality.com/user/66435',
    Linn: 'https://v2.horsereality.com/user/136244',
    LunaSommer: 'https://v2.horsereality.com/user/131121',
    LynxVagabond: 'https://v2.horsereality.nl/user/5797',
    Nagapie: 'https://v2.horsereality.com/user/39129',
    Reysies: 'https://v2.horsereality.com/user/20072',
    Sarah_The_Candle: 'https://v2.horsereality.com/user/150678',
    thanksbutnah: 'https://v2.horsereality.com/user/53147',
    Tieria: 'https://v2.horsereality.com/user/18159',
    Villy: 'https://v2.horsereality.com/user/115389',
    Yumy: 'https://v2.horsereality.com/user/100782'
}

function Credit(name, breeds) {
    const url = users[name]
    return (
        e('li', null,
            e('p', {className: 'disclaimer'},
                e('a', {target: '_blank', href: url}, name),
                `: ${breeds}`
            )
        )
    )
}

const dataCreditsModal = e(Modal, {
    name: 'Data Credits',
    children: [
        e('p', {className: 'disclaimer'}, 'Many thanks to the following individuals who have created color guides and/or volunteered to collect data for this site.'),
        e('ul', null,
            Credit('aBREEviate', 'Knabstrupper, PRE'),
            Credit('Aca', 'Thoroughbred'),
            Credit('Allendria', 'Irish Cob'),
            Credit('ArufaurufuChan', 'Icelandic, Trakehner'),
            Credit('Casper', 'Brumby'),
            Credit('Dark-Cornelius', 'Camargue, Cleveland, Fjord, Mustang, Suffolk Punch, Thoroughbred'),
            Credit('Dreepy', 'Lusitano'),
            Credit('--Equestrian--', 'Brabant, PRE, Thoroughbred'),
            Credit('Falida', 'Oldenburg'),
            Credit('Foam', 'Arabian, Camargue, Exmoor, Fjord, Haflinger, Icelandic, Norman Cob, Oldenburg, PRE, Shire, Thoroughbred, Welsh Pony'),
            Credit('JessaB', 'Noriker, Quarter Horse, Thoroughbred'),
            Credit('Karmaleon', 'PRE'),
            Credit('Kit-Kat', 'Thoroughbred'),
            Credit('Linn', 'Arabian, Irish Cob'),
            Credit('LunaSommer', 'Knabstrupper'),
            Credit('LynxVagabond', 'Friesian, Shire, Thoroughbred'),
            Credit('Nagapie', 'Arabian, Finnhorse'),
            Credit('Reysies', 'Noriker'),
            Credit('Ruttis', 'Thoroughbred'),
            Credit('silfurskin', 'Camargue, Kladruber, Norman Cob'),
            Credit('Sarah_The_Candle', 'Finnhorse'),
            Credit('thanksbutnah', 'Brumby, Lusitano'),
            Credit('Tieria', 'Noriker'),
            Credit('Villy', 'Lusitano'),
            Credit('Yumy', 'Brumby')
        ),
        e('p', {className: 'disclaimer'}, 'Special thanks to ', e('a', {target: '_blank', href: users.Foam}, 'Foam'), ', who contributed to the majority of our available breeds.')
    ]
});

class MainContent extends React.Component {
    render() {
        return e('div', {className: 'primary-shaft app', id: 'primary-shaft'},
            e('h1', {className: 'tool-page-title'}, 'Realvision'),
            e('div', {className: 'box'},
                e('input', {
                    className: 'horse-url',
                    id: 'horse-url',
                    placeholder: 'https://horsereality.com/horses/...',
                    required: true
                }),
                e('div', {className: 'options-container'},
                    e('h3', null, 'Genes (optional)'),
                    e('p', null, 'Selecting a white pattern or untestable white pattern will add one variation of the phenotype to the resulting image. Because this website\'s data is manually collected, some white patterns do not have an available prediction.'),
                    e('div', {className: 'genes-columns'},
                        e('div', null,
                            e('h4', null, 'Base Color'),
                            e('p', null,
                                'Extension: ',
                                e('select', {id: 'genes-extension'},
                                    e('option', {value: ''}, ''),
                                    e('option', {value: 'e/e'}, 'e/e'),
                                    e('option', {value: 'E/e'}, 'E/e')
                                )
                            ),
                            e('p', null,
                                'Agouti: ',
                                e('select', {id: 'genes-agouti'},
                                    e('option', {value: ''}, ''),
                                    e('option', {value: 'a/a'}, 'a/a'),
                                    e('option', {value: 'A/a'}, 'A/a')
                                )
                            ),
                        ),
                        e('div', null,
                            e('h4', null, 'White Patterns'),
                            e('p', null,
                                'Frame: ',
                                e('select', {id: 'genes-frame'},
                                    e('option', {value: ''}, ''),
                                    e('option', {value: 'OLW'}, 'OLW/n')
                                )
                            ),
                            e('p', null,
                                'Splash White: ',
                                e('select', {id: 'genes-splash_white'},
                                    e('option', {value: ''}, ''),    
                                    e('option', {value: 'SW1'}, 'SW1/n'),
                                    e('option', {value: 'SW1/SW1'}, 'SW1/SW1')
                                )
                            ),
                            e('p', null,
                                'Tobiano: ',
                                e('select', {id: 'genes-tobiano'},
                                    e('option', {value: ''}, ''),
                                    e('option', {value: 'TO'}, 'TO/n'),
                                    e('option', {value: 'TO/TO'}, 'TO/TO')
                                )
                            ),
                            e('p', null,
                                'Roan: ',
                                e('select', {id: 'genes-roan'},
                                    e('option', {value: ''}, ''),
                                    e('option', {value: 'RN'}, 'RN/n')
                                )
                            )
                        ),
                        e('div', null,
                            e('h4', null, 'Untestable'),
                            e('p', null,
                                'Rabicano: ',
                                e('select', {id: 'genes-rabicano'},
                                    e('option', {value: ''}, ''),
                                    e('option', {value: 'rab/rab'}, 'rab/rab')
                                )
                            ),
                            e('p', null,
                                'Sabino2: ',
                                e('select', {id: 'genes-sabino2'},
                                    e('option', {value: ''}, ''),
                                    e('option', {value: 'sab2/sab2'}, 'sab2/sab2')
                                )
                            )
                        )
                    )
                ),
                e('button', {className: 'secondary', onClick: () => {spawnModal(disclaimersModal)}, style: {marginLeft: '0px'}}, `${emoji.warning} Disclaimers`),
                e('button', {className: 'secondary', onClick: () => {spawnModal(dataCreditsModal)}, style: {marginLeft: '0px'}}, `${emoji.man_technologist} Data Credits`),
                e('button', {onClick: () => {predictFoal()}, style: {marginLeft: '0px'}}, `${emoji.crystal_ball} Predict`),
            ),
            e('div', {id: 'result-container'}),
            e(Footer, {page: 'vision', settingsModal: modals.settings, creditsModal: modals.credits})
        )
    }
}

class HorseResults extends React.Component {
    render() {
        const horse = e(
            'div', {className: 'box results', style: {width: '100%', marginRight: '20px'}},
            e('div', {className: 'preview-titlebar'},
                e('a', {href: `https://www.horsereality.${this.props.tld}/horses/${this.props.id}/`}, e('h1', null, this.props.name)),
                e('button',
                    {style: {marginLeft: '15px'}, onClick: () => {importMulti()}},
                    'Import to Multi'
                ),
                e('button',
                    {onClick: () => {basicShare(this.props.id, this.props.tld, 'vision')}},
                    'Share'
                )
            ),
            e('img', {src: this.props.url})
        )
        const details = e(
            'div', {className: 'box details'},
            e('h3', null, 'Color'),
            e('p', {style: {marginBottom: '10px'}}, this.props.details.color),
            e('h3', null, 'Genotype'),
            e('p', null, this.props.details.dilution.trim())
        )

        return e(React.Fragment, {children: [horse, details]})
    }
}

const availableGenes = ['extension', 'agouti', 'frame', 'splash_white', 'tobiano', 'roan', 'rabicano', 'sabino2'];

function getGenes() {
    const genes = {}
    for (const geneName of availableGenes) {
        const selectElement = document.querySelector(`#genes-${geneName}`);
        const option = selectElement.selectedOptions[0].value;
        if (option == '') {
            genes[geneName] = null;
        } else {
            genes[geneName] = option;
        }
    }
    return genes
}

let currentHorseLayerData = null;

async function predictFoal() {
    const horse_url_input = document.querySelector('#horse-url');
    const horse_url = horse_url_input.value;
    if (!horse_url) {
        showError('Input box must not be empty.')
        return
    }
    horse_url_input.value = null;

    const genes = getGenes();
    const useWatermark = getUseWatermark();
    const response = await fetch('/api/predict', {
        method: 'POST',
        body: JSON.stringify({url: horse_url, genes: genes, watermark: useWatermark}),
        headers: {'Content-Type': 'application/json'}
    });
    const data = await response.json();
    if (!response.ok) {
        showError(data.message);
        return
    }

    // display the horse
    const resultContainer = document.querySelector('#result-container');
    const results = e(HorseResults, data);
    ReactDOM.unmountComponentAtNode(resultContainer);
    ReactDOM.render(results, resultContainer)
    delete data.message;
    delete data.url;

    data.source = 'Realvision';
    currentHorseLayerData = data;
}

async function importMulti() {
    if (!currentHorseLayerData) {
        showError('No horse is present.');
        return
    }
    const encodedData = base64UrlEncode(JSON.stringify(currentHorseLayerData));
    const loc = window.location;
    const url = `${loc.protocol}//${loc.host}/merge/multi?data=${encodedData}`;
    window.open(url);
}

function loadMain() {
    ReactDOM.render(e(MainContent), container);
}

async function loadCheckShare() {
    const queryParams = new URLSearchParams(window.location.search);
    const shareId = queryParams.get('share');
    const tld = queryParams.get('tld') || 'com';
    if (!shareId) return false
    if (['com', 'nl'].indexOf(tld) == -1) return false

    const url = `https://www.horsereality.${tld}/horses/${shareId}/`
    document.querySelector('#horse-url').value = url;

    for (const geneName of availableGenes) {
        const geneValue = queryParams.get(geneName);
        if (geneValue) {
            const selectElement = document.querySelector(`#genes-${geneName}`);
            for (const option of selectElement.options) {
                if (option.value == geneValue) {
                    option.selected = true;
                }
            }
        }
    }

    await predictFoal()
}

loadMain();
if (getCookie('realtools-realvision-has-read-popup') != 'true') {
    spawnModal(e(Modal, {
        name: 'Welcome to Realvision',
        children: [
            e('p', null, 'It seems that this is your first time here, so there are a few things you need to know to be able to use Realvision to its fullest extent.'),
            e('br'),
            e('p', null, `Please click the ${emoji.warning} Disclaimers button, to the far left of the ${emoji.crystal_ball} Predict button, for essential information on how Realvision works.`),
            e('br'),
            e('p', null, `The ${emoji.man_technologist} Data Credits button lists all the people that helped to make Realvision possible.`),
            e('br'),
            e('p', null, 'Finally, the gear icon on the bottom right allows you to modify the website\'s settings, and the Credits button links you to some information on who made Realtools as well as some support info.'),
            e('br'),
            e('p', null, 'Please click "I understand" if you have read and understood all of the above text, and this popup will be out of your way forever.'),
            e('button', {
                style: {margin: 'auto', marginTop: '15px'},
                onClick: (event) => {
                    setCookie({name: 'realtools-realvision-has-read-popup', value: 'true'})
                    ReactDOM.unmountComponentAtNode(event.target.parentNode.parentNode.parentNode)
                }
            },
                'I understand'
            )
        ]
    }))
}
loadCheckShare();
