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
     ReferenceWidget, ImageWidget
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
from Products.TutorWeb.interfaces import IPrintable, ISponsor
if PLONE_VERSION == 4:
    from Products.Archetypes import atapi
    from config import PROJECTNAME

   
class Sponsor(base.ATCTContent):
    """A sponsor for a tutor-web site, Department or a Tutorial which could typically be viewed on a tutor-web site or
    on printed content belonging to tutor-web. Can contain a logo, url and additional text as well as a title.
    A sponsor is implemented as base contents and uses interface, ISponsor.
    """
   
        
    schema = schemata.ATContentTypeSchema.copy() + Schema((
        
        StringField('title',
                required=True,
                searchable=0,
                default='tutor-web sponsor',
                widget=StringWidget(
                    label='Title',
                    description='A title for the sponsor.',
                    i18n_domain='plone'),
               
            ),
         StringField('sponsorurl',
              searchable=0,
              default='http://sponsor-url.com',
              widget=StringWidget(label='Specify the web address of the sponsor',
                                description='url for sponsor',
                                
                                ),
              
              ),
         TextField('sponsortext',
              searchable=0,
              default='',
              default_content_type='text/plain',
              allowable_content_types=('text/plain'),
              widget=TextAreaWidget(label='Additional text, more detailed information about the sponsor.',
                                description='additional sponsor text', 
                               
                                
                                ),    
              ),
        ImageField('sponsorlogo',
                   #original_size=(600,600),
                   max_size=(200,200),
                   #sizes={ 'mini' : (80,80),
                   #        'normal' : (200,200),
                   #         'big' : (100,100),
                   #         'maxi' : (500,500),
                   #        },
                   widget=ImageWidget(label='Sponsor logo',
                                      description='logo', 
                                     
                                       ),
        ),
        
        
       
     ))
   
    implements(ISponsor)
    global_allow = False
    meta_type = 'Sponsor'          # zope type name
    portal_type = meta_type          # plone type name
    archetype_name = 'Sponsor' # friendly type name
    _at_rename_after_creation = True  #automatically create id
    security = ClassSecurityInfo()
        
    
    def initializeObject(self):
        """Called after the creatation of Sponsor
           publish sponsor so it becomes available for viewing for all users
        """
        self.tryWorkflowAction("publish", ignoreErrors=True)
    security.declarePrivate('tryWorkflowAction')
    def tryWorkflowAction(self, action, ignoreErrors=False, comment=None):
        """publish sponsor"""
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
    def publishAll(self, typeofobject=None, originalobj=None):
        """publish sponsor"""
        self.tryWorkflowAction("publish", ignoreErrors=True)
    def haveChanged(self):
        parent = aq_parent(self)
        parenttype = parent.Type()
        # should use interface instead FIXME
        # only letting tutorial know of changes not lecture as no sponsor info in lectures at the moment
        if (parenttype == 'Tutorial'):
            parent.editedObject()
     
# Register this type in Zope
if PLONE_VERSION == 3:
    registerATCTLogged(Sponsor)
else:
    atapi.registerType(Sponsor, PROJECTNAME)

