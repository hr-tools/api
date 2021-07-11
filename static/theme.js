let theme = 'light';
//let switchButton = null;

function useDark() {
    if (theme == 'dark') {return}
    const element = document.createElement('link');
    element.id = 'dark-mode-stylesheet';
    element.rel = 'stylesheet';
    element.href = '/static/style-dark.css';

    document.getElementsByTagName('head')[0].appendChild(element);
    theme = 'dark';
    setCookie({name: 'realmerge-theme', value: theme});
}

function useLight() {
    if (theme == 'light') {return}
    const stylesheetLink = document.querySelector('#dark-mode-stylesheet')
    if (!stylesheetLink) {return}

    stylesheetLink.remove();
    theme = 'light';
    setCookie({name: 'realmerge-theme', value: theme});
}

function toggleTheme() {
    switch (theme) {
        case 'light':
            useDark();
            break
        case 'dark':
            useLight();
            break
    }
    return theme
}

if (getCookie('realmerge-theme') == 'dark') {toggleTheme()}
