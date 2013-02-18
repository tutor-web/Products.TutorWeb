## Script (Python) "lecture_questions_download_update"
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
update = context.writeQuestionsToFile()
# redirect back to lecture questions view
target = 'lecture_questions'    
container.REQUEST.RESPONSE.redirect(target)
    
