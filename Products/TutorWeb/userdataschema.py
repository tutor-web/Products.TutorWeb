from plone.app.users.userdataschema import IUserDataSchemaProvider
from zope.interface import implements
from zope import schema
from Products.CMFPlone import PloneMessageFactory as _


class UserDataSchemaProvider(object):
    implements(IUserDataSchemaProvider)

    def getSchema(self):
        """
        """
        return IEnhancedUserDataSchema


from plone.app.users.userdataschema import IUserDataSchema
def validateAccept(value):
    if not value == True:
        return False
    return True


 
class IEnhancedUserDataSchema(IUserDataSchema):
    """ Use all the fields from the default user data schema, and add various
    extra fields.
    """
    #fullname = schema.TextLine(
    #    title=_(u'label_full_name', default=u'Full Name'),
    #    description=_(u'help_full_name_creation',
    #                  default=u"Enter full name, e.g. John Smith."),
    #    required=True)

    accept = schema.Bool(
        title =_(u'label_accept', default=u'Accept terms of use'),
        description=_(u'help_accept',
                      default=u"By logging on to the tutor-web I agree that my grades can be recorded into a database, these can be viewed by instructors in the appropriate courses and the grades can be used anonymously for research purposes."
"Check this box if you agree to the conditions."),
        required=True,
        constraint=validateAccept,
        )
