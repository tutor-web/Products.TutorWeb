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
import sqlalchemy as sql
from collective.lead.interfaces import IDatabase

import tempfile
import os

class ClassInformation(object):
    """Information concerning a class
    """
    
    implements(IClassInformation)
    
    class_id = None
    schoolinformation = None
    class_name = None
    email = None
    
    def __init__(self, schoolinformation, class_name, email):
        #tmpout = tempfile.mkdtemp()  
        #tex_fd, tex_absname = tempfile.mkstemp(dir=tmpout, suffix='.class-init')
        #os.write(tex_fd, 'school id is ' + str(schoolinformation.school_id) + '\n')
        self.schoolinformation = schoolinformation
        self.class_name = class_name
        self.email = email

    def addToDataBase(self):
        '''Make sure classinformation does not already exist in database'''
        #tmpout = tempfile.mkdtemp()  
        #tex_fd, tex_absname = tempfile.mkstemp(dir=tmpout, suffix='.class-addtodatabase')
        #os.write(tex_fd, 'before getutility\n')
        db = getUtility(IDatabase, name='tutorweb.quizquestioninformation')
        #os.write(tex_fd, 'after getutitliy\n')
        session = db.session
        try:
            session.save(self)
            #os.write(tex_fd, 'after save\n')
        except:
            '''not successful, possibly dupliate key'''
            #os.write(tex_fd, 'except\n')
        session.flush()
        #os.write(tex_fd, 'after flush\n')
class ClassLocator(object):
    """Find class 
    """
    
    implements(IClassLocator)
    
        
    def class_by_id(self, class_id):
        """Get an IClassInformation from a class id
           Make sure class_id is part of database table
        """
        db = getUtility(IDatabase, name='tutorweb.quizquestioninformation')
        session = db.session
        classinfo = session.query(ClassInformation).get(class_id)
        return classinfo
        
    def class_by_name(self, class_name, schoolinformation):
        """Get an IClassInformation from a class title and school
           which should be unique across table, max one result returned
           Returns False if no record found
        """
        #tmpout = tempfile.mkdtemp()  
        #tex_fd, tex_absname = tempfile.mkstemp(dir=tmpout, suffix='.class-by_name')
        #os.write(tex_fd, 'before getutility\n')
        db = getUtility(IDatabase, name='tutorweb.quizquestioninformation')
        #connection = db.connection
        session = db.session
        #os.write(tex_fd,'stud info: ' + str(schoolinformation.school_id) + '\n')
        #statement = sql.select([ClassInformation.c.class_id],
                               
        #                            (ClassInformation.c.class_name == class_name) &
        #                            (ClassInformation.c.schoolinformation.school_id == schoolinformation.school_id),
                               
        #                       distinct=True)
        #results = connection.execute(statement).fetchall()
        q = session.query(ClassInformation).join(ClassInformation.schoolinformation).filter(SchoolInformation.school_id==schoolinformation.school_id).filter(ClassInformation.class_name==class_name)
        results = q.all()
        if (len(results) > 0):
            '''found class'''
            #os.write(tex_fd,'found classinformation\n')
            #os.write(tex_fd, 'class id from result ' + str(results[0].class_id) + '\n')
            #return self.class_by_id(results[0].class_id)
            return results[0]
        else:
            return False

   
    def  updateName(self, class_id, class_name, email):
        """Get an IClassInformation from a class id
           Make sure class_id is part of database table
        """
        #tmpout = tempfile.mkdtemp()  
        #tex_fd, tex_absname = tempfile.mkstemp(dir=tmpout, suffix='.updateClass_Name-database')
        #os.write(tex_fd, 'before getutility\n')
        #os.write(tex_fd, 'id is ' + class_id + '\n')
        #os.write(tex_fd, 'id is also ' + str(int(class_id)) + '\n')
        db = getUtility(IDatabase, name='tutorweb.quizquestioninformation')
        session = db.session
        
        classinfo = session.query(ClassInformation).get(long(class_id))
        session.refresh(classinfo)
        #if (schoolinfo):
        #os.write(tex_fd, "found classinfo\n")
        classinfo.class_name = class_name
        classinfo.email = email
        session.update(classinfo)
        #session.save(schoolinfo)
        session.flush()
        #os.write(tex_fd, "after saved to database\n")
