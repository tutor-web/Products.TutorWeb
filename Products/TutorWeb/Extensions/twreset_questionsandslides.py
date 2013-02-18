import sys
from os import listdir
import re
from Products.Archetypes.utils import make_uuid
from Products.CMFCore.utils import getToolByName
import tempfile
import os
from htmlentitydefs import entitydefs




# The main migrate function
# by default files are used from path = twpath
def twreset_questionsandslides(self):
    # transform all content for all lecs/slides/questions.
   
    # create a tempfile for logging
    # careful this file is not automatically removed
    #logdir ='/tmp'
    #if (not (os.path.exists(logdir))):
    #    os.mkdir(logdir)
    #tex_fd, tex_absname = tempfile.mkstemp(dir=logdir, suffix='.twedit_questions')
    
    
    container = self
    lectureids = container.getFolderContents(contentFilter={"portal_type": "Lecture"})
    
    for lec in lectureids:
        
            l = lec.getObject()
	    slideids  = l.getFolderContents(contentFilter={"portal_type": "Slide"})
	    
	    questionids = l.getFolderContents(contentFilter={"portal_type": "TutorWebQuestion"})
	     # set the slide
	    for s in slideids:
                'bla bla'
		SlObj = s.getObject() 
                SlObj.editedObject()
                SlObj.updateTransformableText()
                SlObj.reindexObject()
            for q in questionids:
                QueObj = q.getObject() 
                QueObj.editedObject()
                QueObj.reindexObject()
	
	
	
    return 'finished transforming latex text on slides and questions ' + str(len(lectureids)) + ", " + str(len(slideids)) + ', ' + str(len(questionids))
