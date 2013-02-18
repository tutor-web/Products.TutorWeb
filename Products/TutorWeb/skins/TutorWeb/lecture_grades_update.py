## Script (Python) "lecture_grades_update"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpathh
##parameters=
##title=Redirects to the projects folder
##


#!/usr/local/bin/python


"""This script is called when the update grades button is pressed. 
"""

REQUEST = container.REQUEST
update = context.writeLectureGrades()
target = 'lecture_results'    
container.REQUEST.RESPONSE.redirect(target)
    
