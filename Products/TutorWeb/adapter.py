from plone.app.users.browser.personalpreferences import UserDataPanelAdapter

class EnhancedUserDataPanelAdapter(UserDataPanelAdapter):
    """
    """
    #def get_fullname(self):
    #    return self.context.getProperty('fullname', '')
    #def set_fullname(self, value):
    #    return self.context.setMemberProperties({'fullname': value})
    #fullname = property(get_fullname, set_fullname)

    def get_accept(self):
        return self.context.getProperty('accept', '')
    def set_accept(self, value):
        return self.context.setMemberProperties({'accept': value})
    accept = property(get_accept, set_accept)
