## Controller Python Script "register"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##title=Enroll in course
##parameters=
##
from Products.CMFPlone import PloneMessageFactory as _
from ZODB.POSException import ConflictError

REQUEST = context.REQUEST


#user1 = member.getId()
msg = context.addUser()
context.plone_utils.addPortalMessage(_(msg))
return state.set(status='success')

