async def relogin(hr_client):
    # This function (and this file as a whole) exists only to support the v1
    # API without a major refactor to make use of the new horsereality wrapper.

    # If you are interested, you can view the original (unreliable) code here:
    # https://github.com/hr-tools/api/blob/bbe98ae1743f033fff294afb43f3b9202deeaa8f/api/auth.py

    try:
        return hr_client.http.cookies['horsereality']
    except KeyError:
        await hr_client.login()
        return hr_client.http.cookies['horsereality']
