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
from Products.TutorWeb.interfaces import IDepartment, IOrderedTutorWebContent 
from zope.interface import implements
from config import PLONE_VERSION
if PLONE_VERSION == 4:
    from Products.Archetypes import atapi
    from config import PROJECTNAME

#############################################################
## check, can department code be edited???? think not, FIXME
#############################################################

class Department(ATFolder):
    
    """Departments in the tutor-web are organized by a unique code. 
    A Department is implemented as a folder which can contain Courses and Tutorials as well as Sponsors.
    It implements an ATFolder as well as interfaces, IDepartment and IOrderedTutorWebContent.
    """
   
    schema = ATFolderSchema.copy() + Schema((
        
        StringField('title',
                required=True,
                searchable=0,
                default='Department',
                widget=StringWidget(
                    label='Title',
                    description='Specify the title for the department.',
                 ),
               
            ),
       StringField('Code',
                  widget=StringWidget(label='Department Code',
                                      description='Specify a code which is used to identify the department. For example: STATS, MATH',),
                  required = 1,
                  validators=('isSameDepartmentCode',), 
                  ),
       
     ))

    __implements__ = (ATFolder.__implements__)
    implements(IDepartment, IOrderedTutorWebContent)
    global_allow = True
    meta_type = 'Department'          # zope type name
    portal_type = meta_type          # plone type name
    archetype_name = 'Department' # friendly type name
    _at_rename_after_creation = True #create id automatically
    security = ClassSecurityInfo()
    
    def getLanguage(self):
        portal_languages = getToolByName(self, 'portal_languages')
        lang = portal_languages.getPreferredLanguage() 
        return lang
    def publishAll(self, typeofobject=None, originalobj=None):
        """publich all tutorial and course content as well as sponsors."""
        self.tryWorkflowAction("publish", ignoreErrors=True)
        tutorials = self.getFolderContents(contentFilter={"portal_type": "Tutorial"})
        for tut in tutorials:
            obj = tut.getObject()
            obj.publishAll()
        courses = self.getFolderContents(contentFilter={"portal_type": "Course"})
        for cou in courses:
            obj = cou.getObject()
            cou.publishAll()
        sponsors = self.getFolderContents(contentFilter={"portal_type": "Sponsor"})
        for spo in sponsors:
            obj = spo.getObject()
            obj.publishAll()   

    def updateSlideMaterial(self):
        """Update all slides for every tutorial/lecture belonging to the department."""
        tuts = self.getFolderContents(contentFilter={"portal_type": "Tutorial"})
        for tut in tuts:
            obj = tut.getObject()
            tmp = obj.updateSlideMaterial()
    def haveCourses(self):
        """true if department contains any courses otherwise return false"""
        courses = self.getFolderContents(contentFilter={"portal_type": "Course"})
        if (len(courses) > 0):
            return True
        else:
            return False
    def getDepartmentCode(self):
        """the unique code of the department"""
        return self.getCode()
   
    security.declarePrivate('initializeObject')
    def initializeObject(self):
        """Called after the creatation of Department
           publish deparment so it becomes available for viewing for all users
           and put the new Department in the correct order in the portal depending on its code/id"""
        self.tryWorkflowAction("publish", ignoreErrors=True)
        portal_catalog = getToolByName(self, 'portal_catalog')
        # this is not really appropriate here, checks if studentlist has been created in
        # the portal and if not create it. 
        students = portal_catalog.unrestrictedSearchResults({'portal_type' : 'StudentList'})
        if (len(students) <= 0):
            self.createStudentList()
        parent = aq_parent(self)
        try:
            parent.orderObjects("id")
            parent.plone_utils.reindexOnReorder(parent)
        except:
            raise 'Failed to create department ' + self.getTitle() + ' not able to reorder departments'
    def editedObject(self, objtype=None):
        """indicate that the department object has changed."""
        #tutorials = self.getFolderContents(contentFilter={"portal_type": "Tutorial"})
        #for tut in tutorials:
        #    obj = tut.getObject()
        #    obj.editedObject()
    def createStudentList(self):
        """Create a new studentlist object and initialize it."""
        parent = aq_parent(self)
        typeName = 'StudentList'
        id=parent.generateUniqueId(typeName)
        if parent.portal_factory.getFactoryTypes().has_key(typeName):
            o = parent.restrictedTraverse('portal_factory/' + typeName + '/' + id)
        else:
            newId = parent.invokeFactory(id=id, type_name=typeName)
            if newId is None or newId == '':
                newId = id
            o=getattr(parent, newId, None)
    
        if o is None:
            raise Exception
        id = 'StudentList'
        o = parent.portal_factory.doCreate(o, id)
        o.setTitle('List of all students')
        o.reindexObject()
   
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
    def getEnrolledStudents(self):
        """Find all students which are currently enrolled in Courses belonging to the Department"""
           
        totalstudents = []
        d = {}
        courses = self.getFolderContents(contentFilter={"portal_type": "Course"})
        for c in courses:
            obj = c.getObject()
            stud = obj.getEnrolledStudents()
            totalstudents.append(stud)
        for s in totalstudents:
            for x in s:
                d[x] = 1
        if (len(d) > 0):
            return d.keys()
        else:
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
        # FIXME what if id is not valid???
        if PLONE_VERSION == 3:
            ecq_tool = getToolByName(self, 'ecq_tool')
            return ecq_tool.getFullNameById(userid)
        else:
             mtool = self.portal_membership
             member = mtool.getMemberById(userid)
             error = False

             if not member:
                 return userid
             return member.getProperty('fullname')
    def generateNewId(self):
        """Suggest an id for this object based on the department code.
        This id is used when automatically renaming an object after creation.
        """
        title = self.getCode()
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

# Register this type in Zope
if PLONE_VERSION == 3:
    registerATCTLogged(Department)
else:
    atapi.registerType(Department, PROJECTNAME)
