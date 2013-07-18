from zope.interface import implements
from zope.component import getUtility
try:
    from zope.component.hooks import getSite
except ImportError:
    from zope.app.component.hooks import getSite

from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName


from Products.TutorWeb.interfaces import IStudentInformation
from Products.TutorWeb.interfaces import IStudentLocator
import sqlalchemy as sql
from collective.lead.interfaces import IDatabase

import tempfile
import os

class StudentInformation(object):
    """Information concerning a student taking a quiz
    """
    
    implements(IStudentInformation)
    
    student_id = None
    student_username = None
    student_randomnumber = None
    student_firstname = None
    student_family = None
    student_email = None
   
    
    def __init__(self, student_username, student_randomnumber, student_firstname, student_family, student_email):
        
        self.student_username = student_username
        self.student_randomnumber = student_randomnumber
        self.student_firstname = student_firstname
        self.student_family = student_family
        self.student_email = student_email

    def addToDataBase(self):
        '''Make sure studentinformation does not already exist in database'''
        db = getUtility(IDatabase, name='tutorweb.quizquestioninformation')
        session = db.session
        try:
            session.save(self)
        except:
            '''not successful, possibly dupliate key'''
        session.flush()
        
class StudentLocator(object):
    """Find student who is participating in a quiz 
    """
    
    implements(IStudentLocator)
    
        
    def student_by_id(self, student_id):
        """Get an IStudentInformation from a student id
           Make sure student_id is part of database table
        """
        db = getUtility(IDatabase, name='tutorweb.quizquestioninformation')
        session = db.session
        studentinfo = session.query(StudentInformation).get(student_id)
        return studentinfo
        

    def student_by_randomnumber(self, student_randomnumber):
        """Get an IStudentInformation from a student randomnumber
           which should be unique across table, max one result returned
           Returns False if no record found
        """
        db = getUtility(IDatabase, name='tutorweb.quizquestioninformation')
        connection = db.connection
        
        statement = sql.select([StudentInformation.c.student_id],
                               
                                    StudentInformation.c.student_randomnumber == student_randomnumber,
                                   
                               
                               distinct=True)
        results = connection.execute(statement).fetchall()
       
        if (len(results) > 0):
            '''found student'''
            return self.student_by_id(results[0][0])
        else:
            return False
