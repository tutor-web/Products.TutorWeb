"""A standalone page showing screenings of a particular film at a particular
cinema. This view is registered for ICinema, and takes the film as a request
parameter.
"""

from datetime import datetime, timedelta

from zope.component import getUtility

from Acquisition import aq_inner
from AccessControl import getSecurityManager

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName

from plone.memoize.instance import memoize


from Products.TutorWeb.interfaces import IQuizLocator

#from Products.TutorWeb import CinemaMessageFactory as _
from Products.CMFPlone import PloneMessageFactory as _

from Products.TutorWeb import config
import tempfile
import os

class QuizInfoView(BrowserView):
    """List quiz information
    """
        
    __call__ = ViewPageTemplateFile('quizinfo.pt')
    #def getFullName(self):
    #    if not usern then fullname
    #    else fullnamen
        
    @memoize
    def student_questions(self):
        lecture = aq_inner(self.context)
        user = {'user_id' : self.request.get('user_id', None),
                               'state'   : self.request.get('state', None),
                };
        
        if (not (user['user_id'] is None)):
            '''id given in url as in tutor-web/...?user='name' '''
            candidateId = user['user_id']   
        else:
            '''use logged-in member'''
            member = self.context.portal_membership.getAuthenticatedMember() 
            candidateId = member.getId();
           
        context_path = self.context.getPhysicalPath()
        path = '/'.join(context_path)
        locator = getUtility(IQuizLocator)
        
        return locator.questions_by_student(path, candidateId)
        
        
    
