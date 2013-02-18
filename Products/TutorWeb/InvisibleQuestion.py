from Products.Archetypes.public import OrderedBaseFolder
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.folder import ATFolderSchema

from Products.DataGridField import DataGridField, DataGridWidget
from Products.DataGridField.Column import Column
from Products.DataGridField.SelectColumn import SelectColumn
from Products.DataGridField.RadioColumn import RadioColumn
from Products.DataGridField.CheckboxColumn import CheckboxColumn
from Products.DataGridField.FixedColumn import FixedColumn
from Products.DataGridField.DataGridField import FixedRow
from Products.DataGridField.HelpColumn import HelpColumn
#from Products.DataGridField.RadioColumn import RadioColumn

from Products.Archetypes.public import DisplayList
from Products.CMFCore import permissions
from AccessControl import ClassSecurityInfo, getSecurityManager

import re
import os
import shutil
import tempfile
from Products.CMFCore.utils import getToolByName
import string
from Products.Archetypes import atapi
from Acquisition import aq_parent
from config import *
from permissions import *
from tools import *
from Products.Archetypes.public import Schema, BooleanField, BooleanWidget, \
     IntegerField, IntegerWidget, StringField, TextField, \
     TextAreaWidget, StringWidget, RichWidget, SelectionWidget, ImageWidget, ImageField, ReferenceField, ReferenceWidget
#from random import random
import random
from zope.interface import implements
from Products.TutorWeb.interfaces import IPrintable, IQuestion, IOrderedTutorWebContent
from Products.validation.validators import *
from zope.event import notify
if PLONE_VERSION == 4:
    from Products.Archetypes import atapi
    from config import PROJECTNAME

class InvisibleQuestion(ATFolder):
    '''a tutorweb question '''
    archetype_name = portal_type = meta_type = 'InvisibleQuestion'
    #implements(IPrintable, IQuestion, IOrderedTutorWebContent)
    global_allow = 0

    ANSWER_FORMATS = DisplayList ((
    ('text/plain', 'Plain Text'),
    ('text/latex', 'LaTeX'),
    ('text/structured', 'Structured Text'),
    ('text/restructured', 'reStructured Text'),
    ('text/html', 'HTML'),
    ))
    schema = ATFolderSchema.copy() + Schema((
         StringField('title',
                required=False,
                searchable=0,
                default='Question',
                widget=StringWidget(
                    label='Title',
                    description='The title of the question',
                    ),
                
            ),
         ReferenceField('OriginalQuestion',
                    #vocabulary="getAvailableCourses",
                    widget=ReferenceWidget(
                           label="original quiz question",
                           description='A question student has been asked',
                           destination=".",
                           #destination_types=("QuestionResult",),
                           visible={'view':'invisible', 'edit':'invisible'},
                           
                           ),
                       multiValued=False,
                       relationship='isOriginalQuestion',
                       allowed_types= ("TutorWebQuestion",),
                        
                   ),
           StringField('ImageUrl',
                default='',
                validators=('isURL',), 
                ),
          ImageField('QuestionImage',
                   #original_size=(600,600),
                   #max_size=(600,600),
                   sizes={ 'mini' : (80,80),
                           'normal' : (200,200),
                            'big' : (100,100),
                            'maxi' : (500,500),
                           },
                   widget=ImageWidget(label='Slide image',
                                      description='Main image for slide, displayed to the right of main text of the slide. Possible formats for uploaded images are: png, gif and jpeg.', 
                                      #macro='tutorwebimage',
                             # condition ='object/isImageFormat',
                                       )),
          TextField('question', # See 'description' property
                                        # of the widget.
                searchable=0,
                required=True,
                primary=True,
                allowable_content_types=('text/plain',
                    'text/structured',
                    'text/restructured',
                    'text/latex',
                    'text/r',
                    'text/r-latex',
                    ),
                default_output_type='text/latex',
                default_content_type='text/latex',
                mutator='setQuestionText',
                widget=RichWidget(
                    label='Question',
                    macro='tutorwebquestion',
                    modes='edit',
                    visible={'view':'invisible', 'edit': 'invisible'},
                    description='The question text. This is what the '
                    'candidate will see.',
                    rows=10,
                    ),
                
            ),
       
         TextField('quizQuestion', # See 'description' property
                                        # of the widget.
                allowable_content_types=('text/plain','text/html',),
                default_output_type='text/html',
                default_content_type='text/html',
                #accessor='transformQuizQuestion',
                widget=RichWidget(
                    label='rendered quiz question',
                    visible={'view':'invisible', 'edit':'invisible'},
                    ),
              
            ),
       
       
          StringField('AnswerFormat',
                vocabulary=ANSWER_FORMATS,
                default='text/plain',
                widget=SelectionWidget(label='Answer text format',
                                       description='Select the text format used for the answer text.',
                                     visible={'edit':'invisible', 'view':'invisible'},   ),
                ),
          DataGridField('AnswerList',
                searchable=0, # One unit tests checks whether text search works
                widget = DataGridWidget(label='Answers',
                    description='Specify the answer text, if the answer is correct and if the answer should be in a randomized order when displayed in a quiz.',
                     columns= {
                    "answertext" : Column("Answer text"),                
                    "correct" : CheckboxColumn("Correct"),
                    "randomize" : CheckboxColumn("Randomize", default='1'),
                    "answerid" : FixedColumn("Id", visible=False),
                    },
                          visible={'edit':'invisible', 'view':'invisible'},               
                    ),   
                columns=('answertext', 'correct', 'randomize', 'answerid'),
                
            ),
         TextField('quizQuestionExplanation', # See 'description' property
                                        # of the widget.
                allowable_content_types=('text/html',),
                default_output_type='text/html',
                default_content_type='text/html',
                #accessor='transformQuizQuestion',
                widget=RichWidget(
                    label='rendered quiz question explanation',
                    visible={'edit':'invisible'},
                    ),
              
          ),
          BooleanField('allowMultipleSelection',
                # If 'allowMultipleSelection' is True, this is a
                # multiple answer question, i.e. one where more than
                # one answer can be true. Otherwise it is a multiple
                # choice question, i.e. exactly only one answer is
                # correct.  The question_view template is designed to
                # support this. When 'allowMultipleSelection' is True,
                # radio buttons will be generated.  If not, check
                # boxes will be shown.  See also 'description'
                # property of the widget.
                accessor='isAllowMultipleSelection',
                default=0,
                searchable=False,
                widget=BooleanWidget(
                    label='Allow Multiple Selection',       
                    description='If the selection of multiple answers should be possible, mark this checkbox.',
                     visible={'edit':'invisible', 'view':'invisible'},
                    ),
                read_permission=PERMISSION_STUDENT,
            ),
          BooleanField("randomOrder", # See 'description' property
                                        # of the widget.
                accessor='isRandomOrder',
                required=False,
                default=1,
                read_permission=PERMISSION_INTERROGATOR,
                widget=BooleanWidget(
                    label='Randomize Answer Order',
                    description='Check this box if you want the answers '
                    'to this question to appear in a different, random '
                    'order for each candidate. Otherwise the '
                    'same order as in the &quot;contents&quot;-view will '
                    'be used.',
                    modes='view',
                    
                     visible={'edit':'invisible', 'view':'invisible'},
                    ),
                #read_permission=PERMISSION_STUDENT,
            ),
            IntegerField("numberOfRandomAnswers", # See 'description'
                                                  # property of the
                                                  # widget.
                default=-1,
                read_permission=PERMISSION_INTERROGATOR,
                widget=IntegerWidget(
                    label='Number of Random Answers',
                    description='The number of answers which are randomly '
                    'selected when a new quiz question is generated for a candidate. '
                    'A value &lt;= 0 means that all answers '
                    'will be used.',
                     visible={'edit':'invisible', 'view':'invisible'},
                   ),
                #read_permission=PERMISSION_STUDENT,
            ),
          IntegerField('points', # See 'description' property of the widget.
                accessor='getPointsPrivate',
                required=False,
                default=1,
                #validators=('isPositiveInt'),
                read_permission=PERMISSION_INTERROGATOR,
                widget=IntegerWidget(
                    label='Points',       
                    description='The number of points assigned to this question.',
                    visible={'edit':'invisible', 'view':'invisible'},
                    ),
                #read_permission=PERMISSION_STUDENT,
            ),
            BooleanField('tutorGraded',
                accessor='isTutorGraded',
                default=False,
                #searchable=False,
                widget=BooleanWidget(
                    label='Tutor-Graded',
                    description='If answers to this question are graded manually, mark this checkbox.',
                    modes='view',
                     visible={'edit':'invisible', 'view':'invisible'},
                    ),
                #read_permission=PERMISSION_STUDENT,
               
            ),
         
        ))
    numaskedfor = 0
    numcorrect = 0
    transformrquestion = False
    inlineanswer = False
    NOTAinQuestion = False
    ans = DisplayList()
    changed = False

    
    security = ClassSecurityInfo()
    def setQuestionText(self, value, **kwargs):
        '''set question text'''
        f = self.getField('question')
        f.set(self, value, raw=True, **kwargs)
    def createQuestionResult(self):
        """Create a new questionresult object for student and initialize it."""
        typeName = 'QuestionResult'
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
        o.setTitle('Question result')
        o.reindexObject()
        return o
    def publishAll(self, typeofobject=None, originalobj=None):
        '''publich content'''
        self.tryWorkflowAction("publish", ignoreErrors=True)
    def editedObject(self, objtype=None):
        '''hmmm'''
        #parent = aq_parent(self)
        #grandparent = aq_parent(parent)
        #grandparent.setQuestionChanged(True)
        #self.setQuestionAndAnswer() 
    def setChanged(self, ch):
        '''hmm'''
        #self.changed = ch
        #lec = aq_parent(self)
        #tut = aq_parent(lec)
        #tut.setQuestionChanged(True)
    def getQuestImgUrl(self):
        return self.getImageUrl()    
    def getQuestImg(self):
        return self.getQuestionImage()
        #return self.getField('QuestionImage').get(self)
    def getQuestImgTag(self):
        qimage = self.getQuestImg()
        if (qimage):
            return self.getQuestionImage().tag()
        else:
            return ""
        
        #return self.getField('QuestionImage').get(self).tag()
    def getQuestionExplanationData(self):
        return self.getField('quizQuestionExplanation').get(self)
    def getQuestionData(self):
        texttype = self.question.getContentType()
        if (texttype == 'text/latex'):
            outputtext = self.getField('quizQuestion').get(self)
        elif (texttype == 'text/r'):
            text = self.getRawQuestion()
            outputtext = self.getQuizQuestion()
        elif (texttype == 'text/r-latex'):
             text = self.getRawQuestion()
             outputtext = self.getField('quizQuestion').get(self)
        else:
            outputtext= self.getQuizQuestion()
        if (self.inlineanswer == True):
            out = outputtext.split('TWPULLDOWNMENU')
            return out
        else:
            return outputtext
   
    security.declarePrivate('initializeObject')
    def initializeObject(self):
        self.setQuestionAndAnswer()
        self.tryWorkflowAction("publish", ignoreErrors=True)       
    security.declarePrivate('tryWorkflowAction')
    def tryWorkflowAction(self, action, ignoreErrors=False, comment=None):
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
    def setQuestionAndAnswer(self):
        ''' if it is an r questiont then should create answers as needed'''
        ans = self.getAnswerList()
        rowcounter = 0
        
        for row in ans:  
            row['answerid'] = str(rowcounter)
            rowcounter = rowcounter + 1
        texttype = self.question.getContentType()
        haveNota = False
        if (texttype == 'text/r' or texttype=='text/r-latex'):
            
            rawtext = self.getRawQuestion()
            if ('NOTA' in rawtext):
                haveNota = True
            
            
            text = self.renderRQuestion(self.getQuestion(), 'bitmap(file=png_fd)\r\n')
            
            numans = len(text) - 1
            #if (len(text) == 5): # s == (question,ans1,ans2,ans3,NOTA)
            # must have at least one answer to use NOTA
            if (haveNota and numans > 2):
                
                if (text[numans][0] == '2' or ('NA' in text[numans])):
                    s = text[0:numans]
                    corrans = 0
                    haveNota = False
                else:
                    if (text[numans][0] == '1' or ('NOTA+' in text[numans])):
                        corrans = 3
                        s = text
                        s[numans] = 'None of the above'
                    elif (text[numans][0] == '0' or ('NOTA-' in text[numans])):
                        corrans = 0
                        s = text
                        s[numans] = 'None of the above'
                    elif (text[numans][0] == '4' or ('AOB+' in text[numans])):
                        corrans = 3
                        s = text
                        s[numans] = 'All of the above'
                    elif (text[numans][0] == '3' or ('AOB-' in text[numans])):
                        corrans = 0
                        s = text
                        s[numans] = 'All of the above'
                    else:
                        '''This is an error'''
                        s = text[0:numans]
                        corrans = 0
                   
            else:
                s = text
                corrans = 0
            #
            numanswersneeded = (len(s)-1) - rowcounter
            if (numanswersneeded != 0):
                numanswersneeded = len(s) - 1
                tempans = []
                numans = 0
                while (numanswersneeded > 0):
                    #temp = self.createAnswer() 
                    temprow = {}
                    temprow['answertext'] = ''
                    temprow['correct'] = ''
                    temprow['randomize'] = ''
                    temprow['answerid'] = str(numans)
                    tempans.append(temprow)
                    numanswersneeded = numanswersneeded - 1
                    numans =  numans + 1
                self.setAnswerList(tempans)
            counter = 0
            answers = self.getAnswerList()
            numans = len(answers)
            # can move this code up no need for two while loops here!
            while (counter < numans):
                if (counter == (numans - 1) and haveNota): # REMEMBER s, text..
                    answers[counter]['answertext'] = s[counter+1] 
                    answers[counter]['randomize'] = ''
                else:
                    answers[counter]['randomize'] = '1'
                answers[counter]['correct'] = ''
                counter = counter + 1
                # PUTTING THIS HERE
                # FIXME NOT CORRECT
            if (numans > 0):
                answers[corrans]['correct'] = '1'        
        self.reindexObject()
        self.transformrquestion = True
        self.transformQuizQuestion()
        self.NOTAinQuestion = haveNota
        #lec = aq_parent(self)
        #tut = aq_parent(lec)
        #tut.questionchanged = True
    security.declareProtected(View, 'isRQ')
    def isRQ(self):
        type = self.question.getContentType()
        return (type == 'text/r' or type == 'text/r-latex')
    security.declareProtected(View, 'toTransformR')
    def toTransformR(self):
        return (self.transformrquestion and self.isRQ())
    #security.declareProtected(View, 'setTransformR')
    def setTransformR(self, value):
        self.transformrquestion = value
    security.declareProtected(View, 'getTransformR')
    def getTransformR(self):
        return self.transformrquestion
    def getAnswerDisplay(self):
        return self.ans
   
    security.declarePublic("renderRQuestion")
    def renderRQuestion(self, questiontext, HEADER):
        "jaso"
        tmpout = tempfile.mkdtemp()
        png_fd, png_absname = tempfile.mkstemp(dir=tmpout, suffix='.png')
        render = False
        
        setdatafiles = False
        if ('read' or 'source' in questiontext):
            tmpout1 = tempfile.mkdtemp()    
            setdatafiles = True        
            parent = aq_parent(self)
            extradata = parent.getAllExtraFiles()
            for ext in extradata:
                extra = ext.getObject()
                filename = extra.getTitle()
                extraid = extra.getId()
                f = open(tmpout1+'/'+extraid,'w')
                text = str(extra.getField('file').get(extra).data)
                for ex in extradata:
                    extobj = ex.getObject()
                    extid = extobj.getId()
                    if (extid in text):
                        text = text.replace(extid, '/'+tmpout1+'/'+extid)
                f.write(text)
                f.close()
                if (extraid in questiontext):    
                    text = str(extra.getField('file').get(extra).data) 
                    questiontext = questiontext.replace(extraid, '/'+tmpout1+'/'+extraid)
       
        try:
            stdin,stdout = os.popen2('R --slave')
            try:
                stdin.write('bitmap(file="'+png_absname+'")\r\n')
            except:
                return 'FAILURE'
            try:
                stdin.write(questiontext)
                stdin.write('\r\n')
                stdin.write('dev.off()')
                try:
                    stdin.flush()
                    try:
                        stdin.close()
                        try:
                            s = stdout.read() #s should be of the form %s|%s|%s|%s
                            try:
                                stdout.flush()
                                render = True
                                try:
                                    stdout.close()
                                except:
                                    ''' bla bla'''
                            except:
                                 ''' bla bla'''

                        except:
                            ''' bla bla'''
                        
                    except:
                        '''bla bla'''
                except:
                    '''bla bla'''
            except:
                '''bla bla'''
        except:
            render = False
        
        
        # if exists png file then read data and set
        # else set png file as empty DELETE_IMAGE
        try:
            mainimagefile = open(png_absname, 'r')
        except:
            '''Could not open image file??'''
        try:
            mainimage = mainimagefile.read()
        except:
            '''could not read from image file???'''
        mainimagefile.close()
        try:
            if (mainimage):
                self.setQuestionImage(mainimage)
            else:
                self.setQuestionImage('DELETE_IMAGE')
                
        except:
            '''????'''

        if (render is True):
            s = s.split("|")
        else:
            s = questiontext.split("|")
           
        
        #remove temporary directories created by the use of tempfile'''
        os.close(png_fd)
        try:
            shutil.rmtree(tmpout, True)
            if (setdatafiles):
                shutil.rmtree(tmpout1, True)
        except OSError, (errno, strerror):
            print "tutorial pdf:(shutil.rmtree %s) OSError[%s]: %s" % \
                     (tmpout, errno, strerror)  
            
        numins = len(s)
        if ("null device" in s[numins-1]):
            temp = s[numins-1]
            temp = temp.split("null device")
            s[numins-1] = temp[0]
        return s
    # Should only do this if asking for a new question - in quiz
    # need to set a boolean thingy...
    def getMyId(self):
        return self.getId() + '/'
    def findPicText(self, text):
        '''lsllsls'''
       
        if ('#PICTURE' in text):
            s1 = text.split('#PICTURE')
            s2 = s1[1]
           
            if ('#TEXT' in s2):
                s3 = s2.split('#TEXT')
                o
                return s3[0]
            else:
                
                 return s2
        else:
            return ''
    def findTextText(self, text):
        '''lsllsl'''
        
        if ('#TEXT' in text):
            s1 = text.split('#TEXT')
            s2 = s1[1]
            
            if ('#PICTURE' in s2):
                s3 = s2.split('#PICTURE')
                
                return s3[0]
            else:
               
                return s2
        else:
            return ''
    security.declareProtected(View, 'transformRQuestion')
    def transformRQuestion(self):
        if (self.toTransformR()):
            self.ans = DisplayList()
            text = self.getRawQuestion()
            type = self.question.getContentType()
            if (type == 'text/r' or type == 'text/r-latex'):
                '''r based transformation needed'''
                haveNota = False
                if ('NOTA' in text):
                    haveNota = True
                
                rdata = self.renderRQuestion(self.getQuestion(), 'bitmap(file=png_fd\r\n')
                # Fixme must have at least three answers??
                #numans = max((len(rdata) - 2), 3)
                numans = len(rdata) -1
                
                counter = 0
                ans1 = self.getAnswerList()
                # CAREFULE, out of RANGE if not....
                # FIXME
                if (haveNota):
                    numans = numans - 1
                while (counter < numans):
                    #tmp = rdata[counter+1].replace('<br>', '\\n')
                    #ansobj = b.getObject()
                    ans1[counter]['answertext'] = rdata[counter+1]
                    self.ans.add(str(counter), rdata[counter+1])
                    counter = counter + 1
                
                if (haveNota and (len(ans1) > counter)):
                    self.ans.add(str(counter), ans1[counter]['answertext'])
                #tmp = rdata[0].replace('<br>', '\\n')
                #tmp = self.transformText('text/plain', rdata[0])
                self.setQuizQuestion(rdata[0])
                self.quizQuestion.setContentType(self, 'text/plain')
                self.reindexObject()
        return 'nothing'
    security.declareProtected(View, 'transformSettingOrigin')
    def transformSettingOrigin(self, type, text, origin):
        
        trans = getToolByName(self, 'portal_transforms')
        
        data = trans.convertTo('text/html', text, mimetype=type, usedby=self)
        objects = data.getSubObjects()
        for x in objects:       
            if hasattr(self, x):
                self.manage_delObjects([x])
            if hasattr(self, origin+x):
                self.manage_delObjects([origin+x])    
            self.manage_addImage(origin+x, objects[x])
            container = self[origin+x]
            container.manage_permission(
                  permissions.View, 
                  roles = ["Anonymous", "Authenticated", "Manager"],
                  acquire=False)  
            container.manage_permission(
                  'Delete objects', 
                  roles = ["Anonymous", "Authenticated", "Manager"],
                  acquire=False)
        transformedtext = data.getData()
        if (type == 'text/latex'):
            path = '/'.join(self.getPhysicalPath())
            transformedtext = transformedtext.replace('SRC="', 'SRC="'+path+'/')     
        for x in objects:
            transformedtext = transformedtext.replace(x, origin+x)
        self.reindexObject()
        return transformedtext
    security.declareProtected(View, 'transformText')
    def transformText(self, type, text):
        
        trans = getToolByName(self, 'portal_transforms')
        
        data = trans.convertTo('text/html', text, mimetype=type, usedby=self)
        objects = data.getSubObjects()
        for x in objects:       
            if hasattr(self, x):
                self.manage_delObjects([x])
            self.manage_addImage(x, objects[x])
            container = self[x]
            container.manage_permission(
                  permissions.View, 
                  roles = ["Anonymous", "Authenticated", "Manager"],
                  acquire=False)  
            container.manage_permission(
                  'Delete objects', 
                  roles = ["Anonymous", "Authenticated", "Manager"],
                  acquire=False)
        transformedtext = data.getData()
        if (type == 'text/latex'):
            path = '/'.join(self.getPhysicalPath())
            transformedtext = transformedtext.replace('SRC="', 'SRC="'+path+'/')     
       
        return transformedtext       
    security.declareProtected(View, 'transformQuestion')
    def transformQuestion(self, type, answertype, text, answertext):
        #tmpout = tempfile.mkdtemp() 
        #tex_fd, tex_absname = tempfile.mkstemp(dir=tmpout, suffix='.transformQuestion')
        ans1 = self.getAnswerList()
        self.ans = DisplayList()
       
        if ((answertype == type) and type == 'text/latex'):
            # transform together, to get image numbers correct
            transformtext = text + '\nANSWER'+answertext
            #os.write(tex_fd, 'start of transformtext' + '\n')
            #os.write(tex_fd, transformtext)
            #data = self.transformText(type, transformtext)
            data = self.transformSettingOrigin(type, transformtext, 'question')
            
            endswith = data.endswith('<BR><HR>\n')
            
            endswith = data.endswith('<BR><HR>\n\n')
            
            if (data.endswith('<BR><HR>\n\n')):
                data = data[:-10]
           
            data1 = data.split('ANSWER')
            self.setQuizQuestion(data1[0])
            self.quizQuestion.setContentType(self, 'text/html')
            numans = len(data1)
            for i in range(1, numans):
                self.ans.add(str(i-1), data1[i])
                  
                
        else:
            
             #data = self.transformText(type, text)
             data = self.transformSettingOrigin(type, text, 'question')
             if (data.endswith('<BR><HR>\n\n')):
                data = data[:-10]
             self.setQuizQuestion(data)
             self.quizQuestion.setContentType(self, 'text/html')
             #data = self.transformText(answertype, answertext)
             data = self.transformSettingOrigin(answertype, answertext, 'question')
             if (data.endswith('<BR><HR>\n\n')):
                data = data[:-10]
             data1 = data.split('ANSWER')
             numans = len(data1)
             for i in range(0, numans):
                 self.ans.add(str(i), data1[i])
                
        
        self.reindexObject()
    def inlineAnswer(self):
        return self.inlineanswer
    def transformQuizQuestion(self):
        text = self.getRawQuestion()
        if ('TWPULLDOWNMENU' in text):
            self.inlineanswer = True
        else:
            self.inlineanswer = False
        type = self.question.getContentType()
        # don't need to do this if text is text/plain
        # FIXME
        answertype=self.getAnswerFormat()
        answers = self.getAnswerList()
        answertext = ''
        for row in answers:
            answertext = answertext + row['answertext'] + 'ANSWER'
        answertext = answertext[0:-6]
        if (type == 'text/r'):
            self.transformRQuestion()
            #set data to be converted
            type = 'text/plain'
        elif (type == 'text/r-latex'):
            self.transformRQuestion()
            type = 'text/plain'
            # NB NB FIXME
            # Not correct will get html
            text = self.getRawQuizQuestion()
            answers = self.getAnswerList()
            answertext = ''
            for row in answers:
                answertext = answertext + row['answertext'] + 'ANSWER'
            #!!!! MUST ADDD !!!!!!!!!!
            # set answer, answer could be latex as well
            # FIXME *****************************************
            #text = text.replace('\\latex', '')
            #data = self.transformText('text/latex', text)
            #self.setQuizQuestion(data)
            self.transformQuestion('text/latex', 'text/latex', text, answertext)
        else:
            self.transformQuestion(type, answertype, text, answertext)                    
           
    

    security.declareProtected(View, 'makeNewTest')
    def makeNewTest(self):
        """generate a new quiz"""
        
        answersrand = []
        answersnorand = []
        
        grid = self.getWrappedField('AnswerList')
        answer = 'no answer'
        rowrandom = grid.search(self, randomize='1')
        numa = len(rowrandom)
        num1 = str(numa)
       
        rownotrandom = grid.search(self, randomize='')
        numa = len(rownotrandom)
        num1 = str(numa)
        
        for a in rowrandom:
            answersrand.append(a['answerid'])
        for a in rownotrandom:
            answersnorand.append(a['answerid'])
        ##if self.isRandomOrder() and (not suMode):
        if self.isRandomOrder():
            # use random order
            numRnd = 0
            suggestedAnswerIds = []
            if (len(answersrand) > 0):
                suggestedAnswerIds = random.sample(answersrand,
                                             len(answersrand))
            if (len(answersnorand) > 0):
                suggestedAnswerIds = suggestedAnswerIds + answersnorand
            
        else:
            # Use the order in the "contents"-view
            if (len(answersrand) > 0):
                    suggestedAnswerIds = answersrand
            if (len(answersnorand) > 0):
                    suggestedAnswerIds = suggestedAnswerIds + answersnorand
        
        # Store the new suggested answer ids in the results object
        #candidateResult.setSuggestedAnswer(self, suggestedAnswerIds, candidateid)
        return suggestedAnswerIds
    if PLONE_VERSION == 3:
        security.declarePublic('userIsGrader')
        def userIsGrader(self, user):
            mctool = getToolByName(self, 'ecq_tool')
            return mctool.userHasOneOfRoles(user,
                                        ('Manager', ROLE_RESULT_GRADER,),
                                        self)
    security.declarePrivate('getCorrectAnswerIds')
    def getCorrectAnswerIds(self, result):
        """ Return the IDs of the correct answers to this question that
            were presented to the candidate.

            @param result The result object of the candidate.
        """
        suggestedAnswerIds = self.getSuggestedAnswerIds(result)
        retVal = []
        for a in self.contentValues():
            aId = a.getId()
            if a.isCorrect() and (aId in suggestedAnswerIds):
                retVal.append(a.getId())
        return retVal
    security.declareProtected(PERMISSION_STUDENT, 'getPoints')
    def getPoints(self, *args, **kwargs):
        return self.getPointsPrivate(*args, **kwargs)
    def getCandidatePoints(self, result):
        if self.isTutorGraded():
            return result.getTutorPoints(self)
        else:
            # Check if we have a tutor-given or a cached value
            retVal = result.getCachedQuestionPoints(self)
            if retVal is None:
                retVal = self.computeCandidatePoints(result)
                result.setCachedQuestionPoints(self, retVal)
            return retVal
    security.declareProtected(PERMISSION_STUDENT, 'getSuggestedAnswerIds')
    def getSuggestedAnswerIds(self, result):
        """Return a list with the IDs of the answer objects that were
        presented to the candidate.
        
        @param result The candidate's result object.
        """
        return result.getSuggestedAnswer(self)
    security.declarePrivate('computeCandidatePoints')
    def computeCandidatePoints(self, result):
        """Return how many points the candidate got for this question.

        @param result The result object of the candidate.

        If a custom scoring script has been uploaded it will be
        invoked. Otherwise a default method will be used.
        """
        lec = getParent(self)
        #tut = getParent(lec)
        parent = lec.getQuiz()
        
        # The IDs of the questions the candidate could have selected
        # THIS MUST BE CHANGED .. not working!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        suggestedAnswerIds = self.getSuggestedAnswerIds(result)
        # The IDs of answers the candidate should have selected
        #correctAnswerIds   = self.getCorrectAnswerIds(result)
        correctAnswerIds = []
        grid = self.getWrappedField('AnswerList')
        rowcount = grid.search(self, correct='1')
        for row in rowcount:
            correctAnswerIds.append(row['answerid'])
        correctAnswerIds.sort()
        # The IDs of the answers the candidate did select
        givenAnswerIds     = result.getCandidateAnswer(self)
        
        #log("MC Question.getCorrectAnswerIds(): %s\n" % repr(retVal))
        ##customScript = parent.getEvaluationScript(self.portal_type)
        ##if customScript: # use custom script
        ##    return evalFunString(customScript, CUSTOM_EVALUATION_FUNCTION_NAME,
        ##                           [self, result, givenAnswerIds])
        ##else: # default

        

        
        if givenAnswerIds is None:
            givenAnswerIds = []
        givenAnswerIds.sort()
        # Give all the points if everything was
        # correct. Otherwise, give no points.
        return [0, self.getPoints()][givenAnswerIds == correctAnswerIds]
        
if PLONE_VERSION == 3:
    registerATCTLogged(InvisibleQuestion)
else:
    atapi.registerType(InvisibleQuestion, PROJECTNAME)
