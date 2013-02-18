from config import *
from permissions import *
from tools import *

from Products.Archetypes.public import StringField, StringWidget
from Products.DataGridField.DataGridField import DataGridField
from Products.DataGridField.DataGridWidget import DataGridWidget
from Products.DataGridField.Column import Column
from Products.DataGridField.SelectColumn import SelectColumn

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


from Products.TutorWeb.interfaces import IStudentList
from zope.interface import implements

from Products.Archetypes import atapi
from config import PROJECTNAME

from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content import base

StudentTestingSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

        StringField('title',
                required=True,
                searchable=0,
                default='List of Students',
                widget=StringWidget(
                    label='Title',
                    description='title',
                    ),
                
            ),
         DataGridField('StudentIdList',
                searchable=True, # One unit tests checks whether text search works
                widget = DataGridWidget(label='StudentIds',
                     columns= {
                    "studentid" : Column("Student Id"),
                    "randomnumber" : Column("Random id number"),
                    "email": Column("Student email"),
                }
                    ),
                               
                columns=('studentid', 'randomnumber', 'email'),
                
            ),  
          
        ))


#########################################################
## check can course code be editited??????, if not FIXME
########################################################

class StudentTesting(base.ATCTContent):

    """
    A Course belongs to a specific Department although it can contain tutorials from any Department.
    A course has a specific code which is used together with the Department code to uniquely identify the Course.
    Students can be enrolled in a Course. A course is implemented as a folder which can contain additional files
corresponding to relevant Literature and has references to the tutorials which belong to it. It also implements
 a list of students which have enrolled in the course. Only registered users of the tutor-web can enroll in a course.
    It is implemented as an ATFolder as well as interfaces, ICourse and IOrderedTutorWebContent. 
    """
   
    schema = StudentTestingSchema
    
    ##__implements__ = (ATFolder.__implements__)
    ##implements(ICourse, IOrderedTutorWebContent)
    implements(IStudentList)
    global_allow = True
    meta_type = 'StudentTesting'          # zope type name
    portal_type = meta_type          # plone type name
    archetype_name = 'StudentTesting' # friendly type name
    _at_rename_after_creation = True
    security = ClassSecurityInfo()
    
    def publishAll(self, typeofobject=None, originalobj=None):
        """publich content"""
        self.tryWorkflowAction("publish", ignoreErrors=True)
            
   
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
    def getAllList(self):
        return self.getStudentIdList()    
    def addStudent(self, studid):
        
        grid = self.getWrappedField('StudentIdList')
        rowrandom = grid.search(self, studentid=studid)
        
        if (len(rowrandom) <=0):
            ''' add new student to list'''
            # generate a random number
            
            randnum = str(random())[2:]
            rowrandom = grid.search(self, randomnumber=randnum)
            while(len(rowrandom) > 0):
                randnum = str(random())[2:]
                rowrandom = grid.search(self, randomnumber=randnum)
            # find student e-mail
            member = self.portal_membership.getMemberById(studid)
            studentemail = member.getProperty('email', None)
            rows = []
            temprow = {}
            temprow['studentid'] = studid
            temprow['randomnumber'] = randnum
            temprow['email'] = studentemail
            rows.append(temprow)
            original = self.getStudentIdList()
            list = original + tuple(rows)
            self.setStudentIdList(list)
            return randnum
        else:
            return rowrandom[0]['randomnumber']

    def getStudentIdNumber(self, studid):
        
        grid = self.getWrappedField('StudentIdList')
        rowrandom = grid.search(self, studentid=studid)
        
        if (len(rowrandom) <= 0):
            
            return self.addStudent(studid)
        else:
            return rowrandom[0]['randomnumber']   
# Register this type in Zope
#registerATCTLogged(Course)
atapi.registerType(StudentTesting, PROJECTNAME)
