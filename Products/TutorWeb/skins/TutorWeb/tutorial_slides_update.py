## Script (Python) "tutorial_slides_update"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpathh
##parameters=
##title=Redirects to the projects folder
##


#!/usr/local/bin/python

#

REQUEST = container.REQUEST
update = context.updateSlideMaterial()

target = 'tutorial_view'    
container.REQUEST.RESPONSE.redirect(target)
    
