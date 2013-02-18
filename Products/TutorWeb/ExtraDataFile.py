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
     IntegerField,  ReferenceField, IntegerWidget, StringField, TextField, \
     ImageField, TextAreaWidget, StringWidget, SelectionWidget, RichWidget, \
     ReferenceWidget, ImageWidget, FileField, FileWidget
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

from Products.Archetypes.interfaces import IObjectInitializedEvent, IObjectEditedEvent
from zope.interface import implements
from Products.TutorWeb.interfaces import IPrintable, IExtraDataFile, IOrderedTutorWebContent
from Products.ATContentTypes.content import file
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
#from Products.Archetypes.atapi import FileField
#from Products.Archetypes.atapi import FileWidget
from Products.Archetypes.atapi import PrimaryFieldMarshaller  
from Products.Archetypes.atapi import AnnotationStorage
from Products.validation.validators.SupplValidators import MaxSizeValidator
from Products.validation.config import validation
from Products.validation import V_REQUIRED

from config import PLONE_VERSION
if PLONE_VERSION == 4:
    from Products.Archetypes import atapi
    from config import PROJECTNAME

class ExtraDataFile(file.ATFile):
    """Slides can use information from ExtraDataFiles for rendering material."""
   
    implements(IPrintable, IExtraDataFile, IOrderedTutorWebContent)
    global_allow = False
    meta_type = 'ExtraDataFile'          # zope type name
    portal_type = meta_type          # plone type name
    archetype_name = 'ExtraDataFile' # friendly type name
    _at_rename_after_creation = True  #automatically create id
    security = ClassSecurityInfo()

   
    def publishAll(self, typeofobject=None, originalobj=None):
        '''publich content'''
        # for now do nothing
    def initializeObject(self):
        parent = aq_parent(self)
        parent.updateRImages()
    def editedObject(self, objtype=None):
        parent = aq_parent(self)
        parent.editedObject()
        parent.updateRImages()
    def haveChanged(self):
        parent = aq_parent(self)
        # let lecture and tutorial know that have changed
        parent.setChanged(True)
        # must also let all the slides know that there are changes
        parent.updateRImages()
   
    
   
     
# Register this type in Zope
if PLONE_VERSION == 3:
    registerATCTLogged(ExtraDataFile)
else:
    atapi.registerType(ExtraDataFile, PROJECTNAME)



