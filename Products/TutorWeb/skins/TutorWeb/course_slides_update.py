## Script (Python) "course_slides_update"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpathh
##parameters=
##title=Redirects to the projects folder
##


#!/usr/local/bin/python


"""This script is called when the slides update button is pressed in a course.
"""

REQUEST = container.REQUEST
update = context.updateSlideMaterial()
# redirect back to course view
target = 'course_view'    
container.REQUEST.RESPONSE.redirect(target)
    
