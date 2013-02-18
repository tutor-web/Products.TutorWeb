from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase

DESIGNER = 'Grades may be recorded and used anonymously for research purposes.'


class CreditsViewlet(ViewletBase):
    render = ViewPageTemplateFile('./skins/TutorWeb/credits.pt')

    def update(self):
        # set here the values that you need to grab from the template.
        # stupid example:
        self.designer = DESIGNER
