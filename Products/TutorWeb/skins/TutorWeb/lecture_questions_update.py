## Script (Python) "lecture_questions_update"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpathh
##parameters=
##title=Redirects to the projects folder
##


#!/usr/local/bin/python

REQUEST = container.REQUEST
updated = context.addQuestionsFromLatexFile()

if updated:
    
    target = 'lecture_questions'    
    container.REQUEST.RESPONSE.redirect(target)
else:
    target = 'lecture_questions_updateError' 
    container.REQUEST.RESPONSE.redirect(target)
