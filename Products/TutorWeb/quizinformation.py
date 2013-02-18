from zope.interface import implements
from zope.component import getUtility
from zope.app.component.hooks import getSite

from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName


from Products.TutorWeb.interfaces import IQuizInformation
from Products.TutorWeb.interfaces import IStudentInformation
from Products.TutorWeb.interfaces import IQuestionInformation
from Products.TutorWeb.interfaces import IQuizLocator
from Products.TutorWeb.interfaces import ITakeQuiz
from Products.TutorWeb.studentinformation import StudentInformation
from Products.TutorWeb.questioninformation import QuestionInformation
import sqlalchemy as sql
from collective.lead.interfaces import IDatabase

import tempfile
import os
from types import *

class QuizInformation(object):
    """Information concerning a quiz taken by students
    """
    
    implements(IQuizInformation)
    
    quiz_id = None
    studentinformation = None
    questioninformation = None
    quiz_location = None
    quiz_time = 0
    student_answer = -1
    answer_time = 0

    def __init__(self, studentinformation, questioninformation, quiz_location, quiz_time, student_answer, answer_time):
        
        self.studentinformation = studentinformation
        self.questioninformation = questioninformation
        self.quiz_location = quiz_location
        self.quiz_time = quiz_time
        if ('no answer' in str(student_answer)):
            self.student_answer = -1
        else:
            self.student_answer = student_answer
        self.answer_time = answer_time

class QuizLocator(object):
    """Find quiz information
    """
    implements(IQuizLocator)
    
    def questions_by_student(self, lecture, student):
    #def questions_by_student(self, lecture, student, from_date, to_date):
        '''Return a list of all questions requested by a student in
           a particular lecture (dates not implemented between specified dates).
           Returns a list of IQuizInformation instances
        '''
       
        db = getUtility(IDatabase, name='tutorweb.quizquestioninformation')
        session = db.session
        
        # the mysql selection of questions by a student and quiz_location
        #SELECT quiz_information.quiz_id, student_information.student_username, question_information.question_location FROM quiz_information LEFT JOIN student_information ON quiz_information.student_id=student_information.student_id LEFT JOIN question_information ON quiz_information.question_id=question_information.question_id WHERE student_information.student_username='audbjorg' AND quiz_information.quiz_location='/tutor-web...';
       
        #filtering criterion is comparable to the WHERE clause of a select.     
        #QuizInformation.studentinformation, QuizInformation.questioninformation are comparable to what would be used in a sql ON clause in JOIN   
        q = session.query(QuizInformation).join(QuizInformation.studentinformation).join(QuizInformation.questioninformation).filter(StudentInformation.student_username==student).filter(QuizInformation.quiz_location==lecture)
    
        #Return the results represented by this Query as a list.
        #This results in an execution of the underlying query.
        results = q.all()
        return results
    def quiz_by_id(self, quiz_id):
        """Get an IQuizInformation from a question id
        """
        
        db = getUtility(IDatabase, name='tutorweb.quizquestioninformation')
        session = db.session
        
        quizinfo = session.query(QuizInformation).get(quiz_id)
        
        return quizinfo

class TakeQuiz(object):
    """Write quiz/question/student information to database
    """
    
    implements(ITakeQuiz)
    def __call__(self, quizinfo):
        """Take quiz
        """
        
        db = getUtility(IDatabase, name='tutorweb.quizquestioninformation')
        
        session = db.session
        session.refresh(quizinfo.questioninformation)
       
        if (str(quizinfo.student_answer) == str(quizinfo.questioninformation.correct_id)):
            '''correct answer'''
            quizinfo.questioninformation.num_correct = quizinfo.questioninformation.num_correct + 1
           
        quizinfo.questioninformation.num_asked_for = quizinfo.questioninformation.num_asked_for + 1
        session.update(quizinfo.questioninformation)
        session.save(quizinfo)
        session.flush()
        
