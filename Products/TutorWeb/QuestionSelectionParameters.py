from AccessControl import ClassSecurityInfo, getSecurityManager
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.public import Schema, BaseSchema, BaseContent, \
     ObjectField, IntegerField, StringField, DateTimeField, BooleanField, FloatField, \
     ReferenceField
from Products.Archetypes.Widget import TypesWidget, StringWidget, \
     BooleanWidget, ReferenceWidget, DecimalWidget
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget \
     import ReferenceBrowserWidget
from Products.ATContentTypes.content.base import ATCTContent
from Products.ATContentTypes.content.schemata import ATContentTypeSchema

from Products.DataGridField import DataGridField, DataGridWidget
from Products.DataGridField.Column import Column
from Products.DataGridField.SelectColumn import SelectColumn
from Products.DataGridField.RadioColumn import RadioColumn
from Products.DataGridField.CheckboxColumn import CheckboxColumn
from Products.DataGridField.FixedColumn import FixedColumn
from Products.DataGridField.DataGridField import FixedRow
from Products.DataGridField.HelpColumn import HelpColumn

from config import *
from permissions import *
from tools import *
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.Archetypes.public import BaseSchema, Schema, BooleanField, \
     StringField, TextField, SelectionWidget, TextAreaWidget, RichWidget, \
     BaseContent
from Products.Archetypes.Widget import TypesWidget, IntegerWidget, \
     BooleanWidget, StringWidget
from Products.Archetypes.utils import DisplayList
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.folder import ATFolderSchema
from Products.Archetypes import atapi
import tempfile
from Products.CMFCore.utils import getToolByName
from random import random
import shutil
from Products.Archetypes import atapi
from config import PROJECTNAME
from Products.TutorWeb.BaseQuestionSelectionParameters import BaseQuestionSelectionParameters
from Products.TutorWeb.BaseQuestionSelectionParameters import BaseQuestionSelectionParametersSchema

from Products.validation.validators.RangeValidator import RangeValidator
from Products.validation import validation
validRange = RangeValidator("validRange", -1.0, 1.000001)
validation.register(validRange)

# class extending BaseQuestionSelectionParameters
# returns by default values contained in a referenced BaseQuestionSelectionParameters object
   
class QuestionSelectionParameters(BaseQuestionSelectionParameters):
    """Container for parameres used when selection a question in a quiz."""

    _at_rename_after_creation = True
    schema = BaseQuestionSelectionParametersSchema.copy() + Schema((
            FloatField("historical_selection_probability", 
                   required=False,
                   default='-1.0',
    #               # -1.0 <= value < 1.000001
                   validators = ('validRange',),
                   widget=DecimalWidget(description='Probability of selecting questions in a quiz from previous lectures. Possible values:\n'
 '-1.0: Historical selection probability obtained from values set in parent Tutorial.\n'                                         
 '1.0: All questions from previous lectures and current are used as a selection pool.'
 'h: For h between 0 and 1, select from pool with probability h vs current lecture only with probability 1-h.'
 '0.0: Only select questions from the current lecture.',
                       
        ),),

           ReferenceField('BaseSelectionParameters',
                    required = 1,        
                    widget=ReferenceWidget(
                           label="Default parameters used when selecting questions",
                           description='Object containing default values for choosing questions.',
                           destination=".",
                           destination_types=("BaseQuestionSelectionParameters",),
                           
                           ),
                       multiValued=False,
                       relationship='DefaultValues',
                       allowed_types= ("BaseQuestionSelectionParameters",),
                        
                   ), 
            
            
    ))
    security = ClassSecurityInfo()
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
    def findHistorical_selection_probability(self):
        if (self.getField('historical_selection_probability').get(self)  >= 0.0):
            return self.getField('historical_selection_probability').get(self)
        else:
            
            baseparams = self.getBaseSelectionParameters()
            if (baseparams):
                return baseparams.getHistorical_selection_probability()
            else:
                return 1.0
    
atapi.registerType(QuestionSelectionParameters, PROJECTNAME)
