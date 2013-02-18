#
#Must use a different way of finding current question
# the last question in last is not working
# or if I sort it first by date
# can do that - OK
# maybe I will do that
import time
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
     IntegerField,  ReferenceField, FloatField, IntegerWidget, StringField, TextField, \
     ImageField, TextAreaWidget, StringWidget, SelectionWidget, RichWidget, ReferenceWidget, ImageWidget
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget \
     import ReferenceBrowserWidget
from Products.Archetypes.utils import DisplayList
from Products.Archetypes import atapi
from Products.CMFCore.permissions import View

from ZPublisher.HTTPRequest import FileUpload
from htmlentitydefs import entitydefs
import re
import os
import shutil
import tempfile
from zope.event import notify
from difflib import *
from Acquisition import aq_parent
try:
    from plone.i18n.normalizer.interfaces import IUserPreferredURLNormalizer
    from plone.i18n.normalizer.interfaces import IURLNormalizer
    URL_NORMALIZER = True
except ImportError:
    URL_NORMALIZER = False


from string import *
from zope.component import adapter

from Products.Archetypes import atapi
from config import PROJECTNAME

from Products.TutorWeb import DEBUG
from datetime import datetime, timedelta
#from Products.TutorWeb.interfaces import INewQuizQuestionEvent, NewQuizQuestionEvent
     
## try: # New CMF  
##     from Products.CMFCore import permissions as CMFCorePermissions
##     from Products.CMFCore.permissions import AddPortalContent
   
## except: # Old CMF  
##     from Products.CMFCore import CMFCorePermissions
##     from Products.CMFCore.CMFCorePermissions import AddPortalContent
    
class QuizResult(ATFolder):
    """Keeps together all the questions results for a specific student from a quiz in a specific lecture."""
   
    
    
    schema = ATFolderSchema.copy() + Schema((
        
        StringField('title',
                required=True,
                searchable=0,
                default='Quiz result',
                widget=StringWidget(
                    label='Title',
                    description='The main title of the tutorial.',
                    i18n_domain='plone'),
               
            ),
        BooleanField('openquest',
                     default=0,
                      widget=BooleanWidget(visible={'edit':'invisible', 'view':'invisible'}, ),),
        BooleanField('haveanswer',
                     default=0,
                      widget=BooleanWidget(visible={'edit':'invisible', 'view':'invisible'}, ),
                  ),
                     
        ImageField('CurrentQuestionImage',
                   #original_size=(600,600),
                   #max_size=(600,600),
                   sizes={ 'mini' : (80,80),
                           'normal' : (200,200),
                            'big' : (100,100),
                            'maxi' : (500,500),
                           },
                   widget=ImageWidget(label='quis question image',
                                      description='Image for the current question, displayed to the right of main text of the slide. Possible formats for uploaded images are: png, gif and jpeg.', 
                                      #macro='tutorwebimage',
                             # condition ='object/isImageFormat',
                                       )),
        ReferenceField('StudentQuestions',
                    #vocabulary="getAvailableCourses",
                    widget=ReferenceWidget(
                           label="quiz question",
                           description='A question student has been asked',
                           destination=".",
                           #destination_types=("QuestionResult",),
                           #visible={'edit':'invisible'},
                           
                           ),
                       multiValued=True,
                       relationship='hasQuestion',
                       allowed_types= ("InvisibleQuestion",),
                        
                   ),  

        ReferenceField('CurrentQuestion',
                    #vocabulary="getAvailableCourses",
                    widget=ReferenceWidget(
                           label="quiz question which is open",
                           description='A question student is being asked',
                           destination=".",
                           #destination_types=("QuestionResult",),
                           #visible={'edit':'invisible'},
                           
                           ),
                       multiValued=False,
                       relationship='hasOpenQuiz',
                       allowed_types= ("InvisibleQuestion",),
                        
                   ),  
        ComputedField('grade',
                  expression='context.computeGrade()',
                  widget=StringWidget(visible={'edit':'invisible','view':'invisible' },),
          
            ),
        IntegerField('totalattempts',
                     default='0',
                     widget=IntegerWidget(description='Number of times students has submitted a questions to quiz.', 
                                         visible={'edit':'invisible','view':'invisible'}, ),
                  ),
         IntegerField('correctattempts',
                        default='0',
                     widget=IntegerWidget(description='Number of times students has submitted a questions to quiz.', 
                                         visible={'edit':'invisible', 'view':'invisible'}, ),
                  ),
         FloatField('totscore',
                     default=0.0,
                     widget=IntegerWidget(description='total score so far.', 
                                       visible={'edit':'invisible','view':'invisible' },   ),
                  ),
           StringField('lasteightgrades',
                       default='[]',
                     widget=StringWidget(description='Number of times students has submitted a questions to quiz.', 
                                         visible={'edit':'invisible','view':'invisible' }, ),),
         StringField('studentRandId',
                       default='',
                     widget=StringWidget(description='random generated id to identify student.', 
                                         visible={'edit':'invisible','view':'invisible' }, ),
        ),
        StringField('studentId',
                       default='',
                     widget=StringWidget(description='login id of student.', 
                                         visible={'edit':'invisible','view':'invisible' }, ),                   
       ),

          #StringField('chosenquestid',
          #             default='',
          #           widget=StringWidget(description='Number of times students has submitted a questions to quiz.', 
          #                               visible={'view':'invisible', 'edit':'invisible'}, ),
          #        ),

       #StringField('chosenquestpath',
       #                default='',
       #              widget=StringWidget(description='Number of times students has submitted a questions to quiz.', 
        #                                 visible={'view': 'invisible', 'edit':'invisible'}, ),
         #         ),
       
     ))
    __implements__ = (ATFolder.__implements__)
    
    global_allow = False
    meta_type = 'QuizResult'          # zope type name
    portal_type = meta_type          # plone type name
    archetype_name = 'QuizResult' # friendly type name
    #_at_rename_after_creation = True  #automatically create id
    security = ClassSecurityInfo()
    
    # ATT: Make sure this work when create from twmigrate.py
    changed = True
    studentgrade = atapi.ATFieldProperty('grade')
    totalscore = atapi.ATFieldProperty('totscore')
    scoresofar = []
    # REMEMBER check if reversed or not when displayed????????
    lasteight = atapi.ATFieldProperty('lasteightgrades')
    quizattempts = atapi.ATFieldProperty('totalattempts')
    correctquizattempts = atapi.ATFieldProperty('correctattempts')
    chosenquestionid = atapi.ATFieldProperty('chosenquestid')
    chosenquestionpath = atapi.ATFieldProperty('chosenquestpath')
    #openquestion = atapi.ATFieldProperty('openquest')
    
    def __init__(self, oid=None, **kwargs):
        self.changed = True
        ATFolder.__init__(self, oid, **kwargs)
    
    # Must add:

    # getVocabulary is now in Lecture.py
    # returns the answers
    # getSelectedItem() in Lecture.py
    # questionIsInline in Lecture.py
    # isCorrect(item) in Lecture.py
    #
    # get chosen question already here
    #   then must transformR(True)
    #   then transformquizquestion
    #   getQuestionData()
    #   inlineAnswer()
    #  getQuestImg and getQuestionImageTag
    #
    def getQuestionResultForQuestion(self, question):
        qresults = question.getFolderContents(contentFilter={"portal_type": "QuestionResult"})
        return qresults[0].getObject()
    def getVocabulary(self):
        """return the possible answers formatted as vocabulary"""
        question = self.getCurrentQuestion()
        if (question):
            qr = self.getQuestionResultForQuestion(question)
            suggestedAnswerIds = (qr.getSuggestedAnswer())
            idl = DisplayList()
            ans = question.getAnswerDisplay().values()
       
            for id in suggestedAnswerIds:
                idl.add(id, ans[int(id)])
            return Vocabulary(idl, self, None)
        else:
            '''bad error no open question'''
            return ''
        
    def isCorrect(self, item):
        question = self.getCurrentQuestion()
        if (question):
            answers = question.getAnswerList()
            for row in answers:
                if (row['answerid'] == str(item)):
                    if (row['correct'] == '1'):
                        return True
            return False
        else:
            return False
    def startQuiz(self):
        '''student has asked for a question in quiz'''
        parent = aq_parent(self)
        lec = aq_parent(parent)
        if (DEBUG):
            tmpout = tempfile.mkdtemp()
            tex_fd, tex_absname = tempfile.mkstemp(dir=tmpout, suffix='.startQuiz')
            os.write(tex_fd, 'Starting selection of quiz question\n')
        
        hasq = self.openQuiz()
        msg = []
        msg.append(True)
        # taken care of that - set no answer and written to log
        # close that question
        if (hasq):
            msg.append('question replaced')
        else:
            msg.append('A question has been saved to quiz')
        msg.append(self.Creator())
        #parent = aq_parent(self)
        if (DEBUG):
            usable_question = lec.getQuizQuestion(tex_fd, True)
        else:
            usable_question = lec.getQuizQuestion()
        if (usable_question[0] == -1):
            '''no questions available'''
            msg[0] = False
            msg[1] = 'Sorry but no questions available in Lecture ' + usable_question[1] + '. Please contact your instructor if you believe you have found an error in the system, including the given error message'
            return msg
        elif(usable_question[0] == False):
            '''False could not create result for student'''
            msg[0] = False
            msg[1] = 'Fatal error could not start quiz in Lecture ' + usable_question[1] + '. Please contact your instructor if you believe you have found an error in the system, including the error message'
            return msg
        elif (usable_question[0] == -2):
            '''no answers set for the question'''
            msg[0] = False
            msg[1] = 'Sorry but no answers have been set for the selected question: ' + usable_question[2] + ' located in ' + usable_question[3] + '. Please try again or contact your instructor if you believe you have found and error in the system, including this message'
            return msg
        elif (usable_question[0] == -3):
            '''no answer set as correct in question'''
            msg[0] = False
            msg[1] = 'Sorry but no correct answer has been set to the selected question: ' + usable_question[2] + ' located in ' + usable_question[3] + '. Please try again or contact your instructor if you believe you have found an error in the system, including this error message'
            return msg
                
        else:
            '''have a valid question'''
            origquest = usable_question[0]
            if (DEBUG):
                os.write(tex_fd, '###########################\n')
                os.write(tex_fd, 'question used in quiz\n')
                os.write(tex_fd, str(origquest.getId()) + '\n')
                os.write(tex_fd, str(origquest.getRawQuestion()) + '\n')
        
            # set as invisble question with questionresult
            newq = self.createQuestion()
            qr = newq.createQuestionResult()
            # this info is repeated, but leave for now
            # FIXME
            if (len(self.getStudentRandId()) > 0):
                qr.setStudentId(self.getStudentRandId())
            else:
                # find from other location
                quiz = aq_parent(self)
                lec = aq_parent(quiz)
                tut = aq_parent(lec)
                dep = aq_parent(tut)
                mysite = aq_parent(dep)
                studentlistobj = mysite.getFolderContents(contentFilter={"portal_type": "StudentList"})
                if (len(studentlistobj) > 0):
                    studentlist = studentlistobj[0].getObject()
                    studentlist.addStudent(self.Creator())
                    randid = studentlist.getStudentIdNumber(self.Creator())
                    self.setStudentRandId(randid)
                    qr.setStudentId(randid)
            qr.setLecPath(lec.getPhysicalPath())
            # have created a quiz question with corresponding questuionresults
            # now set information from original question to quiz question
            # I probably don't need all the info but lets start by that
            questiontext = origquest.getRawQuestion()
            texttype = origquest.question.getContentType()
            mutated = origquest.getAnswerList()
            answertype = origquest.getAnswerFormat()
            newq.setQuestionText(questiontext, mimetype=texttype)
            newq.setAnswerList(mutated)
            newq.setAnswerFormat(answertype)
        
            # if its r or r/latex questions then need to be updated
            if (texttype == 'text/r' or texttype == 'text/r-latex'):
                newq.initializeObject()
               
            else:    
                newq.ans = origquest.ans
                newq.NOTAinQuestion = origquest.NOTAinQuestion
                newq.inlineanswer = origquest.inlineanswer
                newq.transformrquestion = origquest.transformrquestion
                newq.setQuizQuestion(origquest.getRawQuizQuestion(), mimetype=origquest.quizQuestion.getContentType())
                # add the image if any
                # ATT
                # asuming r-images do not contain image
                # would be generated within the r code itself?
                # HMMMMM
                img = origquest.getQuestionImage()
                newq.setQuestionImage(img)
            # add image url if any
            imgurl = origquest.getImageUrl()
            if (len(imgurl) > 0):
                newq.setImageUrl(imgurl)
            newq.numcorrect = origquest.numcorrect
            newq.numaskedfor = origquest.numaskedfor
            # need additionally to set:
            # quisQuestion
            
            
            newq.setQuizQuestionExplanation(origquest.getRawQuizQuestionExplanation(), mimetype='text/html')
           
           
            newq.setOriginalQuestion(origquest)
            
            # instead of using original question
            # use the invisible question
            suggestedanswers = newq.makeNewTest()
            grid = newq.getWrappedField('AnswerList')
            correctAnswerIds = []
            rowcorrect = grid.search(newq, correct='1')
            for row in rowcorrect:
                correctAnswerIds.append(row['answerid'])
            
            qr.setNewQuestion(suggestedanswers, correctAnswerIds, origquest.getPhysicalPath(), origquest.UID())
            
            
            if (len(suggestedanswers) > 0):
                '''set the first element in value as selected
                answer, anything will do'''
                qr.setSelectedAnswer(suggestedanswers[0])
                 
            else:
                '''what to do bad error'''
                msg[0] == False
                msg[1] = 'Fatal error'
                return msg
            qr.reindexObject()
            newq.reindexObject()
            self.reindexObject()
            if (DEBUG):
                os.write(tex_fd, str(newq.getId()) + '\n')
                os.write(tex_fd, str(newq.getRawQuestion()) + '\n')
                os.close(tex_fd)
            
            return msg
        
    def setTotalscore(self, val):
        self.setTotscore(val)
        #self.totalscore = val
    def setLastEightList(self, val):
        tmp = []
        for s in val:
            tmp.append(int(s))
        self.scoresofar = tmp
        tmpstr0 = str(val)
        tmpstr1 = tmpstr0.replace(',', '')
        self.setLasteightgrades(tmpstr1)
    def setLastEight(self, val):
        # value is a string
       
        tmpstr0 = val.replace(',', '')
        tmpstr1 = tmpstr0.replace('[', '')
        tmpstr2 = tmpstr1.replace(']','')
        scorelist = tmpstr2.split()
       
        tmp = []
        for s in scorelist:
            if (len(s) > 0):
                tmp.append(int(s))
        self.scoresofar = tmp
        self.setLasteightgrades(tmpstr0)
    def setScoresofar(self, val):
        self.scoresofar = val
    def getCreator(self):
        return self.Creator()
    def getSelectedAnswerToQuestion(self, question):
        #qr =  self.getStudentQuestionResult() 
        qr = self.getQuestionResultForQuestion(question)
        value = qr.getSelectedAnswer()
        #value = qr.getCandidateAnswer()
       
        answerdisplay = question.getAnswerDisplay()
        #index = int(value[0])
       
        return answerdisplay.getValue(value)
    def getSelectedItem(self):
        question = self.getCurrentQuestion()
        qr = self.getQuestionResultForQuestion(question)
        return qr.getSelectedAnswer()
    def questionIsInline(self):
        question = self.getCurrentQuestion()
        if (question > 0):
            return question.inlineAnswer()
        else:
            return False
    def getCandidateAnswerInTest(self):
        
        question = self.getCurrentQuestion()
        if (question):
            qr = self.getQuestionResultForQuestion(question)
            return (qr.getCandidateAnswer())
    security.declareProtected(PERMISSION_STUDENT, 'getOriginalQuestion')
    def getOriginalQuestion(self, quest):
        return quest.getOriginalQuestion()
        
    security.declareProtected(PERMISSION_STUDENT, 'getChosenQuestion')
    def getChosenQuestion(self):
        # always assume we are dealing with the last question
        question = self.getCurrentQuestion()
        if (question):
            return question
        else:
            return False
       
       
    def computeGrade(self):
        return float(self.getTotscore())
    def getSuggestedAnswerInTest(self):
        qr = self.getQuestionResultForQuestion(question)
        return (qr.getSuggestedAnswer())
    def setSelectedAnswerInTest(self, value):
        question = self.getCurrentQuestion()
        if (question):
            qr = self.getQuestionResultForQuestion(question)
            qr.setSelectedAnswer(value)
            qr.reindexObject()
    def unsetCandidateAnswerToQuestion(self):
        #qr =  self.getStudentQuestionResult()
        #qresults = self.getFolderContents(contentFilter={"portal_type": "QuestionResult"})
        #qr = qresults[0].getObject()
        question = self.getCurrentQuestion()
        if (question):
            qr = self.getQuestionResultForQuestion(question)
            qr.unsetCandidateAnswer()
            qr.reindexObject()
    def setCandidateAnswerToQuestion(self, value):
        question = self.getCurrentQuestion()
        if (question):
            qr = self.getQuestionResultForQuestion(question)               
            qr.gotAnswer()
            origquestion = question.getOriginalQuestion()
            qr.setCandidateAnswer([value], origquestion)
            qr.writetolog()
            correctans = qr.getCorrectAnswer()
            l = qr.getSuggestedans().split('\t')
            v = l[int(value)-1]
            if v in correctans:
                # this can lead ot database conflict error   
                origquestion.numcorrect = origquestion.numcorrect + 1
                correct = 1
            else:
                correct = 0
                #qr.gotAnswer()
            self.setScore(correct)
            qr.reindexObject()
    def computeAverageGrade(self):
        '''return average grade of student'''
        # compute the average grade of the student for this lecture
        # Average grade is at the moment computed according to points given
        # for the last eight answers:
        # Correct answer gives +1 points
        # Wrong answer gives -0.5 points
        # no answers given or all answers incorrect, grade starts at -0.5
        # Highest average grade is +1, all answers correct       
        # r = number correct answers of last m= 8 answers
        # average grade = ((-0.5)*(m-r)+r)/m
        # later more complex methods of computing grades need to be specified.
    
        numcorrect = 0
        for i in self.scoresofar:
            if float(i) > 0.0:
                numcorrect = numcorrect + 1
        # average grade is computed from the last 8 answers
        m = 8.0
        return ((-0.5)*(m-float(numcorrect))+float(numcorrect))/m
    def computeGrade1(self, remove):
        #tmpout = tempfile.mkdtemp()
        #tex_fd, tex_absname = tempfile.mkstemp(dir=tmpout, suffix='.computegradae1')
        #os.write(tex_fd, 'computegrade1\n')

        #tmp1 = self.getTotscore()
        #tmp = float(tmp1)
        #if (remove == 0):
        #    tmp = tmp + 0.5
        #else:
        #    tmp = tmp - 1.0
        #lastscore = self.scoresofar[0]
        #if (lastscore == 0):
        #    tmp = tmp - 0.5
        #else:
        #    tmp = tmp + 1.0
        
        total = 0.0
        for i in self.scoresofar:
            if float(i) == 0.0:
                total = total - 0.5
            else:
                total = total + 1
        self.setTotscore(total)
        
        #questions = self.getStudentQuestions()
        #portal_catalog = getToolByName(self, 'portal_catalog')
        ##questions = self.portal_catalog.searchResults(
        ##    portal_type = "InvisibleQuestion",
        ##    sort_on="Date",
        ##    path='/'.join(self.getPhysicalPath()),
        ##    )
        ##total = 0.0
        ##self.scoresofar = []
        ##for q in questions:
         ##   qr = self.getQuestionResultForQuestion(q.getObject())
         ##   if (qr.candidateAnswer == qr.correct):
          ##      total = total + 1.0
           ##     self.scoresofar.insert(0,1)
          ##  else:
          ##      total = total - 0.5
          ##      self.scoresofar.insert(0,0)
        ##self.setLasteightgrades(str(self.scoresofar))    
        ##self.setTotscore(total)
        self.reindexObject()
        #os.write(tex_fd, str(self.scoresofar) + '\n')
        #os.write(tex_fd, str(total) + '\n')
        #os.write(tex_fd, str(self.getPhysicalPath()) + '\n')
        #bla = '/'.join(self.getPhysicalPath())
        #os.write(tex_fd, str(bla) + '\n')
        #os.write(tex_fd, str(len(questions)) + '\n')
        
        return self.getLasteightgrades()    
    def getLastPoint(self):
        if (len(self.scoresofar) > 0):
            return self.scoresofar[0]
        else:
            return None
    security.declarePublic('setScore')
    def setScore(self, s):
        numinscore = 8
        if (len(self.scoresofar) == numinscore):
            tmp = self.scoresofar[numinscore-1]
            self.scoresofar = self.scoresofar[:numinscore-1]
            #self.scoresofar = self.scoresofar + [s]
            self.scoresofar.insert(0, s)
            self.setLasteightgrades(str(self.scoresofar))
            self.computeGrade1(tmp)
            #self.setLasteightgrades(str(self.scoresofar))
        else:
            tmp = float(self.getTotscore())
            if (s is 0):
                tmp = tmp - 0.5
            else:
                tmp = tmp + 1.0
            self.setTotscore(tmp)
            #tmp = 0           
            #self.computeGrade1(tmp)
            #self.scoresofar = self.scoresofar + [s]
            self.scoresofar.insert(0, s)
            self.setLasteightgrades(str(self.scoresofar))
            #self.computeGrade1(tmp)
        temp = self.getTotalattempts()
        temp = temp + 1
        self.setTotalattempts(temp)
        if (s is not 0):
            temp = self.getCorrectattempts()
            temp = temp + 1
            self.setCorrectattempts(temp)
        self.reindexObject()
    def closedQuiz(self):
        msg = []                                  
        question = self.getCurrentQuestion()
        if (question):
            qr = self.getQuestionResultForQuestion(question)
            if (not qr.hasSubmittedQuestion()):
                '''this could only happen if double click on button'''
                # what to do, student want to submit the same answer twice
                # no don't allow that
                msg.append(True)
                msg.append('Already answered')
                return msg
            else:
                msg.append(False)
                msg.append('Your answer has been saved.') 
                return msg
    def openQuiz(self):
        #qr = self.getStudentQuestionResult()
        # get the last question
        question = self.getCurrentQuestion()
        if (question):
            qr = self.getQuestionResultForQuestion(question)
            if (qr.hasSubmittedQuestion()):       
                #Set this question as false
                # For the moment the result is not restored
                # should print out results for wrong question
                 
                #self.setCandidateAnswerToQuestion('no answer')
                value = 'no answer'
                qr.setCandidateAnswer([value], question.getOriginalQuestion())
                correctans = qr.getCorrectAnswer()
                if value in correctans:
                    origquestion = question.getOriginalQuestion()
                    # this can lead to database conflict error
                    # WHAT TO DO????
                    #qobj = question[0].getObject()
                    origquestion.numcorrect = origquestion.numcorrect + 1
                    correct = 1
                else:
                    correct = 0
                qr.gotAnswer()
                self.setScore(correct)
                qr.reindexObject()
            #quizquestionstring = qr.getQuizInfo()
                self.writetolog(qr)       
                return True
            else:
                return False
        else:
            '''no question set yet'''
            return False
    security.declareProtected(PERMISSION_STUDENT, 'writetolog')
    def writetolog(self, qr):
        # FIXME !!!!
        # add code to check if dir exists and then create..
        logdir = productdir + '/log'
        if (not (os.path.exists(logdir))):
            os.mkdir(logdir)
        f = open(logdir+'/questionandanswer.txt','a')
        #qr = self.getStudentQuestionResult()
        #qresults = self.getFolderContents(contentFilter={"portal_type": "QuestionResult"})
        #qr = qresults[0].getObject()
        text = qr.getQuizInfo()
        text = text + str(datetime.now()) + "\n"
        f.write(text)
        f.close()
        #os.system('echo ' + text + ' >> /tmp/twquiz/questionandanswer.txt')
    
    def setNewQuestionInTest(self, suggestedanswer, correctids, questpath, qid):
        
        #notify(NewQuizQuestionEvent(self, suggestedanswer, correctids, questpath, qid))
        question = self.getCurrentQuestion()
        if (question):
            qr = self.getQuestionResultForQuestion(question)
        #qresults = self.getFolderContents(contentFilter={"portal_type": "QuestionResult"})
        #qr = qresults[0].getObject()
        #self.manage_delObjects(qresults)
        ##randid = qr.getStudid()
        ##lecpath = qr.getLecturepath()
        ##ids = self.objectIds() # Plone 3 or older
        #ids = folder.keys()      # Plone 4 or newer
        
        #ids = []
        ##if len(ids) > 0:
            #manage_delObject will mutate the list
            # so we cannot give it tuple returned by objectIds()
         ##   ids = list(ids)
         ##   self.manage_delObjects(ids)
        ##qr = self.createQuestionResult()
        ##qr.setStudentId(self.Creator())
        
        #parent = aq_parent(self)
        #lecpath = parent.getPhyisicalPath()
        ##qr.setLecturepath(lecpath)
        ##self.setStudentQuestionResult(qr)
        
        ##transaction.begin()

            qr.setNewQuestion(suggestedanswer, correctids, questpath, qid)
        ##qr._p_changed = True
        ##self._p_changed = True
        ##transaction.commit()
        #portal_catalog = getToolByName(self, 'portal_catalog')
        #students = portal_catalog.unrestrictedSearchResults({'portal_type' : 'StudentList'})
        #if (len(students) > 0):
        #    numlists = str(len(students))
            
        #    objid = students[0].getObject()
            #objid.addStudent(candidateId)
        #    randid = objid.getStudentIdNumber(self.Creator())
            
        ##qr.setStudentId(randid)
            qr.reindexObject()
    # This method is only called once after object creation.
    #security.declarePrivate('at_post_create_script')
    #def at_post_create_script(self):
    #    self.tryWorkflowAction("publish", ignoreErrors=True)
        
    def at_post_edit_script(self):
        '''function called after edit in the main edit view of the tutorial.'''
    #    self.changed = True
   
        #qresults = self.getFolderContents(contentFilter={"portal_type": "QuestionResult"})
        #if (len(qresults) > 0):
        #    qr = qresults[0].getObject()
        #    self.setStudentQuestionResult(qr) 
    #security.declarePrivate('tryWorkflowAction')
    #def tryWorkflowAction(self, action, ignoreErrors=False, comment=None):
    #    wtool = self.portal_workflow
    #    wf = wtool.getWorkflowsFor(self)[0]
    #    if wf.isActionSupported(self, action):
    #        if comment is None:
    #            #userId = getSecurityManager().getUser().getId()
    #            comment = 'State changed' 
    #        wtool.doActionFor(self, action, comment=comment)
    #    elif not ignoreErrors:
    #        raise TypeError('Unsupported workflow action %s for object %s.'
    #                        % (repr(action), repr(self)))
    #def getError(self):
    #    self.portal_factory.doCr()
    #def createQuestionResult(self):
    #    """Create a new questionresult object for student and initialize it."""
    #    typeName = 'QuestionResult'
    #    id=self.generateUniqueId(typeName)
    #    if self.portal_factory.getFactoryTypes().has_key(typeName):
    #        o = self.restrictedTraverse('portal_factory/' + typeName + '/' + id)
    #    else:
    #        newId = self.invokeFactory(id=id, type_name=typeName)
    #        if newId is None or newId == '':
    #            newId = id
    #        o=getattr(self, newId, None)
    
    #    if o is None:
    #        raise Exception
    #    o = self.portal_factory.doCreate(o, id)
    #    o.setTitle('Question result')
    #    o.reindexObject()
    #    return o
    def removeQuestion(self):
        portal_catalog = getToolByName(self, 'portal_catalog')
        questions = self.portal_catalog.searchResults(
            portal_type = "InvisibleQuestion",
            sort_on="Date",
            path='/'.join(self.getPhysicalPath()),
            )

        
        if (len(questions) > 7):
            '''should removes the oldest one'''
            self.manage_delObjects([questions[0].getId])

    def createQuestion(self):
        """Create a new questionresult object for student and initialize it."""
        # if neede delete a question
        # only keep 8 questons going
        typeName = 'InvisibleQuestion'
        self.removeQuestion()
        id=self.generateUniqueId(typeName)
        if self.portal_factory.getFactoryTypes().has_key(typeName):
            o = self.restrictedTraverse('portal_factory/' + typeName + '/' + id)
        else:
            newId = self.invokeFactory(id=id, type_name=typeName)
            if newId is None or newId == '':
                newId = id
            o=getattr(self, newId, None)
    
        if o is None:
            raise Exception
        o = self.portal_factory.doCreate(o, id)
        #o.setTitle('Question result')
        
        invquest = self.getStudentQuestions()
        invquest.append(o)
        self.setStudentQuestions(invquest)
        self.setCurrentQuestion(o)
        
        return o   
# Register this type in Zope
registerATCTLogged(QuizResult)

#@adapter(INewQuizQuestionEvent)
#def setNewQuizQuestionInformation(NewQuizQuestionEvent):
#    tmpout = tempfile.mkdtemp()
#    tex_fd, tex_absname = tempfile.mkstemp(dir=tmpout, suffix='.nequizquestionevent')
#    os.write(tex_fd, 'in newquiquesitonevent\n')
    #os.write(tex_fd, str(NewQuizQuestionEvent.qid) + '\n')
    #os.write(tex_fd, str(obj.getTitle()) + '\n')
    
