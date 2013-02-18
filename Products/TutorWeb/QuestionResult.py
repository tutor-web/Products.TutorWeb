from Products.Archetypes.public import *
from Products.Archetypes.public import OrderedBaseFolder
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.folder import ATFolderSchema
from AccessControl import ClassSecurityInfo
from Products.CMFCore import permissions as CMFCorePermissions
import transaction
from config import *
from permissions import *
from tools import *
from Products.Archetypes.public import Schema, BooleanField, BooleanWidget, \
     IntegerField,  ReferenceField, IntegerWidget, StringField, TextField, \
     TextAreaWidget, StringWidget, SelectionWidget, RichWidget, ReferenceWidget
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget \
     import ReferenceBrowserWidget
from Products.Archetypes.utils import DisplayList
from Products.Archetypes import atapi
from Products.CMFCore.permissions import View
from zope.component import getUtility
from Products.TutorWeb.interfaces import IStudentLocator
from Products.TutorWeb.interfaces import IQuestionLocator
from Products.TutorWeb.interfaces import ITakeQuiz
from Products.TutorWeb.quizinformation import QuizInformation
from Products.TutorWeb.studentinformation import StudentInformation
from Products.TutorWeb.questioninformation import QuestionInformation
from Products.TutorWeb.questionmodification import QuestionModification
from Products.TutorWeb.interfaces import IQuestionResult  
from zope.interface import implements                                              

from ZPublisher.HTTPRequest import FileUpload
from htmlentitydefs import entitydefs
import re
import os
import shutil
import tempfile
from difflib import *
from Acquisition import aq_parent
try:
    from plone.i18n.normalizer.interfaces import IUserPreferredURLNormalizer
    from plone.i18n.normalizer.interfaces import IURLNormalizer
    URL_NORMALIZER = True
except ImportError:
    URL_NORMALIZER = False


from string import *
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata 
from time import strftime
import time

from datetime import datetime, timedelta 

if PLONE_VERSION == 4:
    from Products.Archetypes import atapi
    from config import PROJECTNAME
    
class QuestionResult(ATFolder):
    """A results to a specific question for a student taking a specific quiz."""
   
    
    
    schema = ATFolderSchema.copy() + Schema((
        
        StringField('title',
                required=True,
                searchable=0,
                default='Result to question',
                widget=StringWidget(
                    label='Title',
                    description='The main title of the tutorial.',
                    i18n_domain='plone'),
               
            ),
        
        StringField('chosenquestid',
                       default='',
                     widget=StringWidget(description='id of chosen quiz question', 
                                         visible={'edit':'invisible', 'view':'invisible',}, ),
                  ),
        
        
        StringField('chosenquestpath',
                       default='',
                     widget=StringWidget(description='path to where question comes from', 
                                         visible={'edit':'invisible','view':'invisible'}, ),
                  ),
        
       BooleanField('openquest',
                       default=0,
                     widget=BooleanWidget(description='True if student already has requested a question but not answered it.', 
                                         visible={'edit':'invisible','view':'invisible'}, ),
                  ),

       StringField('anslist',
                       default='0',
                     widget=StringWidget(description='The students selected answer.', 
                                         visible={'edit':'invisible','view':'invisible'}, ),
                  ),

       StringField('candidateans',
                       default='-1',
                     widget=StringWidget(description='the students submitted answer', 
                                         visible={'edit':'invisible', 'view':'invisible'}, ),
                  ),
        StringField('suggestedans',
                       default='',
                     widget=StringWidget(description='Suggested answers to student.', 
                                         visible={'edit':'invisible', 'view':'invisible'}, ),
                  ),
        StringField('correctans',
                       default='',
                     widget=StringWidget(description='correctanswer.', 
                                         visible={'edit':'invisible', 'view':'invisible'}, ),
                  ),
        StringField('lecturepath',
                       default='',
                     widget=StringWidget(description='lecture quiz path.', 
                                         visible={'edit':'invisible', 'view':'invisible'}, ),
                  ),
        StringField('studid',
                       default='',
                     widget=StringWidget(description='id of student.', 
                                         visible={'edit':'invisible', 'view':'invisible'}, ),
                  ),
        StringField('timeofquest',
                       default='',
                     widget=StringWidget(description='time when student gets question.', 
                                         visible={'edit':'invisible', 'view':'invisible'}, ),
                  ),
        StringField('quizresultinfo',
                       default='',
                     widget=StringWidget(description='Result of quiz for logging purposes.', 
                                         visible={'edit':'invisible','view':'invisible' }, ),
                  ),
        
     ))
    __implements__ = (ATFolder.__implements__)
    implements(IQuestionResult)

    global_allow = False
    meta_type = 'QuestionResult'          # zope type name
    portal_type = meta_type          # plone type name
    archetype_name = 'QuestionResult' # friendly type name
    #_at_rename_after_creation = True  #automatically create id
    security = ClassSecurityInfo()

    #chosenquestionid = ''
    chosenquestionid = atapi.ATFieldProperty('chosenquestid')
    #chosenquestionpath = ''
    chosenquestionpath = atapi.ATFieldProperty('chosenquestpath')
    #openquestion = False
    openquestion = atapi.ATFieldProperty('openquest')
    
    NO_ANSWER = ['-1'] # an arbitrary object
    # the student's selected answer
    
    #answerlist = '0'
    answerlist = atapi.ATFieldProperty('anslist')
    # the students submitted answer
    #candidateAnswer = ['-1']
    candidateAnswer = atapi.ATFieldProperty('candidateans')
    # the answers the student got
    #suggestedAnswer = []
    suggestedAnswer = atapi.ATFieldProperty('suggestedans')
    #correct = []
    correct = atapi.ATFieldProperty('correctans')
    lecquizpath = atapi.ATFieldProperty('lecturepath')
    studentid = atapi.ATFieldProperty('studid')
    #timenow = strftime("%d-%m-%Y %H:%M:%S")
    timenow = atapi.ATFieldProperty('timeofquest')
    quizinfo = atapi.ATFieldProperty('quizresultinfo')
    #def __init__(self, oid=None, **kwargs):
    #    self.changed = True
    #    ATFolder.__init__(self, oid, **kwargs)
    def setLecPath(self, p):
        self.lecquizpath = p
    def setNewQuestion(self, suggestedanswer, correctids, questpath, qid):
        '''set new question info'''
        #self.suggestedAnswer = suggestedanswer
        tmp = ''
        counter = 0
        num = len(suggestedanswer)
        while (counter < num):
            tmp = tmp + suggestedanswer[counter]
            if (counter < num-1):
                tmp = tmp + '\t'
            else:
                tmp = tmp
            counter = counter + 1
        self.setSuggestedans(tmp)
        #self.chosenquestionpath = questpath
        self.setChosenquestpath(questpath)
        #self.timenow = strftime("%d-%m-%Y %H:%M:%S")
        #self.setTimeofquest(strftime("%d-%m-%Y %H:%M:%S"))                    
        self.setTimeofquest(datetime.now())
        #self.openquestion = True
        self.setOpenquest(1)
        #self.chosenquestionid = qid
        self.setChosenquestid(qid)
        #self.correct = correctids
        tmp = ''
        counter = 0
        num = len(correctids)
        while (counter < num):
            tmp = tmp + correctids[counter]
            if (counter < num-1):
                tmp = tmp + '\t'
            else:
                tmp = tmp
            counter = counter + 1
        self.setCorrectans(tmp)
        self.setQuizresultinfo(self.getStudid() + '\t' + str(self.getTimeofquest()) + '\t' + ('/'.join(self.getLecturepath())) + '\t' + ('/'.join(self.getChosenquestpath())) + '\t' + "['"+ str(self.getCorrectans())+"']" + '\t')
        #self.writetolog()
    def getQuestionId(self):
        #return self.chosenquestionid
        return self.getChosenquestid()
    def setStudentId(self, sid):
        #self.studentid = sid
        self.setStudid(sid)
    def getQuizInfo(self):
        return self.getQuizresultinfo()
    def getCorrectAnswer(self):
        #return self.correct
        return self.getCorrectans().split('\t')
    def gotAnswer(self):
        #self.openquestion = False
        self.setOpenquest(0)
        self.reindexObject()
        ##self._p_changes = True
        #self.writetolog()
    security.declareProtected(PERMISSION_STUDENT, 'writetolog')
    def writetolog(self):
        # FIXME !!!!
        # add code to check if dir exists and then create..
        logdir = productdir + '/log'
        if (not (os.path.exists(logdir))):
            os.mkdir(logdir)
        f = open(logdir+'/questionandanswer.txt','a')
        #qr = self.getStudentQuestionResult()
        #qresults = self.getFolderContents(contentFilter={"portal_type": "QuestionResult"})
        #qr = qresults[0].getObject()
        text = self.getQuizInfo()
        text = text + str(datetime.now()) + "\n"
        f.write(text)
        f.close()
    def hasSubmittedQuestion(self):
        
        #return self.openquestion
        return self.getOpenquest()
    def setSelectedAnswer(self, value):
        #self.answerlist = value
        self.setAnslist(value)
        self.reindexObject()
    def getSelectedAnswer(self):
        #return self.answerlist
        return self.getAnslist()
    def getSuggestedAnswer(self):
        
        
        #return self.suggestedAnswer
        tempa = self.getSuggestedans()
       
        return self.getSuggestedans().split('\t')
        
    def getCandidateAnswer(self):
        
        #return self.candidateAnswer
        return self.getCandidateans().split('\t')
    def updateDatabase(self, new, origquestion):
        '''write quiz information to database'''
        # start by finding student information
        
        studlocator = getUtility(IStudentLocator)
        studentinfo = studlocator.student_by_randomnumber(self.getStudid())
        if (not studentinfo):
            '''student has not been added database'''    
            email = 'not known'
            firstname = ''
            familyname = ''
            loginname = ''
            membership = self.portal_membership
            member = membership.getAuthenticatedMember() 
            if member:
                loginname = member.getUserName()
                email = member.getProperty('email')
                fullname = member.getProperty('fullname')
                tempname = fullname.split()
                if (len(tempname) > 1):
                    familyname = tempname[1]
                    firstname = tempname[0]
                elif (len(tempname) == 1):
                    familyname = fullname
                    
            student = StudentInformation(loginname, self.getStudid(), firstname, familyname, email)
            student.addToDataBase()
            # now find the student just added
            studentinfo = studlocator.student_by_randomnumber(self.getStudid())
        
        # find the question from the database
        questlocator = getUtility(IQuestionLocator)
        questioninfo = questlocator.question_by_uid(self.getChosenquestid()) 
        if (not questioninfo):
            '''question has not been added to database'''
            qpath = '/'.join(self.getChosenquestpath())
            # number of time askefor has already been updated
            # will be updated again in TakeQuiz, so subtract by one
            try:
                int(self.getCorrectans())
                
                corrans = int(self.getCorrectans())
                
            except:
                #just setting coorect answer to BIG number, indicating error in the database'
                corrans = 333
            question = QuestionInformation(qpath, (origquestion.numaskedfor-1),  origquestion.numcorrect, corrans, self.getChosenquestid())
            question.addToDataBase()
            # get the newly added question
            questioninfo = questlocator.question_by_uid(self.getChosenquestid())
            # also add question to question-modification table
            qm = QuestionModification(questioninfo.question_id, datetime.now())
            qm.addToDataBase()
        # now add the quiz info
        takequiz = getUtility(ITakeQuiz)
        takequiz(QuizInformation(studentinfo, questioninfo, ('/'.join(self.getLecturepath())), self.getTimeofquest(), new, datetime.now()))

    def setCandidateAnswer(self, new, origquestion):
        '''update candidate answer and write information to database'''
        temp = ''
        num = len(new)
        counter = 0
        l = self.getSuggestedans().split('\t')
        while (counter < num):
            if new[counter] == "no answer":
                temp = temp + new[counter]
            else:
                temp = temp + l[int(new[counter])-1]
            #temp = temp + new[counter]
            if (counter < num-1):
                temp = temp + '\t'
            else:
                temp = temp
            counter = counter + 1
        #tmpout = tempfile.mkdtemp()
        #tex_fd, tex_absname = tempfile.mkstemp(dir=tmpout, suffix='.setCandidateAns')
        #os.write(tex_fd, 'Set answer from quiz\n')
        #os.write(tex_fd, temp)    
        ##transaction.begin()
        if self.getCandidateans() != temp:
            self.setCandidateans(temp)
        
        self.setQuizresultinfo(self.getStudid() + '\t' + str(self.getTimeofquest()) + '\t' + ('/'.join(self.getLecturepath())) + '\t' + ('/'.join(self.getChosenquestpath())) + '\t' + "['" + str(self.getCorrectans()) + "']" + '\t' + '['+ temp + ']'
 + '\t')
        self.reindexObject()
        # need to write to database
        if new[0] == "no answer":
            self.updateDatabase(new, origquestion)

        else:
            self.updateDatabase(str(l[int(new[0])-1]), origquestion)
       
        ##transaction.commit()
    def unsetCandidateAnswer(self):
        
        #self.setCandidateAnswer(self.NO_ANSWER)
        self.setCandidateans('-1')
        self.reindexObject()
    def haveCandidateAnswer(self):
        
        #return self.candidateAnswer is not self.NO_ANSWER
        return self.getCandidateans() is not '-1'
   
     
# Register this type in Zope
if PLONE_VERSION == 3:
    registerATCTLogged(QuestionResult)
else:
    atapi.registerType(QuestionResult, PROJECTNAME)
