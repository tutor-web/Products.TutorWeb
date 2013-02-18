from AccessControl import ClassSecurityInfo, getSecurityManager
from Products.Archetypes.public import OrderedBaseFolder
from Products.CMFCore.permissions import View
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.folder import ATFolderSchema
from Products.Archetypes.public import BaseSchema, Schema, BooleanField, \
     StringField, TextField, ReferenceField, ImageField, SelectionWidget, TextAreaWidget, \
     BaseContent
from Products.Archetypes.Widget import TypesWidget, IntegerWidget, \
     BooleanWidget, StringWidget, RichWidget, SelectionWidget, ImageWidget
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget \
     import ReferenceBrowserWidget
from Products.ATContentTypes.content.base import ATCTContent
from Products.ATContentTypes.content.schemata import ATContentTypeSchema, finalizeATCTSchema


from Products.TutorWeb import twutils

from config import *
from permissions import *
from tools import *
from Products.Archetypes.utils import DisplayList

import os
import re
from string import *
import shutil
from cStringIO import StringIO
import tempfile
from Products.CMFCore.utils import getToolByName
from Products.CMFCore import permissions
from zope.interface import implements
from Products.TutorWeb.interfaces import IPrintable, ISlide, IOrderedTutorWebContent
if PLONE_VERSION == 4:
    from Products.Archetypes import atapi
    from config import PROJECTNAME
class Slide(ATFolder):
    """The basic slide represents a part of a lecture consisting of several slides.
    The basic component of the tutor-web is the slide. A slide can contain four main components:
    maintext, and main graphic, explanation text and explanation graphic. Additionally related material relevant to a given
slide can be set, detailed material, examples handouts and alternative material.
    """
    IMAGE_FORMATS = DisplayList ((
    ('none', 'No image'),
    ('image', 'png, gif or jpeg'),
    ('fig', 'Fig'),
    ('r', 'R'),
    ('gnuplot', 'gnuplot'),
    ))
   
   
    schema = ATFolderSchema.copy() + Schema((
    
        StringField('id',
                  widget=StringWidget(description='Change ID to become more readable. Slides appear in alphabetical order based on this value.', modes='edit',),
                  required = 1,
                  ),
         StringField('title',
                required=True,
                searchable=0,
                default='Slide',
                widget=StringWidget(
                    label='Title',
                    description='The main title of the slide',
                  ),
                
            ),
         ReferenceField('ExtraMaterials',
                       widget=ReferenceBrowserWidget(
                           label="Extra material",
                           description='Extra material connected to the slide material.',
                           destination=".",
                           destination_types=("File",),
                           visible={'edit':'invisible'},
                           ),
                       
                       #required = 1,
                       multiValued=True,
                       relationship='hasExtraMaterial',
                       allowed_types= ("File",),
                       ),
         BooleanField("UpdateSlideText",                                 
                default=1,
                 widget=BooleanWidget(
                    label='Update transformable slide text data',
                    description='Check this box if you want transformable text data '
                    'to be updated.',
                   
                    ),
            ),
         BooleanField("SlideTextChanged", 
                default=0,
                 widget=BooleanWidget(
                    label='This is a control parameter to check if text has been changed recently.',
                    #label_msgid='randomize_answer_order_label',
                    description='Slide is updated if text has been changed.',
                    visible={'edit':'invisible'},
                   
                    ),
            ),
        TextField('SlideText',
              searchable=0,
              default_content_type='text/latex',
              default_output_type='text/latex',
              accessor='SlideTextRaw',
              mutator='setSlideText',
              allowable_content_types=('text/latex', 'text/plain', 'text/structured', 'text/restructured', 'text/html'),
              widget=RichWidget(label='Main text',
                                description='Main content of the slide', macro='tutorwebtext_notkupu', allow_file_upload=1,
                               
                               
                                
                                ),
             
              ),
         StringField('SlideTextView',
              searchable=0,
            
              widget=StringWidget(label='Main text',
                                description='Main content of the slide', 
                                macro='tutorwebtext_view',
                                visible={'edit':'invisible'},
                               
                                
                                ),
              
              ),
        StringField('SlideImageFormat',
                vocabulary=IMAGE_FORMATS,
                default='none',
                widget=SelectionWidget(label='Image format',
                                       description='Select the format of the main image. It can be a file with format png, gif or jpeg. Or the main image can be rendered from a text based image format of type R, Gnuplot or Fig.',),
                ),
        
        TextField('SlideImageText',
              allowable_content_types=(),
              default_output_type='text/plain', 
              default_content_type='text/plain',
              widget=RichWidget(label='Image definnition',
                                description='Main image for slide, displayed to the right of main text of the slide. Possible formats are: fig, gnuplot and R.',  allow_file_upload=1, macro='tutorwebtext_notkupu',
                                #condition ='not:object/isImageFormat',
                               ),
             
                ),
        StringField('SlideImageCaption',
                    widget=TextAreaWidget(label="Main image caption",
                                        description="Main image caption",),
        ),
        ImageField('SlideImage',
                   #original_size=(600,600),
                   max_size=(600,600),
                   #sizes={ 'mini' : (80,80),
                   #        'normal' : (200,200),
                   #         'big' : (100,100),
                   #         'maxi' : (500,500),
                   #        },
                   widget=ImageWidget(label='Slide image',
                                      description='Main image for slide, displayed to the right of main text of the slide. Possible formats for uploaded images are: png, gif and jpeg.', macro='tutorwebimage',
                             # condition ='object/isImageFormat',
                                       )),
        
        ImageField('SlideImageWWW',
                    max_size=(300,300),
                    widget=ImageWidget(description='Explanation image for slide, displayed at the bottom of the slide to the right of explanation text. Possible formats for uploaded images are: png, gif and jpeg.',
                                       macro='tutorwebimage',
                                       modes='view',
                                       visible={'view':'invisible','edit':'invisible'},),),
        TextField('Explanation',
              searchable=0,
              accessor='ExplanationRaw',
              mutator='setExplanation',
              default_content_type='text/latex',
              default_output_type='text/latex',
              allowable_content_types=('text/latex','text/plain', 'text/structured', 'text/restructured', 'text/html',),
              widget=RichWidget(label='Explanation text',
                                description='Explantory material, displayed at the bottom of the slide', macro='tutorwebtext_notkupu_small',  allow_file_upload=1,
             
                               ),
             
              ),
        StringField('ExplanationView',
              searchable=0,
              
              widget=StringWidget(label='Main text',
                                description='Main content of the slide',
                                macro='tutorwebtext_view',
                                #macro='tutorwebtext_notkupu', allow_file_upload=1,
                               visible={'edit':'invisible'},
                               
                                
                                ),
              
             
              ),
        StringField('ExplanationImageFormat',
                vocabulary=IMAGE_FORMATS,
                default='none',
                widget=SelectionWidget(label='Image format',
                                       description='Select the format of the explanation image. It can be a file with format png, gif or jpeg. Or the main image can be rendered from a text based image format of type R, Gnuplot or Fig.',
                                       #visible = {'edit': 'invisible'},
                                       ),
                ),
        TextField('ExplanationImageText',
              allowable_content_types=(),
              default_output_type='text/plain',
              default_content_type='text/plain',
              widget=RichWidget(label='Image definition',
                                description='Explanation image for slide, displayed at the bottom of the slide to the right of the explanation text. Possible formats are: fig, gnuplot and R',macro='tutorwebtext_notkupu',allow_file_upload=1,
                                #visible={'edit': 'invisible'},
                                      ),
              
                ),
               
        StringField('ExplanationImageCaption',
                    widget=TextAreaWidget(label="Explanation image caption",
                                        description="Explanation image caption",
                                        #visible={'edit': 'invisible'},  
                                          ),
        ),
        ImageField('ExplanationImage',
                    max_size=(600,600),
                    widget=ImageWidget(label='Explanation image',
                                       description='Explanation image for slide, displayed at the bottom of the slide to the right of explanation text. Possible formats for uploaded images are: png, gif and jpeg.',
                                       #visible={'edit':'invisible'},
                                       ),
                   ),
        
       ImageField('ExplanationImageWWW',
                    max_size=(200,200),
                    
                    widget=ImageWidget(description='Explanation image for slide, displayed at the bottom of the slide to the right of explanation text. Possible formats for uploaded images are: png, gif and jpeg.',
                                       macro='tutorwebimage',
                                       modes='view',
                                       visible={'view':'invisible','edit':'invisible'},),),
        TextField('Details',
              searchable=0,
              accessor='DetailsRaw',
              mutator='setDetails',
              default_content_type='text/latex',
              default_output_type='text/html',
              allowable_content_types=('text/latex','text/plain', 'text/structured', 'text/restructured',),
              widget=RichWidget(description='Detailed information on the topic of the slide which can be accessed from the main slide view and is part of the pdf document which can be displayed for each tutorial.', macro='tutorwebtext_notkupu', allow_file_upload=1, 
             
                               ),
             
              ),
         StringField('DetailsView',
              searchable=0,
              
              widget=StringWidget(label='Main text',
                                description='Main content of the slide', 
                                 macro='tutorwebtext_view',
                               
                               visible={'edit':'invisible'},
                               
                                
                                ),
              
             
              ),
        TextField('Examples',
              searchable=0,
              accessor='ExamplesRaw',
              mutator='setExamples',
              default_content_type='text/latex',
              default_output_type='text/latex',
              allowable_content_types=('text/latex','text/plain', 'text/structured', 'text/restructured', 'text/html'),
              widget=RichWidget(description='Examples for slide which can be accessed from the main slide view and is part of the pdf document which can be displayed for each tutorial.', macro='tutorwebtext_notkupu', allow_file_upload=1, 
             
                               ),
             
              ),
         StringField('ExamplesView',
              searchable=0,
             
              widget=StringWidget(label='Main text',
                                description='Main content of the slide',
                                 macro='tutorwebtext_view',
                                #macro='tutorwebtext_notkupu', allow_file_upload=1,
                               visible={'edit':'invisible'},
                               
                                
                                ),
               
             
              ),
        TextField('Alternative',
              searchable=0,
              accessor='AlternativeRaw',
              mutator='setAlternative',
              default_content_type='text/latex',
              default_output_type='text/html',
              allowable_content_types=('text/latex','text/plain', 'text/structured', 'text/restructured', 'text/html',),
              widget=RichWidget(description='Alternate educational material for slide which can be accessed from the main slide view.', macro='tutorwebtext_notkupu', allow_file_upload=1,
             
                               ),
             
              ),
         StringField('AlternativeView',
              searchable=0,
              
              widget=StringWidget(label='Main text',
                                description='Main content of the slide',
                                 macro='tutorwebtext_view',
                               
                               visible={'edit':'invisible'},
                               
                                
                                ),
              
             
             
              ),
        TextField('Handout',
              searchable=0,
              accessor='HandoutRaw',
              mutator='setHandout',
              default_content_type='text/latex',
              default_output_type='text/html',
              allowable_content_types=('text/latex','text/plain', 'text/structured', 'text/restructured', 'text/html'),
              widget=RichWidget(description='Handout for slide which can be accessed from the main slide view and is part of the pdf document which can be displayed for each tutorial.', macro='tutorwebtext_notkupu', allow_file_upload=1,
             
                               ),
              
              ),
         StringField('HandoutView',
              searchable=0,
             
              widget=StringWidget(label='Main text',
                                description='Main content of the slide',
                                 macro='tutorwebtext_view',
                                #macro='tutorwebtext_notkupu', allow_file_upload=1,
                               visible={'edit':'invisible'},
                               
                                
                                ),
               
             
             
              ),
        TextField('SlideReference',
              searchable=0,
              accessor='SlideReferenceRaw',
              mutator='setSlideReference',
              default_content_type='text/latex',
              default_output_type='text/html',
              allowable_content_types=('text/latex','text/plain', 'text/structured', 'text/restructured', 'text/html'),
              widget=RichWidget(label='Reference',
                                description='Slide references are printed as part of a pdf document which can be displayed for each tutorial.', macro='tutorwebtext_notkupu',  allow_file_upload=1,
             
                               ),
             
              ),
         StringField('SlideReferenceView',
              searchable=0,
             
              widget=StringWidget(label='Main text',
                                description='Main content of the slide',
                                 macro='tutorwebtext_view',
                                
                               visible={'edit':'invisible'},
                               
                                
                                ),
              
             
             
              ),
        ))

    implements(IPrintable, ISlide, IOrderedTutorWebContent)
    security = ClassSecurityInfo()
    # This prevents the Questions from showing up as a portal content type
    global_allow = False
    meta_type = 'Slide'          # zope type name
    portal_type = meta_type          # plone type name
    archetype_name = 'Slide' # friendly type name
    changed = True
    def useExplanationFig(self):
        return EXPLANATION_FIG
    def publishAll(self, typeofobject=None, originalobj=None):
        '''publich content'''
        # publish slide
        self.tryWorkflowAction("publish", ignoreErrors=True)

    def RawSlideText(self):    
        return self.getRawSlideText()
    def RawExplanation(self):
        return self.getRawExplanation()
    def RawDetails(self):
        return self.getRawDetails()
    def RawExamples(self):
        return self.getRawExamples()
    def RawAlternative(self):
        return self.getRawAlternative()
    def RawHandout(self):
        return self.getRawHandout()
    def SlideTextRaw(self):    
        return self.getSlideTextView()
    def ExplanationRaw(self):
        return self.getExplanationView()
    def DetailsRaw(self):
        return self.getDetailsView()
    def ExamplesRaw(self):
        return self.getExamplesView()
    def AlternativeRaw(self):
        return self.getAlternativeView()
    def HandoutRaw(self):
        return self.getHandoutView()
    def SlideReferenceRaw(self):
        return self.getSlideReferenceView()
    def setSlideText(self, value, **kwargs):
        '''set main slide text'''
        f = self.getField('SlideText')
        f.set(self, value, raw=True, **kwargs)
        self.setSlideTextView(value)
    def setSlideTextView(self,value):
        """update and render appropriate slide text material"""
        if (self.UpdateSlideText):
            f = self.getField('SlideTextView')
            text = self.getRawSlideText()
            type = self.SlideText.getContentType()
            value = self.transformText(type, text, 'slidetext')
            f.set(self, value)
            self.setSlideTextChanged(1)
    def setSlideTextView2(self, value):
         f = self.getField('SlideTextView')
         f.set(self, value)
    def setSlideTextView3(self, value):
         f = self.getField('SlideTextView')
         text = self.getRawSlideText()
         type = self.SlideText.getContentType()
         val = self.transformText(type, text, 'slidetext') 
         f.set(self, val)
    def setSlideTextView1(self, value):
         f = self.getField('SlideTextView')
         text = self.getRawSlideText()
         type = self.SlideText.getContentType()
         val = self.transformText(type, text, 'slidetext')
         f.set(self, val)
         f1 = self.getField('ExplanationView')
         text1 = self.getRawExplanation()
         type1 = self.Explanation.getContentType()
         value1 = self.transformText(type1, text1, 'explanation')
         f1.set(self, value1)
         f2 = self.getField('DetailsView')
         text2 = self.getRawDetails()
         type2 = self.Details.getContentType()
         value2 = self.transformText(type2, text2, 'details')
         f2.set(self, value2)
         f3 = self.getField('ExamplesView')
         text3 = self.getRawExamples()
         type3 = self.Examples.getContentType()
         value3 = self.transformText(type3, text3, 'examples')
         f3.set(self, value3)
         f4 = self.getField('HandoutView')
         text4 = self.getRawHandout()
         type4 = self.Handout.getContentType()
         value4 = self.transformText(type4, text4, 'handout')
         f4.set(self, value4)
         f5 = self.getField('AlternativeView')
         text5 = self.getRawAlternative()
         type5 = self.Alternative.getContentType()
         value5 = self.transformText(type5, text5, 'alternative')
         f5.set(self, value5)
         f6 = self.getField('SlideReferenceView')
         text6 = self.getRawSlideReference()
         type6 = self.SlideReference.getContentType()
         value6 = self.transformText(type6, text6, 'reference')
         f6.set(self, value6)
         return 'success'
    def setExplanation(self, value, **kwargs):
        '''set explanation with raw data and explanation view with transformed data.'''
        f = self.getField('Explanation')
        f.set(self, value, raw=True, **kwargs)
        self.setExplanationView(value)
    def setExplanationView(self,value):
        if (self.UpdateSlideText):
            f = self.getField('ExplanationView')
            text = self.getRawExplanation()
            type = self.Explanation.getContentType()
            value = self.transformText(type, text, 'explanation')
            f.set(self, value)
            self.setSlideTextChanged(1)
    def setDetails(self, value, **kwargs):
        '''set details text'''
        f = self.getField('Details')
        f.set(self, value, raw=True, **kwargs)
        self.setDetailsView(value)
    def setDetailsView(self,value):
        if (self.UpdateSlideText):
            f = self.getField('DetailsView')
            text = self.getRawDetails()
            type = self.Details.getContentType()
            value = self.transformText(type, text, 'details')
            f.set(self, value) 
    def setExamples(self, value, **kwargs):
        '''set examples text'''
        f = self.getField('Examples')
        f.set(self, value, raw=True, **kwargs)
        self.setExamplesView(value)
    def setExamplesView(self,value):
        if (self.UpdateSlideText):
            f = self.getField('ExamplesView')
            text = self.getRawExamples()
            type = self.Examples.getContentType()
            value = self.transformText(type, text, 'examples')
            f.set(self, value)
    def setAlternative(self, value, **kwargs):
        '''set alternative text'''
        f = self.getField('Alternative')
        f.set(self, value, raw=True, **kwargs)
        self.setAlternativeView(value)
    def setAlternativeView(self,value):
        if (self.UpdateSlideText):
            f = self.getField('AlternativeView')
            text = self.getRawAlternative()
            type = self.Alternative.getContentType()
            value = self.transformText(type, text, 'alternative')
            f.set(self, value)
    def setHandout(self, value, **kwargs):
        '''set handout text'''
        f = self.getField('Handout')
        f.set(self, value, raw=True, **kwargs)
        self.setHandoutView(value)
    def setHandoutView(self,value):
        if (self.UpdateSlideText):
            f = self.getField('HandoutView')
            text = self.getRawHandout()
            type = self.Handout.getContentType()
            value = self.transformText(type, text, 'handout')
            f.set(self, value)    
    def setSlideReference(self, value, **kwargs):
        '''set slide reference'''
        f = self.getField('SlideReference')
        f.set(self, value, raw=True, **kwargs)
        self.setSlideReferenceView(value)
    def setSlideReferenceView(self,value):
        if (self.UpdateSlideText):
            f = self.getField('SlideReferenceView')
            text = self.getRawSlideReference()
            type = self.SlideReference.getContentType()
            value = self.transformText(type, text, 'reference')
            f.set(self, value)    
    def setSlideImageW(self):
        # only works for image for the moment
        value = self.getSlideImage()
        #calc heigth and width
        if (value):
            f = self.getField('SlideImageWWW')
            f.set(self, value)
        if (EXPLANATION_FIG):
            value = self.getExplanationImage()
            #calc heigth and width
            if (value):
                f = self.getField('ExplanationImageWWW')
                f.set(self, value)
        self.changed = False
        
    security.declarePublic('imageHasChanged')
    def imageHasChanged(self):
        return self.changed
    security.declarePublic('getSlideImageFactor')
    def getSlideImageFactor(self, maxw, maxh, fieldname):
        #ct, width, heigth = getImageInfo(self.getSlideImage())
        #value = self.getSlideImage()
        #calc heigth and width
        #f = self.getField('SlideImageWWW')
        #f.set(self, value)
        f = self.getField(fieldname)
        #w = f.getAttr(self, 'width')
        width, heigth = f.getSize(self)
        #width = 350
        #heigth = 120
        if width > maxw or \
                       heigth > maxh:
                    factor = min(float(300)/float(width),
                                 float(300)/float(heigth))
        else:
            factor = 1
        
        return factor
        #return w
    def getImage(self):
        return 1, 1
    
    security.declarePrivate('initializeObject')
    def initializeObject(self):
        self.tryWorkflowAction("publish", ignoreErrors=True)
        parent = aq_parent(self)
        parent.orderObjects("id")
        parent.plone_utils.reindexOnReorder(parent)
        #self.reindexObject()
        self.changed = True
        self.renderImages()
    def editedObject(self, objtype=None):
        parent = aq_parent(self)
        parent.editedObject()
        self.renderImages()
    def renderImages(self):
        self.renderMainImage()
        if (EXPLANATION_FIG):
            self.renderExplanationImage()
        self.setSlideImageW()
    def setChanged(self, ch):
        #self.changed = ch
        lec = aq_parent(self)
        lec.setChanged(True)
        
    def setChanged(self, ch):
        #self.changed = ch
        lec = aq_parent(self)
        lec.setChanged(True)
        tut = aq_parent(lec)
        tut.setChanged(True)    
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
    
    def haveChanged(self):
        self.changed = True
        self.renderImages()
    security.declareProtected(View, 'transformSlideText')
    def transformSlideText(self, val):
        type = self.SlideText.getContentType()
        data = self.transformText(type, val, 'slidetext')
        self.setSlideTextView(data)
    security.declareProtected(View, 'updateTransformableText')
    def updateTransformableText(self):
        #use loop to go through everything...
        type = self.SlideText.getContentType()
        transformtext =  self.getRawSlideText()
        data = self.transformText(type, transformtext, 'slidetext')
        #self.setSlideTextView(data)
        f = self.getField('SlideTextView')
        f.set(self, data)  
        #self.SlideTextView.setContentType(self, 'text/html')
        type = self.Explanation.getContentType()
        transformtext =  self.getRawExplanation()
        data = self.transformText(type, transformtext, 'explanation')
        self.setExplanationView(data)
        #self.ExplanationView.setContentType(self, 'text/html')
        type = self.Details.getContentType()
        transformtext =  self.getRawDetails()
        data = self.transformText(type, transformtext, 'details')
        self.setDetailsView(data)
        #self.DetailsView.setContentType(self, 'text/html')
        type = self.Examples.getContentType()
        transformtext =  self.getRawExamples()
        data = self.transformText(type, transformtext, 'examples')
        self.setExamplesView(data)
        #self.ExamplesView.setContentType(self, 'text/html')
        type = self.Alternative.getContentType()
        transformtext =  self.getRawAlternative()
        data = self.transformText(type, transformtext, 'alternative')
        self.setAlternativeView(data)
        #self.AlternativeView.setContentType(self, 'text/html')
        type = self.Handout.getContentType()
        transformtext =  self.getRawHandout()
        data = self.transformText(type, transformtext, 'handout')
        self.setHandoutView(data)
        #self.HandoutView.setContentType(self, 'text/html')
        type = self.SlideReference.getContentType()
        transformtext =  self.getRawSlideReference()
        data = self.transformText(type, transformtext, 'reference')
        self.setSlideReferenceView(data)
        #self.SlideReferenceView.setContentType(self, 'text/html')
    security.declareProtected(View, 'transformText')
    def transformText(self, type, text, origin):
        
        trans = getToolByName(self, 'portal_transforms')
        
        data = trans.convertTo('text/html', text, mimetype=type, usedby=self)
        objects = data.getSubObjects()
        #mobj = data.getMetadata()['fileName']
        #for d in mobj:
        #    mobj = 'bla'
        counter = 0
        for x in objects:
            if hasattr(self, x):
                self.manage_delObjects([x])
            if hasattr(self, origin+x):
                self.manage_delObjects([origin+x])
            self.manage_addImage(origin+x, objects[x])
           
            container = self[origin+x]
            counter = counter + 1
            #tempname = container.getTitle()
            #container.setTitle('bla')
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
    def isImageFormat(self):
        image_type = self.getSlideimageFormat()
        if (image_type == 'image'):
            return True
        else:
            return False
    def renderMainImage(self):
        # should add checkes for if it empy, try, except code as well...
        image_type = self.getSlideImageFormat()
        rendered_image = 'DELETE_IMAGE'
        text = self.getSlideImageText()
        im = self.getSlideImage()
        if (im and (image_type != 'image')):
            self.setSlideImage(rendered_image)
        if ((len(text) > 0) and ((image_type == 'image') or (image_type == 'none'))):
            self.setSlideImageText('')
        
        if (image_type == 'fig'):
            rendered_image = self.renderImage(text,'fig2dev -L png', '')
            
        elif (image_type == 'gnuplot'):
            HEADER = 'set terminal png color\n'
            rendered_image = self.renderImage(text, 'gnuplot', HEADER)
        elif (image_type == 'r'):
            
            #HEADER = 'png(file="/dev/stdout")\r\n'
            HEADER = 'bitmap(file="/dev/stdout")\r\n'
            #rendered_image = self.renderImage(text, 'R --slave', HEADER)
            rendered_image = self.renderRQuestion(text, HEADER)
           
        else:
            ''' do nothing for the moement '''
        if (image_type != 'image'):
            if (rendered_image != 'FAILURE'):
                try:
                    self.setSlideImage(rendered_image)
                    return True
                except:
                    return False
            else:
                return False
        else:
            ''' Return true if image type is png, jpeg, gif - no rendering needed.'''
            return True
    def renderExplanationImage(self):
        # should add checkes for if it empy, try, except code as well...
        image_type = self.getExplanationImageFormat()
        text = self.getExplanationImageText()
        rendered_image = 'DELETE_IMAGE'
        im = self.getExplanationImage()
        if (im and (image_type != 'image')):
            self.setExplanationImage(rendered_image)
        if ((len(text) > 0) and ((image_type == 'image') or (image_type == 'none'))):
            self.setExplanationImageText('')
        
        if (image_type == 'fig'):
            rendered_image = self.renderImage(text, 'fig2dev -L png', '')    
        elif (image_type == 'gnuplot'):
            HEADER = 'set terminal png color\n'
            rendered_image = self.renderImage(text, 'gnuplot', HEADER)
        elif (image_type == 'r'):
            #HEADER = 'postscript(file="/dev/stdout")\r\n'
            #HEADER = 'png(file="/dev/stdout")\r\n'
            HEADER = 'bitmap(file="/dev/stdout")\r\n'
            #rendered_image = self.renderImage(text, 'R --slave', HEADER)
            rendered_image = self.renderRQuestion(text, HEADER)

            #if (rendered_image != 'DELETE_IMAGE'):
            #    rendered_image = twutils.ps2png(rendered_image)
        else:
            ''' do nothing for the moement '''
        if (image_type != 'image'):
            if (rendered_image != 'FAILURE'):
                self.setExplanationImage(rendered_image)
                return True
            else:
                return False
        else:
            return True
    
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
            return 'FAILURE'
        try:
            mainimage = mainimagefile.read()
        except:
            '''could not read from image file???'''
            return 'FAILURE'
        mainimagefile.close()
        #try:
        #    if (mainimage):
        #        self.setQuestionImage(mainimage)
        #    else:
        #        self.setQuestionImage('DELETE_IMAGE')
                
        #except:
        #    '''????'''

        #if (render is True):
        #    s = s.split("|")
        #else:
        #    s = questiontext.split("|")
           
        
        #remove temporary directories created by the use of tempfile
        # and close file
        os.close(png_fd)
        try:
            shutil.rmtree(tmpout, True)
            if (setdatafiles):
                shutil.rmtree(tmpout1, True)
        except OSError, (errno, strerror):
            print "tutorial pdf:(shutil.rmtree %s) OSError[%s]: %s" % \
                     (tmpout, errno, strerror)  
            
        
        if (mainimage):
            return mainimage
        else:
            return 'DELETE_IMAGE'
    def renderImage(self, image_text, cmd, header):
        if (len(image_text) > 0):
            # this is only for text?? does it work for files as well??
            # if isinstance(text, FileUpload):
            #       text = text.read()
            madetemp = 0
            if (cmd ==  'R --slave'):
                '''r transformation'''
                # must check for extra data
                if ('read' or 'source' in image_text):
                    tmpout = tempfile.mkdtemp()
                    madetemp = 1
                  
                    parent = aq_parent(self)
                    extradata = parent.getAllExtraFiles()
                    for ext in extradata:
                        extra = ext.getObject()
                        filename = extra.getTitle()
                        extraid = extra.getId()
                        f = open(tmpout+'/'+extraid,'w')
                        text = str(extra.getField('file').get(extra).data)
                        for ex in extradata:
                            extobj = ex.getObject()
                            extid = extobj.getId()
                            if (extid in text):
                                text = text.replace(extid, '/'+tmpout+'/'+extid)
                        f.write(text)
                        f.close()
                           
                        if (extraid in image_text): 
                            # Only works if extra data is a file!
                            text = str(extra.getField('file').get(extra).data)  
                            image_text = image_text.replace(extraid, '/'+tmpout+'/'+extraid)
                                
            if (cmd ==  'fig2dev -L png' or cmd == 'fig2dev -L eps'):
                parent = aq_parent(self)
                extradata = parent.getAllExtraFiles()
                tmpout = tempfile.mkdtemp()
                madetemp = 1
                for ext in extradata:
                    extra = ext.getObject()
                    filename = extra.getTitle()
                    extraid = extra.getId()
                    if (extraid in image_text):
                        f = open(tmpout+'/'+extraid,'w')
                        text = str(extra.getField('file').get(extra).data) 
                        f.write(text)
                        f.close()
                        image_text = image_text.replace(extraid, '/'+tmpout+'/'+extraid)
                    
            try:
                stdin, stdout = os.popen2(cmd)
            except:
                return 'FAILURE'
            try:
                stdin.write(header)
            except:
                return 'FAILURE'
            try:
                stdin.write(image_text)
            except:
                return 'FAILURE'
            try:
                stdin.flush()
            except:
                return 'FAILURE'
            try:
                stdin.close()
            except:
                return 'FAILURE'
            try:
                rendered_image = stdout.read()
            except:
                return 'FAILURE'
            try:
                stdout.flush()
            except:
                return 'FAILURE'
            try:
                stdout.close()
            except:
                return 'FAILURE'
                #return rendered_image
            if (madetemp == 1):
                self.cleanDir(tmpout)
            return rendered_image
            
        else:
            return 'DELETE_IMAGE'
        
    def getTableMain(self):
        return ['SlideText', 'SlideImage']
    def getTableExplanation(self):
        return ['Explanation', 'ExplanationImage']
    security.declareProtected(View, 'cleanDir')
    def cleanDir(self, tmpout):
        '''remove temporary directories created by the use of tempfile'''
        try:
            shutil.rmtree(tmpout, True)
        except OSError, (errno, strerror):
            print "tutorial pdf:(shutil.rmtree %s) OSError[%s]: %s" % \
                              (tmpout, errno, strerror)   


    security.declareProtected(View, 'canEdit')
    def canEdit(self):
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
            '''failed to ascertain who the user is.'''
            return 0
# Register this type in Zope
if PLONE_VERSION == 3:
    registerATCTLogged(Slide)
else:
    atapi.registerType(Slide, PROJECTNAME)
