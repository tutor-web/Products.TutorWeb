from zope.interface import Interface
from zope import schema

from zope.app.container.constraints import contains

#from optilux.cinemacontent import CinemaMessageFactory as _
from Products.CMFPlone import PloneMessageFactory as _

# Exceptions

class ReservationError(Exception):
    """Exception raised if there is an error making a reservation
    """

    def __init__(self, message):
        Exception.__init__(self, message)
        self.error_message = message

#Content types

class IDepartment(Interface):
    """An folder objects which contains object belong to a tutorial such as lectures and sponsors.
    """
    
    title = schema.TextLine(title=_(u"Object title"),
                            required=True)

class ICourse(Interface):
    """An folder objects which contains object belong to a tutorial such as lectures and sponsors.
    """
    
    title = schema.TextLine(title=_(u"Object title"),
                            required=True)

class ISchool(Interface):
    """An folder object containing classes.
    """
    contains('Products.Tutorweb.interfaces.IClass')
    title = schema.TextLine(title=_(u"Object title"),
                            required=True)

    description = schema.TextLine(title=_(u"Description"),
                                  description=_(u"A short summary of this folder"))
class IClass(Interface):
    """An object which describes classes belonging to a specific school.
    """
    title = schema.TextLine(title=_(u"Object title"),
                            required=True)

     #description = schema.TextLine(title=_(u"Description"),
     #                             description=_(u"A short summary of this folder"))
class ISchoolFolder(Interface):
    """An folder object containing schools.
    """
    contains('Products.Tutorweb.interfaces.ISchool')
    title = schema.TextLine(title=_(u"Object title"),
                            required=True)

    description = schema.TextLine(title=_(u"Description"),
                                  description=_(u"A short summary of this folder"))

class ITutorial(Interface):
    """An folder objects which contains object belong to a tutorial such as lectures and sponsors.
    """
    
    title = schema.TextLine(title=_(u"Object title"),
                            required=True)

class ILecture(Interface):
    """An folder objects which contains object belong to a tutorial such as lectures and sponsors.
    """
    
    title = schema.TextLine(title=_(u"Object title"),
                            required=True)
class ISlide(Interface):
    """An folder objects which contains object belong to a tutorial such as lectures and sponsors.
    """
    
    title = schema.TextLine(title=_(u"Object title"),
                            required=True)
class IQuestion(Interface):
    """An folder objects which contains object belong to a tutorial such as lectures and sponsors.
    """
    
    title = schema.TextLine(title=_(u"Object title"),
                            required=True)

class IQuiz(Interface):
    """An folder objects which contains object belong to a tutorial such as lectures and sponsors.
    """
    
    title = schema.TextLine(title=_(u"Object title"),
                            required=True)
class IResult(Interface):
    """An folder objects which contains object belong to a tutorial such as lectures and sponsors.
    """
    
    title = schema.TextLine(title=_(u"Object title"),
                            required=True)
class IQuestionResult(Interface):
    """An folder objects which contains object belong to a tutorial such as lectures and sponsors.
    """
    
    title = schema.TextLine(title=_(u"Object title"),
                            required=True)
class IBaseQuestionSelectionParameters(Interface):
    """An object which contains information conerning how questions are selected in a quiz.
    """
    
    title = schema.TextLine(title=_(u"Object title"),
                            required=True)
class ISponsor(Interface):
    """An object which contains contains information related to sponsors, displayed on the site.
    """
    
    title = schema.TextLine(title=_(u"Object title"),
                            required=True)

class IStudentList(Interface):
    """An object which contains informatio concerning a student taking a test.
    """   
    title = schema.TextLine(title=_(u"Object title"),
                            required=True)


class IExtraDataFile(Interface):
    """An folder objects which contains object belong to a tutorial such as lectures and sponsors.
    """
    
    title = schema.TextLine(title=_(u"Object title"),
                            required=True)
class IPrintable(Interface):
    """An object which contains content wich can be printed to a pdf document.
    Should it be part of tutorial????
    """
    
    title = schema.TextLine(title=_(u"Object title"),
                            required=True)
    
class IOrderedTutorWebContent(Interface):
    """TutorWeb ordered content and by default is published, or available for viewing to anonymous or logged on users
    """
    
    title = schema.TextLine(title=_(u"Object title"),
                            required=True)
######################################################3
# Entities found in the tutor-web database

class IQuestionModification(Interface):
    """Information concerning a questions modification times
    """
    
    modification_id = schema.Int(title=_(u"Question modification identifier"),
                              description=_(u"A unique id for the modification"),
                              required=True,
                              readonly=True)
    
    question_id = schema.TextLine(title=_(u"Question which was modified"),
                           description=_(u"The question object which was modified"),
                           required=True,
                           readonly=True)
    modification_time = schema.Date(title=_(u"Date/Time when question with id=question_id was modified"),
                         )
class IQuestionInformation(Interface):
    """Information concerning a question used in a quiz
    """
    
    question_id = schema.Int(title=_(u"Question identifier"),
                              description=_(u"A unique id for the question"),
                              required=True,
                              readonly=True)
    
    question_location = schema.TextLine(title=_(u"Question location"),
                           description=_(u"The url of the question (/dep/tut/lec/q)"),
                           required=True,
                           readonly=True)
                           
    num_asked_for = schema.Int(title=_(u"Number of times apperead in quiz"),
                         )
    
    num_correct = schema.Int(title=_(u"Number of times correctly answered"),
                                   description=_(u"Number of times question has been correctly answered by a student."))
    correct_id = schema.Int(title=_(u"Id of correct answer to the question"),
                                   description=_(u"Id - default 0 - to the correct answer."))

class IStudentInformation(Interface):
    """Information concerning a student
    """
    
    student_id = schema.Int(title=_(u"Student identifier"),
                              description=_(u"A unique id for a student"),
                              required=True,
                              readonly=True)
    
    student_code = schema.TextLine(title=_(u"Student username"),
                           required=True,
                           readonly=True)
    student_randomnumber = schema.TextLine(title=_(u"Student random number"),
                           required=True,
                           readonly=True)                      
    student_firstname = schema.TextLine(title=_(u"Student first name"),
                         )

    student_familyname = schema.TextLine(title=_(u"Student family name"),
                         )
   
    student_email = schema.TextLine(title=_(u"Student e-mail"),)
class ISchoolInformation(Interface):
    """Information concerning a school
    """
    
    school_id = schema.Int(title=_(u"School identifier"),
                              description=_(u"A unique id for a school"),
                              required=True,
                              readonly=True)
    school_name = schema.TextLine(title=_(u"School name"),
                           required=True,
                           readonly=True)
class IClassInformation(Interface):
    """Information concerning a class
    """
    
    class_id = schema.Int(title=_(u"Class identifier"),
                              description=_(u"A unique id for a class"),
                              required=True,
                              readonly=True)
    schoolinformation = schema.Object(title=_(u"School"),
                           schema=ISchoolInformation,      
                           required=True,
                           readonly=True)
    class_name = schema.TextLine(title=_(u"Class name"),
                           required=True,
                           readonly=True)
    email = schema.TextLine(title=_(u"Email"),
                           required=True,
                           readonly=True)
class IClassRegistrationInformation(Interface):
    """Information concerning a student registering in class
    """
    
    classregisration_id = schema.Int(title=_(u"Class registration identifier"),
                              description=_(u"A unique id for a class registration"),
                              required=True,
                              readonly=True)
    studentinformation = schema.Object(title=_(u"Student"),
                           schema=IStudentInformation,      
                           required=True,
                           readonly=True)
    classinformation = schema.Object(title=_(u"Class"),
                           schema=IClassInformation,      
                           required=True,
                           readonly=True)
    registration_date_start = schema.Date(title=_(u"Date/Time when class registration starts"),)
    registration_date_end = schema.Date(title=_(u"Date/Time when class registration ends"),
                         )
class IQuizInformation(Interface):
    """Information concerning a student
    """
    
    quiz_id = schema.Int(title=_(u"Quiz identifier"),
                              description=_(u"A unique id for a question requested by a student."),
                              required=True,
                              readonly=True)
    
    studentinformation = schema.Object(title=_(u"Student"),
                           schema=IStudentInformation,      
                           required=True,
                           readonly=True)
    questioninformation = schema.Object(title=_(u"Question"),
                           schema=IQuestionInformation,       
                           required=True,
                           readonly=True)                      
    quiz_location = schema.TextLine(title=_(u"Lecture Url"),
                         )

    quiz_time = schema.Date(title=_(u"Date/Time when question requested"),
                         )
    student_answer = schema.Int(title=_(u"Id of student answer"),
                                   description=_(u"Id of the answer the student gave."),)
    answertime = schema.Date(title=_(u"Date/Time when question answered"),)

                            
# Database services
class IQuestionLocator(Interface):
    """find question information from database"""
    def question_by_id(question_id):
        """Get a IQuestionInformation from a question id
        """
class IQuestionModificationLocator(Interface):
    """find modified question from database"""
    def questionmodification_by_id(modification_id):
        """Get a IQuestionModification from a question id
        """
class IStudentLocator(Interface):
    """find student information from database"""
    def student_by_id(student_id):
        """Get a IStudentInformation from a student id"""
    def student_by_randomnumber(student_randomnumber):
        """Get a IStudentInformation from a student id""" 
class ISchoolLocator(Interface):
    """find school information from database"""
    def school_by_id(school_id):
        """Get a ISchoolInformation from a school id"""
class IClassLocator(Interface):
    """find class information from database"""
    def class_by_id(class_id):
        """Get a IClassInformation from a class id"""
class IClassRegistrationLocator(Interface):
    """find class registration information from database"""
    def classregistration_by_id(classregistration_id):
        """Get a IClassRegistrationInformation from a class registrationid"""
class IQuizLocator(Interface):
    """find quiz information from database"""
    def quiz_by_id(quiz_id):
        """Get a IQuizInformation from a quiz id"""
class ITakeQuiz(Interface):
    """update database with new quiz information"""
    def __call__(self, quizinfo):
        """Take quiz
        """
##################################################################3
# Database connectivity
        
class IDatabaseSettings(Interface):
    """Database connection settings.
    """
    
    drivername = schema.ASCIILine(title=_(u"Driver name"),
                                  description=_(u"The database driver name"),
                                  default='mysql',
                                  required=True)

    hostname = schema.ASCIILine(title=_(u"Host name"),
                                description=_(u"The database host name"),
                                default='localhost',
                                required=True)
                                
    port = schema.Int(title=_(u"Port number"),
                      description=_(u"The database port number. Leave blank to use the default."),
                      required=False)
                                
    username = schema.ASCIILine(title=_(u"User name"),
                                description=_(u"The database user name"),
                                required=True)

    password = schema.Password(title=_(u"Password"),
                                description=_(u"The database password"),
                                required=False)
                                
    database = schema.ASCIILine(title=_(u"Database name"),
                                description=_(u"The name of the database on this server"),
                                required=True)
