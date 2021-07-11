const e = React.createElement//} catch (error) {}

function getCookie(cookieName) {
    const name = cookieName + "=";
    const ca = document.cookie.split(';');
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i].trim();
        if ((c.indexOf(name)) == 0) {
            return c.substr(name.length);
        }

    }
    return null
}

function setCookie(cookie) {
    document.cookie = `${cookie.name}=${cookie.value}; samesite=lax; path=/; expires=Tue, 19 Jan 2038 04:14:07 GMT`;
}

function toggleNav() {
    const menu = document.querySelector('#nav-drop-up');
    if (menu.style.display == 'none' || !menu.style.display) {
        menu.style.display = 'block';
    } else {
        menu.style.display = 'none';
    }
}
