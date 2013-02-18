from zope.interface import implements
from zope.component import getUtility
from zope.app.component.hooks import getSite

from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName


from Products.TutorWeb.interfaces import IQuestionModification
from Products.TutorWeb.interfaces import IQuestionModificationLocator
                                         
import sqlalchemy as sql
from collective.lead.interfaces import IDatabase

import tempfile
import os

class QuestionModification(object):
    """Information concerning modification time of a question used in quiz
    """
    
    implements(IQuestionModification)
    
    modification_id = None
    question_id = None
    modification_time = 0
    

    def __init__(self, question_id, modification_time):
        self.question_id = question_id
        self.modification_time = modification_time
       

    def addToDataBase(self):
        '''Make sure questionmodification does not already exist in database'''
        db = getUtility(IDatabase, name='tutorweb.quizquestioninformation')
        session = db.session
        try:
            session.save(self)
        except:
            '''not successful, possibly dupliate key'''
        session.flush()
class QuestionModificationLocator(object):
    """Find questions which have been modified used in quiz
    """
    
    implements(IQuestionModificationLocator)
    
        
    def questionmodification_by_id(self, modification_id):
        """Get an IQuestionModification from an id
           Make sure modification_id is part of table
        """
        db = getUtility(IDatabase, name='tutorweb.quizquestioninformation')
        session = db.session
        questioninfo = session.query(QuestionInformation).get(question_id)
        return questioninfo

    ##def question_by_uid(self, question_uid):
    ##    """Get an IQuestionInformation from a question unique id
    ##       Should be unique across table, max one result returned
    ##       Returns False if no record found
    ##    """
    ##    db = getUtility(IDatabase, name='tutorweb.quizquestioninformation')
    ##    connection = db.connection
        
    ##    statement = sql.select([QuestionInformation.c.question_id],
    ##     QuestionInformation.c.question_unique_id == question_uid,                   
   ##                            distinct=True)
   ##     results = connection.execute(statement).fetchall()
   ##     if (len(results) > 0):
   ##         return self.question_by_id(results[0][0])
   ##     else:
    ##        return False
    ##def question_by_path(self, question_path):
    ##    """Get an IQuesitonInformation from a question path
    ##       Returns a list of questions with path = question_path
    ##       I no questions found returns False
    ##    """
    ##     
    ##    db = getUtility(IDatabase, name='tutorweb.quizquestioninformation')
    ##    connection = db.connection
        
    ##    statement = sql.select([QuestionInformation.c.question_id],
                               
    ##                                QuestionInformation.c.question_location == question_path,
                                   
                               
     ##                          distinct=True)
     ##   results = connection.execute(statement).fetchall()
       
     ##   if (len(results) > 0):
     ##       return results
      ##  else:
##            return False
