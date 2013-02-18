## Script (Python) "redirect"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=url

#!/usr/local/bin/python


""" Redirects to the given URL, avoiding encoding issues """

REQUEST  = context.REQUEST
RESPONSE = REQUEST.RESPONSE

return RESPONSE.redirect(context.str(url))
