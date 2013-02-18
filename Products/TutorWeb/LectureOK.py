from Products.Archetypes.public import *
from Products.Archetypes.public import OrderedBaseFolder
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.folder import ATFolderSchema
from AccessControl import ClassSecurityInfo
from Products.CMFCore import permissions as CMFCorePermissions
from config import *
from permissions import *
from tools import *
from Products.Archetypes.public import Schema, BooleanField, BooleanWidget, \
     IntegerField, IntegerWidget, StringField, TextField, \
     TextAreaWidget, StringWidget, SelectionWidget, RichWidget
from Products.Archetypes.utils import DisplayList
from AccessControl import ClassSecurityInfo, getSecurityManager
from Products.CMFCore.permissions import View
from ZPublisher.HTTPRequest import FileUpload
from htmlentitydefs import entitydefs
import re
import os
import shutil
import tempfile
import string
from Acquisition import aq_parent
from random import randint
import random
from string import *
from struct2latex import *
from zope.interface import implements
from Products.TutorWeb.interfaces import IPrintable, ILecture, IOrderedTutorWebContent

try:
    from plone.i18n.normalizer.interfaces import IUserPreferredURLNormalizer
    from plone.i18n.normalizer.interfaces import IURLNormalizer
    URL_NORMALIZER = True
except ImportError:
    URL_NORMALIZER = False

from zope.component import adapter, getMultiAdapter, getUtility

from zope.app.container.interfaces import INameChooser
from Products.Archetypes import atapi
from config import PROJECTNAME
from config import PLONE_VERSION
from Products.TutorWeb.item_allocation import *
from Products.ATContentTypes.lib import constraintypes

from Products.TutorWeb.interfaces import IQuestionLocator
from Products.TutorWeb.questionmodification import QuestionModification
from datetime import datetime, timedelta

class Lecture(ATFolder):
    """Lecture belongs to a specific Tutorial and would typically be constructed around a specific subject. 
    A set of lectures should encompass a specific tutorial topic.
    A lecture can contain slides and questions as well as extradatafiles which are used when
    rendering slide data.
    Lectures are implemented as ATFolder with interfaces to ILecture and IOrderedTutorWebContent and IPrintable"""
    
    schema = ATFolderSchema.copy() + Schema((
        StringField('id',
                  widget=StringWidget(description='Change ID to become more readable. Lectures appear in alphabetical order based on this value.', modes='edit',),
                  required = 1,
                  ),
        StringField('title',
                required=True,
                searchable=0,
                default='Lecture',
                widget=StringWidget(
                    label='Title',
                 ),
                
            ),
        TextField('LectureReference',
              searchable=0,
              default_content_type='text/plain',
              default_output_type='text/html',
              allowable_content_types=('text/latex','text/plain', 'text/structured', 'text/restructured',), 
              widget=RichWidget(label='Reference',
                                description='Reference for the Lecture a part of a pdf document which can be displayed for a tutorial.', modes='edit',
                                allow_file_upload=1,
             
                               ),
            
              ),          
        FileField('Pdf',
                    widget=FileWidget(description='pdf, generated from the available slides',
                                        macro='slideshowpdf',
                                        modes='view',
                                        visible={'view':'invisible','edit':'invisible'},
                                        
                                        ),
                  ),

         FileField('QuestionTex',
                    widget=FileWidget(description='tex file with a list of questions',
                                        macro='lecturequestiontex',
                                     ),
                   read_permission=CMFCorePermissions.ModifyPortalContent,
                  ),
        FileField('DownloadQuestionTex',
                    widget=FileWidget(description='tex file with a list of questions',
                                        macro='downloadlecturequestionstex',
                                        visible={'edit':'invisible'},
                                        
                                        ),
                   read_permission=CMFCorePermissions.ModifyPortalContent,
                  ),
         FileField('LectureGrades',
                    widget=FileWidget(description='file which contains grades of all students in lecture',
                                        macro='lecturegradesfile',
                                        visible={'edit':'invisible'},
                                        
                                        ),
                   read_permission=CMFCorePermissions.ModifyPortalContent,
                  ),
        # allowed in edit then need to generate
        # everytime is edited?? hmm?
        # also just have a button to generate

         ComputedField('numSlides',
                  expression='context.computeNumSlides()',
                  widget=StringWidget(modes=('view',)),
                  ),
        ComputedField('numQuestions',
                  expression='context.computeNumQuestions()',
                  widget=StringWidget(modes=('view',)),
                  ),
         ComputedField('numRQuestions',
                  expression='context.computeNumRQuestions()',
                  widget=StringWidget(modes=('view',)),
                  ),
        
     ))
    
    __implements__ = (ATFolder.__implements__)
    implements(IPrintable, ILecture, IOrderedTutorWebContent)
    global_allow = False
    meta_type = 'Lecture'          # zope type name
    portal_type = meta_type          # plone type name
    archetype_name = 'Lecture' # friendly type name
    security = ClassSecurityInfo()
    # ATT: Make sure this work when create from twmigrate.py
    changed = True
    
    def __init__(self, oid=None, **kwargs):
        self.changed = True
        ATFolder.__init__(self, oid, **kwargs)
    
    def writeLectureGrades(self):
        '''updates student grades to file'''
        wholelist = '## Grades from lecture: ' + self.getTitle() + '\n'
        wholelist = wholelist + '## loginname,  e-mail,  randomid,  grade,  number of correct answers, number of questions submitted,  last eight questions 0 then question was wrong 1 question was correct\n\n'   
        # get studentidlist
        studentdict = {}
        studlist = ''
        tut = aq_parent(self)
        dep = aq_parent(tut)
        mysite = aq_parent(dep)
        studentlistobj = mysite.getFolderContents(contentFilter={"portal_type": "StudentList"})
        if (len(studentlistobj) > 0):
            studentlist = studentlistobj[0].getObject()
            studlist = studentlist.getStudentIdList()
            # lets put it into a dictionary
            # studentidlist has
            # studentid, randomnumber, email
            templist = []
            for row in studlist:
                templist.append(row['randomnumber'])
                if (len(row['email']) < 1):
                    templist.append('NOEMAIL@somemail.com')
                else:
                    templist.append(row['email'])
                templist.append(tut.getFullName(row['studentid']))
                studentdict[row['studentid']] = templist
                templist = []
        if (len(studentdict) > 0):
            '''have some students'''
            # now find the students which have taken a test in lecture
            students = self.getParticipants()
            students.sort()
            for stud in students:
                '''write to file all relevant info for grading'''
                ''' lecture, grade, correct, attempts, last eight'''
                res = self.hasSubmitted(stud, None)
                if (res):
                    wholelist = wholelist + stud + '\t' + studentdict[stud][1] + '\t' + studentdict[stud][0] + '\t' +  str(res.studentgrade) + '\t' + str(res.correctquizattempts) + '\t' + str(res.quizattempts) + '\t' + str(res.lasteight) + '\n' 
        self.setLectureGrades(wholelist)
    def publishAll(self, typeofobject=None, originalobj=None):
        """publich lecture as well as all slides and questions belonging to lecture"""
    
        self.tryWorkflowAction("publish", ignoreErrors=True)
        slides = self.getFolderContents(contentFilter={"portal_type": "Slide"})
        for sl in slides:
            obj = sl.getObject()
            obj.publishAll()
        questions = self.getFolderContents(contentFilter={"portal_type": "TutorWebQuestion"})
        for que in questions:
            obj = que.getObject()
            obj.publishAll()
        # this is called when lecture cloned, or copy/pasted so much update references for quizresults
        portal_catalog = getToolByName(self, 'portal_catalog')
        brains = portal_catalog.unrestrictedSearchResults({'portal_type' : 'QuizResult'}, path='/'.join(self.getPhysicalPath()))
        for b in brains:
            o = b.getObject()
            # lets make this a list if later have more than one qr
            # but at the moment only possibleto have one question result
            questionresult = portal_catalog.unrestrictedSearchResults({'portal_type' : 'QuestionResult'}, path='/'.join(o.getPhysicalPath()))
            for qr in questionresult:
                obj = qr.getObject()
                o.setStudentQuestionResult(obj)
    def getParticipants(self):
        """return all student which have participated in quizes belonging to this tutorial"""
        
        portal_catalog = getToolByName(self, 'portal_catalog')
        brains = portal_catalog.unrestrictedSearchResults({'portal_type' : 'QuizResult'}, path='/'.join(self.getPhysicalPath()))
        keys = {}
        
        if (len(brains) > 0):
            for b in brains:
                keys[b.Creator] = 1
            return keys.keys()
        else:
            return False
        
    def updateSlideMaterial(self):
        """update data on all slides belonging to lecture"""
        slides = self.getFolderContents(contentFilter={"portal_type": "Slide"})
        for sl in slides:
            obj = sl.getObject()
            tmp = obj.setSlideTextView1('something')
            #maybe?
            obj.setSlideTextChanged(1)
    security.declareProtected(View, 'updatePdfMaterial')
    def updatePdfMaterial(self):
        """generate a new pdf file"""  
        self.setLecture_pdf()
    def updateRImages(self):
        """render images which have fig or r format"""
        #FIXME bad function name
        slides = self.getFolderContents(contentFilter={"portal_type": "Slide"})
        for sl in slides:
            obj = sl.getObject()
            image_type = obj.getSlideImageFormat()
            if (image_type == 'r' or image_type == 'fig'):
                obj.renderMainImage()
            if (EXPLANATION_FIG):
                image_type = obj.getExplanationImageFormat()
                if (image_type == 'r' or image_type == 'fig'):
                    obj.renderExplanationImage()
            obj.setSlideImageW()
    def getFullName(self, userid):
        """return the fullname of user with the given id"""
        if PLONE_VERSION == 3:
            ecq_tool = getToolByName(self, 'ecq_tool')
            return ecq_tool.getFullNameById(userid)
        else:
            parent = aq_parent(self)
            return parent.getFullName(userid)
    def getChanged(self):
        return self.changed
    def setSelectedAnswerInResult(self, value):
        """set the answer to a selected question in the current quiz"""
        result= self.getCurrentResult() 
        question=result.getChosenQuestion()
        result.setSelectedAnswerInTest(value)
    def setSelectionStartOfQuiz(self):
        """indicate that a student has asked for a quiz question"""
        result = self.getCurrentResult()
        value = result.getSuggestedAnswerInTest()
        if (len(value) > 0):
            ''' set the first element in value as selected answer
                anything will do'''
            result.setSelectedAnswerInTest(value[0])
        else:
            '''what to do, bad error'''
    def getSelected(self):
        """return the answer a student gave to a question in quiz"""
        result= self.getCurrentResult() 
        question=result.getChosenQuestion()
        return result.getSelectedAnswerToQuestion(question)
    def getSelectedItem(self):
        """return the actual answer a student has selected"""
        user = getSecurityManager().getUser()
        candidateId = user.getId()
        portal_catalog = getToolByName(self, 'portal_catalog')
        br = portal_catalog.unrestrictedSearchResults({'portal_type' : 'QuizResult', 'Creator': candidateId},path='/'.join(self.getPhysicalPath()))
        if (len(br) > 0):
            result= br[0].getObject() 
            if (result):
                #return (result.getSelectedItem())
                return (result.getCandidateAnswerInTest())
            else:
                return False
        return False
    def getQuestionImage(self):
        result= self.getCurrentResult() 
        question=result.getChosenQuestion()
        return question.getQuestImg()
    def getQuestionImageTag(self):
        result= self.getCurrentResult() 
        question=result.getChosenQuestion()
        result.setCurrentQuestionImage(question.getQuestionImage())
        image = result.getCurrentQuestionImage()
        if (image):
            return result.getCurrentQuestionImage().tag()
        else:
            return ""
    def getVocabulary(self):
        """return the possible answers formatted as vocabulary"""
        result= self.getCurrentResult() 
        question=result.getChosenQuestion()
        suggestedAnswerIds = result.getSuggestedAnswerInTest()
        idl = DisplayList()
        ans = question.getAnswerDisplay().values()
       
        for id in suggestedAnswerIds:
            idl.add(id, ans[int(id)])
        return Vocabulary(idl, self, None)
       
    def isCorrect(self, item):
        """returns true if answer with id=item is correct else false"""
        result= self.getCurrentResult() 
        question=result.getChosenQuestion()
        
        answers = question.getAnswerList()
        for row in answers:
            if (row['answerid'] == str(item)):
                if (row['correct'] == '1'):
                    return True
        return False
    def hasAlreadyOpenQuestion(self, res):
        """true is student has asked for a new question but has an unanswered question"""
        return res.openQuiz()
  
    def hasSubmitted(self, candidateId, usern):
        """returns true is a student with given id has submitted a question to a quiz"""
        portal_catalog = getToolByName(self, 'portal_catalog')
        if (not(usern == None)):
            candidateId = usern
        brains = portal_catalog.unrestrictedSearchResults({'portal_type' : 'QuizResult', 'Creator': candidateId},path='/'.join(self.getPhysicalPath()))
        
        if (len(brains) > 0):
            return brains[0]
        else:
            return False
   
    def questionIsInline(self):
        """true if the question format is inline"""
        result= self.getCurrentResult() 
        question=result.getChosenQuestion()
        return question.inlineAnswer()

    def inlineAnswer(self):
        """true if the question forms is inline"""
        result= self.getCurrentResult() 
        question=result.getChosenQuestion()
        return question.inlineAnswer()
   
    def setChanged(self, ch):
        """indicate that printable material has changed"""
        self.changed = ch
        tut = aq_parent(self)
        tut.setChanged(ch)
    def editedObject(self, objtype=None):
        """indicate that object has changed"""
        tut = aq_parent(self)
        tut.setQuestionChanged(True)
        self.changed = True
        self.reindexObject()
        tut.editedObject()
    def renderNewPdf(self, type):
        """indicate that printable material needs to be updated"""
        self.changed = True
        
    def setQuestionChanged(self, ch):
        """indicate that questions belonging to the lecture have changed"""
        tut = aq_parent(self)
        tut.setQuestionChanged(True)
    def getQuestionSelectionParameters(self):
        portal_catalog = getToolByName(self, 'portal_catalog')
        brains = portal_catalog.unrestrictedSearchResults({'portal_type' : 'QuestionSelectionParameters'}, path='/'.join(self.getPhysicalPath()))
        if len(brains) > 0:
            return brains[0].getObject()
        else:
            return False
    security.declarePrivate('initializeObject')
    def initializeObject(self):
        """called after object has been created
        publish lecture object, reorder object in tutorial, create a new quiz and a temporary title pdf page
        """
    
        parent = aq_parent(self)
        
        if (not self.hasQuiz()):
            self.createQuiz()
       
        parent = aq_parent(self)
        try:
            parent.orderObjects("id")
            parent.plone_utils.reindexOnReorder(parent)
            self.reindexObject()
        except:
            raise 'Error wile creating lecture, ' + self.getTitle() + ' reordering failed.'
        try:
            self.setLecture_pdf()
        except:
            self.setPdf('Pdf file not rendered yet')
        self.tryWorkflowAction("publish", ignoreErrors=True)
        # add an object which contains parameters concerning
        # selection of questions in a Lecture quiz
        obj = self.createNewObject('QuestionSelectionParameters')
        obj.setTitle('QuestionSelectionParameters')
        obj.tryWorkflowAction("publish", ignoreErrors=True)
        parent = aq_parent(self)
        portal_catalog = getToolByName(self, 'portal_catalog')
        brains = portal_catalog.unrestrictedSearchResults({'portal_type' : 'BaseQuestionSelectionParameters'}, path='/'.join(parent.getPhysicalPath()))
        if (len(brains) > 0):
            obj.setBaseSelectionParameters(brains[0].getObject())
        # now remove questionselectionparameters from add menu
        # Enable contstraining
        self.setConstrainTypesMode(constraintypes.ENABLED)
        allowedTypes = self.getLocallyAllowedTypes()
        mytypes = []
        # types not used in add menu
        #ranges = ('QuestionSelectionParameters', 'TutorWebQuiz')
        # for now allow QuestinSelectionParameters
        ranges = ('TutorWebQuiz')
        for t in allowedTypes:
            if t not in ranges:
                mytypes.append(t)
        # Tweak the menu
        self.setLocallyAllowedTypes(mytypes)
        self.setImmediatelyAddableTypes(mytypes)        
        #obj.reindexObject()
    security.declarePrivate('tryWorkflowAction')
    def tryWorkflowAction(self, action, ignoreErrors=False, comment=None):
        """change the action on the lecture"""
        #wtool = getToolByName(self, 'portal_workflow')
        wtool = self.portal_workflow
        wf = wtool.getWorkflowsFor(self)[0]
        if wf.isActionSupported(self, action):
            if comment is None:
                #userId = getSecurityManager().getUser().getId()
                comment = 'State changed' 
            wtool.doActionFor(self, action, comment=comment)
        elif not ignoreErrors:
            raise TypeError('Unsupported workflow action %s for object %s.'
                            % (repr(action), repr(self)))    
    
       
    def haveChanged(self):
        """indicate that lecture material has changed"""
        self.changed = True
       
        
    security.declareProtected(View, 'hasQuestions')
    def hasQuestions(self):
        """true if the lecture contains any questions"""
        portal_catalog = getToolByName(self, 'portal_catalog')
        questions = portal_catalog.unrestrictedSearchResults({'portal_type' : 'TutorWebQuestion'},path='/'.join(self.getPhysicalPath()))
        if (len(questions) > 0):
            return 1
        else:
            return 0
    def writeQuestionsToFile(self):
        '''write questions belonging to lecture to tex file'''
        path='/'.join(self.getPhysicalPath())
        #wholelist = '% Questions contained in lecture: ' + self.getTitle() + ' located in: ' + path + '\n'
        wholelist = ''
        #format of question file
        # %===
        # %ID q-001
        # %title newtitle-q-001
        # %format qformat (latex (default), txt, R)
        # %image imagesource (f. example http://www.example.com/example.png (or some source where image can be found))            
        # Some question text 
        #a) first answer
        #b) second answer
        #c) third answer
        #d.true/d.false) last answer (None of the above/All of the above)       
        # %Explanation 
        # some short explanation 
        
        # start by finding all questions in lecture
        # using portal catalog 
        portal_catalog = getToolByName(self, 'portal_catalog')
        brains = portal_catalog.unrestrictedSearchResults({'portal_type' : 'TutorWebQuestion'}, path='/'.join(self.getPhysicalPath()), sort_on='getId')
        for b in brains:
            obj = b.getObject()
            qformat = obj.question.getContentType()
            # structured, restructured and latex/r questions are not supported
            if ((qformat is 'text/structured') or (qformat is 'text/restructured')):
                continue
           
            # set id and title
            questioninfo = '%ID\t' + b.getId + '\n%title\t' + obj.getTitle() + '\n'
            #add format and image location if any
            # set correct format:
            if (qformat == 'text/latex'):
                format = 'latex'
            elif (qformat == 'text/r'):
                format = 'R'
            elif (qformat == 'text/r-latex'):
                format = 'Rlatex'
            elif (qformat == 'text/plain'):
                format = 'txt'

            questioninfo = questioninfo + '%format\t' + format + '\n'
               
            if (len(obj.getImageUrl()) > 2):
                '''add location of an image'''
                questioninfo = questioninfo + '%image\t' + obj.getImageUrl() + '\n'
            questioninfo = questioninfo + '%r\t' + str(obj.numcorrect) + '\n'
            questioninfo = questioninfo + '%n\t' + str(obj.numaskedfor) + '\n'
            wholelist = wholelist+questioninfo
            # next comes the question text
            qtext = obj.getQuestion()
           
            wholelist = wholelist + qtext + '\n'
            if format is not 'R':
                # then the answers
                answertext = obj.getAnswerList()
                counter = 0
                for ans in answertext:
                    anstext = str(ans['answertext'])
                    #if not isinstance(anstext, unicode):
                    #    outputtext = anstext.decode('latin-1').encode('utf-8')
                    #else:
                    #    outputtext = anstext.encode('utf-8')
                    outputtext = anstext
                    if counter == (len(answertext) - 1):
                        '''last answer'''
                        # check if need to set d.false/d.true
                        if (("None of the above" in outputtext) or ("All of the above" in outputtext)):
                            if (ans['correct']):
                                myletter = string.lowercase[counter]+'.true)\t'
                            else:
                                myletter = string.lowercase[counter]+'.false)\t'
                        else:
                            myletter = string.lowercase[counter]+')\t'
                    else:
                        myletter = string.lowercase[counter]+')\t'
                    wholelist = wholelist + myletter+ outputtext + '\n'
                    counter = counter + 1
            # at last comes the explanation text if any
            #qexpl = obj.questionExplanationRaw()
            qexpl = obj.getRawQuestionExplanation()        
            if (len(qexpl) > 0):
                wholelist = wholelist + '\n%Explanation\t' + qexpl + '\n'    
            # %=== is a separator between questions
            wholelist = wholelist +  '%===\n'  
        self.setDownloadQuestionTex(wholelist)
    def addQuestionsFromLatexFile(self):
        '''Add questioned defined in latex file'''
        # use portal catalog to find a specific question as needed
        portal_catalog = getToolByName(self, 'portal_catalog')
        # start by getting text from file
        qtext = str(self.getField('QuestionTex').get(self).data)
        # if qtext is empty then delete all latex questions
        if len(qtext) < 1:
            '''no file'''
            brains = portal_catalog.unrestrictedSearchResults({'portal_type' : 'TutorWebQuestion'}, path='/'.join(self.getPhysicalPath()))
            for b in brains:
                obj = b.getObject()
                qformat = obj.question.getContentType()
                if ((qformat == 'text/latex') or (qformat == 'text/plain') or (qformat == 'text/r') or (qformat == 'text/r-latex')):
                    # delete obj
                    self.manage_delObjects([b.getId])
                 
        #format of question file
        # %===
        # %ID q-001
        # %title newtitle-q-001
        # %format qformat (latex (default), txt, R, Rlatex)
        # %image imagesource (f. example http://www.example.com/example.png (or some source where image can be found))            
        # Some question text 
        #
        #a) first answer
        #b) second answer
        #c) third answer
        #d.true/d.false) last answer (None of the above/All of the above)       
        # %Explanation 
        # some short explanation
        #%===
        # %ID and %title are optional, if not included default
        # settings used for id and title
        # explanation is also optional, if not set no short explanation is
        # included for the question.
        # %=== is a mark to deliminate between two questions.
        questionsplittermark = '\n%===' 
              
        # now start by creating questions and answers according to file
        # qtext contains the whole file
        # what if file starts with '%===' then not \n
        questionslist = qtext.split(questionsplittermark)
        #set regexp of finding Explanation, title and ID of a question
        explanationpattern = re.compile('(?<=^%Explanation\s).*$(?ims)')
        startof_explanationpattern = re.compile('^%Explanation(?im)')
        titlepattern = re.compile('(?<=^%title\s).*(?im)')
        # recognize if image set
        imagepattern = re.compile('(?<=^%image\s).*(?im)')
        imagepattern2 = re.compile('(^%image\s).*(?im)')
        titlepattern2 = re.compile('(^%title\s).*(?im)')
        # recognize if num correct asnwers set
        numcorrectpattern = re.compile('(?<=^%r\s).*(?im)')
        numcorrectpattern2 = re.compile('(^%r\s).*(?im)')
        # recognize if num appeared in quiz set
        numquizpattern = re.compile('(?<=^%n\s).*(?im)')
        numquizpattern2 = re.compile('(^%n\s).*(?im)')
        # recognize question format
        qformatpattern = re.compile('(?<=^%format\s).*(?im)')
        qformatpattern2 = re.compile('(^%format\s).*(?im)')
        # recognize id format
        idpattern = re.compile('(?<=^%ID\s).*(?im)')
        idpattern2 = re.compile('(^%ID\s).*(?im)')
        # set pattern to find answers
        # a) answertext, b) answertext, c) answertext
        answerpattern = re.compile(r'(^([a-z](\)\s|\))))(?im)')
        # d.false), d.true)
        answerpattern_truefalse = re.compile(r'^([a-z]\.(true|false)((\)\s)|(\))))(?im)')
        
        # now start going through all question/answers
        numq = 0
        for que in questionslist:
            ''' go through all the questions'''
            # start by checking if any line starts with
            #%ID and/or %title
            if (len(que.strip()) < 2):
                '''no questions text, try next'''
                continue
            foundid = re.search(idpattern, que)
            foundtitle = re.search(titlepattern, que)
            foundimage = re.search(imagepattern, que)
            foundexpl = re.search(explanationpattern, que)
            foundqformat = re.search(qformatpattern, que)
            foundnumcorrect = re.search(numcorrectpattern, que)
            foundnumquiz = re.search(numquizpattern, que)
            newid = None
            # set default values for title and short explanation
            newtitle = 'Question'
            newexplanation = ''
            #default format for questions and answers is latex
            texttype = 'text/latex' 
            # set new id if needed else use given id
            if foundid:
                newid = foundid.group().strip()
                # remove id line from rest of question
                foundid2 = re.search(idpattern2, que)
                que = que[0:foundid2.start()]+que[foundid2.end():]
            if foundqformat:
                newtype = foundqformat.group().strip()
                if newtype == 'R':
                    texttype = 'text/r'
                elif newtype == 'Rlatex':
                    texttype = 'text/r-latex' 
                elif newtype == 'txt':
                    texttype = 'text/plain'
                else: 
                    texttype = 'text/latex'
            
                # remove format line from rest of question
                foundqformat2 = re.search(qformatpattern2, que)
                que = que[0:foundqformat2.start()]+que[foundqformat2.end():]
                
            if (newid is None) or (not newid in self.objectIds()):
                # first create a question, using newid if set
                # otherwise use default id
                if newid is None:
                    newid = self.generateNewIdForQuestion()
                QueObj = self.createNewObject('TutorWebQuestion', newid)
            else:
                # find the question with the specified id
                brains = portal_catalog.unrestrictedSearchResults({'portal_type' : 'TutorWebQuestion', 'id' : newid}, path='/'.join(self.getPhysicalPath()))
                QueObj = brains[0].getObject()
                # write to database that question has been changed
                questlocator = getUtility(IQuestionLocator)
                questioninfo = questlocator.question_by_uid(QueObj.UID())
                if (questioninfo):
                    '''question is part of database i.e. has been used in a quiz'''
                    qm = QuestionModification(questioninfo.question_id, datetime.now())
                    qm.addToDataBase()
            
            
            # set the title    
            if foundtitle:
                temptitle = foundtitle.group().strip()
                newtitle = temptitle.decode('utf-8')
                # remove title line from rest of question
                foundtitle2 = re.search(titlepattern2, que)
                que = que[0:foundtitle2.start()]+que[foundtitle2.end():]
                
            QueObj.setTitle(newtitle)
             # set the image
            if foundimage:
                tempimage = foundimage.group().strip()
                newimage = tempimage.decode('utf-8')
                # remove image line from rest of question
                foundimage2 = re.search(imagepattern2, que)
                que = que[0:foundimage2.start()]+que[foundimage2.end():]
                
                QueObj.setImageUrl(newimage)
            # set number of correct answers
            if foundnumcorrect:
                tempnumcorrect = foundnumcorrect.group().strip()
                newnumcorrect = tempnumcorrect.decode('utf-8')
                # remove numcorrect line from rest of question
                foundnumcorrect2 = re.search(numcorrectpattern2, que)
                que = que[0:foundnumcorrect2.start()]+que[foundnumcorrect2.end():]
                
                QueObj.numcorrect = int(newnumcorrect)
             # set number of times question appeared in quiz
            if foundnumquiz:
                tempnumquiz = foundnumquiz.group().strip()
                newnumquiz = tempnumquiz.decode('utf-8')
                # remove num in quiz line from rest of question
                foundnumquiz2 = re.search(numquizpattern2, que)
                que = que[0:foundnumquiz2.start()]+que[foundnumquiz2.end():]
                
                QueObj.numaskedfor = int(newnumquiz)    
            # set explanation text
            if (foundexpl):
                tempexplanation = foundexpl.group().strip()
                newexplanation = tempexplanation.decode('utf-8')
                # remove explanation text from rest of questions
                startexpl = re.search(startof_explanationpattern, que)
                que = que[0:startexpl.start()]
            QueObj.setQuestionExplanationText(newexplanation, mimetype='text/latex')
            # Now find the question and answers
            # could be of the format [a-z])
            answers = answerpattern.finditer(que)
            foundanswers = answerpattern.search(que)
            # could also be [a-z].false) or [a-z].true)
           
            answer_truefalse = answerpattern_truefalse.finditer(que)
            
            # 
            textlist = []
            # beginning of question text
            startstring = 0
            #default, first answer correct and answers are randomized.
            correctans = 1
            randomize = True
            # have removed explanation text
            # therefore if not have d.true/d.false format the answers
            # end by endof the text.
            endofquestions = len(que)
            for i in answer_truefalse:
                # set end of [a-z]) answer pattern
                # assume [a-z].true/false) would always be the last answer.
                endofquestions = i.start()
            #set the question/answer text
            if (foundanswers):
                for i in answers:
                    # just assumed that question text ends before first answer found
                    textlist.append(que[startstring:i.start()].strip())
                    # beginning of next answer
                    startstring = i.end()
                # last abswer
                textlist.append(que[startstring:endofquestions])
                # now check for d.true/false) answer
                # if d.true/false format is the only answer
                # it will not be made into a single answer but becomes
                # part of the question text!!!
                answer_truefalse = answerpattern_truefalse.finditer(que)
                for i in answer_truefalse:
                    textlist.append(que[i.end():len(que)])
                    if (("true" or "True" or "TRUE") in i.group()):
                        # the last answer is correct
                        correctans = len(textlist)-1
                    randomize = False
                    QueObj.NOTAinQuestion = True
            elif ((not foundanswers) and ((texttype == 'text/r') or (texttype=='text/r-latex'))):
                '''no answers found, as for R questions'''
                textlist.append(que.strip())
            else:
                '''error must have some answers'''
                self.manage_delObjects([QueObj.getId()])
                return False
            
           
            mutated = []
            
            # first comes the question itself
            # FIXME missing check for if textlist if empty
            questiontext = textlist[0].decode('utf-8')
            QueObj.publishAll()
            QueObj.setQuestionText(questiontext, mimetype=texttype)
            # then come the answers
            counter = 1
            while (counter < len(textlist)):
                 # for the answers
                row = {}
                row['correct'] = ''
                row['answertext'] = ''
                row['randomize'] = ''
                answertext = textlist[counter]
                if not isinstance(answertext, unicode):
                    charset = self.getCharset()
                    answertext2 = unicode(answertext, charset)
                else:
                    answertext2 = answertext
               
                answertext1 = answertext2.encode('utf-8')
                row['answertext'] = answertext1
                # randomize all answers except d.false/true) format
                # which is always assumed to be the last answer
                if (randomize or ((randomize == False) and counter < (len(textlist)-1))):
                    row['randomize'] = '1'
                 
                if (counter == correctans):
                    #set which answer is correct
                    # either the first answer or last answer being d.true
                    row['correct'] = '1'
                
                counter = counter + 1
                mutated.append(row)
                
            if (len(mutated) > 0):
                '''have set some answers'''
                QueObj.setAnswerList(mutated)
                QueObj.setAnswerFormat(texttype)
            QueObj.initializeObject()
            QueObj.reindexObject() 
        		    
                     
        if (len(questionslist) > 0):
            self.reindexObject()
            #need to update pdf  file for all questions in tutorial
            self.setQuestionChanged(True)
        return True
    
    # create a new object in obj with type
    def createNewObject(self, objtype, givenid = None):
        """Create a new object of type = type and initialize it."""
        
        typeName = objtype
        obj = self
        if givenid is None:
            
            givenid=obj.generateUniqueId(typeName)
        
        if obj.portal_factory.getFactoryTypes().has_key(typeName):
            o = obj.restrictedTraverse('portal_factory/' + typeName + '/' + givenid)
            newId = givenid
        else:
            newId = obj.invokeFactory(id=givenid, type_name=typeName)
            if newId is None or newId == '':
                newId = givenid
            
            o=getattr(obj, newId, None)
        if o is None:
            raise Exception
	
    
        
        o = obj.portal_factory.doCreate(o, newId) 
        return o
    def generateNewIdForQuestion(self):
        ''' Suggest an id for question based on number of questions '''
        
        maxId = 0
        pattern = '^q-[0-9][0-9][0-9]$'
        usedids = []
        for id in self.objectIds():
        
            if (re.match(pattern, id)):
                usedids.append(id)
        usedids.sort()
        if (len(usedids) > 0):
            lastvalue = usedids[len(usedids)-1]
            intId = int(lastvalue[-3:]) + 1
        else:
            intId = 1
        #intId = int(tempids(len(usedids) + 1
        #if (intId == 1):
        #    intId = 999
        try:
            if (intId > 99):
                newid = 'q-'+str(intId)
            elif (intId > 9):
                newid = 'q-0'+str(intId)
            else:
                newid = 'q-00'+str(intId)
        except (TypeError, ValueError):
                newid = 'error'
    

        if not newid:
            return None
        # Don't do anything without the plone.i18n package
        if not URL_NORMALIZER:
            return None
        if not isinstance(newid, unicode):
            charset = self.getCharset()
            newid = unicode(newid, charset)
        request = getattr(self, 'REQUEST', None)
        if request is not None:
            return IUserPreferredURLNormalizer(request).normalize(newid)

        return queryUtility(IURLNormalizer).normalize(newid)
        
    def createResult(self):
        """Create a new "QuizResult" object and initialize it."""
        typeName = 'QuizResult'
        id=self.generateUniqueId(typeName)
        if (not self.hasQuiz()):
            self.createQuiz()
        quiz = self.getQuiz()
        if quiz.portal_factory.getFactoryTypes().has_key(typeName):
            o = quiz.restrictedTraverse('portal_factory/' + typeName + '/' + id)
        else:
            newId = quiz.invokeFactory(id=id, type_name=typeName)
            if newId is None or newId == '':
                newId = id
            o=getattr(quiz, newId, None)
    
        if o is None:
            raise Exception
       
        o = quiz.portal_factory.doCreate(o, id)
       
        
        #mctool = getToolByName(self, 'ecq_tool')
        
        candidateId = o.Creator()
        #name = mctool.getFullNameById(candidateId)
        name = self.getFullName(candidateId)
        o.setTitle(name)
        tempval = []
        o.setScoresofar(tempval)
        # create a question result object if needed
        #qr = o.createQuestionResult()
       
        #qr.setStudentId(candidateId)
        
       
        #qr.setLecturepath(self.getPhysicalPath())
        
        #o.setStudentQuestionResult(qr)
        #o.reindexObject()
        # should check if student has a random id
       
        portal_catalog = getToolByName(self, 'portal_catalog')
        students = portal_catalog.unrestrictedSearchResults({'portal_type' : 'StudentList'})
        if (len(students) > 0):
            numlists = str(len(students))
            
            objid = students[0].getObject()
            objid.addStudent(candidateId)
            randid = objid.getStudentIdNumber(candidateId)
            o.setStudentRandId(randid)
            o.setStudentId(candidateId)
            #qr.setStudentId(randid)
            
           
        return o
    def createResultForStudent(self, studentid):
        """Create a new "QuizResult" object and initialize it."""
        typeName = 'QuizResult'
        id=self.generateUniqueId(typeName)
        quiz = self.getQuiz()
        if quiz.portal_factory.getFactoryTypes().has_key(typeName):
            o = quiz.restrictedTraverse('portal_factory/' + typeName + '/' + id)
        else:
            newId = quiz.invokeFactory(id=id, type_name=typeName)
            if newId is None or newId == '':
                newId = id
            o=getattr(quiz, newId, None)
    
        if o is None:
            raise Exception
       
        o = quiz.portal_factory.doCreate(o, id)
       
        
        #mctool = getToolByName(self, 'ecq_tool')
        
        candidateId = studentid
        #name = mctool.getFullNameById(candidateId)
        name = self.getFullName(candidateId)
        o.setTitle(name)
        tempval = []
        o.setScoresofar(tempval)
        o.setCreators(studentid)
        # create a question result object if needed
        qr = o.createQuestionResult()
       
        qr.setStudentId(candidateId)
        
       
        qr.setLecPath(self.getPhysicalPath())
        
        o.setStudentQuestionResult(qr)
        o.reindexObject()
        # should check if student has a random id
       
        portal_catalog = getToolByName(self, 'portal_catalog')
        students = portal_catalog.unrestrictedSearchResults({'portal_type' : 'StudentList'})
        if (len(students) > 0):
            numlists = str(len(students))
            
            objid = students[0].getObject()
            objid.addStudent(candidateId)
            randid = objid.getStudentIdNumber(candidateId)
            
            qr.setStudentId(randid)
        quiz.reindexObject()   
        return o
    def createLectureExtrasFolder(self):
        """Depricated"""
        typeName = 'Folder'
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
        id = 'data'
        o = self.portal_factory.doCreate(o, id)
        o.setTitle('Extra Data')
        o.reindexObject()
    def createQuiz(self):
        """Create a new quiz object and initialize it."""
        typeName = 'TutorWebQuiz'
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
        id = 'quiz'
        o = self.portal_factory.doCreate(o, id)
        o.setTitle('Lecture Quiz')
        o.reindexObject()
   
    
           
    def setRoles(self):
         """ Makes the context available for student and tutor only.
    
         """
    
         # View is an one of Plone's own permissions. It defines
         # who are allowed to view the object.
         # Roles student, tutor and manager are allowed to view the context.
         self.manage_permission(
             CMFCorePermissions.View, 
             roles = ["Authenticated", "Manager"],
             acquire=False)   
    security.declareProtected(View, 'hasQuiz')
    def hasQuiz(self):
        """True if lecture contains a quiz"""
        quiz = self.listFolderContents(contentFilter={"portal_type": "TutorWebQuiz"})
        if (len(quiz) > 0):
            return 1
        else:
            return 0
    security.declareProtected(View, 'getQuiz')
    def getQuiz(self):
        """return quiz object which belongs to lecture"""
        quiz = self.listFolderContents(contentFilter={"portal_type": "TutorWebQuiz"})
        for q in quiz:
            return q
        if (len(quiz) == 0):
            return False
    def haveExtraData(self):
        portal_catalog = getToolByName(self, 'portal_catalog')
        brains = portal_catalog.unrestrictedSearchResults({'portal_type' : 'File'}, path='/'.join(self.getPhysicalPath())+'/data')
        if (len(brains) > 0):
            return True
        else:
            return False
    def haveDataFolder(self):
        portal_catalog = getToolByName(self, 'portal_catalog')
        brains = portal_catalog.unrestrictedSearchResults({'portal_type' : 'Folder', 'id' : 'data'}, path='/'.join(self.getPhysicalPath()))
        if (len(brains) > 0):
            return True
        else:
            return False    
    def getDataFolder(self):
        """Depricated"""
        portal_catalog = getToolByName(self, 'portal_catalog')
        brains = portal_catalog.unrestrictedSearchResults({'portal_type' : 'Folder', 'id' : 'data'}, path='/'.join(self.getPhysicalPath()))
        if (len(brains) > 0):
            return brains[0].getObject()
        else:
            return False 
    def haveExtraDataFile(self):
        """True if lecture contains any ExtraDataFile"""
        portal_catalog = getToolByName(self, 'portal_catalog')
        brains = portal_catalog.unrestrictedSearchResults({'portal_type' : 'ExtraDataFile'}, path='/'.join(self.getPhysicalPath()))
        if (len(brains) > 0):
            return True
        else:
            return False   
    def getAllExtraFiles(self):
        """return the ids of all ExtraDataFiles belonging to the lecture"""
        portal_catalog = getToolByName(self, 'portal_catalog')
        brains = portal_catalog.unrestrictedSearchResults({'portal_type' : 'ExtraDataFile'}, path='/'.join(self.getPhysicalPath()))
        return brains
    
    def getAllExtraFilesIds(self):
        """return the actual ids as strings of all ExtraDataFiles belonging to lecture"""
        portal_catalog = getToolByName(self, 'portal_catalog')
        brains = portal_catalog.unrestrictedSearchResults({'portal_type' : 'ExtraDataFile'}, path='/'.join(self.getPhysicalPath()))
        extrafilesids = []
        for b in brains:
            extrafilesids.append(b.id)
        return extrafilesids
   
    def getCurrentResult(self, candidateid=None):
        """return the quiz result object of a user which is logged in or a
        user with the given candidateid if current user has appropriate priviledges."""
        user = getSecurityManager().getUser()
        candidateId = user.getId()
      
        if (candidateid != None):
           
            if (self.canSeeQuestions()):
                candidateId = candidateid
        
        portal_catalog = getToolByName(self, 'portal_catalog')
        brains = portal_catalog.unrestrictedSearchResults({'portal_type' : 'QuizResult', 'Creator': candidateId},path='/'.join(self.getPhysicalPath()))
        
        if (len(brains) > 0):
            return brains[0].getObject()
        else:
            return None
    def maybeMakeNewResult(self, candidateid=None):
        """If the candidate hasn't seen this quiz yet, generate a new
        one.  Otherwise, do nothing."""
        
        result = self.getCurrentResult(candidateid)
        if (result is None):
            result = self.createResult()
        
        return result
    if PLONE_VERSION == 3:
        security.declarePublic('userIsGrader')
        def userIsGrader(self, user):
            quiz = self.getQuiz()
            return quiz.userIsGrader(user)
    
        security.declarePublic('userIsManager')
        def userIsManager(self, user):
            mctool = getToolByName(self, 'ecq_tool')
            return mctool.userHasOneOfRoles(user, ('Manager',), self)
    
    # item_allocation -- a placeholder
    def item_allocation_temp(self, numansvec, corransvec, grade):
        selectedindex = random.randint(0, (len(numansvec)-1))
        return(selectedindex)

    security.declareProtected(View, 'getQuizQuestion')
    def getQuizQuestion(self, tex_fd = 'tempfile', debug=False):
        ''' find a new quiz question '''
        
        REQUEST = self.REQUEST 
        hasPressedQuiz = REQUEST.get('has_just_submitted', False)
        
        ## what happends if no lectures in tutorial!!!!
        #get the parent...
        parent = aq_parent(self)
        # get questions belonging to self and above..
        
        lectures = parent.listFolderContents(contentFilter={"portal_type": "Lecture"})
        tmp = lectures.sort(lambda x,y:cmp(x.id, y.id))

        # add all possible questions from lec1 and up
        # assume the first lecture id is the first lecture...

        numlectures = len(lectures)
        num = 0
        lecindex = 0
        testquestions = []
        # find index of lecture
        numquestions = 0
        if (numlectures > 0):
            portal_catalog = getToolByName(self, 'portal_catalog')

            # add the probabilty setting for selected questions
            # also from previous lectures or not.
            # Originally just implemented for either 0.0 or 1.0
            # 0.0, only select questions from the current lecture
            # 1.0 select also from previous lectures
            # revision: select with prob hsp from previous lectures
            
            # find the parent tutorial
            parent = aq_parent(self)
            selectionparams = self.getQuestionSelectionParameters()
            if not selectionparams:
                # use historical selection probability which is part
                # of Tutorial.py - original setup
                try:
                    hsp = parent.getHistorical_selection_probability()
                   
                except:
                    # default value of historical selection probability 
                    # hsp not found to be part of Tutorial.py
                    hsp = 1.0
            else:
                '''have set a new objectc containing question selection parameters'''
                # returns value set in parameters belonging to Lecture.py
                # if not set in Lecture.py use values from Tutorial.py
                hsp = selectionparams.findHistorical_selection_probability()
                
            #if hsp == 1.0:
            utmp=random.uniform(0.,1.)
            if utmp <= hsp:
                while (lectures[lecindex].getId() != self.getId()):
                    lecindex = lecindex + 1
            
                
                while (num <= lecindex):
                    # add all question from lec[0..lexindex] to questionlist to be selected randomly from.
                    #questions = lectures[num].listFolderContents(contentFilter={"portal_type": "TutorWebQuestion"})
                    questions = portal_catalog.unrestrictedSearchResults({'portal_type' : 'TutorWebQuestion'},path='/'.join(lectures[num].getPhysicalPath())) 
                    for q in questions:
                        testquestions.append(q)
                        
                     
                    num = num + 1
          
            else:
                testquestions = portal_catalog.unrestrictedSearchResults({'portal_type' : 'TutorWebQuestion'},path='/'.join(self.getPhysicalPath())) 
        ## CAREFUL this should be questions - probably if using all questions
        #numincurrent = len(testquestions)
       
        # randomly select a questions biaz to a questions from a previous lec.??
        # must make sure which is included, 0 and len or len-1??
        # this is not biazed..

        # should use the difficult level numcorrect/numaskedfor

        # if NO QUESTIONS this will not work!!!!
        returnmsg = []
        returnmsg.append(-1)
        returnmsg.append(self.getTitle() + ' in location: ' + '/'.join(self.getPhysicalPath()))

        
        if (len(testquestions) <= 0):
            '''no questions available'''
            return returnmsg
        # if no object of type QuizResult as been created for student
        # this will also not work
        user = getSecurityManager().getUser()
        candidateId = user.getId()
        quizresult = self.hasSubmitted(candidateId, None)
        if (not quizresult):
            '''bad error'''
            # no result yet created for student
            # what to do?
            returnmsg[0] = False
            return returnmsg
        ##selectedindex = randint(0, (len(testquestions)-1))
        # new selection method, 10.03.11
       
        # not sure if can assume NumPY is installed
        # from Numeric import *
        # becomes vec num answers to ea Q
        #numansvec=arange(0.,numquestions)
        # becomes num corr answers
        #corransvec=arange(0.,numquestions)
        # becomes index of difficulty
        #difficulty=arange(0.,numquestions)    
        numansvec =[]
        corransvec = []
        difficulty = []
        grade = -0.5
        #qindex=0
        #numiteration = len(testquestions)-1
        #for qindex in range(0,numiteration):
        for q in testquestions:
            '''do something'''
            qobj = q.getObject()
            numansvec.append(qobj.numaskedfor)
            corransvec.append(qobj.numcorrect)
            if qobj.numaskedfor > 0:    # be sensible even if no answers
                difficulty.append(1.-qobj.numcorrect/qobj.numaskedfor)
            else:
                difficulty.append(random.uniform(0.,1.))
        
        
       
        
        res = quizresult.getObject()
        # later more complex methods of computing grades need to be specified.
        # at the moment computed from m=8 last answers and
        # r = number of correct answers depending on the last 8
        # average grade = ((-0.5)*(m-r)+r)/m
        grade = res.computeAverageGrade()
        
        #selectedindex = self.item_allocation_temp(numansvec,corransvec,grade)
        if NUMPY:
            if (debug):
            
                selectedindex = item_allocation(numansvec,corransvec,grade, tex_fd, True)
            else:
                selectedindex = item_allocation(numansvec,corransvec,grade)
        else:
            selectedindex = self.item_allocation_temp(numansvec,corransvec,grade)
        qobj = testquestions[selectedindex].getObject()
        temp = qobj.getAnswerList()
        grid = qobj.getWrappedField('AnswerList')
        texttype = qobj.question.getContentType()
        
        if ((len(temp) < 1) and not ((texttype == 'text/r') or (texttype == 'text/r-latex'))):
            '''no answers even though it is not a question with r format'''
            returnmsg[0] = -2
            returnmsg.append(qobj.getTitle())
            returnmsg.append('/'.join(qobj.getPhysicalPath()))
            return returnmsg
        correctAnswerIds = []
        rowcorrect = grid.search(qobj, correct='1')
        if (len(rowcorrect) < 1 and not ((texttype == 'text/r') or (texttype == 'text/r-latex'))):
            '''no answer has been set as correct cannot continue with this question'''
            returnmsg[0] = -3
            returnmsg.append(qobj.getTitle())
            returnmsg.append('/'.join(qobj.getPhysicalPath()))
            return returnmsg
            
        for row in rowcorrect:
            correctAnswerIds.append(row['answerid'])
        
        if (debug):
            os.write(tex_fd, '########################################\n')
            os.write(tex_fd, 'output from lecture,getQuizQuestion\n')
            os.write(tex_fd, 'id of question used: ' + str(qobj.getId()) + '\n')
            os.write(tex_fd, 'selected index: ' + str(selectedindex) + '\n')
            os.write(tex_fd, 'grade is: ' + str(grade) + '\n')
            
            counter = 0
            os.write(tex_fd, 'list of questions used in selection\n')
            os.write(tex_fd, 'index\tquestionid\tnumrequested\tnumcorrect\n')
            for q in testquestions:
                temp = q.getObject()
                os.write(tex_fd, str(counter) + '\t') 
                os.write(tex_fd, str(temp.getId()) + '\t')
                os.write(tex_fd, str(numansvec[counter]) + '\t')
                os.write(tex_fd, str(corransvec[counter]) + '\n')
                counter = counter + 1
            os.write(tex_fd, 'end of output from lecture.getQuizQuestion\n')
        
        #suggestedanswers = qobj.makeNewTest()
        #res.setNewQuestionInTest(suggestedanswers, correctAnswerIds, qobj.getPhysicalPath(), qobj.UID())
        
        
        qobj.numaskedfor = qobj.numaskedfor + 1
        returnmsg[0] = qobj
        return returnmsg
        
       

    security.declareProtected(View, 'canSeeQuestions')
    def canSeeQuestions(self):
        """return true if user has appropriate authority to edit/view question content"""
        try:
            user = getSecurityManager().getUser()
           
            groups = user.getGroups()
           
            if (user.has_role('Manager')):
                return 1
            elif(user.has_role('Editor')):
                return 1
            elif(user.has_role('Owner')):
                return 1
            elif('teacher' in groups):
                return 1
            else:
                plu = getToolByName(self,'plone_utils')
                gILR = plu.getInheritedLocalRoles
                inherited_roles = gILR(self)
                
                counter = 0
                while (counter < len(inherited_roles)):
                    if (user.getId() in inherited_roles[counter]):
                        if (('Editor' in inherited_roles[counter][1]) or ( 'Owner' in inherited_roles[counter][1])):
                           return 1
                    counter = counter + 1
                return 0
            
            

        except:
            '''can not establish who user is'''
            return 0
    security.declareProtected(View, 'getLecture_pdf')
    def getLecture_pdf(self):
        """generate a new pdf file if content has changed"""
        if (self.changed == True):
            self.setLecture_pdf()
        return 'anything'
    security.declareProtected(View, 'render_pdf')
    def render_pdf(self, tmpout, tex_absname, dviname, psname, pdfname):
        """run latex, dvips, ps2pdf to render a pdf file"""
        
        try:
            # run latex 
            status = os.system('echo Q | latex -interaction=nonstopmode -output-directory=' + tmpout + ' ' + tex_absname)
            
        except:
            '''failed to run latex'''
            return 'failed to run latex'
        try:
            os.system('dvips -f ' + dviname + ' > '+ psname)
        except:
            '''failed to run dvips'''
            return 'failed to run dvips'
        try:
            os.system('ps2pdf '+ psname + ' ' + pdfname)
        except:
            '''failed to run ps2pdf'''
            return 'failed to run ps2pdf'
        try:
            #os.chmod(pdfname, 0755) 
            pdffile = file(pdfname).read()
            return pdffile
        except:
           
            return 'Failed to read data from file while rendering pdf file.'
    security.declareProtected(View, 'getSuitableImageSize')
    def getSuitableImageSize(self, haveMainText, haveExpText):
         if ((not haveMainText) and (not haveExpText)):
             image_size = 9
         elif ((haveMainText) and (not haveExpText)):         
             image_size = 6
         elif ((haveExpText and (not haveMainText))):                
             image_size = 7
         elif (haveMainText and haveExpText):
             image_size = 5
         else:
             image_size = 0
         return image_size

    security.declareProtected(View, 'renderImage')
    def renderImage(self, sl, slidetext, slideimage, imagetype):
        if (imagetype == 'fig'):
            text = slidetext
            main_image = sl.renderImage(text, 'fig2dev -L eps', '')
                    
        elif (imagetype == 'r'):
            HEADER = 'postscript(file="/dev/stdout")\r\n'
            text = slidetext
            main_image = sl.renderImage(text, 'R --slave', HEADER)
        elif (imagetype == 'gnuplot'):
            HEADER = 'set terminal epslatex color\n'
            text = slidetext
            main_image = sl.renderImage(text, 'gnuplot', HEADER)    
        else:
            main_image = slideimage
        return main_image
    security.declareProtected(View, 'setTitle_pdf')
    def setTitle_pdf(self):
        """render an initial title page"""
        # render if needed from slides belonging to lectures...
        #Exceptions?
        #latex2html takes xxx.tex and creates directory with the name xxx
        #htmldir = tex_absname[:-4]+'/'
        #htmlfilename = htmldir+'index.html'
        #what if there is only a pictures?? and no text
        # should the explanation be tabular if no pictures
        # should the picture be tabualar if no text??
        # what if only explanation no main text or image

        #####
        # if text on slide more than one page does not work!!, at least in tutorweb
        #if (not self.questiontransform):
        if (True):
            try:
                tmpout = tempfile.mkdtemp()
            except:
                self.setPdf('Rendering pdf file failed - not able to create temporary directory.')
                return
            # created temporary directory /tmp/tmpout
            try:

                tex_fd, tex_absname = tempfile.mkstemp(dir=tmpout, suffix='.tex')
                pdfdir = tex_absname[:-4]+'/'
                textfilename=tmpout+'/mytextfile.txt'
                psfilename=tmpout+'/mypsfile.ps'
                dviname = tex_absname[:-3] + 'dvi'
                psname = tex_absname[:-3] + 'ps'
                pdfname = tex_absname[:-3]+'pdf'
                ps6name = tex_absname[:-3] + '6ps'
            except:
                self.setPdf('Rendering pdf file failed - not able to create temporary file.')
                self.cleanDir(tmpout)
                return
            # created temporary file in /tmp/tmpout/tmp*
            try:
                self.setHeading(tex_fd)
            except:
                self.setPdf('Rendering pdf file failed - not able to write preamble for latex file in lecture printout')
                os.close(tex_fd)
                self.cleanDir(tmpout)
                return
            #no more slides to add, finish latex document
            os.write(tex_fd, '\\end{document}'+'\n')#try:
            pdftext = self.render_pdf(tmpout, tex_absname, dviname, psname, pdfname)

            
            self.setPdf(pdftext)
            os.close(tex_fd)
            self.cleanDir(tmpout)
            self.changed = True
    security.declareProtected(View, 'setLecture_pdf')
    def setLecture_pdf(self):
        """render pdf/latex files for lecture"""
        # render if needed from slides belonging to lectures...
        #Exceptions?
        #latex2html takes name xxx.tex and creates directory with name xxx
        #htmldir = tex_absname[:-4]+'/'
        #htmlfilename = htmldir+'index.html'
        #what if there is only a pictures?? and no text
        # should the explanation be tabular if no pictures
        # should the picture be tabualar if no text??
        # what if only explanation no main text or image

        #####
        # if text on slide more than one page does not work!!, at least in tutorweb
        #if (not self.questiontransform):
        #tmpfig = tempfile.mkdtemp()    
        #fig_fd, fig_absname = tempfile.mkstemp(dir=tmpfig, suffix='.figfile')
        #os.write(fig_fd, 'in fig file')
        if (True):
            try:
                tmpout = tempfile.mkdtemp() 
            except:
                self.setPdf('Rendering pdf file failed - not able to create temporary directory.')
                return
            # created temporary directory /tmp/tmpout
            try:

                tex_fd, tex_absname = tempfile.mkstemp(dir=tmpout, suffix='.tex')
                pdfdir = tex_absname[:-4]+'/'
                textfilename=tmpout+'/mytextfile.txt'
                psfilename=tmpout+'/mypsfile.ps'
                dviname = tex_absname[:-3] + 'dvi'
                psname = tex_absname[:-3] + 'ps'
                pdfname = tex_absname[:-3]+'pdf'
                ps6name = tex_absname[:-3] + '6ps'
            except:
                self.setPdf('Rendering pdf file failed - not able to create temporary file.')
                self.cleanDir(tmpout)
                return
            # created temporary file in /tmp/tmpout/tmp*
            try:
            
                self.setHeading(tex_fd)
            except:
                self.setPdf('Rendereing pdf file failed - not able to write preamble for latex file in lecture printout')

            slides = self.listFolderContents(contentFilter={"portal_type": "Slide"})
                
            #tmp = slides.sort(lambda x,y:cmp(x.id, y.id))
            #for i in self.listFolderContents(contentFilter={"portal_type": "Slide"}):
            numslides = len(slides)
            for i in slides:
                #i = i.getObject()
                TITLE= i.Title()
                main_image = self.renderImage(i, i.getSlideImageText(), i.getSlideImage(), i.getSlideImageFormat())
                maincaption = i.getSlideImageCaption()
                if (EXPLANATION_FIG):
                    explanation_image = self.renderImage(i, i.getExplanationImageText(), i.getExplanationImage(), i.getExplanationImageFormat())
                    explcaption = i.getExplanationImageCaption()
                    haveExpImage = (explanation_image != 'FAILURE' and explanation_image)
                else:
                    explanation_image = False
                    explcaption = ''
                    haveExpImage = False
                # get text
                main_text_type = i.SlideText.getContentType()
                explanation_text_type = i.Explanation.getContentType()
                maintext = i.getRawSlideText()
                explanationtext = i.getRawExplanation()

                #figure out sizes of images in the pdf slide-show
                haveMainText = (len(maintext) > 0)
                haveExpText = (len(explanationtext) > 0)
                haveMainImage = (main_image != 'FAILURE' and main_image)
                expimage_size = 0
                image_size = 0
                if (not EXPLANATION_FIG):
                    if (haveMainImage):
                        image_size = self.getSuitableImageSize(haveMainText, haveExpText)

                else:
                    if (haveMainImage and (not haveExpImage)):
                        image_size = self.getSuitableImageSize(haveMainText, haveExpText)

                    elif (haveMainImage and haveExpImage):
                        image_size = self.getSuitableImageSize(haveMainText, haveExpText)
                        image_size = image_size -1
                        expimage_size = image_size -3
                    elif (haveExpImage and (not haveMainImage)):
                        expimage_size = self.getSuitableImageSize(haveMainText, haveExpText)
                        expimage_size = expimage_size - 3
                    
                    else:
                        expimage_size =0
                        image_size = 0
               
                os.write(tex_fd, '\\begin{frame}[fragile]'+'\n')
                os.write(tex_fd, '\\frametitle{' + TITLE +'}'+'\n')
                if (len(maintext) > 0 or haveMainImage):   
                    try:
                        self.setSlide(tex_fd, textfilename, main_text_type, maintext, main_image, i.getSlideImageFormat(), tmpout, image_size, maincaption)
                    except:
                        os.write(tex_fd, 'Failed to write main text of slide'+'\n')

###                if (len(explanationtext) > 0 or haveExpImage):
                if (len(explanationtext) > 0): ###
                    try:
                        os.write(tex_fd, '% before setSlide explanation\n')
###                        self.setSlideExpl(tex_fd, textfilename, explanation_text_type, explanationtext, explanation_image, expimage_type, tmpout, expimage_size, explcaption)
                        # REM ########
                        # not showing explanation image - even though set
                        self.setSlideExpl(tex_fd, textfilename, explanation_text_type, explanationtext, tmpout)
                    except:
                        os.write(tex_fd, 'Failed to write Explanation text of slide'+'\n')
                os.write(tex_fd, '\\end{frame}'+'\n')     

            #no more slides to add, finish latex document
            os.write(tex_fd, '\\end{document}'+'\n')
            pdftext = self.render_pdf(tmpout, tex_absname, dviname, psname, pdfname)

            
            self.setPdf(pdftext)
            self.reindexObject()
            #clean up files
            os.close(tex_fd)
            self.cleanDir(tmpout)
            self.changed = False
            
    security.declareProtected(View, 'cleanDir')
    def cleanDir(self, tmpout):
        '''removed temp directory and subdirectories created by using tempfile'''
        try:
            shutil.rmtree(tmpout, True)
        except OSError, (errno, strerror):
            print "tutorial pdf:(shutil.rmtree %s) OSError[%s]: %s" % \
                              (tmpout, errno, strerror)   
    def setSlide(self, tex_fd, textfilename, texttype, slidetext, slideimage, imagetype, tmpout, imagesize, caption):
        """set slide text for pdf files"""
        try:
            txt_fd, txt_absname = tempfile.mkstemp(dir=tmpout, suffix='.txt')
            image_fd, image_absname = tempfile.mkstemp(dir=tmpout, suffix='.png')
            imageeps = image_absname[:-3]+'eps'
            t_fd, t_absname = tempfile.mkstemp(dir=tmpout, suffix='.eps')
        except:
             ''' could not create txt file in setslide'''
             # something needed here !!!! 
             # FIXME - is it ok to return
             os.write(tex_fd, '% unable to create temporary txt file\n')
             return      
        os.write(tex_fd, '\\begin{tabular}{ll}'+'\n')
                    
        haveImage = (slideimage != 'FAILURE' and slideimage)
       
        #have either text or image
##        if (len(slidetext) > 0 and haveImage):
##            leftwidth=0.6    # Widths when both text and figures
##            rightwidth=0.4
##        elif (len(slidetext) > 0):
##            rigthwidth=0
##            leftwidth=1
##        else:
##            rightwidth=1
##            leftwidth=0
       
        if (len(slidetext) > 0 and haveImage):
            leftwidth=0.48    # Widths when both text and figures
            rightwidth=0.48
        elif (len(slidetext) > 0 and (not haveImage)):
            rightwidth=0
            leftwidth=0.97
        else:
            rightwidth=0.97
            leftwidth=0
       
        if(len(slidetext) > 0):
            # Start handling the text part - always upper left
            #
	    os.write(tex_fd, '\\begin{minipage}{'+str(leftwidth)+'\\textwidth}'+'\n')            
	    #os.write(tex_fd, '\\begin{columns}'+'\n')
	    #os.write(tex_fd, '\\column{'+str(leftwidth)+'\\textwidth}'+'\n')
	    #os.write(tex_fd, '{\\tiny'+'\n')
            if ((texttype == 'text/latex') or (texttype == 'text/x-tex')):
                # might be another than tex probably ...
                try:
                    os.write(tex_fd, slidetext)
                    #os.write(tex_fd, 'latex texts')
                except:
                    os.write(tex_fd, 'no latex text')
            elif (texttype == 'text/plain'):
                #text output
                try:
                    os.write(txt_fd, slidetext)
                except:
                    slidetext = 'could not write to file' + slidetext
                try:
                    os.system(bindir+'/txt2latex.htm ' + txt_absname + ' > ' + textfilename)
                    try:
                        slidetext = file(textfilename).read()
                    except:
                        slidetext = 'could not read file'
                except:
                    slidetext = 'could not do text-latex'

                try:
                    slidetext = self.tidyup(slidetext)
                    os.write(tex_fd, slidetext)
                    # os.write(tex_fd, '\\\\')
                except:
                    os.write(tex_fd, 'no text texts')
            elif (texttype == 'text/structured'):

                try:
                    t = LaTeX(slidetext)

                except:
                    t = 'could not execute LaTeX'
                os.write(tex_fd, str(t))
            elif ((texttype == 'text/restructured') or (texttype == 'text/x-rst')):
                try:
                    os.write(txt_fd, slidetext)
                except:
                    slidetext = 'could not write to file' + slidetext
                try:
                    os.system('rst2latex.py ' + txt_absname + ' > ' + textfilename)
                    for eachline in file(textfilename):
                        if (self.settext(eachline) == -1):
                            os.write(tex_fd, eachline)


                except:
                    slidetext = 'could not do rest-latex'
                    os.write(tex_fd, slidetext)  
            elif (texttype == 'text/html'):
                html_fd, html_absname = tempfile.mkstemp(dir=tmpout, suffix='.html')
                html2texfilename = html_absname[:-4] + 'tex'
                try:
                    os.write(html_fd, slidetext)
                except:
                    slidetext = 'could not write to file' + slidetext
                try:
                    os.system(bindir+'/html2tex ' + html_absname)
                    try:
                        slidetext = file(html2texfilename).read()
                    except:
                        slidetext = 'could not read file in setSlide text/html'
                except:
                    slidetext = 'could not do text-latex'

                try:
                    #slidetext = self.tidyup(slidetext)
                    os.write(tex_fd, slidetext)
                    # os.write(tex_fd, '\\\\')
                except:
                    os.write(tex_fd, 'no text texts')
                os.close(html_fd)
            else:
                os.write(tex_fd, '\n'+texttype+'\n')
            os.write(tex_fd, '\n')
            #os.write(tex_fd, '}'+'\n')
            # end of tiny
	    os.write(tex_fd, '\\end{minipage}'+'\n')
            ####################################################
       
        # now set image if any
        if (haveImage):
            # set the image if any
            try:
                try:
                    #if (imagetype == 'fig'):
                    #    os.write(image_fd, slideimage)
                    if (imagetype == 'image'):
                        os.write(image_fd, str(slideimage.data))
                except:
                    os.write(image_fd, 'no image data')
                try:
                    #os.system('imgtops --landscape ' + image_absname + ' > ' + psfilename)
                    #os.system('convert ' + image_absname + ' ' + imageeps)
                    if (imagetype == 'fig'):
                        #os.system('fig2dev -L eps ' + image_absname + ' ' + imageeps)
                        os.write(t_fd, slideimage)
                    elif (imagetype == 'r'):
                        os.write(t_fd, slideimage)
                    elif (imagetype == 'gnuplot'):
                        os.write(t_fd, slideimage) 
                    else:
                        os.system('convert -resize x500 ' + image_absname + ' ' + imageeps)
                    #os.system('convert -resize x500 ' + image_absname + ' ' + imageeps)
                    ##  os.write(tex_fd, '%\\begin{minipage}[t]{0.25\\textwidth}'+'\n')
                    ##             os.write(tex_fd, '\\resizebox{0.9\\textwidth}{!}{'+'\n')
                    ##             os.write(tex_fd, '\\rotatebox{-90}{'+'\n')
                    ##             os.write(tex_fd, '\\includegraphics{'+psfilename+'}'+'\n')
                    ##             os.write(tex_fd, '}'+'\n'+'}'+'\n')
                    ##             os.write(tex_fd, '%\\end{minipage}'+'\n')
                    ##             os.write(tex_fd,'}'+'\n')  # Ending main image - tiny
                    ##             os.write(tex_fd, '\\end{minipage}'+'\n')
                    ##os.write(tex_fd, '\\begin{figure}[h]'+'\n')
                    if (imagetype == 'r' or imagetype == 'gnuplot' or imagetype == 'fig'):
                        psimage = file(t_absname).read()
                    else:
                        psimage = file(imageeps).read()
                    if (len(psimage) > 0):
                        os.write(tex_fd, '\\hspace{0.5mm}'+'\n')                        
                        os.write(tex_fd, '\\begin{minipage}{'+str(rightwidth)+'\\textwidth}'+'\n')                        
                        #os.write(tex_fd, '\\begin{columns}'+'\n') #########################################
			#os.write(tex_fd, '\\column{'+str(rightwidth)+'\\textwidth}'+'\n')
                        #os.write(tex_fd, '{\\tiny'+'\n')
                        os.write(tex_fd, '\\begin{figure}\n')
                        #os.write(tex_fd, '\\resizebox{5cm}{!}{'+'\n')
                        os.write(tex_fd, '\\resizebox{'+str(imagesize)+'cm}{!}{'+'\n')
                        if (imagetype == 'r'):
                           os.write(tex_fd, '\\rotatebox{-90}{'+'\n')
                        if (imagetype == 'r' or imagetype == 'gnuplot' or imagetype=='fig'):
                            os.write(tex_fd, '\\includegraphics{'+t_absname+'}'+'\n')
                        else:
                            os.write(tex_fd, '\\includegraphics{'+imageeps+'}'+'\n')
                        
                        #    os.write(tex_fd, '\n')
                        #os.write(tex_fd, '}'+'\n'+'}'+'\n')
                        os.write(tex_fd, '}\n')
                        ##os.write(tex_fd, '\\end{figure}'+'\n')
                        #os.write(tex_fd,'}'+'\n')  # Ending main image - tiny
                        if (imagetype == 'r'):
                            os.write(tex_fd, '}'+'\n')
                        
                        if (len(caption) > 0):
                            os.write(tex_fd, '\\caption{\scriptsize '+caption+'}\n')
                        os.write(tex_fd, '\\end{figure}\n')
                        os.write(tex_fd, '\\end{minipage}'+'\n')                        
			#\begin{figure}[h]
                        #\resizebox{8cm}{!}{
                        #\rotatebox{-90}{
                        #\includegraphics{BASEFIG}
                        #\caption{BASECAPTION} % This really should be in a caption!!
                        #\end{figure}
                        ## }
                        ##   }
                    
                except:
                    ''' do something '''
            except:
                os.write(image_fd, 'no image data')
        #os.write(tex_fd, '\\end{columns}'+'\n')
	os.write(tex_fd, '\\end{tabular}'+'\n')
       
        # close files
        os.close(txt_fd)
        os.close(image_fd)
        os.close(t_fd)
###    def setSlideExpl(self, tex_fd, textfilename, texttype, slidetext, slideimage, imagetype, tmpout, imagesize, caption):
    def setSlideExpl(self, tex_fd, textfilename, texttype, slidetext, tmpout):
        """set slide text for pdf files"""
        try:
            txt_fd, txt_absname = tempfile.mkstemp(dir=tmpout, suffix='.txt')
###            image_fd, image_absname = tempfile.mkstemp(dir=tmpout, suffix='.png')
###            imageeps = image_absname[:-3]+'eps'
###            t_fd, t_absname = tempfile.mkstemp(dir=tmpout, suffix='.eps')
        except:
             ''' could not create txt file in setslide'''
             # something needed here !!!! 
             # FIXME - is it ok to return
             os.write(tex_fd, '% unable to create temporary txt file\n')
             return      
#        os.write(tex_fd, '\\begin{tabular}{ll}'+'\n')
                    
###        haveImage = (slideimage != 'FAILURE') 
##        if (len(slidetext) > 0 and haveImage):
##            leftwidth=0.5    # Widths when both text and figures
##            rightwidth=0.5
##        elif (len(slidetext) > 0):
##            rigthwidth=0
##            leftwidth=1
##        else:
##            rightwidth=1
##            leftwidth=0                        
        if(len(slidetext) > 0):
            # Start handling the text part - always upper left
            #
##	    os.write(tex_fd, '\\begin{minipage}{'+str(leftwidth)+'\\textwidth}'+'\n')            
	    #os.write(tex_fd, '\\begin{columns}'+'\n')
	    #os.write(tex_fd, '\\column{'+str(leftwidth)+'\\textwidth}'+'\n')
	    os.write(tex_fd, '{\\scriptsize'+'\n')
            os.write(tex_fd, '\\vfill'+'\n')
            os.write(tex_fd, '\\begin{spacing}{1}'+'\n')
            if ((texttype == 'text/latex') or (texttype == 'text/x-tex')):
                # might be another than tex probably ...
                try:
                    os.write(tex_fd, slidetext)
                    #os.write(tex_fd, 'latex texts')
                except:
                    os.write(tex_fd, 'no latex text')
            elif (texttype == 'text/plain'):
                #text output
                try:
                    os.write(txt_fd, slidetext)
                except:
                    slidetext = 'could not write to file' + slidetext
                try:
                    os.system(bindir+'/txt2latex.htm ' + txt_absname + ' > ' + textfilename)
                    try:
                        slidetext = file(textfilename).read()
                    except:
                        slidetext = 'could not read file'
                except:
                    slidetext = 'could not do text-latex'

                try:
                    slidetext = self.tidyup(slidetext)
                    os.write(tex_fd, slidetext)
                    # os.write(tex_fd, '\\\\')
                except:
                    os.write(tex_fd, 'no text texts')
            elif (texttype == 'text/structured'):

                try:
                    t = LaTeX(slidetext)

                except:
                    t = 'could not execute LaTeX'
                os.write(tex_fd, str(t))
            elif ((texttype == 'text/restructured') or (texttype == 'text/x-rst')):
                try:
                    os.write(txt_fd, slidetext)
                except:
                    slidetext = 'could not write to file' + slidetext
                try:
                    os.system('rst2latex.py ' + txt_absname + ' > ' + textfilename)
                    for eachline in file(textfilename):
                        if (self.settext(eachline) == -1):
                            os.write(tex_fd, eachline)


                except:
                    slidetext = 'could not do rest-latex'
                    os.write(tex_fd, slidetext)  
            elif (texttype == 'text/html'):
                html_fd, html_absname = tempfile.mkstemp(dir=tmpout, suffix='.html')
                html2texfilename = html_absname[:-4] + 'tex'
                try:
                    os.write(html_fd, slidetext)
                except:
                    slidetext = 'could not write to file' + slidetext
                try:
                    os.system(bindir+'/html2tex ' + html_absname)
                    try:
                        slidetext = file(html2texfilename).read()
                    except:
                        slidetext = 'could not read file in setSlide text/html'
                except:
                    slidetext = 'could not do text-latex'

                try:
                    #slidetext = self.tidyup(slidetext)
                    os.write(tex_fd, slidetext)
                    # os.write(tex_fd, '\\\\')
                except:
                    os.write(tex_fd, 'no text texts')
                os.close(html_fd)
            else:
                os.write(tex_fd, '\n'+texttype+'\n')
            os.write(tex_fd, '\n')
            os.write(tex_fd, '\\end{spacing}'+'\n')
            os.write(tex_fd, '}'+'\n')
            # end of scriptsize
##	    os.write(tex_fd, '\\end{minipage}'+'\n')
            ####################################################
        # now set image if any
################################3
        # close files
        os.close(txt_fd)
###        os.close(image_fd)
###        os.close(t_fd)



          
    def setPrintText(self, tex_fd, tmpout, textfilename, texttype, slidetext):
        
        try:
            txt_fd, txt_absname = tempfile.mkstemp(dir=tmpout, suffix='.txt')
        
        
            if(len(slidetext) > 0):
                # Start handling the text part - always upper left
                #
                if ((texttype == 'text/latex') or (texttype == 'text/x-tex')):
                    # might be another than tex probably ...
                    try:
                        os.write(tex_fd, slidetext)
                        #os.write(tex_fd, 'latex texts')
                    except:
                        os.write(tex_fd, 'no latex text')
                elif (texttype == 'text/plain'):
                    #text output
                    try:
                        os.write(txt_fd, slidetext)
                    except:
                        slidetext = 'could not write to file' + slidetext
                    try:
                        os.system(bindir+'/txt2latex.htm ' + txt_absname + ' > ' + textfilename)
                        try:
                            slidetext = file(textfilename).read()
                        except:
                            slidetext = 'could not read file'
                    except:
                        slidetext = 'could not do text-latex'

                    try:
                        slidetext = self.tidyup(slidetext)
                        os.write(tex_fd, slidetext)
                    except:
                        os.write(tex_fd, 'no text texts')
                elif (texttype == 'text/structured'):

                    try:
                        t = LaTeX(slidetext)

                    except:
                        t = 'could not do LaTeX'
                    os.write(tex_fd, str(t))
                elif ((texttype == 'text/restructured') or (texttype == 'text/x-rst')):
                    try:
                        os.write(txt_fd, slidetext)
                    except:
                        slidetext = 'could not write to file' + slidetext
                    try:
                        os.system('rst2latex.py ' + txt_absname + ' > ' + textfilename)
                        for eachline in file(textfilename):
                            if (self.settext(eachline) == -1):
                                os.write(tex_fd, eachline)


                    except:
                        slidetext = 'could not do rest-latex'
                        os.write(tex_fd, slidetext)
                elif (texttype == 'text/html'):
                    html_fd, html_absname = tempfile.mkstemp(dir=tmpout, suffix='.html')
                    html2texfilename = html_absname[:-4] + 'tex'
                    try:
                        os.write(html_fd, slidetext)
                    except:
                        slidetext = 'could not write to file' + slidetext
                    try:
                        os.system(bindir+'/html2tex ' + html_absname)
                        try:
                            slidetext = file(html2texfilename).read()
                        except:
                            slidetext = 'could not read file in setPrintText text/html'
                    except:
                        slidetext = 'could not do text-latex'
                
                    try:
                        #slidetext = self.tidyup(slidetext)
                        os.write(tex_fd, slidetext)
                        # os.write(tex_fd, '\\\\')
                    except:
                        os.write(tex_fd, 'could not write tex to file')
                    os.close(html_fd)
                else:
                    os.write(tex_fd, '\n'+ texttype + '\n')
            os.close(txt_fd)

        except:
            slidetext = 'could not make tmpfile in setPrintText'
            os.write(tex_fd, slidetext)
        os.write(tex_fd, '\n')
       
            #os.write(tex_fd, '}'+'\n')
            # end of tiny
            #os.write(tex_fd, '\\end{minipage}'+'\n')
    def setPrintTextWithoutVerbatim(self, tex_fd, tmpout, textfilename, texttype, slidetext):
       
       
        try:
            txt_fd, txt_absname = tempfile.mkstemp(dir=tmpout, suffix='.txt')
        
        
            if(len(slidetext) > 0):
                # Start handling the text part - always upper left
                #
                if ((texttype == 'text/latex') or (texttype == 'text/x-tex')):
                    # might be another than tex probably ...
                    slidetext = self.removeVerbatim(slidetext)
                    try:
                        os.write(tex_fd, slidetext)
                        #os.write(tex_fd, 'latex texts')
                    except:
                        os.write(tex_fd, 'no latex text')
                elif (texttype == 'text/plain'):
                    #text output
                    try:
                        os.write(txt_fd, slidetext)
                    except:
                        slidetext = 'could not write to file' + slidetext
                    try:
                        os.system(bindir+'/txt2latex.htm ' + txt_absname + ' > ' + textfilename)
                        try:
                            slidetext = file(textfilename).read()
                        except:
                            slidetext = 'could not read file'
                    except:
                        slidetext = 'could not do text-latex'

                    try:
                        slidetext = self.tidyup(slidetext)
                        slidetext = self.removeVerbatim(slidetext)
                        os.write(tex_fd, slidetext)
                    except:
                        os.write(tex_fd, 'no text texts')
                elif (texttype == 'text/structured'):

                    try:
                        t = LaTeX(slidetext)
                        #try:
                        #    t = self.removeVerbatim(str(t))
                        #except:
                        #    t = 'could not do removeVerbatim'
                    except:
                        t = 'could not do LaTeX'
                    #t = 'in text/structured'
                    os.write(tex_fd, str(t))
                elif ((texttype == 'text/restructured') or (texttype == 'text/x-rst')):
                    try:
                        os.write(txt_fd, slidetext)
                    except:
                        slidetext = 'could not write to file' + slidetext
                    try:
                        os.system('rst2latex.py ' + txt_absname + ' > ' + textfilename)
                        # Ok need special case for verbatim or change code
                        for eachline in file(textfilename):
                            if (self.settext(eachline) == -1):
                                #eachline = self.removeVerbatim(eachline)
                                os.write(tex_fd, eachline)


                    except:
                        slidetext = 'could not do rest-latex'
                        os.write(tex_fd, slidetext)       
                elif (texttype == 'text/html'):
                    html_fd, html_absname = tempfile.mkstemp(dir=tmpout, suffix='.html')
                    html2texfilename = html_absname[:-4] + 'tex'
                    try:
                        os.write(html_fd, slidetext)
                    except:
                        slidetext = 'could not write to file: ' + slidetext
                    try:
                        os.system(bindir+'/html2tex ' + html_absname)
                        try:
                            slidetext = file(html2texfilename).read()
                        except:
                            slidetext = 'could not read file in setprintwithoutverb in text/html'
                    except:
                        slidetext = 'could not do html-latex'

                    try:
                        slidetext = self.removeVerbatim(slidetext)
                    except:
                        slidetext = 'could not do remove verbatin - html2latex'
                    try:
                        os.write(tex_fd, slidetext)
                        # os.write(tex_fd, '\\\\')
                    except:
                        os.write(tex_fd, 'could not write tex')
                    os.close(html_fd)
                else:
                    os.write(tex_fd, '\n'+texttype+'\n')
            os.close(txt_fd)

        except:
            slidetext = 'could not make tmpfile in setPrintText'
            os.write(tex_fd, slidetext)
        os.write(tex_fd, '\n')
       
            #os.close(txt_fd)
            #os.write(tex_fd, '}'+'\n')
            # end of tiny
            #os.write(tex_fd, '\\end{minipage}'+'\n')
    security.declareProtected(View, 'removeVerb') 
    def removeVerb(self, text):
        beginstr = '\\verb^'
        endstr = '^'
        start = text.find(beginstr)
        end = 1
        # does not work if verbatim inside verbatim - should that happen?
        while (start >= 0):
            end = text.find(endstr, start, len(text))
            body = text[start+len(beginstr):end]
            b1 = body.replace('\\', '\\\\')
            b2 = b1.replace('[', '\\[')
            b3 = b2.replace(']', '\\]')
            b4 = b3.replace('$', '\\$')
            text = text[:start+len(beginstr)] + b4 + text[end:]
            ##start = -1
            start = text.find(beginstr, end+len(endstr), len(text))
        #text2 = text.replace('begin', 'segin')
        text2 = text.replace('\\verb^', '{\\texttt')
        text3 = text2.replace('^', '}')
        return text3
    security.declareProtected(View, 'removeVerbatim')
    def removeVerbatim(self, text):
        beginstr = '\\begin{verbatim}'
        endstr = '\\end{verbatim}'
        start = text.find(beginstr)
        end = 1
        # does not work if verbatim inside verbatim - should that happen?
        while (start >= 0):
            end = text.find(endstr, start, len(text))
            body = text[start+len(beginstr):end]
            b1 = body.replace('\\', '\\\\')
            b2 = b1.replace('[', '\\[')
            b3 = b2.replace(']', '\\]')
            b4 = b3.replace('$', '\\$')
            text = text[:start+len(beginstr)] + b4 + text[end:]
            ##start = -1
            start = text.find(beginstr, end+len(endstr), len(text))
        #text2 = text.replace('begin', 'segin')
        text2 = text.replace('\\begin{verbatim}', '{\\texttt')
        text3 = text2.replace('\\end{verbatim}', '}')
        return text3
    def tidyup(self, text):
        try:
             index1 = text.find('\\begin{document}')
        except:
             index1 = 0
        try:
             index2 = text.find('\\end{document}')
        except:
             index2 = len(text)
        # this has to fix, do later,,,
        if ((index != -1) and (index2 != -1)):
             text1 = text[index1+16:index2]
        else:
             text1 = 'index1 is: ' + index1 + ' index2 is: ' + index2 + ' ' + text
        return text1
        #return 'intidyup'
    def settext(self, line):
        
        if (line.find('\\usepackage') != -1):
             return 1
        elif (line.find('\\documentclass') != -1):
             return 1
        elif (line.find('\\begin{document}') != -1):
             return 1
        elif (line.find('\\end{document}') != -1):
             return 1
        elif (line.find('\\author') != -1):
             return 1
        elif (line.find('\\title') != -1):
             return 1
        elif (line.find('\\raggedbottom') != -1):
             return 1
        elif (line.find('\\date') != -1):
             return 1
        elif (line.find('extrarowheight') != -1):
             return 1
        else:
            return -1
                  
    def cutlatextext(self, text, start, finish):
        index1 = text.find(start)
        index2 = text.find(finish)
        if (index1 != -1):
            text1 = text[0:index1]
            if (index2 != -1):
                text2 = text1 + text[index2+len(finish):]
                return text2
            else:
                # could not find end of text to cut
                return text1
        else:
            # could not find beginning of text to cut
            return text
    def cutalllines(self, text, str):
        text1 = text.split('\n')
        counter = 0
        text2 = ''
        while(counter < len(text1)):
            index = text1[counter].find(str)
            if (index == -1):
                text2 = text2 + text1[counter]
            counter = counter + 1
        return text2
            
    def cutlatexline(self, text, str):
        index1 = text.find(str)
        if (index1 != -1):
            text1 = text[0:index1]
            index2 = text1.find('\n', index1)
            if (index2 != -1):
                text2 = text1 + text1[index2:]
                return text2
            return text1
        else:
            return text
    def cutlatexstring(self, text, str):
        text1 = text.replace(str, '')
        return text1
        
                
    def setHeading(self, tex_fd):
        titlefile=self.Title()
        parent = aq_parent(self)
        dep = aq_parent(parent)
        subtitlefile = parent.Title()
        authorfile = parent.getAuthor()
        dept = dep.getCode()+parent.getCourseCode()+'.'+parent.getNumberCode()
        strtitle = '\\title{'+titlefile+'}'+'\n'
        strsubtitle='\\subtitle{('+dept + ': ' + subtitlefile+')}'+'\n'
        strauthor='\\author{{\\green '+authorfile+'}}'+'\n'

        os.write(tex_fd, '\\documentclass[%'+'\n')   
        os.write(tex_fd, ']{beamer}'+'\n')
        os.write(tex_fd, '\\usepackage{graphics,amsmath,amsfonts,amssymb}'+'\n')
        os.write(tex_fd, '\\usepackage[T1]{fontenc}'+'\n')
        os.write(tex_fd, '\\usepackage[numbers, sort&compress]{natbib}' + '\n')
        os.write(tex_fd, '\\usepackage[utf8]{inputenc}' + '\n')
        os.write(tex_fd, '\\usepackage{float, rotating, subfigure}\n')
        os.write(tex_fd, '\\usepackage[skip=2pt]{caption}\n')
        os.write(tex_fd, '\\usepackage{setspace}\n')
        os.write(tex_fd, '\\newcommand{\\bs}{\\boldsymbol}\n')
        os.write(tex_fd, '\\newcommand{\\bi}{\\begin{itemize}\\item}\n')
        os.write(tex_fd, '\\newcommand{\\ei}{\\end{itemize}}\n')
        os.write(tex_fd, '\\newcommand{\\eq}[1]{\\begin{equation} #1 \\end{equation}}\n')
        os.write(tex_fd, '\\newcommand{\\ea}[1]{\\begin{eqnarray} #1 \\end{eqnarray}}\n')
        os.write(tex_fd, '\\newcommand{\\vs}{\\vspace{2mm}}\n')
        os.write(tex_fd, '\\makeatletter\n')
        os.write(tex_fd, '\\makeatother\n')
#        os.write(tex_fd, '\\hypersetup{pdfpagemode=FullScreen}'+'\n')
	os.write(tex_fd, '\\usetheme{CambridgeUS}'+'\n')
	os.write(tex_fd, '\\usecolortheme{dolphin}'+'\n')
        os.write(tex_fd, '\\setbeamerfont{caption name}{size=\scriptsize}'+'\n')
        os.write(tex_fd, strtitle)
        os.write(tex_fd, strsubtitle)
        os.write(tex_fd, strauthor)
        os.write(tex_fd, '\\begin{document}'+'\n')
        os.write(tex_fd, '\\maketitle' + '\n')
    def getTableHeadings(self):
        return ['Examples', 'Alternative', 'Details', 'Handout']
    security.declareProtected(View, 'computeNumSlides')
    def computeNumSlides(self):
        '''Find number of slides which belong to this lecture'''
        # also can get handle on objects of specified type if there
        # in anything more in the folder
        # self.listFolderContents(contentFilter={"portal_type":"Tutorial"})
        #return len(self.objectIds())
        return len(self.getFolderContents(contentFilter={"portal_type":"Slide"}))
    security.declareProtected(View, 'computeNumQuestions')
    def computeNumQuestions(self):
        '''Find number of questions which belong to this tutorial'''
        #return len(self.objectIds())
        #questions = self.listFolderContents(contentFilter={"portal_type":"TutorWebQuestion"})
        questions = self.getFolderContents(contentFilter={"portal_type":"TutorWebQuestion"})
        return len(questions)
        #numquestions = len(questions)
        #numrquestions = 0
        #for q in questions:
        #    obj = q.getObject()
        #    qtype = obj.getContentType()
        #    if (qtype == 'text/r'):
        #        numrquestions = numrquestions + 1
        #return (numquestions - numrquestions)
    security.declareProtected(View, 'computeNumRQuestions')
    def computeNumRQuestions(self):
        '''Find number of r questions which belong to this tutorial'''
        #return len(self.objectIds())
        questions = self.getFolderContents(contentFilter={"portal_type":"TutorWebQuestion"})
        numquestions = len(questions)
        numrquestions = 0
        for q in questions:
            qobj = q.getObject()
            qtype = qobj.getContentType()
            if (qtype == 'text/r' or qtype == 'text/r-latex'):
                numrquestions = numrquestions + 1
        return numrquestions
# Register this type in Zope
#registerATCTLogged(Lecture)
if PLONE_VERSION == 3:
    registerATCTLogged(Lecture)
else:
    atapi.registerType(Lecture, PROJECTNAME)
