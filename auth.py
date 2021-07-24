import asyncio
from bs4 import BeautifulSoup
import json

config = json.load(open('config.json'))

def sneak_token(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    inputs = soup.find_all('input', attrs={'name': '_token', 'type': 'hidden'})
    try:
        token_input = inputs[0]
        token = token_input['value']
    except (IndexError, KeyError):
        msg = 'Couldn\'t fetch the required information for authenticating with Horse Reality.'
        raise Exception(msg)
    else:
        return token

async def get_laravel_csrf_token(tld, session):
    # HR uses the laravel framework and generates a unique token for
    # Cross-Site Request Forgery (CSRF) protection. this makes logging in a
    # bit more tedious for us but luckily it can be abstracted away by simply
    # further pretending we're a normal user; we GET v2 /login first and sneak
    # the token from the login form
    response = await session.get(f'https://v2.horsereality.{tld}/login')
    html_text = await response.text()
    loop = asyncio.get_event_loop()
    token = await loop.run_in_executor(None, sneak_token, html_text)
    return token
    # btw HR has very pretty error pages. big ups @ design team

async def relogin(tld, session):
    token = await get_laravel_csrf_token(tld, session)
    login_response = await session.post(
        f'https://v2.horsereality.{tld}/login',
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        data={
            '_token': token,
            'email': config['authentication'][tld]['email'],
            'password': config['authentication'][tld]['password']
        },
        allow_redirects=False
    )
    if login_response.status != 302:
        # when redirecting is enabled, this will be 200 because the
        # client lands on /horses, but this is not what we want, because
        # then the location header is not present. we could also check if
        # the current page is still /login, but assuming standard HTTP
        # practices are followed, we shouldn't have to worry about the
        # status code changing suddenly
        msg = 'Invalid credentials for the .%s server.' % tld
        raise ValueError(msg)

    get_cookie_url = login_response.headers['location']
    cookie_response = await session.get(get_cookie_url, allow_redirects=False)
    # www.horsereality.tld/?v2_auth_token=xxx

    cookie = cookie_response.cookies['horsereality']
    # thankfully HR returns the cookie value we need
    # here so we can skip a lot of annoying decoding stuff

    config['authentication'][tld]['cookie'] = cookie.value
    # Morsels should have an `.expires` but i couldn't get that to work
    # properly (aka: i'm stupid) so we just don't deal with it

    json.dump(config, open('config.json', 'w'))
    return cookie.value
