from Products.Archetypes.public import *
from Products.Archetypes.public import OrderedBaseFolder
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.folder import ATFolderSchema
from AccessControl import ClassSecurityInfo
from Products.CMFCore import permissions as CMFCorePermissions
from OFS.Image import Image as BaseImage
from config import *
from permissions import *
from tools import *
from Products.Archetypes.public import Schema, BooleanField, BooleanWidget, \
     IntegerField,  FloatField, ReferenceField, IntegerWidget, StringField, TextField, \
     TextAreaWidget, StringWidget, SelectionWidget, RichWidget, ReferenceWidget
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget \
     import ReferenceBrowserWidget
from Products.Archetypes.utils import DisplayList

from Products.CMFCore.permissions import View

from ZPublisher.HTTPRequest import FileUpload
from htmlentitydefs import entitydefs
import re
import os
import shutil
import tempfile
from difflib import *
from Acquisition import aq_inner, aq_parent
try:
    from plone.i18n.normalizer.interfaces import IUserPreferredURLNormalizer
    from plone.i18n.normalizer.interfaces import IURLNormalizer
    URL_NORMALIZER = True
except ImportError:
    URL_NORMALIZER = False

from zope.component import adapter, getMultiAdapter, getUtility

from zope.app.container.interfaces import INameChooser

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from zope.app.container.interfaces import IContainerModifiedEvent, IObjectRemovedEvent
from zope.lifecycleevent.interfaces import IObjectCreatedEvent, IObjectCopiedEvent, IObjectModifiedEvent
from Products.Archetypes.interfaces import IObjectInitializedEvent, IObjectEditedEvent
from zope.app.container.interfaces import IObjectAddedEvent, IObjectMovedEvent
from Products.TutorWeb.portlets import sponsors
from OFS.interfaces import IObjectClonedEvent, IObjectWillBeRemovedEvent, IObjectWillBeMovedEvent
from Products.CMFPlone import PloneMessageFactory as _ 
from zope.interface import implements
from Products.TutorWeb.interfaces import IPrintable, ITutorial, ILecture, ISponsor, ISlide, \
IQuestion, IExtraDataFile, IDepartment, ICourse, IOrderedTutorWebContent

from string import *
if PLONE_VERSION == 4:
    from Products.Archetypes import atapi
    from config import PROJECTNAME       
## try: # New CMF  
##     from Products.CMFCore import permissions as CMFCorePermissions
##     from Products.CMFCore.permissions import AddPortalContent
   
## except: # Old CMF  
##     from Products.CMFCore import CMFCorePermissions
##     from Products.CMFCore.CMFCorePermissions import AddPortalContent
from Products.ATContentTypes.lib import constraintypes
    
class Tutorial(ATFolder):
    """Tutorial is a part of a single Department as well as a Course within that Department
    but can also be used in different Courses. 
    Tutorials are implemented as folders which can contain Lectures and extra literature 
    which are based on a distinctive topic. It can also contain distrinctive sponsors.
    It is implemented as an ATFolder and has interfaces ITutorial and IOrderedTutorWebContent."""
   
    # The languge of relevant material in the Tutorial
    # This needs to be more extensive
    # FIXME, FIXME
    LANGUAGE_FORMATS = DisplayList ((
    ('en', 'English'),
    ('is', 'Icelandic'),
    ))
    
    schema = ATFolderSchema.copy() + Schema((
        
        StringField('title',
                required=True,
                searchable=0,
                default='Tutorial',
                widget=StringWidget(
                    label='Title',
                    description='The main title of the tutorial.',
                    i18n_domain='plone'),
               
            ),
        StringField('ShortTitle',
                required=True,
                searchable=0,
                widget=StringWidget(
                    label='Short title',
                    description="Add a short title for the tutorial which will be used as part of identification.",
                    
            ),
        ),
        ReferenceField('DepartmentCourse',
                    required = 1,
                    vocabulary="getAvailableCourses",
                    widget=ReferenceWidget(
                           label="Department Course",
                           description='Course within the deparment which the tutorial belongs to.',
                           destination=".",
                           destination_types=("Course",),
                           
                           ),
                       multiValued=False,
                       relationship='inDepartmentCourse',
                       allowed_types= ("Course",),
                        
                   ),       
        StringField('NumberCode',
                required = 1,   
                widget=StringWidget(label='Numeric course code',
                                       description='Specify the numeric code for this tutorial. A tutorial can be identified based on the department and course it belongs to along with the numberic code. For example: STATS 101 1, where STATS corresponds to the department, 101 corresponds to the course and 1 identifies the tutorial.',),
                     ),
        
         ReferenceField('Courses',
                       widget=ReferenceWidget(
                           label="Courses",
                           description='Courses which the tutorial can belong to',
                           destination=".",
                           destination_types=("Course",),
                           macro='backward_reference',
                           visible={'edit':'invisible'},
                           ),
                       
                       multiValued=True,
                       relationship='inCourses',
                       allowed_types= ("Course",),
                        
                       ),       
        
        
        StringField('TutorialLanguage',
                #vocabulary=LANGUAGE_FORMATS,
                vocabulary='getLanguages',
                default='English',
                widget=SelectionWidget(label='Language',
                    description='Select the tutorial language. ',modes='edit'),
                ),
        
        StringField('Author',
                    required = 1,
                    widget=StringWidget(description='Author(s) of the tutorial')),
        IntegerField('Credits',
                 default='0',
                 widget=IntegerWidget(description='Number of Credits given for the tutorial',
                                 ),
                ),
        FloatField("historical_selection_probability", 
                   
                   required=False,
                   default='1.0',
                   widget=IntegerWidget(description='Probability of selecting questions in a quiz from previous lectures. At the moment only using either 1.0 or 0.0.'
 '1.0: All questions from previous lectures are selected randomly as well as from the current lecture.'
'0.0: Only select questions from the current lecture.',
        ),
       ),
        TextField('TutorialReference',
              searchable=0,
              default_content_type='text/plain',
              default_output_type='text/html',
              allowable_content_types=('text/latex','text/plain', 'text/structured', 'text/restructured',),    
              widget=RichWidget(label='Reference',
                                description='Reference for the Tutorial, a part of a pdf document which can be displayed for the tutorial.', modes='edit',
                                allow_file_upload=1,
             
                               ),
            
              ),
        TextField('PdfPreamble',
              searchable=0,
              default_content_type='text/plain',
              default_output_type='text/html',
              allowable_content_types=('text/plain',),
              widget=RichWidget(label='Pdf preamble',
                                description='Set the latex preamble used to generate a pdf document.', modes='edit',
                                allow_file_upload=1,
             
                               ),
            
              ),
               
        TextField('PdfPostamble',
              searchable=0,
              default_content_type='text/plain',
              default_output_type='text/html',
              allowable_content_types=('text/plain',),
              widget=RichWidget(description='Set the latex postable used to generate a pdf document.', modes='edit', allow_file_upload=1,
             
                               ),
             
              ),
       
        FileField('Pdf',
                    default='',
                    widget=FileWidget(description='pdf, generated from the available lectures',
                                      macro='paperpdf',  
                                      visible={'view':'invisible','edit':'invisible'},
                                        
                                        ),
        ),
         FileField('LatexFile',
                    default='',
                    widget=FileWidget(description='latex, generated from the available lectures',
                                      macro='paperlatex',  
                                      visible={'view':'invisible','edit':'invisible'},
                                        
                                        ),
        ),
        FileField('LatexLog',
                    default='',
                    widget=FileWidget(description='log latex, generated from the available lectures',
                                      macro='paperlog',  
                                      visible={'view':'invisible','edit':'invisible'},
                                        
                                        ),
        ),        
        FileField('QuestionFile',
                    searchable=0,
                    default='',
                    widget=FileWidget(description='pdf, generated from available questions.',
                                      macro='paperquestion',  
                                      visible={'view':'invisible','edit':'invisible'},
                                        
                                        ),
                  #read_permission=CMFCorePermissions.ModifyPortalContent, 

                  ),
        
        ComputedField('numLectures',
                  expression='context.computeNumLectures()',
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
    implements(IPrintable, ITutorial, IOrderedTutorWebContent)
    global_allow = False
    meta_type = 'Tutorial'          # zope type name
    portal_type = meta_type          # plone type name
    archetype_name = 'Tutorial' # friendly type name
    _at_rename_after_creation = True  #automatically create id
    security = ClassSecurityInfo()
    
    # ATT: Make sure this work when create from twmigrate.py
    changed = True
    questionchanged = True
    

    def __init__(self, oid=None, **kwargs):
        self.changed = True
        ATFolder.__init__(self, oid, **kwargs)
    def publishAll(self, typeofobject=None, originalobj=None):
        """publich tutorial as well as lecture content and sponsors.."""
        self.tryWorkflowAction("publish", ignoreErrors=True)
        lectures = self.getFolderContents(contentFilter={"portal_type": "Lecture"})
        for lec in lectures:
            obj = lec.getObject()
            obj.publishAll()
        sponsors = self.getFolderContents(contentFilter={"portal_type": "Sponsor"})
        for spo in sponsors:
            obj = spo.getObject()
            obj.publishAll()
        # called when object if copy/pasted or cloned
        # need to update references
        # not easy to do??? FIXME
    def getLanguage(self):
        portal_languages = getToolByName(self, 'portal_languages')
        langs = portal_languages.listSupportedLanguages()
        return langs
    def getLanguages(self):
        portal_languages = getToolByName(self, 'portal_languages')
        langs = portal_languages.listSupportedLanguages()
        return DisplayList(langs)
    def getLecture(self, lecid):
        """return lecture object with the specified lecid"""
        # what if lecid is not valid, maybe a problem
        # FIXME
        portal_catalog = getToolByName(self, 'portal_catalog')
        brains = portal_catalog.unrestrictedSearchResults({'portal_type' : 'Lecture', 'id' : lecid}, path='/'.join(self.getPhysicalPath()))
        if (len(brains) > 0):
            return brains[0].getObject()
        else:
            return False
    def haveAcknowledgements(self):
        """Returns true if there are any sponsors which belong to the tutorial"""
        portal_catalog = getToolByName(self, 'portal_catalog')
        query = {}
        query['Type'] = 'Sponsor'
        basepath = '/'.join(self.getPhysicalPath())
        pathlevel=1
        query['path'] = {'query' : basepath, 'depth' : pathlevel}
       
        brains = portal_catalog(query)
        if (len(brains) > 0):
            return True
        else:
            return False
    def haveAcknowledgementFolder(self):
        """Depricated, return true of tutorials contains a folder with id==acknowledgement"""
        portal_catalog = getToolByName(self, 'portal_catalog')
        brains = portal_catalog.unrestrictedSearchResults({'portal_type' : 'Folder', 'id' : 'acknowledgement'}, path='/'.join(self.getPhysicalPath()))
        if (len(brains) > 0):
            return True
        else:
            return False    
    def getAcknowledgementFolder(self):
        """Depricated, returns the folder object with id = acknowledgement"""
        portal_catalog = getToolByName(self, 'portal_catalog')
        brains = portal_catalog.unrestrictedSearchResults({'portal_type' : 'Folder', 'id' : 'acknowledgement'}, path='/'.join(self.getPhysicalPath()))
        if (len(brains) > 0):
            return brains[0].getObject()
        else:
            return False  
    def getAcknowledgements(self):
        """Returns the ids of all sponsors belonging to the tutorial"""
        portal_catalog = getToolByName(self, 'portal_catalog')
        query = {}
        query['Type'] = 'Sponsor'
        basepath = '/'.join(self.getPhysicalPath())
        pathlevel=1
        query['path'] = {'query' : basepath, 'depth' : pathlevel}
        brains = portal_catalog(query)
        return brains
    def getAcknowledgementsData(self):
        """Depricated, returns the ids of all files in a data folder belonging to tutorial"""
        portal_catalog = getToolByName(self, 'portal_catalog')
        brains = portal_catalog.unrestrictedSearchResults({'portal_type' : 'File'}, path='/'.join(self.getPhysicalPath())+'/data')
        return brains
    def getLiteratureFiles(self):
        """Return the file ids of all files belonging to the tutorial"""
        litfiles = self.getFolderContents(contentFilter={"portal_type": "File"})
        return litfiles
    
    def computeGrades(self, userId):
        """find grade for a user with the given userId, from all quiz results in every lecture
           belonging to the tutorial.
        """
        lecs = self.getFolderContents(contentFilter={"portal_type": "Lecture"})
        numlecs = len(lecs)
        portal_catalog = getToolByName(self, 'portal_catalog')
        brains = portal_catalog.unrestrictedSearchResults({'portal_type' : 'QuizResult', 'Creator': userId}, path='/'.join(self.getPhysicalPath()))
        points = 0.0
        for b in brains:
            points = points + b.studentgrade
            creat = b.Creator     
        if (numlecs > 0):
            return float(points/numlecs)
        else:
            return 0.0
    def updateSlideMaterial(self):
        """update slide text for every slide in every lecture which belongs to the tutorial."""
        lecs = self.getFolderContents(contentFilter={"portal_type": "Lecture"})
        for lec in lecs:
            obj = lec.getObject()
            tmp = obj.updateSlideMaterial()
    def isLoggedOn(self):
        """ return true is a user is logged on else false"""
        mtool = getToolByName(self, 'portal_membership')
        if mtool.isAnonymousUser():
            return False
        else:
            return True    
    def getFullName(self, userid):
        """return fullname of a user with the given userid"""
        # FIXME, what if id is not valid???
        if PLONE_VERSION == 3:
            ecq_tool = getToolByName(self, 'ecq_tool')
            return ecq_tool.getFullNameById(userid)
        else:
            parent = aq_parent(self)
            return parent.getFullName(userid)
    def getParticipants(self):
        """return all students which have participated in quizes belonging to this tutorial"""
        portal_catalog = getToolByName(self, 'portal_catalog')
        brains = portal_catalog.unrestrictedSearchResults({'portal_type' : 'QuizResult'}, path='/'.join(self.getPhysicalPath()))
        keys = {}
        if (len(brains) > 0):
            for b in brains:
                keys[b.Creator] = 1
            return keys.keys()
        else:
            return False
    def getCourseCode(self):
        """return the code of the primary course which the tutorial belongs to"""
        course = self.getDepartmentCourse()
        if (course):
            return course.getCode()
        else:
            return 'XXX'
    def getQuiz(self):
        """returns the quiz object of any lecture belonging to the tutorial"""
        portal_catalog = getToolByName(self, 'portal_catalog')
        availablelectures = portal_catalog.unrestrictedSearchResults({'portal_type' : 'Lecture'}, path='/'.join(self.getPhysicalPath()))
        if (len(availablelectures) > 0):
            obj = availablelectures[0].getObject()
            return obj.getQuiz()
        else:
            return False  
        
    def canSeeQuestions(self):
        """if current user has the role of a manager, editor, owner or belongs to the group: teacher
         then return True else False"""
        parent = aq_parent(self)
        return parent.canSeeQuestions()
    def getAvailableCourses(self):
        """return courses which belong to the department which the tutorial belongs to"""
        portal_catalog = getToolByName(self, 'portal_catalog')
        parent = aq_parent(self)
        availablecourses = portal_catalog.unrestrictedSearchResults({'portal_type' : 'Course'}, path='/'.join(parent.getPhysicalPath()))
        pair = []
        for c in availablecourses:
            pair.append((c.UID, c.Title))
           
        return DisplayList(pair)
    def renderNewPdf(self, type):
        """inidcate that printed material needs to be rerendered as changes have occured"""
        self.changed = True
    def editedObject(self, objtype=None):
        """indicate that the tutorial object has changed."""
        self.changed = True
        # must check if this is needed???
        self.questionchanged = True
        ##portal_catalog = getToolByName(self, 'portal_catalog')
        ##brains = portal_catalog.unrestrictedSearchResults({'portal_type' : 'QuizResult'}, path='/'.join(self.getPhysicalPath()))
        ##for b in brains:
        ##    res = b.getObject()
        ##    res.computeGrade1('0')
        ##    #res.setTotscore(666.0)
        ##    res.reindexObject()
        lectures = self.getFolderContents(contentFilter={"portal_type": "Lecture"})
        for lec in lectures:
            obj = lec.getObject()
            obj.changed = True
            obj.reindexObject()
    def setChanged(self, ch):
        self.changed = ch
    def setQuestionChanged(self, ch):
        self.questionchanged = ch
    def normidgeneration(self, title):
        # Can't work w/o a title
        if not title:
            return None
        # Don't do anything without the plone.i18n package
        if not URL_NORMALIZER:
            return None
        

        if not isinstance(title, unicode):
            charset = self.getCharset()
            title = unicode(title, charset)

        request = getattr(self, 'REQUEST', None)
        if request is not None:
            return IUserPreferredURLNormalizer(request).normalize(title)

        return queryUtility(IURLNormalizer).normalize(title) 
    def getQuestionSelectionParameters(self):
        portal_catalog = getToolByName(self, 'portal_catalog')
        brains = portal_catalog.unrestrictedSearchResults({'portal_type' : 'BaseQuestionSelectionParameters'}, path='/'.join(self.getPhysicalPath()))
        if len(brains) > 0:
            return brains[0].getObject()
        else:
            return False    
    def generateNewId(self):
        """Suggest an id for this tutorial based on the department and course codes and the short title of the tutorial.
        This id is used when automatically renaming an object after creation.
        """
        parent = aq_parent(self)
        title = (parent.getCode()+self.getCourseCode()+self.getNumberCode()+self.getShortTitle()).strip()
        # Can't work w/o a title
        if not title:
            return None

        # Don't do anything without the plone.i18n package
        if not URL_NORMALIZER:
            return None
        # Don't do anything without the plone.i18n package
        if not URL_NORMALIZER:
            return None

        if not isinstance(title, unicode):
            charset = self.getCharset()
            title = unicode(title, charset)

        request = getattr(self, 'REQUEST', None)
        if request is not None:
            return IUserPreferredURLNormalizer(request).normalize(title)

        return queryUtility(IURLNormalizer).normalize(title)

    security.declareProtected(View, 'computeNumLectures')
    def computeNumLectures(self):
        """Find number of lectures which belong to this tutorial"""
        lectures = self.getFolderContents(contentFilter={"portal_type":"Lecture"})
        return (len(lectures))
    security.declareProtected(View, 'computeNumQuestions')
    def computeNumQuestions(self):
        """Find number of questions which belong to this tutorial"""
        lectures = self.getFolderContents(contentFilter={"portal_type":"Lecture"})
        numquestions = 0
        for l in lectures:
            obj = l.getObject()
            nq = obj.computeNumQuestions()
            numquestions = numquestions + nq
        return numquestions
        
    security.declareProtected(View, 'computeNumRQuestions')
    def computeNumRQuestions(self):
        """Find number of r questions which belong to this tutorial"""
        lectures = self.getFolderContents(contentFilter={"portal_type":"Lecture"})
        numrquestions = 0
        for l in lectures:
            obj = l.getObject()
            rq = obj.computeNumRQuestions()
            numrquestions = numrquestions + rq
        return numrquestions
    
    security.declareProtected(View, 'removeVerbatim')
    def removeVerbatim(self, text):
        """replace verbatim with texttt, in latex formatted text
        """
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
            start = text.find(beginstr, end+len(endstr), len(text))
        text2 = text.replace('\\begin{verbatim}', '{\\texttt')
        text3 = text2.replace('\\end{verbatim}', '}')
        return text3
   
    def createObjectXX(self, typeName):
        """Create a new object=typeName and initialize it."""
        objid = self.generateUniqueId(typeName)
        if self.portal_factory.getFactoryTypes().has_key(typeName):
            o = self.restrictedTraverse('portal_factory/' + typeName + '/' + objid)
           
            newId = objid
        else:
            newId = self.invokeFactory(id=objid, type_name=typeName)
            
            if newId is None or newId == '':
                newId = objid
            o=getattr(self, newId, None)
    
        if o is None:
            raise Exception
        o = self.portal_factory.doCreate(o, newId)
        return o
    security.declarePrivate('initializeObject')
    def initializeObject(self):
        """called after object is first created
        publish object and reorder content of department
        """
        self.tryWorkflowAction("publish", ignoreErrors=True)    
        parent = aq_parent(self)
        try:
            parent.orderObjects("id")
            parent.plone_utils.reindexOnReorder(parent)
        except:
            raise 'Failed to create tutorial ' + self.getTitle() + ' not able to reorder tutorials'
        # just to have something in pdf doc.
        self.setTitle_pdf()
        # create an object to hold paramerts used when questions are
        # selected in quiz
        obj = self.createObjectXX('BaseQuestionSelectionParameters')
        obj.setTitle('QuestionSelectionParameters')
        # Enable contstraining so not all types are visible in the add menu
        self.setConstrainTypesMode(constraintypes.ENABLED)  
        allowedTypes = self.getLocallyAllowedTypes()
        mytypes = []
        # types not used in add menu
        # remove, leave in for the moment
        ##ranges = ('BaseQuestionSelectionParameters')
        ##for t in allowedTypes:
        ##    if t not in ranges:
        ##        mytypes.append(t)

        ## # Tweak the menu
        ##self.setLocallyAllowedTypes(mytypes)
        ##self.setImmediatelyAddableTypes(mytypes)
        obj.tryWorkflowAction("publish", ignoreErrors=True)
        obj.reindexObject()
   
    def lecturehaschanged(self):
        """indicate that tutorial has changed"""
        self.changed = True
    def haveChanged(self):
        """indicate that tutorial and all its lectures have changed"""
        self.changed = True
        lectures = self.getFolderContents(contentFilter={"portal_type": "Lecture"})
        for i in lectures:
            obj = i.getObject()
            obj.setChanged(True)
         
    security.declarePrivate('tryWorkflowAction')
    def tryWorkflowAction(self, action, ignoreErrors=False, comment=None):
        """changed action of tutorial"""
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
    def getError(self):
        self.portal_factory.doCr()
    security.declareProtected(View, 'getTutorial_pdf')
    def getQuestion_pdf(self):
        '''only render a new latex file if questions have changes'''
        if (self.questionchanged == True):
            self.setQuestions_pdf()
        
        return 'nothing'    
    security.declareProtected(View, 'getTutorial_pdf')
    def getTutorial_pdf(self):
        # REMEMBER TAKE OUT FOR TESTING - ERROR
        if (self.changed == True):
            self.setTutorial_pdf()
        
        return 'nothing'
    
    security.declareProtected(View, 'render_pdf')
    def render_pdf(self, tmpout, tex_absname, dviname, psname, pdfname):
        """run latex, dvips, ps2pdf to render a pdf file"""
        
        try:
            # run latex twice
            status = os.system('echo Q | latex -interaction=nonstopmode -output-directory=' + tmpout + ' ' + tex_absname)
            status = os.system('echo Q | latex -interaction=nonstopmode -output-directory=' + tmpout + ' ' + tex_absname)
            tex_logfile =tex_absname[:-3]+'log'
            logfile = open(tex_logfile, 'r')
            logfilestring = logfile.read()
            self.setLatexLog(logfilestring)
            logfile.close()

        except:
            '''failed to run latex'''
            #self.setPdf('Failed to execute latex while rendering pdf file.')
            #self.cleanDir(tmpout)
            return 'failed to run latex'
        try:
            os.system('dvips -f ' + dviname + ' > '+ psname)
        except:
            '''failed to run dvips'''
            #self.setPdf('Failed to execute dvips while rendering pdf file.')
            #self.cleanDir(tmpout)
            return 'failed to run dvips'
        try:
            os.system('ps2pdf '+ psname + ' ' + pdfname)
        except:
            '''failed to run ps2pdf'''
            #self.setPdf('Failed to execute ps2pdf while rendering pdf file.')
            #self.cleanDir(tmpout)
            return 'failed to run ps2pdf'
        try:
            #os.chmod(pdfname, 0755) 
            pdffile = file(pdfname).read()
            return pdffile
        except:
            #self.setPdf('Failed to read data from file while rendering pdf file.')
            #self.setPdf('could read pdfile')
            #self.cleanDir(tmpout)
            return 'Failed to read data from file while rendering pdf file.'
   #     try:    
            #self.setPdf(pdffile)
            # then I must clean up temp dir...
   #         return pdffile
            #self.setPdf('should have set pdffile')
   #     except:
            #self.setPdf('could not set pdf file')
            #self.cleanDir(tmpout)
   #         return 'could not set pdf file' 
    security.declareProtected(View, 'setTitle_pdf')
    def setTitle_pdf(self):
        """Set an initial title page for the lecture pdf of the tutorial"""
        #pdf version of all lectures belonging to tutorial
        # start by generating the tmp files
        try:
            tmpout = tempfile.mkdtemp()     
        except:
            self.setPdf('Rendering pdf file failed - not able to create temporary directory.')
            self.setLatexFile('% System failed to create temporary directory /tmp/tmp* for latex files.')
            self.setLatexLog('% System failed to create temporary directory /tmp/tmp* for latex files.')
            return
        # temp directory created
        try:
            tex_fd, tex_absname = tempfile.mkstemp(dir=tmpout, suffix='.tex')
            tex_logfile = tex_absname[:-3]+'log'
            pdfdir = tex_absname[:-4]+'/'
            textfilename=tmpout+'/mytextfile.txt'
            dviname = tex_absname[:-3] + 'dvi'
            psname = tex_absname[:-3] + 'ps'
            pdfname = tex_absname[:-3]+'pdf'
        except:
            self.setPdf('Rendering pdf file failed - not able to create temporary file.')
            self.setLatexFile('% System failed to create temporary latex file')
            self.setLatexLog('% System failed to create temporary directory /tmp/tmp* for latex files.')
            self.cleanDir(tmpout)
        
            return
        # created temporary file in /tmp, start by setting preamble
        try:
            self.setPreamble(tex_fd)
        except:
            self.setPdf('Not able to write to latex preamble to temp file while rendering pdf-file.')
            texfilestring = file(tex_absname).read()
            self.setLatexFile(texfilestring)
            os.close(tex_fd)
            
            #logfile = open(tex_logfile, 'r')
            
            #logfilestring = logfile.read()
            #self.setLatexLog(logfilestring)
            #logfile.close()
            self.cleanDir(tmpout)
            return
        # set the first page of the pdf document
        try:
            self.setTitlePage(tex_fd, tmpout)
            os.write(tex_fd, '\\newpage' + '\n')
            os.write(tex_fd, '\\tableofcontents' + '\n')
            os.write(tex_fd, '\\newpage' + '\n')
            os.write(tex_fd, '\n')
        except:
            self.setPdf('Not able to render title page for pdf-file.')
            texfilestring = file(tex_absname).read()
            self.setLatexFile(texfilestring)
            os.close(tex_fd)
            
            #logfile = open(tex_logfile, 'r')
            #logfilestring = logfile.read()
            #self.setLatexLog(logfilestring)
            #logfile.close()
            self.cleanDir(tmpout)
            return
        os.write(tex_fd, '\\end{document}'+'\n')
        #set latex output
        texfilestring = file(tex_absname).read()
        self.setLatexFile(texfilestring)
        #logfile = open(tex_logfile, 'r')
        #logfilestring = logfile.read()
        #self.setLatexLog(logfilestring)
        #logfile.close()
        #convert to pdf
        pdftext = self.render_pdf(tmpout, tex_absname, dviname, psname, pdfname)
        self.setPdf(pdftext)
        os.close(tex_fd)    
        self.cleanDir(tmpout)
        self.changed = True
   
    security.declareProtected(View, 'setPDFImage')    
    def setPDFImage(self, j, tex_fd, tex_absname, tmpout, category, lectitle, slidetitle, figwidth):
        '''set image in slide j, depending on category in tex_fd'''
       
        if (category == 'MAIN'):
            maincaption = j.getSlideImageCaption()
            image_type = j.getSlideImageFormat()
            text = j.getSlideImageText()
            
        elif (category == "EXPLANATION"):
            maincaption = j.getExplanationImageCaption()
            image_type = j.getExplanationImageFormat()
            text = j.getExplanationImageText()
        if (image_type == 'fig'):
            main_image = j.renderImage(text, 'fig2dev -L eps', '')
        elif (image_type == 'r'):
            HEADER = 'postscript(file="/dev/stdout")\r\n'
            main_image = j.renderImage(text, 'R --slave', HEADER)
        elif (image_type == 'gnuplot'):
            HEADER = 'set terminal epslatex color\n'
            main_image = j.renderImage(text, 'gnuplot', HEADER)    
        else:
            if (category == 'MAIN'):
                main_image = j.getSlideImage()
            elif (category == 'EXPLANATION'):
                main_image = j.getExplanationImage()
         
            
        haveMainImage = (main_image != 'FAILURE' and main_image)
        
        if (haveMainImage):
            
            try:
                image_fd, image_absname = tempfile.mkstemp(dir=tmpout, suffix='.png')
                imageeps = image_absname[:-3]+'eps'
                t_fd, t_absname = tempfile.mkstemp(dir=tmpout, suffix='.eps')
               
            except:
                '''Can't make main image temp file'''
               
                self.setPdf('While rendering pdf, could not create temporary image file /tmp/tmp.png or /tmp/tmp.eps')
                #set latex output
                texfilestring = file(tex_absname).read()
                self.setLatexFile(texfilestring)
                os.close(tex_fd)
                           
                self.cleanDir(tmpout)
                return 'ERROR'
                            
            try:
                           
                if (image_type == 'image'):
                    os.write(image_fd, str(main_image.data))
            except:
                            #os.write(image_fd, 'no image data')
                            #set latex output
                texfilestring = file(tex_absname).read()
                self.setLatexFile(texfilestring)
                           
                self.setPdf('Not able to set image in pdf-file, in lecture: '+lectitle + ' and slide: '+slidetitle)
                os.close(t_fd)
                os.close(image_fd)
                os.close(tex_fd)
                self.cleanDir(tmpout)
                return 'ERROR'
            #try:
            #    os.system('imgtops --landscape ' + image_absname + ' > ' + psfilename)
            # This is done diff when look ad paper.txt in tutorial STATS!!!!!
            #    psimage = file(psfilename).read()
            #    if (len(psimage) > 0):
                                #os.write(tex_fd, '\\begin{minipage}[t]{0.25\\textwidth}'+'\n')
                        
            try:
                           
                if (image_type == 'fig'):
                    #os.system('fig2dev -L eps ' + image_absname + ' ' + imageeps)
                    os.write(t_fd, main_image)
                elif (image_type == 'r'):
                               
                    os.write(t_fd, main_image)
                elif (image_type == 'gnuplot'):
                               
                    os.write(t_fd, main_image)
                    #os.write(imageeps, main_image)
                else:
                   
                    os.system('convert -resize x500 ' + image_absname + ' ' + imageeps)
            except:
                '''what to do'''
                           
                texfilestring = file(tex_absname).read()
                self.setLatexFile(texfilestring)
                           
                self.setPdf('Not able to render image of type ' + image_type + ' in pdf-file. In lecture: ' + lecturetile + ' and slide: ' + slidetitle)
                os.close(t_fd)
                os.close(image_fd)
                os.close(tex_fd)
                self.cleanDir(tmpout)
                return 'ERROR'
            boxwidth = '0.25'
            os.write(tex_fd, '\\begin{figure}[h]\n')
            #os.write(tex_fd, '\\begin{figure}\n')
            os.write(tex_fd, '\\begin{tabular}{ll}' + '\n')
            os.write(tex_fd, '\\begin{minipage}{'+figwidth+'\\textwidth}'+ '\n')
                        
            #os.write(tex_fd, '\\resizebox{0.9\\textwidth}{!}{'+'\n')
            #os.write(tex_fd, '\\scalebox{10}{10} {' + '\n')
            os.write(tex_fd, '\\resizebox{7cm}{!}{'+'\n')
            if (image_type == 'r'):
                os.write(tex_fd, '\\rotatebox{-90}{'+'\n')
            if (category == 'MAIN'):
                os.write(tex_fd, '\\centering' + '\n')
            if (image_type == 'r' or image_type == 'gnuplot' or image_type == 'fig'):
                os.write(tex_fd, '\\includegraphics{'+t_absname+'}'+'\n')
            else:
                os.write(tex_fd, '\\includegraphics{'+imageeps+'}'+'\n')
                        
            os.write(tex_fd, '}'+'\n')
                #os.write(tex_fd, '}'+'\n'+'}'+'\n')
            if (image_type == 'r'):
                os.write(tex_fd, '}'+'\n')
            if (len(maincaption) > 0):
                #os.write(tex_fd, ' \n')
                os.write(tex_fd, '\\caption{'+maincaption+'}\n')
                #os.write(tex_fd, ' \n')
                       
            os.write(tex_fd, '\\end{minipage}'+'\n')
                       
                        
            # close file descriptors - finished writing image
            os.close(image_fd)
            os.close(t_fd)
            return 'IMAGE'
        else:
            return 'NOIMAGE'
    #### Problem, if course and department codes changed this will not be reflected in the pdf unless
    #### other printable parts of the tutorials are changed!!!!!!
    #### FIXME
    security.declareProtected(View, 'setTutorial_pdf')
    def setTutorial_pdf(self):
        """generate lecture pdf for the tutorial"""
        #pdf version of all lectures belonging to tutorial
        # start by generating the tmp files
        try:
            tmpout = tempfile.mkdtemp()     
        except:
            #raise TypeError('Unsupported workflow actionfor object .')
        #                   % (repr(action), repr(DepObj)))
            #print "tutorial pdf:(shutil.rmtree %s) OSError[%s]: %s" % \
            #                  (tmpout, errno, strerror)
            self.setLatexFile('% System failed to create temporary directory /tmp/tmp* for latex files.')
            self.setLatexLog('% System failed to create temporary directory /tmp/tmp* for latex files. ')
            self.setPdf('Rendering pdf file failed - not able to create temporary directory.')
            #self.setPdf('error occured')
            #raise 'error again in pdf'
            #raise TypeError('error in pdf')
            return
        # temp directory created
        try:
            tex_fd, tex_absname = tempfile.mkstemp(dir=tmpout, suffix='.tex')
            pdfdir = tex_absname[:-4]+'/'
            textfilename=tmpout+'/mytextfile.txt'
            tex_logfile = tex_absname[:-3]+'log'
            dviname = tex_absname[:-3] + 'dvi'
            psname = tex_absname[:-3] + 'ps'
            pdfname = tex_absname[:-3]+'pdf'
            # set preample
        except:
            self.setLatexFile('% System failed to create temporary file /tmp/tmp*.')
            self.setLatexLog('% System failed to create temporary file /tmp/tmp*.')
            self.setPdf('Rendering pdf file failed - not able to create temporary file.')
            self.cleanDir(tmpout)
            return
        try:
            self.setPreamble(tex_fd)
        except:
            self.setPdf('Not able to write preamble to temp latex file.')
            #set latex output
            texfilestring = file(tex_absname).read()
            self.setLatexFile(texfilestring)
            os.close(tex_fd)
            
            #logfile = open(tex_logfile, 'r')
            #logfilestring = logfile.read()
            #self.setLatexLog(logfilestring)
            #logfile.close()
            self.cleanDir(tmpout)
            return
        try:
            self.setTitlePage(tex_fd, tmpout)
            os.write(tex_fd, '\\newpage' + '\n')
            os.write(tex_fd, '\\tableofcontents' + '\n')
            os.write(tex_fd, '\\newpage' + '\n')
            os.write(tex_fd, '\n')
        except:
            #set latex output
            texfilestring = file(tex_absname).read()
            self.setLatexFile(texfilestring)
            #logfile = open(tex_logfile, 'r')
            #logfilestring = logfile.read()
            #self.setLatexLog(logfilestring)
            #logfile.close()
            self.setPdf('Not able to render title page for pdf-file.')
            os.close(tex_fd)
            self.cleanDir(tmpout)
            return
        try:
            #go through all lectures
            templec = 0
            tempslide = 0
            #this is very bad if no lectures and/or slides

            #FIX
            lectures = self.getFolderContents(contentFilter={"portal_type": "Lecture"})
            #tmp = lectures.sort(lambda x,y:cmp(x.id, y.id))
            #for i in  self.listFolderContents(contentFilter={"portal_type": "Lecture"}):
            for i in lectures:
                i = i.getObject()
                templec = i
                lectitle= i.Title()

                os.write(tex_fd, '\section{' + '\n')
                os.write(tex_fd, lectitle + '\n')
                os.write(tex_fd, '}' + '\n')
                # Set the Contents page
                slides = i.getFolderContents(contentFilter={"portal_type": "Slide"})
                #tmp = slides.sort(lambda x,y:cmp(x.id, y.id))
                #for j in i.listFolderContents(contentFilter={"portal_type": "Slide"}):
                for j in slides:
                    j = j.getObject()
                    # Header stuff for the slide - this is a new subsection
                    tempslide = j
                    slidetitle = j.Title()
                    
                    os.write(tex_fd, '\\subsection{' + '\n')
                    os.write(tex_fd, slidetitle + '\n')
                    os.write(tex_fd, '}' + '\n')

                    #set the main image
                    maintext = j.getRawSlideText()
                    main_text_type = j.SlideText.getContentType()
                    if (len(maintext) > 0):
                        figwidth = '0.75'
                    else:
                        figwidth = '1.0'
                    boxwidth = '0.5'
                        # or is it '1'
                    
                    category = 'MAIN'
                    haveMainImage = self.setPDFImage(j, tex_fd, tex_absname, tmpout, category, lectitle, slidetitle, figwidth)
                   
                    if haveMainImage == 'ERROR':
                        return
                    # end of main image
                    # as it is now, the image goes into the contents part !!!!!!!!!!!!!!!
                   
                    #maintext = self.removeVerbatim(maintext)
                    if (len(maintext) > 0):
                        os.write(tex_fd, '\\begin{minipage}{'+boxwidth+'\\textwidth}' + '\n')
                        os.write(tex_fd, '{\\tiny' + '\n')
                        os.write(tex_fd, '\\fbox{' + '\n')
                        os.write(tex_fd, '\\parbox[c]{3truecm}{' + '\n')
                        try:
                            i.setPrintTextWithoutVerbatim(tex_fd, tmpout, textfilename, main_text_type, maintext)
                        except:
                            os.write(tex_fd, 'could not set main text' + '\n')
                        os.write(tex_fd, '\n')    
                        os.write(tex_fd, '}}}' + '\n')
                        os.write(tex_fd, '\\end{minipage}' + '\n')
                    #os.write(tex_fd, '\\end{tabular}' + '\n')
                    if (haveMainImage == 'IMAGE'):
                        os.write(tex_fd, '\\end{tabular}' + '\n')
                        os.write(tex_fd, '\\end{figure}\n')
                    #os.write(tex_fd, '\\end{longtable}\n')
                    #os.write(tex_fd, '\\begin{longtable}{p{0.75\\textwidth} p{0.25\\textwidth}}\n')
                    #os.write(tex_fd, '\\begin{tabular}{ll}' + '\n')
                    #os.write(tex_fd, '\\begin{minipage}{0.75\\textwidth}' + '\n')
                    #os.write(tex_fd, '\\vspace{10mm}\n')
                    #os.write(tex_fd, '\\\\\n')
                    detail_text_type = j.Details.getContentType()
                    detailtext = j.getRawDetails()
                    example_text_type = j.Examples.getContentType()
                    exampletext = j.getRawExamples()

                    #add details if any
                    setdetail = 0
                    setexampl = 0
                    if (len(detailtext) > 0 and (detailtext != 'No details exist for this slide\n')):
                        setdetail = 1
                        try:
                            os.write(tex_fd, '\n\n')
                            i.setPrintText(tex_fd, tmpout, textfilename, detail_text_type, detailtext)
                        except:
                            os.write(tex_fd, 'could not set details text' + '\n')
                    #add example if any
                    #os.write(tex_fd, '\\\\\n')
                    if (len(exampletext) > 0 and (not(exampletext == 'No examples exist for this slide\n'))):
                        setexampl = 1
                        try:
                            #if (setdetail == 1):
                            #    os.write(tex_fd, '\\\\\n\\pagebreak[2]\n')
                            os.write(tex_fd, '\n\n')
                            i.setPrintText(tex_fd, tmpout, textfilename, example_text_type, exampletext)
                        except:
                            os.write(tex_fd, 'could not set example text' + '\n')
                    # EXPLANATION_FIG, set in config.py
                    if (EXPLANATION_FIG):
                        haveExplImage = self.setPDFImage(j, tex_fd, tex_absname, tmpout, 'EXPLANATION', lectitle, slidetitle, '1.0')
                        if (haveExplImage == 'ERROR'):
                            return
                        if (haveExplImage == 'IMAGE'):
                            os.write(tex_fd, '\\end{tabular}' + '\n')
                            os.write(tex_fd, '\\end{figure}\n')
                         
                    #add slide reference if any
                        
                    reference_text_type = j.SlideReference.getContentType()
                    referencetext = j.getRawSlideReference()
                    if (len(referencetext) > 0):
                        os.write(tex_fd, '\n\n')
                        os.write(tex_fd, '{\\bf References}'+ '\n')
                        #;echo ""
                        try:
                            i.setPrintText(tex_fd, tmpout, textfilename, reference_text_type, referencetext)
                        except:
                            os.write(tex_fd, 'could not set reference text' + '\n')
                    handout_text_type = j.Handout.getContentType()
                    handouttext = j.getRawHandout()
                    handouttext.strip()
                    #handouttext = handouttext[:32]
                    nohandout = 'No homework exist for this slide'
                 ##              No homework exist for this slide
                    if (handouttext[:32] == nohandout):
                        handouttext = handouttext[:32]
                   ##  else:
##                         d = Differ()
##                         result = list(d.compare(handouttext, nohandout))
##                         handouttext = 'start: ' + str(len(result)) + ' and ' + str(result[0]) + 'len of nohandout is: ' + str(len(nohandout)) + ' and len ad handout is: ' + str(len(handouttext)) + 'last in res is: ' + str(result[32])
##                         #for i in result:
##                         #    handouttext = handouttext + i
                        
                    if (len(handouttext) > 0 and (not(handouttext == nohandout))):
                        #;echo ""
                        try:
                            os.write(tex_fd, '\n\n')
                            i.setPrintText(tex_fd, tmpout, textfilename, handout_text_type, handouttext)
                        except:
                            os.write(tex_fd, 'could not set handout text' + '\n')

                    # Alternatives are skipped ??????????????
                   ## notincluded = 'No alternative slides exist for this slide'

                    # add a few blank lines at end of subsection

                    #os.write(tex_fd, '\\vspace{16pt}'+'\n')
                # add lecture references if any
                reference_text_type = i.LectureReference.getContentType()
                referencetext = i.getRawLectureReference()
                os.write(tex_fd, '\n\n')
                if (len(referencetext) > 0):
                    os.write(tex_fd, '{\\bf References}'+ '\n')
                    #;echo ""
                    if (tempslide != 0):
                        try:
                            i.setPrintText(tex_fd, tmpout, textfilename, reference_text_type, referencetext)
                        except:
                            os.write(tex_fd, 'could not set lec ref text' + '\n')
                    # Add a blank page at the end of all sections.
                    os.write(tex_fd, '\\newpage' + '\n')
            if (templec != 0):
                # add a tutorial reference if any
                reference_text_type = self.TutorialReference.getContentType()
                referencetext = self.getRawTutorialReference()
                if (len(referencetext) > 0):
                    os.write(tex_fd, '\\section{References}' + '\n')
                    #;echo ""
                    try:
                        templec.setPrintText(tex_fd, tmpout, textfilename, reference_text_type, referencetext)
                    except:
                        os.write(tex_fd, 'could not set tutorial ref text' + '\n')
                # add trailer for tutorial if any
                #trailer_text_type = i.Trailer.getContentType()
                #trailertext = i.getRawTrailer()
                #if (len(trailertext) > 0):
                    #;echo ""
                #    try:
                #        templec.setPrintText(tex_fd, tmpout, textfilename, trailer_text_type, trailertext)
                #    except:
                #        os.write(tex_fd, 'could not set trailer text' + '\n')
            #no more lectures to add, finish latex document
            postamble = self.getRawPdfPostamble()
            if (len(postamble) > 0):
                ''' do something'''
                # do I need to replace \ with \\ and add \n???
                os.write(tex_fd, postamble)
            else:
                os.write(tex_fd, '\\end{document}'+'\n')
            # set latex output
            texfilestring = file(tex_absname).read()
            self.setLatexFile(texfilestring)
            #logfile = open(tex_logfile, 'r')
            #logfilestring = logfile.read()
            ##self.setLatexLog(logfilestring)
            #logfile.close()
            #convert to pdf
            pdftext = self.render_pdf(tmpout, tex_absname, dviname, psname, pdfname)
            self.setPdf(pdftext)
            self.reindexObject()
               
        except:
            # hmm - failed while looping through lectures
            texfilestring = file(tex_absname).read()
            self.setLatexFile(texfilestring)
            #logfile = open(tex_logfile, 'r')
            #logfilestring = logfile.read()
            #self.setLatexLog(logfilestring)
            #logfile.close()
#self.setLatexFile('% System not able to create temporary directory or files /tmp in order to render pdf files')
            self.setPdf('Rendering pdf-file failed')
         
                            
        os.close(tex_fd)    
        self.cleanDir(tmpout)
        self.changed = False
    security.declareProtected(View, 'cleanDir')
    def cleanDir(self, tmpout):
        """remove temporary directory and subdirectores created by using tempfile"""
        
        try:
            shutil.rmtree(tmpout, True)
        
        except OSError, (errno, strerror):
                    print "tutorial pdf:(shutil.rmtree %s) OSError[%s]: %s" % \
                                       (tmpout, errno, strerror)
    security.declareProtected(View, 'setTitlePage')
    def setTitlePage(self, tex_fd, tempdir):
        """generate the title page of a lecture pdf"""
        
        catalog = getToolByName(self, 'portal_catalog')
        query = dict(object_provides = IPrintable.__identifier__)
        query1 = dict(object_provides = ITutorial.__identifier__)
        results = catalog(query)
        results1 = catalog(query1)
        #os.write(txt_fd, 'num in printable result is ' + str(len(results)) + '\n')
        #os.write(txt_fd, 'num in tutorial result is ' + str(len(results1)) + '\n')
        for res in results1:
            resobj = res.getObject()
            mytype = resobj.Type()
            #os.write(txt_fd, 'got type ' + str(mytype) + '\n')
        titlefile=self.Title()
        authorfile = self.getAuthor()
        if (len(authorfile) == 0):
            authorfile = 'No author set yet'
        parent = aq_parent(self)
        dept = parent.getCode()+self.getCourseCode()+'.'+self.getNumberCode()
        #dept = self.getTutorialCode()
        if (len(dept) == 0):
            dept = 'No department code set yet'
        #strtitle = '\\title{'+dept+'\n'+titlefile+'}'+'\n'
        #strsubtitle='\\subtitle{('+dept + ' ' + subtitlefile+')}'+'\n'
        strauthor='\\author{{'+authorfile+'}}'+'\n'
        copyr = 'This work is licensed under the Creative Commons Attribution-ShareAlike License. To view a copy of this license, visit http://creativecommons.org/licenses/by-sa/1.0/ or send a letter to Creative Commons, 559 Nathan Abbott Way, Stanford, California 94305, USA.' + '\n'
        #stracknowl = 'no logo found as yet, needs to be set' + '\n' 
        os.write(tex_fd, '\\title{'+'\n')
        os.write(tex_fd, dept + '\n')
        os.write(tex_fd, titlefile + '\n')
        os.write(tex_fd, '}' + '\n')
        os.write(tex_fd, strauthor)
        os.write(tex_fd, '\\maketitle' + '\n')
        os.write(tex_fd, '{\\small{\\bf Copyright}' + '\n')
        os.write(tex_fd, copyr + '\n')
        os.write(tex_fd, '}'+'\n')
        # now check for acknowledgetment info
        brains = self.getAcknowledgements()
        numinbrains = str(len(brains))
        #os.write(txt_fd, 'num in brains ' + numinbrains + '\n')
        mypath = '/'.join(self.getPhysicalPath()) + '/acknowledgement'
        #os.write(txt_fd, 'my path is ' + mypath + '\n')
        if (len(brains) > 0):
           
            os.write(tex_fd, '{\\bf ACKNOWLEDGEMENTS}' + '\n')
            os.write(tex_fd, ' \n')
            os.write(tex_fd, '\\vspace{12pt}' + '\n')
            
            for b in brains:
                
                sponsor = b.getObject()
                graphicdata = ''
                urldata = ''
                textdata = ''
                 
                expimage_fd, expimage_absname = tempfile.mkstemp(dir=tempdir, suffix='.png')
                psimage_fd, psimage_absname = tempfile.mkstemp(dir=tempdir, suffix='.ps')
                expimageeps = expimage_absname[:-3]+'eps'
                expt_fd, expt_absname = tempfile.mkstemp(dir=tempdir, suffix='.eps')
               
                os.write(tex_fd, ' \n')
                os.write(tex_fd, '\\begin{tabular}{p{6cm}l}' + '\n')
                #for j in files: 
                   
                #if (('.png' in j) or ('.jpeg' in j) or ('.gif' in j)):
                    ##    # add graphic
                graphicdata = sponsor.getSponsorlogo()
                
                        
                if (len(graphicdata) > 0):
                    
                    os.write(expimage_fd, str(graphicdata.data))   
                    os.system('convert ' + expimage_absname + ' ' + expimageeps)
                    
                else:
                    '''nothing'''
                   
                urldata = sponsor.getSponsorurl()
                
                textdata = sponsor.getRawSponsortext()
               
           ##     # now should write into to pdf file
                
                if (len(textdata) > 0):
                    text = textdata.encode('utf-8')
                    os.write(tex_fd, textdata + '\n')
                    
                else:
                    ll = str(len(textdata))
                   
                if (len(urldata) > 0):
                    text = urldata.encode('utf-8')
                    os.write(tex_fd, urldata + '\n')
                else:
                    ll = str(len(urldata))
                   
                if (len(graphicdata) > 0):
                    os.write(tex_fd, '& ')
                    os.write(tex_fd, '\\resizebox{3cm}{!}{' + '\n')
                    os.write(tex_fd, '\\includegraphics{'+expimageeps+'}'+'\n')
                    os.write(tex_fd, '}' + '\n')
                   
                else:
                    ll = str(len(graphicdata))
                    os.write(tex_fd, '& ' + '\n')
                os.write(tex_fd, ' \n')
                os.write(tex_fd,'\\end{tabular}' + '\n')
                os.close(expimage_fd)
                os.close(psimage_fd)
                os.close(expt_fd) 
        
        # maybe needs small and } as in copyright???
    security.declareProtected(View, 'setPreamble')
    def setPreamble(self, tex_fd):
        """generate the preambe for the pdf latex file"""
        #NOTE: This needs to be appropriate both for generating pdf and ps
        #pdflatex does not currently work when including ps-files!
       
        # Can either use the mathptm package above or run dvips with
        # dvips -Pcmz -Pamz -f < file.dvi > file.ps
        # -- in order to produce decent pdf file subsequently with
        # ps2pdf file.ps
        preamble = self.getRawPdfPreamble()
        if (len(preamble) > 0):
            # do I need new lines
            #preamble = preamble.replace('\\', '\\\\')
            #os.write(tex_fd, preamble)
            os.write(tex_fd, '\\newcommand{\\captionfonts}{\\tiny}\n')
            os.write(tex_fd, '\n')
            os.write(tex_fd, '\\makeatletter\n')
            os.write(tex_fd, '\\long\\def\\@makecaption#1#2{%\n')
            os.write(tex_fd, '\\vskip\\abovecaptionskip\n')
            os.write(tex_fd, '\\sbox\@tempboxa{{\captionfonts #1: #2}}%\n')
            os.write(tex_fd, '\\ifdim \\wd\\@tempboxa >\\hsize\n')
            os.write(tex_fd, '{\\captionfonts #1: #2\\par}\n')
            os.write(tex_fd, '\\else\n')
            os.write(tex_fd, '\\hbox to\\hsize{\\hfil\\box\\@tempboxa\\hfil}%\n')
            os.write(tex_fd, '\\fi\n')
            os.write(tex_fd, '\\vskip\\belowcaptionskip}\n')
            os.write(tex_fd, '\\makeatother\n')
            os.write(tex_fd, '\\parindent 0mm'+'\n')
            os.write(tex_fd, '\\parskip 3mm'+'\n')
            os.write(tex_fd, '\\topmargin 0mm'+'\n')
            os.write(tex_fd, '\\input{epsf}'+'\n')
            os.write(tex_fd, '\\oddsidemargin 15mm'+'\n')
            os.write(tex_fd, '\\textheight 237mm'+'\n')
            os.write(tex_fd, '\\textwidth 145mm'+'\n')
            os.write(tex_fd, '\\headsep .35in'+'\n')
            os.write(tex_fd, '\\fboxrule 0.2mm'+'\n')  #this sets the line width of the boxes
            os.write(tex_fd, '\\fboxsep 6mm'+'\n')  # sets the distance of the text from the boxes

            os.write(tex_fd, preamble)
        else:
            os.write(tex_fd, '\\documentclass[titlepage]{article}' + '\n')
            os.write(tex_fd, '\\usepackage{mathptm}'+ '\n')
            os.write(tex_fd, '\\usepackage{a4,graphics,amsmath,amsfonts,amsbsy}'+'\n')
            os.write(tex_fd, '\\usepackage[T1]{fontenc}'+'\n')
            os.write(tex_fd, '\\usepackage[numbers,sort&compress]{natbib}' + '\n')
            os.write(tex_fd, '\\usepackage[utf8]{inputenc}' + '\n')
            #os.write(tex_fd, '\\usepackage[hang,tiny,bf]{caption}' + '\n')
            os.write(tex_fd, '\\usepackage{float, rotating, subfigure}\n')
            os.write(tex_fd, '\\usepackage[font=scriptsize]{caption}\n')
            os.write(tex_fd, '\\usepackage{longtable}\n')
            os.write(tex_fd, '\\usepackage{framed}\n')
            os.write(tex_fd, '\\usepackage{enumerate}\n')
            os.write(tex_fd, '\\newcommand{\\captionfonts}{\\tiny}\n')
            os.write(tex_fd, '\n')
            os.write(tex_fd, '\\makeatletter\n')
            os.write(tex_fd, '\\long\\def\\@makecaption#1#2{%\n')
            os.write(tex_fd, '\\vskip\\abovecaptionskip\n')
            os.write(tex_fd, '\\sbox\@tempboxa{{\captionfonts #1: #2}}%\n')
            os.write(tex_fd, '\\ifdim \\wd\\@tempboxa >\\hsize\n')
            os.write(tex_fd, '{\\captionfonts #1: #2\\par}\n')
            os.write(tex_fd, '\\else\n')
            os.write(tex_fd, '\\hbox to\\hsize{\\hfil\\box\\@tempboxa\\hfil}%\n')
            os.write(tex_fd, '\\fi\n')
            os.write(tex_fd, '\\vskip\\belowcaptionskip}\n')
            os.write(tex_fd, '\\makeatother\n')
            #documentclass[10pt]{article}
            #\usepackage{a4,graphics,amsmath,amsfonts,amsbsy}
            #\usepackage[T1]{fontenc}
            #\usepackage[numbers,sort&compress]{natbib}
            #\usepackage[utf8]{inputenc}
            os.write(tex_fd, '\\parindent 0mm'+'\n')
            os.write(tex_fd, '\\parskip 3mm'+'\n')
            os.write(tex_fd, '\\topmargin -15mm'+'\n')
            os.write(tex_fd, '\\input{epsf}'+'\n')
            os.write(tex_fd, '\\oddsidemargin 15mm'+'\n')
            os.write(tex_fd, '\\textheight 237mm'+'\n')
            os.write(tex_fd, '\\textwidth 145mm'+'\n')
            os.write(tex_fd, '\\headsep .35in'+'\n')
            os.write(tex_fd, '\\fboxrule 0.2mm'+'\n')  #this sets the line width of the boxes
            os.write(tex_fd, '\\fboxsep 6mm'+'\n')  # sets the distance of the text from the boxes
            os.write(tex_fd, '\\newcommand{\\bs}{\\boldsymbol}\n')
            os.write(tex_fd, '\\newcommand{\\bi}{\\begin{itemize}\\item}\n')
            os.write(tex_fd, '\\newcommand{\\ei}{\\end{itemize}}\n')
            os.write(tex_fd, '\\newcommand{\\eq}[1]{\\begin{equation} #1 \\end{equation}}\n')
            os.write(tex_fd, '\\newcommand{\\ea}[1]{\\begin{eqnarray} #1 \\end{eqnarray}}\n')
            os.write(tex_fd, '\\newcommand{\\vs}{\\vspace{2mm}}\n')
            os.write(tex_fd, '\\newenvironment{block}[1]{\\begin{framed} \\textbf{#1} \\\ }{\\end{framed}}\n')

            os.write(tex_fd, '\\begin{document}'+'\n')
    security.declareProtected(View, 'setQuestionPreamble')
    def setQuestionPreamble(self, tex_fd):
        """generate the preamble for the question pdf/latex file"""
        os.write(tex_fd, '\\documentclass[10pt]{article}' + '\n')
        os.write(tex_fd, '\\usepackage{mathptm}'+ '\n')
        os.write(tex_fd, '\\usepackage{a4,graphics,amsmath,amsfonts,amsbsy}'+'\n')
        os.write(tex_fd, '\\usepackage[T1]{fontenc}'+'\n')
        os.write(tex_fd, '\\usepackage[numbers,sort&compress]{natbib}' + '\n')
        os.write(tex_fd, '\\usepackage[utf8]{inputenc}' + '\n')
        os.write(tex_fd, '\\usepackage{float, rotating, subfigure}\n')
        os.write(tex_fd, '\\usepackage[font=scriptsize]{caption}\n')
        os.write(tex_fd, '\\usepackage{longtable}\n')
        os.write(tex_fd, '\\parindent 0mm'+'\n')
        os.write(tex_fd, '\\parskip 3mm'+'\n')
        os.write(tex_fd, '\\topmargin 0mm'+'\n')
        os.write(tex_fd, '\\input{epsf}'+'\n')
        os.write(tex_fd, '\\oddsidemargin 15mm'+'\n')
        os.write(tex_fd, '\\textheight 237mm'+'\n')
        os.write(tex_fd, '\\textwidth 145mm'+'\n')
        os.write(tex_fd, '\\headsep .35in'+'\n')
        os.write(tex_fd, '\\fboxrule 0.2mm'+'\n')  #this sets the line width of the boxes
        os.write(tex_fd, '\\fboxsep 6mm'+'\n')  # sets the distance of the text from the boxes

        os.write(tex_fd, '\\begin{document}'+'\n')
    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'setQuestions_pdf')
    def setQuestions_pdf(self):
        """generate the questions pdf/latex file but only if changes have been indicated and
          the user has enough authority
        """
        if (self.canSeeQuestions()):
            if (self.questionchanged):
                
                try:
                    tmpout = tempfile.mkdtemp()     
                except:
                    #self.setPdf('Rendering pdf file failed - not able to create temporary directory.')
                    return
                # temp directory created
                try:
                    tex_fd, tex_absname = tempfile.mkstemp(dir=tmpout, suffix='.tex')
                    pdfdir = tex_absname[:-4]+'/'
                    textfilename=tmpout+'/mytextfile.txt'
                    dviname = tex_absname[:-3] + 'dvi'
                    psname = tex_absname[:-3] + 'ps'
                    pdfname = tex_absname[:-3]+'pdf'
                except:
                    #self.setPdf('Rendering pdf file failed - not able to create temporary file.')
                    self.cleanDir(tmpout)
                    return
                # temp file created in /tmp/tmpout/tmp*
                #start by setting preamble
                try:
                    self.setQuestionPreamble(tex_fd)
                except:
                    #self.setPdf('Not able to write to temp file while rendering pdf-file.')
                    os.close(tex_fd)
                    self.cleanDir(tmpout)
                    return
                titlefile=self.Title()
                parent = aq_parent(self)
                dept = parent.getCode()+self.getCourseCode()+'.'+self.getNumberCode()
                os.write(tex_fd, '{\\bf {\\Large ' + dept + ' ' + titlefile)
                os.write(tex_fd, '}}\n')
                os.write(tex_fd, '\\\\\n')
                # find all questions
                lectures = self.getFolderContents(contentFilter={"portal_type": "Lecture"})
                #tmp = lectures.sort(lambda x,y:cmp(x.id, y.id))
                #for i in  self.listFolderContents(contentFilter={"portal_type": "Lecture"}):
                for i in lectures:
                    lec = i.getObject()
                    lectitle= lec.getTitle()

                    os.write(tex_fd, '{\\bf {' + lectitle)
                    os.write(tex_fd, '}}\n')
                    os.write(tex_fd, '\\\\\n')
                #           # Set the Contents page
                    questions = lec.getFolderContents(contentFilter={"portal_type": "TutorWebQuestion"})
                    #tmp = slides.sort(lambda x,y:cmp(x.id, y.id))
                    #for j in i.listFolderContents(contentFilter={"portal_type": "Slide"}):
                                                
                    for j in questions:
                        que = j.getObject()
                        os.write(tex_fd, '{\\bf{')
                        os.write(tex_fd, que.getId())
                        os.write(tex_fd, '}}\n')
                        type = que.question.getContentType()
                        #          text = j.getRawQuestion()
                        #                   
                        if (type == 'text/latex'):
                            qtext = que.getRawQuestion()
                            if not isinstance(qtext, unicode):
                                outputtext = qtext.decode('latin-1').encode('utf-8')
                            else:
                                outputtext = qtext.encode('utf-8')
                           
                            os.write(tex_fd, qtext + '\n')
                        elif (type == 'text/r'):
                            os.write(tex_fd, '\\begin{verbatim}\n')
                            qtext = que.getRawQuestion()
                            if not isinstance(qtext, unicode):
                                outputtext = qtext.decode('latin-1').encode('utf-8')
                            else:
                                outputtext = qtext.encode('utf-8')
                           
                            os.write(tex_fd, qtext + '\n')
                            os.write(tex_fd, '\\end{verbatim}\n')
                            exampletext = que.getRawQuizQuestion()
                            if not isinstance(exampletext, unicode):
                                outputtext1 = exampletext.decode('latin-1').encode('utf-8')
                            else:
                                outputtext1 = exampletext.encode('utf-8')
                            os.write(tex_fd, 'Example output:\n')
                            os.write(tex_fd, '\\begin{verbatim}\n') 
                            #os.write(tex_fd, outputtext1 + '\n')
                            os.write(tex_fd, exampletext + '\n')
                            os.write(tex_fd, '\\end{verbatim}\n')
                        elif (type == 'text/r-latex'):
                            os.write(tex_fd, '\\begin{verbatim}\n')
                            qtext = que.getRawQuestion()
                            if not isinstance(qtext, unicode):
                                outputtext = qtext.decode('latin-1').encode('utf-8')
                            else:
                                outputtext = qtext.encode('utf-8')
                           
                            os.write(tex_fd, qtext + '\n')
                            os.write(tex_fd, '\\end{verbatim}\n')
                            
                            exampletext = que.renderRQuestion(que.getQuestion(), 'bitmap(file=png_fd)\r\n')
                            os.write(tex_fd, 'Example output:\n')
                            os.write(tex_fd, exampletext[0] + '\n')
                        elif (type == 'text/plain'):
                            outputtext = que.getRawQuestion()
                            if not isinstance(outputtext, unicode):
                                text1 = outputtext.decode('latin-1').encode('utf-8')
                            else:
                                text1 = outputtext.encode('utf-8')
                            os.write(tex_fd, '\\begin{verbatim}\n')
                            os.write(tex_fd, text1 + '\n')
                            os.write(tex_fd, '\\end{verbatim}\n')
                        else:
                            htmltext= que.getQuizQuestion()
                            html_fd, html_absname = tempfile.mkstemp(dir=tmpout, suffix='.html')
                            html2texfilename = html_absname[:-4] + 'tex'
                            try:
                                os.write(html_fd, htmltext)
                            except:
                                htmltext = 'could not write to file' + htmltext
                            try:
                                os.system(bindir+'/html2tex ' + html_absname)
                                try:
                                    outputtext = file(html2texfilename).read()
                                except:
                                    outputtext = 'could not read file in setSlide text/html'
                            except:
                                outputtext = 'could not do text-latex'
                            os.write(tex_fd, outputtext + '\n')
                        answertype = que.getAnswerFormat()
                        if (len(que.getAnswerList()) > 0):
                            os.write(tex_fd, '\\renewcommand{\\labelenumi}{\\alph{enumi})}\n')
                            os.write(tex_fd, '\\begin{enumerate}\n')
                            if (answertype == 'text/plain'):
                                answertext = que.getAnswerList()
                                for ans in answertext:
                                    os.write(tex_fd, '\\item\n')
                                    os.write(tex_fd, '\\begin{verbatim}\n')
                                    qtext = str(ans['answertext'])
                                    if not isinstance(qtext, unicode):
                                        outputtext = qtext.decode('latin-1').encode('utf-8')
                                    else:
                                        outputtext = qtext.encode('utf-8')
                                    os.write(tex_fd, str(ans['answertext']) + '\n')
                                    #os.write(tex_fd, outputtext + '\n')
                                    os.write(tex_fd, '\\end{verbatim}\n')
                   
                            elif (answertype == 'text/structured' or answertype == 'text/restructured' or answertype == 'text/html'):
                                answertext = que.getAnswerDisplay()
                                for ans in answertext:
                                    html_fd, html_absname = tempfile.mkstemp(dir=tmpout, suffix='.html')
                                    html2texfilename = html_absname[:-4] + 'tex'
                                    try:
                                        qtext = str(ans['answertext'])
                                        if not isinstance(qtext, unicode):
                                            outputtext = qtext.decode('latin-1').encode('utf-8')
                                        else:
                                            outputtext = qtext.encode('utf-8')
                                        os.write(html_fd, str(ans['answertext']))
                                        #os.write(html_fd, outputtext)    
                                    except:
                                        htmltext = 'could not write to file'
                                    try:
                                        os.system(bindir+'/html2tex ' + html_absname)
                                        try:
                                            outputtext = file(html2texfilename).read()
                                        except:
                                            outputtext = 'could not read file in setSlide text/html'
                                    except:
                                        outputtext = 'could not do text-latex'
                                    os.write(tex_fd, '\\item\n')
                                    os.write(tex_fd, outputtext + '\n')
                            else:
                                answertext = que.getAnswerList()
                                for ans in answertext:
                                    os.write(tex_fd, '\\item\n')
                                    qtext = str(ans['answertext'])
                                    if not isinstance(qtext, unicode):
                                        outputtext = qtext.decode('latin-1').encode('utf-8')
                                    else:
                                        outputtext = qtext.encode('utf-8')
                                    os.write(tex_fd, str(ans['answertext']) + '\n')
                                    #os.write(tex_fd, outputtext + '\n')
                            os.write(tex_fd, '\\end{enumerate}\n')
                
                    
   
                os.write(tex_fd, '\\end{document}\n')
            
            #latexfile = file(tex_absname).read()
            #self.setQuestionFile(latexfile) 
            
                pdftext = self.render_pdf(tmpout, tex_absname, dviname, psname, pdfname)
                self.setQuestionFile(pdftext)
                os.close(tex_fd)
                self.cleanDir(tmpout)
                self.questionchanged = False
            return self.getField('QuestionFile').get(self)  
        else:
            return False
            
            
                                       
       
     
# Register this type in Zope
if PLONE_VERSION == 3:
    registerATCTLogged(Tutorial)
else:
    atapi.registerType(Tutorial, PROJECTNAME)
# Register functions as an event handler, indicated changes which needed to be performed
# whenever a tutor-web content is edited/initialized/copied/removed 
# tutor-web content which contains printable content must be alerted to chages in order
# to re-render pdf/latex material.
# some tutor-web content must be published and reordered upon creation or when being copies

# functions called when content is edited
@adapter(IPrintable, IObjectEditedEvent)
def new_content_edited_to_print(obj, event):
    #tmpout = tempfile.mkdtemp()
    #tex_fd, tex_absname = tempfile.mkstemp(dir=tmpout, suffix='.editedEvent')
    #os.write(tex_fd, 'in objecteditedevent\n')
    obj.editedObject() 
    #os.write(tex_fd, 'after obj.editedObject\n')
@adapter(ISponsor, IObjectEditedEvent)
def new_content_sponsor_edited_to_print(obj, event):
    # only if sponsor is a part of tutorial then changes need to be indicated
    parent = aq_parent(obj)
    if (parent.Type() == 'Tutorial'):
        parent.editedObject()

# functions called when content is copy/pasted
@adapter(IOrderedTutorWebContent, IObjectClonedEvent)
def new_content_orderedcontent_cloned_to_print(obj, event):
    event.object.publishAll(str(event.object.Type()), obj)        
@adapter(IPrintable, IObjectClonedEvent)
def new_content_printable_cloned_to_print(obj, event):
    event.object.editedObject()
    event.object.reindexObject()
       
@adapter(ISponsor, IObjectClonedEvent)
def new_content_sponsor_cloned_to_print(obj, event):
    # only needed if sponsors belongs to a tutorial
    parent = aq_parent(event.object)
    if (parent.Type() == 'Tutorial'):
        parent.editedObject()
        event.object.reindexObject()

# functions called whenever an object is created/removed and copy/cut and pasted
@adapter(IPrintable, IObjectMovedEvent)
def new_content_printable_moved_to_print(obj, event):
    
    if event.newParent is not None:
        if (str(obj.Type()) == 'Tutorial'):
            ''' do nothing'''
        else:
            if (event.newParent.Type() == 'Tutorial' or event.newParent.Type() == 'Lecture'):
                # let parents know that object has been changed
                event.newParent.editedObject(str(obj.Type()))
               
                
    if event.oldParent is not None:
        if (str(obj.Type()) == 'Tutorial'):
            ''' do nothing'''
        else:
            if (event.oldParent.Type() == 'Tutorial' or event.oldParent.Type() == 'Lecture'):
                event.oldParent.editedObject(str(obj.Type()))
               
           
@adapter(IOrderedTutorWebContent, IObjectMovedEvent)
def new_content_orderedcontainer_moved_to_print(obj, event):
    
    if event.newParent is not None:
        event.newParent.orderObjects("id")
        event.newParent.plone_utils.reindexOnReorder(event.newParent)
        try:    
            obj.tryWorkflowAction("publish", ignoreErrors=True)
        except:
            """do nothing - couldn't publish"""
        obj.reindexObject()
        

@adapter(ISponsor, IObjectMovedEvent)
def new_content_sponsor_willbemoved_to_print(obj, event):
   
    if event.newParent is not None:
        if (event.newParent.Type() == 'Tutorial'):
            event.newParent.editedObject()
        obj.reindexObject()
        
    if event.oldParent is not None:
        if (event.oldParent.Type() == 'Tutorial'):
            event.oldParent.editedObject()
            


# functions called when object is created

@adapter(IOrderedTutorWebContent, IObjectInitializedEvent)
def new_content_orderedcontent_added_to_print(obj, event):
    obj.initializeObject()


@adapter(ISponsor, IObjectInitializedEvent)
def new_content_sponsor_added_to_print(obj, event):
    obj.initializeObject()


@adapter(ISponsor, IObjectRemovedEvent)
def new_content_removed_sponsor_to_print(obj, event):  
    obj.haveChanged()
   

   
    
    




