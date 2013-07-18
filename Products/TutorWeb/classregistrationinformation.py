from zope.interface import implements
from zope.component import getUtility
try:
    from zope.component.hooks import getSite
except ImportError:
    from zope.app.component.hooks import getSite

from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName


from Products.TutorWeb.interfaces import IClassInformation
from Products.TutorWeb.interfaces import IClassLocator
from Products.TutorWeb.interfaces import ISchoolInformation
from Products.TutorWeb.schoolinformation import SchoolInformation
from Products.TutorWeb.interfaces import ISchoolLocator
from Products.TutorWeb.interfaces import IClassRegistrationInformation
from Products.TutorWeb.interfaces import IClassRegistrationLocator

import sqlalchemy as sql
from collective.lead.interfaces import IDatabase

import tempfile
import os

class ClassRegistrationInformation(object):
    """Information concerning a student registration in class
    """
    
    implements(IClassRegistrationInformation)
    
    classregistration_id = None
    studentinformation = None
    classinformation = None
    registration_date_start = 0
    registration_date_end = 0
   
    
    def __init__(self, studentinformation, classinformation, registration_date_start, registration_date_end):
        tmpout = tempfile.mkdtemp()  
        tex_fd, tex_absname = tempfile.mkstemp(dir=tmpout, suffix='.registration-init')
        os.write(tex_fd, 'class id is ' + str(classinformation.class_id) + '\n')
        self.studentinformation = studentinformation
        self.classinformation = classinformation
        self.registration_date_start = registration_date_start
        self.registration_date_end = registration_date_end

    def addToDataBase(self):
        '''Make sure classinformation does not already exist in database'''
        tmpout = tempfile.mkdtemp()  
        tex_fd, tex_absname = tempfile.mkstemp(dir=tmpout, suffix='.registration-addtodatabase')
        os.write(tex_fd, 'before getutility\n')
        db = getUtility(IDatabase, name='tutorweb.quizquestioninformation')
        os.write(tex_fd, 'after getutitliy\n')
        session = db.session
        try:
            session.save(self)
            os.write(tex_fd, 'after save\n')
        except:
            '''not successful, possibly dupliate key'''
            os.write(tex_fd, 'except\n')
        session.flush()
        os.write(tex_fd, 'after flush\n')
class ClassRegistrationLocator(object):
    """Find registration
    """
    
    implements(IClassRegistrationLocator)
    
        
    def classregistration_by_id(self, classregistration_id):
        """Get an IClassRegistrationInformation from a class registration id
           Make sure classregistration_id is part of database table
        """
        db = getUtility(IDatabase, name='tutorweb.quizquestioninformation')
        session = db.session
        classregistrationinfo = session.query(ClassRegistrationInformation).get(classregistration_id)
        return classregistrationinfo
        
    def students_by_class(self, classinformation):
        """Return a list of all students registered in a particular class.
           Returns a list of IStudentInformation instances, false if none found
        """
        # not tested, probably does not work
        tmpout = tempfile.mkdtemp()  
        tex_fd, tex_absname = tempfile.mkstemp(dir=tmpout, suffix='.student-by_class')
        os.write(tex_fd, 'before getutility\n')
        db = getUtility(IDatabase, name='tutorweb.quizquestioninformation')
        #connection = db.connection
        session = db.session
        os.write(tex_fd,'class info: ' + str(classinformation.class_id) + '\n')
        #statement = sql.select([ClassInformation.c.class_id],
                               
        #                            (ClassInformation.c.class_name == class_name) &
        #                            (ClassInformation.c.schoolinformation.school_id == schoolinformation.school_id),
                               
        #                       distinct=True)
        #results = connection.execute(statement).fetchall()
        q = session.query(StudentInformation).join(ClassRegistrationInformation.studentinformation).join(ClassRegisrationInformation.classinformation).filter(ClassInformation.class_id==classinformation.class_id).filter(ClassRegisrationInformation.studentinformation==StudentInformation)
        results = q.all()
        if (len(results) > 0):
            '''found student'''
            return results
            
        else:
            return False

   
    
