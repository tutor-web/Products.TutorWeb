from config import PLONE_VERSION

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem
from Products.CMFCore.utils import UniqueObject, getToolByName
import re
import cgi
import urllib
from datetime import datetime

HAS_FIVE_TS = True
try:
    from Products.Five.i18n import FiveTranslationService
    from Products import PlacelessTranslationService
except ImportError:
    HAS_FIVE_TS = False
if PLONE_VERSION == 3:
    from Products.PageTemplates.GlobalTranslationService import \
            getGlobalTranslationService

from config import *
from permissions import *
from tools import makeTransactionUnundoable

class ECQTool(UniqueObject, SimpleItem):
    """Various utility methods."""

            
    if PLONE_VERSION == 3:
            id = 'ecq_tool'
            portal_type = meta_type = 'ECQuiz Tool'
    
            security = ClassSecurityInfo()

            security.declarePublic('getFullNameById')
            def getFullNameById(self, id):
                """
                Returns the full name of a user by the given ID.
                """
        
                mtool = self.portal_membership
                member = mtool.getMemberById(id)
                error = False

                if not member:
                    return id
        
                try:
                    sn        = member.getProperty('sn')
                    givenName = member.getProperty('givenName')
                except:
                    error = True

                if error or (not sn) or (not givenName):
                    fullname = member.getProperty('fullname', '')
            
                if fullname == '':
                    return id
            
                if fullname.find(' ') == -1:
                    return fullname
            
                sn = fullname[fullname.rfind(' ') + 1:]
                givenName = fullname[0:fullname.find(' ')]
            
                return sn + ', ' + givenName

            security.declarePublic('cmpByName')
            def cmpByName(self, candidateIdA, candidateIdB):
                return cmp(self.getFullNameById(candidateIdA),
                   self.getFullNameById(candidateIdB))

    #security.declareProtected(PERMISSION_STUDENT, 'makeTransactionUnundoable')
    # FIXME: permissions
            security.declarePublic('makeTransactionUnundoable')
            def makeTransactionUnundoable(self):
                makeTransactionUnundoable()

            security.declarePublic('parseQueryString')
            def parseQueryString(self, *args, **kwargs):
                return cgi.parse_qs(*args, **kwargs)

            security.declarePublic('parseQueryString')
            def urlencode(self, *args, **kwargs):
                return urllib.urlencode(*args, **kwargs)

    
            security.declarePublic('userHasOneOfRoles')
            def userHasOneOfRoles(self, user, roles, obj):
                if user and roles and obj:
                    userId = user.getId()
                localRoles = obj.get_local_roles_for_userid(userId)
                contextRoles = user.getRolesInContext(obj)
                for role in roles:
                    if (user.has_role(role) or
                        (role in localRoles) or
                        (role in contextRoles)):
                        return True
        # default return value
                return False

                       
InitializeClass(ECQTool)
