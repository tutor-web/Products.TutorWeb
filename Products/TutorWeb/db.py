from persistent import Persistent

from zope.interface import implements
from zope.component import getUtility

from collective.lead import Database
from Products.TutorWeb.interfaces import IDatabaseSettings

from sqlalchemy.engine.url import URL
from sqlalchemy             import Table, Column, ForeignKey
from sqlalchemy.orm import mapper
from sqlalchemy.ext import activemapper
from sqlalchemy.orm import relation
#from sqlalchemy.orm import relationship
from sqlalchemy import schema
from sqlalchemy import *
#from sqlalchemy import Table, relation

from Products.TutorWeb.allocationinformation import AllocationInformation
from Products.TutorWeb.questioninformation import QuestionInformation
from Products.TutorWeb.studentinformation import StudentInformation
from Products.TutorWeb.schoolinformation import SchoolInformation
from Products.TutorWeb.classinformation import ClassInformation
from Products.TutorWeb.classregistrationinformation import ClassRegistrationInformation
from Products.TutorWeb.quizinformation import QuizInformation
from Products.TutorWeb.questionmodification import QuestionModification


class TutorWebQuizDatabaseSettings(Persistent):
    """Database connection settings
    
    We use raw fields here so that we can more easily use a zope.formlib
    form in the control panel to configure it. This is registered as a
    persistent local utility, with name 'tutorweb.quizinformation', which is
    then used by collective.lead.interfaces.IDatabase to find connection settings.
    """
    
    implements(IDatabaseSettings)
    
    drivername = 'mysql'
    hostname = 'localhost'
    port = None
    username = ''
    password = None
    database = ''


class TutorWebQuizDatabase(Database):
    """The quiz database - registered as a utility providing
    collective.lead.interfaces.IDatabase and named 'tutorweb.quizinformation'
    """
    
    @property
    def _url(self):
        settings = getUtility(IDatabaseSettings)
        return URL(drivername=settings.drivername, username=settings.username,
                   password=settings.password, host=settings.hostname,
                   port=settings.port, database=settings.database)
    
    def _setup_tables(self, metadata, tables):
        """Map the database structure to SQLAlchemy Table objects
        """
            
        tables['question_information'] = Table('question_information', metadata, autoload=True)
        tables['student_information'] = Table('student_information', metadata, autoload=True)
        tables['school_information'] = Table('school_information', metadata, autoload=True)
        tables['class_information'] = Table('class_information', metadata, autoload=True)
        tables['classregistration_information'] = Table('classregistration_information', metadata, autoload=True)
        tables['quiz_information'] = Table('quiz_information', metadata, autoload=True)
        tables['allocation_information'] = Table('allocation_information', metadata, autoload=True)
        tables['question_modification'] = Table('question_modification', metadata, autoload=True) 
    def _setup_mappers(self, tables, mappers):
        """Map the database Tables to SQLAlchemy Mapper objects
        """
        mappers['question_information'] = mapper(QuestionInformation, tables['question_information'],
                               properties = {
                                            'questionschanged' : relation(QuestionModification, backref='question')})
        mappers['student_information'] = mapper(StudentInformation, tables['student_information'],
                               properties = {
               'studentquestions' : relation(QuizInformation, backref='student')
               #keywords = relationship('Keyword', secondary=post_keywords, backref='posts')

 })
        mappers['school_information'] = mapper(SchoolInformation, tables['school_information'],
                #               properties = {
               #'schools' : relation(SchoolInformation, backref='school')
               #keywords = relationship('Keyword', secondary=post_keywords, backref='posts')

#}
                )
        mappers['class_information'] = mapper(ClassInformation, tables['class_information'],
                               properties = {
               'schoolinformation' : relation(SchoolInformation),
               #keywords = relationship('Keyword', secondary=post_keywords, backref='posts')

               }
                )
        mappers['classregistration_information'] = mapper(ClassRegistrationInformation, tables['classregistration_information'],
                               properties = {
                                            'studentinformation' : relation(StudentInformation),
                                            'classinformation' : relation(ClassInformation),
                                            })
        mappers['quiz_information'] = mapper(QuizInformation, tables['quiz_information'],
                               properties = {
                                            'questioninformation' : relation(QuestionInformation),
                                            'studentinformation' : relation(StudentInformation),
                                            })
        mappers['allocation_information'] = mapper(AllocationInformation, tables['allocation_information'],
                               properties = {
                                            'question_information' : relation(QuestionInformation),
                                            'student_information' : relation(StudentInformation),
                                            })
        mappers['question_modification'] = mapper(QuestionModification, tables['question_modification'],
                                        
                                           
                                            )
