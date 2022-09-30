import os
import win32api
import win32security
import win32con
import pywintypes
from flask import redirect, url_for, session


def custom_auth_logic():
    print("gotcha bitch")
    return True


def ad_auth(username, password):
    username = username.lower()
    domain = os.environ.get("DOMAIN")
    try:
        token = win32security.LogonUser(
            username,
            domain,
            password,
            win32security.LOGON32_LOGON_NETWORK,
            win32security.LOGON32_PROVIDER_DEFAULT)
        authenticated = bool(token)
        if authenticated == True:
            session['username'] = username
            impersonator = Impersonate(username, password, domain)

            # Get Username by impersonating user
            impersonator.logon()
            fullname = win32api.GetUserNameEx(3)
            impersonator.logoff()
            session['FullName'] = fullname

            custom_auth_logic()
            return redirect(url_for('welcome'))
    except pywintypes.error:
        return redirect(url_for('do_login', error='yes'))



class Impersonate:
    def __init__(self, login, password, domain):
        self.domain = domain
        self.login = login
        self.password = password

    def logon(self):
        self.handle = win32security.LogonUser(self.login, self.domain,self.password,win32con.LOGON32_LOGON_INTERACTIVE,win32con.LOGON32_PROVIDER_DEFAULT)
        win32security.ImpersonateLoggedOnUser(self.handle)

    def logoff(self):
        win32security.RevertToSelf() # terminates impersonation
        self.handle.Close() # guarantees cleanup


