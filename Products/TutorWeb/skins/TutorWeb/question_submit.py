## Script (Python) "question_submit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpathh
##parameters=
##title=Redirects to the projects folder
##


#!/usr/local/bin/python


"""This script is called when a candidate submits a quiz qiestion.
"""

from AccessControl import getSecurityManager
from DateTime import DateTime
from Products.CMFCore import permissions
from Products.CMFPlone import PloneMessageFactory as _
from ZODB.POSException import ConflictError
#from zope.event import notify

REQUEST = container.REQUEST

# taking out, lecture in tw has no domian yet!
#I18N_DOMAIN = context.i18n_domain

#res = context.mymaybeMakeResult()
#start = res.startQuiz()
#user = getSecurityManager().getUser()
#candidateId = user.getId()

#tmp = context.setHasOpenQuiz(True)
#tmp = context.setSubmittedQuiz(False)
##suMode = context.userIsGrader(user)
# Check if "submit was pressed

finished = REQUEST.get('get', False)

if finished:
    res = context.mymaybeMakeResult()
    start = res.startQuiz()
    if (not start[0]):

        #target = context.getActionInfo('object/view')['url']
        target = 'lecture_view'
        context.redirect(target)
        context.plone_utils.addPortalMessage(start[1])
        #context.plone_utils.addPortalMessage(_(u'Sorry, but no questions available in this quiz.'))
        return
    
    else:

       
        target = 'quiz_question_view'    
    
        REQUEST.SESSION.get(start[1]+'get', True)
        REQUEST.SESSION[start[1]+'get'] = True
        container.REQUEST.RESPONSE.redirect('%s?portal_status_message=%s&has_just_submitted=True'
                     % (target, start[1]))

