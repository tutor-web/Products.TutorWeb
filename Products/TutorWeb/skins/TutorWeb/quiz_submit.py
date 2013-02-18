## Script (Python) "submitTest"
##bind container=container
##bind context=context
##

#!/usr/local/bin/python

"""This script is called when a candidate asked for a quiz question,
"""

from AccessControl import getSecurityManager
from DateTime import DateTime


REQUEST = container.REQUEST

# Check if "submit was pressed
finished = REQUEST.get('submit', False)

if finished:
    result = context.mymaybeMakeResult()

    closed = result.closedQuiz()
    if (not closed[0]):
        '''has not gotten an answer already'''
        nullVal = ['I_DONT_KNOW']
        form_data={}

        """The answer `nullVal' is a special case. An answer
        with that ID is generated for every multiple choice
        answer to allow the candidate to select nothing if
        he/she does not know which answer is correct but has
        already checked one of the radio buttons.
        """
        #FOUND = nullVal
        try:
            
            selected = REQUEST.has_key('AnswerPullDown')
            #context.redirect('lecture_view')
            #context.plone_utils.addPortalMessage(str(selected))
            #return
            if str(selected) == '1':
                #context.redirect('lecture_view')
                #context.plone_utils.addPortalMessage(str(selected) + 'selected true')
                #return
                form_data['AnswerPullDown'] = REQUEST.get('AnswerPullDown', nullVal)
                #context.redirect('lecture_view')
                #context.plone_utils.addPortalMessage(str(form_data['AnswerPullDown']))
                #return
                
                if form_data['AnswerPullDown'] != nullVal:
                    result.setCandidateAnswerToQuestion(form_data['AnswerPullDown'])
                    #context.redirect('lecture_view')
                    #context.plone_utils.addPortalMessage("after setcandidateans")
                    
                else:
                    result.unsetCandidateAnswerToQuestion()
            else:
                #result.unsetCandidateAnswerToQuestion()
                result.setCandidateAnswerToQuestion('-1')
                #context.redirect('lecture_view')
                context.plone_utils.addPortalMessage('WARNING: No answer given, question will be marked as incorrect')
                '''do what'''
                #return
                #result.setCandidateAnswerToQuestion(form_data['AnswerPullDown'])
    
            REQUEST.SESSION.set(context.getId(), form_data)

    

            sessname = (getSecurityManager().getUser().getId()) + 'submit'
            REQUEST.SESSION.get(sessname, True)
            REQUEST.SESSION[sessname] = True
            target = 'question_result_view'
            context.redirect('%s?portal_status_message=%s&has_just_submitted=True'
                     % (target, closed[1]))
            #else:
            #    context.redirect('lecture_view')
            #    context.plone_utils.addPortalMessage('You need to select some answer')
        except:
            #REQUEST.SESSION.set(context.getId(), form_data)

    

        
            #sessname = (getSecurityManager().getUser().getId()) + 'submit'
            #REQUEST.SESSION.get(sessname, True)
            #REQUEST.SESSION[sessname] = True
            #target = context.getActionInfo('object/view')['url']
            context.redirect('lecture_view')
            context.plone_utils.addPortalMessage('An error occured while taking quiz, please contact the system administrator')
            return
        
else:
    target = context.getActionInfo('object/view')['url']
    context.redirect(target)
