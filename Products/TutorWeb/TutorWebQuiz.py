import os, os.path
import re
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.folder import ATFolderSchema
from AccessControl import ClassSecurityInfo, getSecurityManager
from Acquisition import *
from Products.Archetypes.utils import shasattr
from DateTime import DateTime
from zipfile import ZipFile
from Products.Archetypes.public import Schema, BooleanField, IntegerField, \
     ObjectField, StringField, Field
from Products.Archetypes.Widget import TypesWidget, BooleanWidget, \
     SelectionWidget, StringWidget
from Products.Archetypes.utils import DisplayList
from Products.CMFCore.utils import getToolByName
from config import *
from permissions import *
from tools import *
from Statistics import Statistics
from Products.validation.interfaces import ivalidator
from Products.validation import validation
from Products.validation import ValidationChain
from Products.validation.exceptions import ValidatorError
import tempfile
from Products.CMFCore.utils import getToolByName
if PLONE_VERSION == 4:
    from Products.Archetypes import atapi
    from config import PROJECTNAME


class TutorWebQuiz(ATFolder):
    '''a tutorweb quiz '''
    archetype_name = portal_type = meta_type = 'TutorWebQuiz'
    security = ClassSecurityInfo()
    #chosenquestions = {}
    _at_rename_after_creation = 1
    
    schema = ATFolderSchema.copy() + Schema((
              StringField('title',
                required=True,
                searchable=0,
                default='Tutorweb Lecture Quiz',
                widget=StringWidget(
                    label='Title',
                    description='Specify the title for the quiz.',
                 ),
               
            ),
            
        ))
    
    security.declarePrivate('at_post_create_script')
    def at_post_create_script(self):
        '''need to add available results to quiz'''
        #lec = aq_parent(self)
        #tut = aq_parent(lec)
        #portal_catalog = getToolByName(self, 'portal_catalog')
        #brains = portal_catalog.unrestrictedSearchResults({'portal_type' : 'Lecture'},path='/'.join(tut.getPhysicalPath()))
        #for b in brains:
        #    lec = b.getObject()
        #    quiz = lec.getQuiz()
        #    students = quiz.getSubmitterIds()
        #    for id in students:
        #        result = lec.createResult(id)
        #    return
    if PLONE_VERSION == 3:
        security.declarePublic('userIsGrader')
        def userIsGrader(self, user):
            mctool = getToolByName(self, 'ecq_tool')
            return mctool.userHasOneOfRoles(user,
                                        ('Manager', ROLE_RESULT_GRADER, 'Owner'),
                                        self)
    
        security.declarePublic('userIsManager')
        def userIsManager(self, user):
            mctool = getToolByName(self, 'ecq_tool')
            return mctool.userHasOneOfRoles(user, ('Manager',), self)
   
    #security.declarePrivate('getResults')
    def getResults(self, candidateId=None):
        
        flt = {'portal_type' : 'QuizResult'}
        if candidateId is not None:
            flt['Creator'] = candidateId
        res = self.contentValues(filter=flt)
        if (len(res) > 0):
            return res
        else:
            return None
   
    #security.declareProtected(PERMISSION_INTERROGATOR, 'getSubmitterIds')
    security.declarePublic('getSubmitterIds')
    def getSubmitterIds(self):
        """Return the IDs of the candidates who have actually
        submitted/taken this quiz.
        """
        d = {}
        res = self.getResults()
        for item in res:
            ## removing workflow states
            ##if item.getWorkflowState() in ['pending', 'graded', 'superseded']:
            d[item.Creator()] = True
        return d.keys()
                
if PLONE_VERSION == 3:
    registerATCTLogged(TutorWebQuiz)
else:
    atapi.registerType(TutorWebQuiz, PROJECTNAME)
