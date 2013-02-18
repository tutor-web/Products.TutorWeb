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

from Products.TutorWeb.interfaces import IClass
from Products.TutorWeb.interfaces import IClassLocator
from Products.TutorWeb.interfaces import ISchoolLocator
from Products.TutorWeb.interfaces import IStudentLocator
from Products.TutorWeb.interfaces import ISchool

from Products.TutorWeb.classinformation import ClassInformation
from Products.TutorWeb.classregistrationinformation import ClassRegistrationInformation
from Products.TutorWeb.schoolinformation import SchoolInformation
from Products.TutorWeb.studentinformation import StudentInformation
from Products.Archetypes.interfaces import IObjectInitializedEvent, IObjectEditedEvent
from OFS.interfaces import IObjectClonedEvent, IObjectWillBeRemovedEvent, IObjectWillBeMovedEvent
from zope.component import adapter, getMultiAdapter, getUtility

from zope.interface import implements
from config import PLONE_VERSION
if PLONE_VERSION == 4:
    from Products.Archetypes import atapi
    from config import PROJECTNAME



#########################################################
## check can course code be editited??????, if not FIXME
########################################################
#expiry = obj.ExpirationDate()

class Class(ATFolder):

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
                default='Class name',
                widget=StringWidget(
                    label='Title',
                    description='Class name',
                    ),
                 validators=('isSameClassName',), 
            ),
        StringField('classDatabaseId',
             widget=StringWidget(label="Database Id",
                    visible={'edit':'invisible', 'view':'invisible'},
             ), ),
        ReferenceField('Tutorials',
                       widget=ReferenceBrowserWidget(
                           label="Tutorials",
                           description='Tutorials which belong to the class',
                           destination=".",
                           destination_types=("Tutorial",),
                           allow_sorting=1,
                           ),
                       
                       #allow_sorting=1,
                       multiValued=True,
                       relationship='hasTutorial',
                       allowed_types= ("Tutorial",),
                       ),
        StringField('Students',
                vocabulary='getAvailableStudents',
                widget=InAndOutWidget(label='Students',
                    description='Students enrolled in the course.',
                    visible={'edit':'invisible', 'view':'invisible'},
                      ),
                ),
        
        StringField('Instructor',
                #vocabulary='getAvailableStudents',
                default = '',    
                widget=StringWidget(label='Instructor',
                    description='Instructor of the class.',
                      ),
                ),
         StringField('ContactInformation',
                #vocabulary='getAvailableStudents',
                default = '',
                widget=StringWidget(label='Contact Information',
                    description='How to contact instructor of the class.',
                      ),
                ),
         ComputedField('numTutorials',
                  expression='context.computeNumTutorials()',
                  widget=StringWidget(modes=('view',)),
                  ),
       
     ))
    
    __implements__ = (ATFolder.__implements__)
    implements(IClass)
    global_allow = True
    meta_type = 'Class'          # zope type name
    portal_type = meta_type          # plone type name
    archetype_name = 'Class' # friendly type name
    _at_rename_after_creation = True
    security = ClassSecurityInfo()
    
    def publishAll(self, typeofobject=None, originalobj=None):
        """publich content"""
        self.tryWorkflowAction("publish", ignoreErrors=True)
        
    def computeGrades(self, userId):
        """return the grade for a student based on userId"""
        # FIXME, what is userId is not a valid id???
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
        if (memberId in studs):
            return userfull + "already enrolled in " + self.getTitle()
        if (type(studs) == type('itsastring')):
            l = []
            l.append(studs)
            l.append(memberId)
            self.getField('Students').set(self, l)
        else:
            studs.append(memberId)
            self.getField('Students').set(self, studs)
        updated = self.updateDatabase(member, memberId)
        
        if updated:
            tit = self.getTitle()
            if not isinstance(tit, unicode):
                charset = self.getCharset()
                tit = unicode(tit, charset)
                
            return userfull + " has been enrolled in " + tit
        else:
            return "could not update database"
        ##return "bla"
    def updateDatabase(self, member, candidateId):
        #start by checking if student already registered in tutorweb
        # has been allocated a random number, if not register
        # then add to database if needed.
        
        portal_catalog = getToolByName(self, 'portal_catalog')
       
        students = portal_catalog.unrestrictedSearchResults({'portal_type' : 'StudentList'})
       
        if (len(students) > 0):
           
            numlists = str(len(students))
            
            objid = self.unrestrictedTraverse(str(students[0].getPath()), None)
            
            ranid = objid.addStudent(candidateId)
            
            studlocator = getUtility(IStudentLocator)
            studentinfo = studlocator.student_by_randomnumber(ranid)
            if (not studentinfo):
                '''student has not been added database'''    
                email = 'not known'
                firstname = ''
                familyname = ''
                loginname = ''
                #membership = self.portal_membership
                #member = membership.getAuthenticatedMember() 
                if member:
                    loginname = member.getUserName()
                    email = member.getProperty('email')
                    fullname = member.getProperty('fullname')
                    tempname = fullname.split()
                    if (len(tempname) > 1):
                        familyname = tempname[1]
                        firstname = tempname[0]
                    elif (len(tempname) == 1):
                        familyname = fullname
                    
                student = StudentInformation(candidateId, ranid, firstname, familyname, email)
                student.addToDataBase()
            # now find the student just added
            studentinfo = studlocator.student_by_randomnumber(ranid)
            # now find classinfo
            classlocator = getUtility(IClassLocator)
            # should check if databaseid is not empty string
            classinfo =  classlocator.class_by_id(int(self.getClassDatabaseId()))
            #check if have date
            start = self.getEffectiveDate()
            stop = self.getExpirationDate()
            # maybe should set default values in initialize
            try:
                '''check if start has been set'''
                i = len(start)
            except:
                start = 0
            try:
                '''check if stop has been set'''
                i = len(stop)
            except:
                stop = 0
            registration = ClassRegistrationInformation(studentinfo, classinfo, start, stop)
            registration.addToDataBase()
            return True
        else:
            return False
    def getEnrolledStudents(self):
        """return all enrolled students"""
        stud = self.getStudents()
        if (type(stud) == type('itsastring')):
            l = []
            l.append(stud)
            sortedlist = l.sort()
            return sortedlist
        else:
            sortedlist = self.getStudents().sort()
            return self.getStudents().sort()
    def getInstructors(self):
        """return all instructors"""
        stud = self.getInstructor()
        if (type(stud) == type('itsastring')):
            l = []
            l.append(stud)
            return l
        else:
            return stud   
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
        """Return the url of the site which the class belongs to """
        portal = getToolByName(self, 'portal_url').getPortalObject()
        return portal
    def isLoggedOn(self):
        """True of user has logged in to the tutor-web else Fase"""
        mtool = getToolByName(self, 'portal_membership')
        if mtool.isAnonymousUser():
            return False
        else:
            return True
    
   
   
    security.declarePrivate('initializeObject')
    def initializeObject(self):
        """Called after class has been created for the first time."""
        self.tryWorkflowAction("publish", ignoreErrors=True)
        '''add school to database when school is created'''
        # get correctschoolinformation
        parent = aq_parent(self)
        schoollocator = getUtility(ISchoolLocator)
        schoolinformation = schoollocator.school_by_id(int(parent.getDatabaseId()))
        # set char set might have for example icelandic letters in title
        tit = self.getTitle()
        if not isinstance(tit, unicode):
            charset = self.getCharset()
            tit = unicode(tit, charset)
            self.setTitle(tit)
        email = self.getContactInformation()
        if not isinstance(email, unicode):
            charset = self.getCharset()
            email = unicode(email, charset)
            self.setTitle(email)
    
        # create class and add to database
        myclass = ClassInformation(schoolinformation, tit, email)
        myclass.addToDataBase()
        #add database id
        self.setClassDatabaseId(str(myclass.class_id))
            
        parent = aq_parent(self)
        
        try:
            parent.orderObjects("id")
            parent.plone_utils.reindexOnReorder(parent)
        except:
            raise 'Failed to create class ' + self.getTitle() + ' not able to reorder classes'
    def editedObject(self, objtype=None):
        '''if class name changed, change also in database'''
        # Need to make sure that class name is unique before 
        # looking for class by name - have added a validator
        # first get handle on the school from sql
        # well if copy/paste school then the title will not change
       
        #classlocator = getUtility(IClassLocator)
        #classlocator.updateName(self.getClassDatabaseId(), self.getTitle(), self.getContactInformation())
        tit = self.getTitle()
        if not isinstance(tit, unicode):
            charset = self.getCharset()
            tit = unicode(tit, charset)
            self.setTitle(tit)
        # set char set 
        email = self.getContactInformation()
        if not isinstance(email, unicode):
            charset = self.getCharset()
            email = unicode(email, charset)
            self.setContactInformation(email)
        
        classlocator = getUtility(IClassLocator)
        
        classlocator.updateName(self.getClassDatabaseId(), tit, email)
    security.declarePrivate('tryWorkflowAction')
    def tryWorkflowAction(self, action, ignoreErrors=False, comment=None):
        """try to change actions for class"""
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
   
    
    security.declareProtected(View, 'computeNumTutorials')
    def computeNumTutorials(self):
        """find number of tutorials which belong to this class"""
        refs = self.getRawTutorials()
        return len(refs)
    def updateSlideMaterial(self):
        """Update all slides for every tutorial/lecture belonging to the class."""
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
    registerATCTLogged(Class)
else:
    atapi.registerType(Class, PROJECTNAME)

@adapter(IClass, IObjectInitializedEvent)
def add_class_to_database(obj, event):
    obj.initializeObject()
@adapter(IClass, IObjectClonedEvent)
def copy_class_to_database(obj, event):
    # MUST disallow copy/paste
    # find out how!!!
    event.object.editedObject()
@adapter(IClass, IObjectEditedEvent)
def edit_class_to_database(obj, event):
   obj.editedObject()
