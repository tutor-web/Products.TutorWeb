from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase

DESIGNER = 'John Doe'

class QuestionAndAnswer(ViewletBase):
    render = ViewPageTemplateFile('./skins/TutorWeb/tutorwebanswerselection1.pt')

    def update(self):
        # set here the values that you need to grab from the template.
        # stupid example:
        self.designer = DESIGNER + '1'
