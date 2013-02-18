## Controller Python Script "register"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Enroll in course
##
from Products.CMFPlone import PloneMessageFactory as _
from ZODB.POSException import ConflictError

REQUEST = context.REQUEST


#user1 = member.getId()
context.addUser()
context.plone_utils.addPortalMessage(_(u'User has been enrolled in course.'))
return state.set(status='success')

