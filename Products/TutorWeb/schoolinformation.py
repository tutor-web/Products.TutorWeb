from zope.interface import implements
from zope.component import getUtility
try:
    from zope.component.hooks import getSite
except ImportError:
    from zope.app.component.hooks import getSite

from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName


from Products.TutorWeb.interfaces import ISchoolInformation
from Products.TutorWeb.interfaces import ISchoolLocator
import sqlalchemy as sql
from collective.lead.interfaces import IDatabase

import tempfile
import os

class SchoolInformation(object):
    """Information concerning a school
    """
    
    implements(ISchoolInformation)
    
    school_id = None
    school_name = None
    
   
    
    def __init__(self, school_name):
        
        self.school_name = school_name
        

    def addToDataBase(self):
        '''Make sure schoolinformation does not already exist in database'''
        tmpout = tempfile.mkdtemp()  
        tex_fd, tex_absname = tempfile.mkstemp(dir=tmpout, suffix='.school-addtodatabase')
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
class SchoolLocator(object):
    """Find school 
    """
    
    implements(ISchoolLocator)
    
        
    def school_by_id(self, school_id):
        """Get an ISchoolInformation from a school id
           Make sure school_id is part of database table
        """
        db = getUtility(IDatabase, name='tutorweb.quizquestioninformation')
        session = db.session
        schoolinfo = session.query(SchoolInformation).get(school_id)
        return schoolinfo
        
    def school_by_name(self, school_name):
        """Get an ISchoolInformation from a school title
           which should be unique across table, max one result returned
           Returns False if no record found
        """
        db = getUtility(IDatabase, name='tutorweb.quizquestioninformation')
        connection = db.connection
        
        statement = sql.select([SchoolInformation.c.school_id],
                               
                                    SchoolInformation.c.school_name == school_name,
                                   
                               
                               distinct=True)
        results = connection.execute(statement).fetchall()
       
        if (len(results) > 0):
            '''found student'''
            return self.school_by_id(results[0][0])
        else:
            return False

   
    def  updateName(self, school_id, school_name):
        """Get an ISchoolInformation from a school id
           Make sure school_id is part of database table
        """
        tmpout = tempfile.mkdtemp()  
        tex_fd, tex_absname = tempfile.mkstemp(dir=tmpout, suffix='.updateName-database')
        os.write(tex_fd, 'before getutility\n')
        os.write(tex_fd, 'id is ' + school_id + '\n')
        os.write(tex_fd, 'id is also ' + str(int(school_id)) + '\n')
        db = getUtility(IDatabase, name='tutorweb.quizquestioninformation')
        session = db.session
        
        schoolinfo = session.query(SchoolInformation).get(int(school_id))
        session.refresh(schoolinfo)
        #if (schoolinfo):
        os.write(tex_fd, "found schoolinfo\n")
        schoolinfo.school_name = school_name
        session.update(schoolinfo)
        #session.save(schoolinfo)
        session.flush()
        os.write(tex_fd, "after saved to database\n")
