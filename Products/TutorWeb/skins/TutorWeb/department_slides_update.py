## Script (Python) "department_slides_update"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpathh
##parameters=
##title=Redirects to the projects folder
##


#!/usr/local/bin/python


"""This script is called when the update slides button is pressed in department view.
"""

REQUEST = container.REQUEST

update = context.updateSlideMaterial()
# redirect back to department view
target = 'department_tutorials'     
container.REQUEST.RESPONSE.redirect(target)
    
