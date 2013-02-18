from Products.Archetypes.public import OrderedBaseFolder
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.folder import ATFolderSchema
from AccessControl import ClassSecurityInfo
from Products.CMFCore import permissions as CMFCorePermissions

from config import *
from permissions import *
from tools import *
from Products.Archetypes.public import Schema, BooleanField, BooleanWidget, \
     IntegerField, IntegerWidget, StringField, \
     TextAreaWidget, StringWidget

from Products.DataGridField.DataGridField import DataGridField
from Products.DataGridField.DataGridWidget import DataGridWidget
from Products.DataGridField.Column import Column
from Products.DataGridField.SelectColumn import SelectColumn
from Products.Archetypes.public import DisplayList
# Import conditionally, so we don't introduce a hard depdendency
try:
    from plone.i18n.normalizer.interfaces import IUserPreferredURLNormalizer
    from plone.i18n.normalizer.interfaces import IURLNormalizer
    URL_NORMALIZER = True
except ImportError:
    URL_NORMALIZER = False
from Acquisition import aq_parent


from AccessControl import ClassSecurityInfo, getSecurityManager
from Products.TutorWeb.interfaces import ISchoolFolder 
from zope.interface import implements
if PLONE_VERSION == 4:
    from Products.Archetypes import atapi
    from config import PROJECTNAME


#############################################################
## check, can department code be edited???? think not, FIXME
#############################################################

class SchoolFolder(ATFolder):
    
    """Departments in the tutor-web are organized by a unique code. 
    A Department is implemented as a folder which can contain Courses and Tutorials as well as Sponsors.
    It implements an ATFolder as well as interfaces, IDepartment and IOrderedTutorWebContent.
    """
   
    schema = ATFolderSchema.copy() + Schema((
        
        StringField('title',
                required=True,
                searchable=0,
                default='School Name',
                widget=StringWidget(
                    label='Title',
                    description='Specify the title for the school folder.',
                 ),
               
            ),
        
        #StringField('Description',
        #          widget=StringWidget(label='Description',
        #                              description='A short summary of this folder',),
                 
        #          ),
       
     ))

    __implements__ = (ATFolder.__implements__)
    implements(ISchoolFolder)
    global_allow = True
    meta_type = 'SchoolFolder'          # zope type name
    portal_type = meta_type          # plone type name
    archetype_name = 'SchoolFolder' # friendly type name
    _at_rename_after_creation = True #create id automatically
    security = ClassSecurityInfo()
    
    def getLanguage(self):
        portal_languages = getToolByName(self, 'portal_languages')
        lang = portal_languages.getPreferredLanguage() 
        return lang
   
    
    def haveCourses(self):
        """true if school folder contains any schools otherwise return false"""
        #schools = self.getFolderContents(contentFilter={"portal_type": "School"})
        #if (len(schools) > 0):
        #    return True
        #else:
        #    return False
   
    
    
    security.declarePrivate('tryWorkflowAction')
    def tryWorkflowAction(self, action, ignoreErrors=False, comment=None):
        """publish deparment"""
        wtool = self.portal_workflow
        wf = wtool.getWorkflowsFor(self)[0]
        if wf.isActionSupported(self, action):
            if comment is None:
                #userId = getSecurityManager().getUser().getId()
                comment = 'State changed' 
            wtool.doActionFor(self, action, comment=comment)
        elif not ignoreErrors:
            raise TypeError('Unsupported workflow action %s for object %s.'
                            % (repr(action), repr(self)))  
    def canSeeQuestions(self):
        """if current user has the role of a manager, editor, owner or belongs to the group: teacher
         then return True else False"""
        try:
            user = getSecurityManager().getUser()
            groups = user.getGroups()
            if (user.has_role('Manager')):
                return True
            elif(user.has_role('Editor')):
                return True
            elif(user.has_role('Owner')):
                return True
            elif('teacher' in groups):
                return True
            else:
                return False
        except:
           '''couldn't determine user'''
           return False
    
    def isLoggedOn(self):
        """If current user has not logged in then return False else True"""
        mtool = getToolByName(self, 'portal_membership')
        if mtool.isAnonymousUser():
            return False
        else:
            return True    
    def getFullName(self, userid):
        """Return the full name of a user based on given id"""
        mtool = self.portal_membership
        member = mtool.getMemberById(userid)
        error = False
        if not member:
            return userid
        return member.getProperty('fullname')

if PLONE_VERSION == 3:
    registerATCTLogged(SchoolFolder)
else:
    atapi.registerType(SchoolFolder, PROJECTNAME)
