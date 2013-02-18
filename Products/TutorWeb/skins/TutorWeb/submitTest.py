## Script (Python) "submitTest"
##bind container=container
##bind context=context
##

#!/usr/local/bin/python
# -*- coding: iso-8859-1 -*-
#
# $Id: submitTest.py,v 1.9 2006/01/26 13:07:19 wfenske Exp $
#
# Copyright © 2004 Otto-von-Guericke-Universität Magdeburg
#
# This file is part of LlsMultipleChoice.
#
# LlsMultipleChoice is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# LlsMultipleChoice is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with LlsMultipleChoice; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

""" This script is called when a candidate submits his/her MultipleChoiceTest, 
    i.e. presses the 'Submit' button of the test form in test_view.pt.
"""

from AccessControl import getSecurityManager
from DateTime import DateTime

request     = container.REQUEST
RESPONSE    = request.RESPONSE

I18N_DOMAIN = 'plone'

submitterId = getSecurityManager().getUser().getId()

# Check whether submission is allowed or not.
## if(context.isPublic() and (not context.hasSubmitted(submitterId))):
##     """ Save the candidate's answers to all the questions
##         he saw.
##     """
##     for questionContainer in [context] + context.getQuestionGroups():
##         for question in questionContainer.getQuestions(submitterId):
##             questionId = question.UID()
##             answersGiven = request.get(submitterId + '_' + questionId)
##             """ The answer ID 'i_dont_know_the_answer_to_this_question' 
##                 is a special case. An answer with that ID is generated for 
##                 every multiple choice answer to allow the candidate to 
##                 select nothing if he/she does not know which answer is correct
##                 but has already marked one of the radio buttons.
##             """
##             if (answersGiven !=
##                 'i_dont_know_the_answer_to_this_question') and \
##                (answersGiven !=
##                 ['i_dont_know_the_answer_to_this_question']):
##                 question.setCandidateAnswer(submitterId, answersGiven)
            
##     context.setCandidateTimeFinish(submitterId, DateTime())
    
##     msg = context.translate(\
##         msgid   = 'answers_saved',\
##         domain  = I18N_DOMAIN,\
##         default = 'Your answers have been saved.')
        
## else:
##     # Submission not allowed.
##     msg = context.translate(\
##         msgid   = 'not_submit_again',\
##         domain  = I18N_DOMAIN,\
##         default = 'You may not submit the test again.')
answersGiven = request.get('questionanswers')
context.setQuestionanswers(answersGiven)
msg = 'Your answer has been saved'        
target_action = context.getTypeInfo().getActionById( 'view' )

""" Set the 'portal_status_message' to 'msg' and set 'has_just_submitted'
    to 'True'. This prevents the 'You have already taken this test.' message
    from being shown immediately after submission.
"""
RESPONSE.redirect(
    '%s/%s?portal_status_message=%s&has_just_submitted=True' % ( context.absolute_url(),
                                         target_action,
                                         msg
                                        )
)
