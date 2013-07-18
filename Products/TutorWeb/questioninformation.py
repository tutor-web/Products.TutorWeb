from zope.interface import implements
from zope.component import getUtility
try:
    from zope.component.hooks import getSite
except ImportError:
    from zope.app.component.hooks import getSite

from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName


from Products.TutorWeb.interfaces import IQuestionInformation
from Products.TutorWeb.interfaces import IQuestionLocator
                                         
import sqlalchemy as sql
from collective.lead.interfaces import IDatabase

import tempfile
import os

class QuestionInformation(object):
    """Information concerning a question used in a quiz
    """
    
    implements(IQuestionInformation)
    
    question_id = None
    question_location = None
    num_asked_for = 0
    num_correct = 0
    correct_id = 0
    question_unique_id = None

    def __init__(self, question_location, num_asked_for, num_correct, correct_id, question_unique_id):
        self.question_location = question_location
        self.num_asked_for = num_asked_for
        self.num_correct = num_correct
        self.correct_id = correct_id
        self.question_unique_id = question_unique_id

    def addToDataBase(self):
        '''Make sure questioninformation does not already exist in database'''
        db = getUtility(IDatabase, name='tutorweb.quizquestioninformation')
        session = db.session
        try:
            session.save(self)
        except:
            '''not successful, possibly dupliate key'''
        session.flush()
class QuestionLocator(object):
    """Find questions used in quiz
    """
    
    implements(IQuestionLocator)
    
        
    def question_by_id(self, question_id):
        """Get an IQuestionInformation from a question id
           Make sure question_id is part of table
        """
        db = getUtility(IDatabase, name='tutorweb.quizquestioninformation')
        session = db.session
        questioninfo = session.query(QuestionInformation).get(question_id)
        return questioninfo

    def question_by_uid(self, question_uid):
        """Get an IQuestionInformation from a question unique id
           Should be unique across table, max one result returned
           Returns False if no record found
        """
        db = getUtility(IDatabase, name='tutorweb.quizquestioninformation')
        connection = db.connection
        
        statement = sql.select([QuestionInformation.c.question_id],
         QuestionInformation.c.question_unique_id == question_uid,                   
                               distinct=True)
        results = connection.execute(statement).fetchall()
        if (len(results) > 0):
            return self.question_by_id(results[0][0])
        else:
            return False
    def question_by_path(self, question_path):
        """Get an IQuesitonInformation from a question path
           Returns a list of questions with path = question_path
           I no questions found returns False
        """
         
        db = getUtility(IDatabase, name='tutorweb.quizquestioninformation')
        connection = db.connection
        
        statement = sql.select([QuestionInformation.c.question_id],
                               
                                    QuestionInformation.c.question_location == question_path,
                                   
                               
                               distinct=True)
        results = connection.execute(statement).fetchall()
       
        if (len(results) > 0):
            return results
        else:
            return False
