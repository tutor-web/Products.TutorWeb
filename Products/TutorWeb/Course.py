from Products.Archetypes.public import OrderedBaseFolder
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.folder import ATFolderSchema
from AccessControl import ClassSecurityInfo
from Products.CMFCore import permissions as CMFCorePermissions

from config import *
from permissions import *
from tools import *
from Products.Archetypes.public import Schema, BooleanField, BooleanWidget, \
     IntegerField, ReferenceField, IntegerWidget, StringField, ComputedField, \
     TextAreaWidget, StringWidget, ReferenceWidget, InAndOutWidget
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget \
     import ReferenceBrowserWidget
from Products.DataGridField.DataGridField import DataGridField
from Products.DataGridField.DataGridWidget import DataGridWidget
from Products.DataGridField.Column import Column
from Products.DataGridField.SelectColumn import SelectColumn
from Products.Archetypes.public import DisplayList
from Products.Archetypes.public import Vocabulary
import tempfile
# Import conditionally, so we don't introduce a hard depdendency
try:
    from plone.i18n.normalizer.interfaces import IUserPreferredURLNormalizer
    from plone.i18n.normalizer.interfaces import IURLNormalizer
    URL_NORMALIZER = True
except ImportError:
    URL_NORMALIZER = False
from Acquisition import aq_parent


from AccessControl import ClassSecurityInfo, getSecurityManager
from Acquisition import aq_base

from Products.TutorWeb.interfaces import ICourse, IOrderedTutorWebContent
from zope.interface import implements
from config import PLONE_VERSION
if PLONE_VERSION == 4:
    from Products.Archetypes import atapi
    from config import PROJECTNAME


#########################################################
## check can course code be editited??????, if not FIXME
########################################################

class Course(ATFolder):

    """
    A Course belongs to a specific Department although it can contain tutorials from any Department.
    A course has a specific code which is used together with the Department code to uniquely identify the Course.
    Students can be enrolled in a Course. A course is implemented as a folder which can contain additional files
corresponding to relevant Literature and has references to the tutorials which belong to it. It also implements
 a list of students which have enrolled in the course. Only registered users of the tutor-web can enroll in a course.
    It is implemented as an ATFolder as well as interfaces, ICourse and IOrderedTutorWebContent. 
    """
   
    schema = ATFolderSchema.copy() + Schema((
       
        StringField('title',
                required=True,
                searchable=0,
                default='Course',
                widget=StringWidget(
                    label='Title',
                    descriptio='Course title',
                    ),
                
            ),
        ReferenceField('Tutorials',
                       widget=ReferenceBrowserWidget(
                           label="Tutorials",
                           description='Tutorials which belong to the course',
                           destination=".",
                           destination_types=("Tutorial",),
                           allow_sorting=1,
                           ),
                       
                      
                       multiValued=True,
                       relationship='hasTutorial',
                       allowed_types= ("Tutorial",),
                       ),
        StringField('Students',
                vocabulary='getAvailableStudents',
                widget=InAndOutWidget(label='Students',
                    description='Students enrolled in the course.',
                      ),
                ),
        
       StringField('Code',
                  widget=StringWidget(label='Numberic Course Code',
                                      description='Specify a numberid code which is used to identify the course. For example: 101, 202',),
                  required = 1,
                  validators=('isSameCourseCode',), 
                  ),
         ComputedField('numTutorials',
                  expression='context.computeNumTutorials()',
                  widget=StringWidget(modes=('view',)),
                  ),
       
     ))
    
    __implements__ = (ATFolder.__implements__)
    implements(ICourse, IOrderedTutorWebContent)
    global_allow = True
    meta_type = 'Course'          # zope type name
    portal_type = meta_type          # plone type name
    archetype_name = 'Course' # friendly type name
    _at_rename_after_creation = True
    security = ClassSecurityInfo()
    
    def publishAll(self, typeofobject=None, originalobj=None):
        """publich content"""
        self.tryWorkflowAction("publish", ignoreErrors=True)
        
    def computeGrades(self, userId):
        """return the grade for a student based on userId"""
        # FIXME, what is userId is not a alid id???
        tutorials = self.getTutorials()
        numtutorials = len(tutorials)
        points = 0.0
        for tut in tutorials:
            points = points + tut.computeGrades(userId)
        if (numtutorials > 0):
            return float(points/numtutorials)
        else:
            return 0.0
    def addUser(self):
        """enroll the logged in user"""
        pm = self.portal_membership
        memberId = pm.getAuthenticatedMember().getId()
        member = pm.getMemberById(memberId)
        userfull = member.getProperty('fullname')
        
        pair = []
        pair.append((userfull, memberId))
        # should check if already enrolled
        studs = self.getStudents()
        if (type(studs) == type('itsastring')):
            l = []
            l.append(studs)
            l.append(memberId)
            self.getField('Students').set(self, l)
        else:
            studs.append(memberId)
            self.getField('Students').set(self, studs)
    def getEnrolledStudents(self):
        """return all enrolled students"""
        stud = self.getStudents()
        if (type(stud) == type('itsastring')):
            l = []
            l.append(stud)
            return l
        else:
            return self.getStudents()
        
    def getAvailableStudents(self):
        """return all registered members of the tutor-web"""
        # FIXME this could be far too big a list to be return in one go
        # needs to return only partly
        pm = self.portal_membership
        pair = []
        for memberId in pm.listMemberIds():
            member = pm.getMemberById(memberId)
            userfull = member.getProperty('fullname')
            pair.append((memberId, userfull))
        return DisplayList(pair)
    def getAvailableStudents2(self):
        """return all registered users of the tutor-web"""
        pm = self.portal_membership
        results = pm.listMembers()
        pair = []
        for r in results:
            pair.append((r.UID, r.Title))
        return DisplayList(pair)
    def getAvailableStudents1(self):
        """return all registered members of the tutor-web"""
        memb = self.portal_membership
        portal_users=getToolByName(self, "acl_users")
        membership = getToolByName(self, 'portal_membership')
        
        #Beware if hundreds of students this is very expensive!
        # need to use search tool
        results = membership.listMembers()
        numstuds = str(len(results))
        
        for r in results:
            r1 = r.getUser()
            userid = r1.getId() 
            userfull1 = membership.getMemberById(userid)
            userfull = userfull1.getProperty('fullname')
            
   
        pair = []
       
        for c in results:
            r = c.getUser()
            pair.append((r.getUserName(), r.getId()))
        return DisplayList(pair)
    def portalUrl(self):
        """Return the url of the site which the course belongs to """
        portal = getToolByName(self, 'portal_url').getPortalObject()
        return portal
    def isLoggedOn(self):
        """True of user has logged in to the tutor-web else Fase"""
        mtool = getToolByName(self, 'portal_membership')
        if mtool.isAnonymousUser():
            return False
        else:
            return True
    def getCourseCode(self):
        return self.getCode()
   
   
    security.declarePrivate('initializeObject')
    def initializeObject(self):
        """Called after course has been created for the first time, publish course
        and reorder department objects"""
        self.tryWorkflowAction("publish", ignoreErrors=True)
        parent = aq_parent(self)
        
        try:
            parent.orderObjects("id")
            parent.plone_utils.reindexOnReorder(parent)
        except:
            raise 'Failed to create course ' + self.getTitle() + ' not able to reorder courses'
   
    security.declarePrivate('tryWorkflowAction')
    def tryWorkflowAction(self, action, ignoreErrors=False, comment=None):
        """try to change actions for course"""
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
           '''could not establish who user is'''
           return False
    def generateNewId(self):
        """Suggest an id for this object based on Department code and Course code.
        This id is used when automatically renaming an object after creation.
        """
        parent = aq_parent(self)
        
        title = (parent.getCode() + self.getCode()).strip()
        # Can't work w/o a title
        if not title:
            return None

        # Don't do anything without the plone.i18n package
        if not URL_NORMALIZER:
            return None

        if not isinstance(title, unicode):
            charset = self.getCharset()
            title = unicode(title, charset)

        request = getattr(self, 'REQUEST', None)
        if request is not None:
            return IUserPreferredURLNormalizer(request).normalize(title)

        return queryUtility(IURLNormalizer).normalize(title)
    
    security.declareProtected(View, 'computeNumTutorials')
    def computeNumTutorials(self):
        """find number of tutorials which belong to this course"""
        refs = self.getRawTutorials()
        return len(refs)
    def updateSlideMaterial(self):
        """Update all slides for every tutorial/lecture belonging to the course."""
        tuts = self.getTutorials()
        for tut in tuts:
            tmp = tut.updateSlideMaterial()
    
    def getFullName(self, userid):
        """Return the full name of a user based on given id"""
        # FIXME what if id is not valid???
        if PLONE_VERSION == 3:

            ecq_tool = getToolByName(self, 'ecq_tool')
            return ecq_tool.getFullNameById(userid)
        else:
            parent = aq_parent(self)
            return parent.getFullName(userid)
# Register this type in Zope
if PLONE_VERSION == 3:
    registerATCTLogged(Course)
else:
    atapi.registerType(Course, PROJECTNAME)


