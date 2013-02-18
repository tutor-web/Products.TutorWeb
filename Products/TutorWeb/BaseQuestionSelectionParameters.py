from AccessControl import ClassSecurityInfo, getSecurityManager
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.public import Schema, BaseSchema, BaseContent, \
     ObjectField, IntegerField, StringField, DateTimeField, BooleanField, FloatField
from Products.Archetypes.Widget import TypesWidget, StringWidget, \
     BooleanWidget
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

from Products.validation.validators.RangeValidator import RangeValidator
from Products.validation import validation
validRange = RangeValidator("validRange", 0.0, 1.000001)
validation.register(validRange)

BaseQuestionSelectionParametersSchema = ATContentTypeSchema.copy() + Schema((
         StringField('title',
                required=True,
                searchable=0,
                default='BaseQuestionSelection',
                widget=StringWidget(
                    label='Title',
                    description='The main title of the object.',
                    i18n_domain='plone'),
               
         ),  
         FloatField("historical_selection_probability", 
                   
                   required=False,
                   default='1.0',
                   # 0.0 <= value < 1.000001 
                   validators = ('validRange',),
                   widget=IntegerWidget(description='Probability of selecting questions in a quiz from previous lectures. At the moment only using either 1.0 or 0.0.'
 '1.0: All questions from previous lectures are selected randomly as well as from the current lecture.'
 '0.0: Only select questions from the current lecture.',
                       

        ),
       ),   
                  
        ))
 
# class containing parameters related to how questions in a quiz are selected
 
class BaseQuestionSelectionParameters(ATCTContent, HistoryAwareMixin):
    """Container for question selection parameters."""

   
    schema = BaseQuestionSelectionParametersSchema
    _at_rename_after_creation = True
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

atapi.registerType(BaseQuestionSelectionParameters, PROJECTNAME)
