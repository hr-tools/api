let theme = 'light';

const element = document.querySelector('#theme')

function useLight() {
    element.href = '';
    theme = 'light';
    setCookie({name: 'realmerge-theme', value: theme});
}

function useGeneric(themeName) {
    element.href = `/static/themes/${themeName}/style.css`;
    theme = themeName;
    setCookie({name: 'realmerge-theme', value: theme});
}

const themeMap = {
    light: () => useLight(),
    dark: () => useGeneric('dark'),
    cherry: () => useGeneric('cherry'),
    rainforest: () => useGeneric('rainforest')
}

const setTheme = themeMap[getCookie('realmerge-theme')];
if (setTheme && setTheme != useLight) setTheme();
