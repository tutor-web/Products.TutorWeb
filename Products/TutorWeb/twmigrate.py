import sys
from os import listdir
import re
from Products.Archetypes.utils import make_uuid
from Products.CMFCore.utils import getToolByName
#########################
## remember to publish content!!!!!!!!!!!!!!!!!!!!!
##  workflow_tool = getToolByName(self, 'portal_workflow')
 ## wtool = self.portal_workflow
##         wf = wtool.getWorkflowsFor(self)[0]
##         if wf.isActionSupported(self, action):
##             if comment is None:
##                 userId = getSecurityManager().getUser().getId()
##                 comment = 'State changed by ' + userId
##             wtool.doActionFor(self, action, comment=comment)
##         elif not ignoreErrors:
##             raise TypeError('Unsupported workflow action %s for object %s.'
##                             % (repr(action), repr(self)))

##################################################
# this should be changed to endswith
isdep_re = re.compile('(.*)\.dep')
def isdep(s):
	return isdep_re.match(s) is not None
istut_re = re.compile('\d{4}(.*)')
def istut(s):
	return istut_re.match(s) is not None
islect_re = re.compile('lecture\d{2}')
def islect(s):
	return islect_re.match(s) is not None
isslide_re = re.compile('sl\d{2}')
def isslide(s):
	return isslide_re.match(s) is not None
# must have at least two digits after Q, will reject Q1
isquestion_re = re.compile('Q\d{2}')
def isquestion(q):
	return isquestion_re.match(q) is not None
def isa(s):
	return s == 'A'

def isd(s):
	return s == 'D'

def ise(s):
	return s == 'E'

def ish(s):
	return s == 'H'

def hasExtra(s):
	if (s == 'D'):
		return 'detail'
	elif (s == 'E'):
		return 'example'
	elif (s == 'H'):
		return 'homework'
	elif (s == 'A'):
		return 'alternative'
	else:
		return ''
def hasImage(ldir, imagename):
	images = []
	for f in ldir:
		m = re.match(imagename, f)
		if (m is not None):
			images.append(f)
	for i in images:
		extension = isImage(i)
		if (extension):
			return i, extension, 'image'
		extension = isTextImage(i)
		if (extension):
			return i, extension, 'text'
	return 0, 0, 0
		    

def isImage(im):
	extension = im.split('.')[1]
	if (extension == 'png' or extension == 'gif' or extension == 'jpg'):
		return extension
	else:
		return 0
def isTextImage(im):
	extension = im.split('.')[1]
	if (extension == 'fig' or extension == 'r' or extension == 'gnuplot' or extension == 'plt'):
		if (extension == 'plt'):
			extension = 'gnuplot'
		return extension
	else:
		return 0

#ishtml_re = re.compile('<([A-Z][A-Z0-9]*)\b[^>]*>(.*?)</\1>')(.*)>(.*)<\/(.*)>'
# this is a bit crude!!!
ishtml_re = re.compile('<(.*)>(.*)<\/(.*)>')
def hasHtml(inputtext):
	return ishtml_re.match(inputtext) is not None	
	
def setText(extrapath, filename, obj):
	texttype = 'text/plain'
	text = ''
	try:
		textfile = open(extrapath+filename+'.tex', 'r')
		text = textfile.read()
		texttype = 'text/x-tex'
		textfile.close()
	except:
		try:
			textfile = open(extrapath+filename+'.txt', 'r')
			text = textfile.read()
			# check if text containts html
			if (hasHtml(text)):
				texttype = 'text/html'
			else:	
				texttype = 'text/plain'
			textfile.close()
		except:
			text = ''
	setContent(obj, text, filename, texttype)
def setContent(obj, text, contenttype, texttype):
	if (contenttype == 'detail'):
		obj.setDetails(text, mimetype=texttype)
	elif (contenttype == 'example'):
		obj.setExamples(text, mimetype=texttype)
	elif (contenttype == 'homework'):
		obj.setHandout(text, mimetype=texttype)
	elif (contenttype == 'alternative'):
		obj.setAlternative(text, mimetype=texttype)
	else:
		obj.setDetails(contenttype, mimetype='text/plain')
		
def twmigrate(self, twpath='/home/audbjorg/work-gunnar/tutor-web/twdata'):
    # for publishing new content
    workflow_tool = getToolByName(self, 'portal_workflow')
    container = self
    dep = 'The deps are: '
    for i in filter(isdep,listdir(twpath)):
        #depid = 'newdep'
        #container.invokeFactory('Department', depid)
        depid = i
        # the title should be found in the dep.info.txt
        try:
            titlefile = open(twpath + '/' + i + '/dep.info.txt', 'r')
            title = titlefile.read()
            title = title.split('%')[0]
            titlefile.close()
        except:
            title = 'depid'
        container.invokeFactory('Department', depid)
        DepObj = getattr(container, depid)
        DepObj.setTitle(unicode(title, 'latin-1'))
      
	comment = 'Publishing department content'
	action = 'publish'
	try:
	     workflow_tool.doActionFor(DepObj, action, comment=comment)
	except:
             raise TypeError('Unsupported workflow action %s for object %s.'
                           % (repr(action), repr(DepObj)))
	DepObj.reindexObject()
        #next set the tutorials
        for j in filter(istut,listdir(twpath+'/'+i)):
             # set id, title, author, lang, courseno, reference and trailer
             tutorialpath = twpath+'/'+i+'/'+j+'/'
             try:
                 titlefile = open(tutorialpath+'/course/titleline.txt', 'r')
                 title = titlefile.read()
                 title = title.strip()
                 titlefile.close()
             except:
                 title = 'no title found'
             tutid = j
             DepObj.invokeFactory('Tutorial', tutid)
             TutObj = getattr(DepObj, tutid)
             TutObj.setTitle(unicode(title, 'latin-1'))
             try:
                 authorfile = open(tutorialpath+'course/author.txt', 'r')
                 author = authorfile.read()
                 author = author.strip()
                 author = unicode(author,'latin-1')
                 authorfile.close()
             except:
                 author = ''
             TutObj.setAuthor(author)
             info = ''
             try:
                 infofile = open(tutorialpath+'course/tutorial.info.txt', 'r')
                 info = infofile.read()
                 info = info.split("%")
                 lang = info[0]
                 coursename = info[2]
                 infofile.close()
             except:
                 lang = 'NN'
                 coursename = 'NN'
             courseno=tutid[0:3] + '.' + tutid[3]
             coursename = coursename + courseno
             TutObj.setTutorialLanguage(lang)
             TutObj.setTutorialCode(coursename)
	     try:
                 trailerfile = open(tutorialpath+'course/trailer.tex', 'r')
                 trailer = trailerfile.read()
                 trailer = trailer.strip()
                 trailerfile.close()
             except:
                 trailer = ''
	     TutObj.setTrailer(trailer, mimetype='text/x-tex')
             try:
                 referencefile = open(tutorialpath+'course/reference.txt', 'r')
                 reference = referencefile.read()
                 reference = reference.strip()
                 referencefile.close()
             except:
                 reference = ''
             TutObj.setTutReference(reference, mimetype='text/plain')
             
            
           
	     comment = 'Publishing tutorial content'
	     action = 'publish'
	     try:
	         workflow_tool.doActionFor(TutObj, action, comment=comment)
	     except:
	         raise TypeError('Unsupported workflow action %s for object %s.'
                           % (repr(action), repr(TutObj)))
	     TutObj.reindexObject()
             for k in filter(islect,listdir(twpath+'/'+i+'/'+j)):
                 # set id, title, reference 
                 lecturepath = twpath+'/'+i+'/'+j+'/'+k+'/'
                 try:
                     titlefile = open(lecturepath+'general/titleline.txt', 'r')
                     title = titlefile.read()
                     title = title.strip()
                     titlefile.close()
                 except:
                     title = 'no title found for lecture'
		 lecid = k
                 TutObj.invokeFactory('Lecture', lecid)
                 LecObj = getattr(TutObj, lecid)
                 LecObj.setTitle(unicode(title, 'latin-1'))
                 try:
                     referencefile = open(lecturepath+'general/reference.txt', 'r')
                     reference = referencefile.read()
                     reference = reference.strip()
                     referencefile.close()
                 except:
		     reference = ''
                 LecObj.setLecReference(reference, mimetype='text/plain')
                
		 comment = 'Publishing lecture content'
		 action = 'publish'
		 try:
		     workflow_tool.doActionFor(LecObj, action, comment=comment)
		 except:
		     raise TypeError('Unsupported workflow action %s for object %s.'
                           % (repr(action), repr(LecObj)))
	         LecObj.reindexObject()
		 # set the slides
                 for l in filter(isslide, listdir(twpath+'/'+i+'/'+j+'/'+k)):
                     # set id, title, main, explanation text and images, reference
                     # and Details, Examples, Alternative and Handout
                     slidepath = twpath+'/'+i+'/'+j+'/'+k+'/'+l+'/'
                     try:
                         titlefile = open(slidepath+'titleline.txt', 'r')
                         title = titlefile.read()
                         title = title.strip()
                         titlefile.close()
                     except:
                         title = 'no title found for slide'
                     slid = l
                     LecObj.invokeFactory('Slide', slid)
                     SlObj = getattr(LecObj, slid)
                     SlObj.setTitle(unicode(title, 'latin-1'))
                     maintexttype = 'text/plain'
                     explanationtexttype = 'text/plain'
		     maintext = ''
		     explanationtext = ''
                     try:
                         maintextfile = open(slidepath+'text.tex', 'r')
                         maintext = maintextfile.read()
                         maintexttype = 'text/x-tex'
                         maintextfile.close()
                     except:
                         try:
                             maintextfile = open(slidepath+'text.txt', 'r')
                             maintext = maintextfile.read()
                             maintexttype = 'text/plain'
                             maintextfile.close()
                         except:
                             maintext = ''
                     SlObj.setMain_text(maintext, mimetype=maintexttype)
                     try:
                         explanationtextfile = open(slidepath+'expln.tex', 'r')
                         explanationtext = explanationtextfile.read()
                         explanationtexttype = 'text/x-tex'
                         explanationtextfile.close()
                     except:
                         try:
                             explanationtextfile = open(slidepath+'expln.txt', 'r')
                             explanationtext = explanationtextfile.read()
                             explanationtexttype = 'text/plain'
                             explanationtextfile.close()
                         except:
                             explanationtext = ''
                   ##   maintext = ''   
                     
                     SlObj.setExplanation_text(explanationtext, mimetype=explanationtexttype)
                     # now set the images if any
		     im, extension, imtype = hasImage(listdir(slidepath), 'base.')
		     if (im):
		          if (imtype == 'text'):
			     #has base image with format: plt, fig, r, gnuplot
			     # imagetype: fig,gnuplot, r
			     SlObj.setMain_imagetype(extension)
			     mainimagefile = open(slidepath+im, 'r')
			     mainimage = mainimagefile.read()
			     SlObj.setText_main_image_body(mainimage, mimetype='text/plain')
			     mainimagefile.close()
			  else:
			     # has a base image with format: png, gif or jpg
			     #extension = im.split('.')[1]
			     mime = 'image/'+extension
			     mainimagefile = open(slidepath+im, 'r')
			     mainimage = mainimagefile.read()
			     SlObj.setMain_upload_image(mainimage, mimetype=mime)
			     SlObj.setMain_imagetype('image')
			     mainimagefile.close()	  


				  
			    
		     im, extension, imtype = hasImage(listdir(slidepath), 'expln.')
		     if (im):
		          if (imtype == 'text'):
			     #has base image with format: plt, fig, r, gnuplot
			     # imagetype: fig,gnuplot, r
			     SlObj.setExplanation_imagetype(extension)
			     mainimagefile = open(slidepath+im, 'r')
			     mainimage = mainimagefile.read()
			     SlObj.setText_explanation_image_body(mainimage, mimetype='text/plain')
			     mainimagefile.close()
			  else:
			     # has a base image with format: png, gif or jpg
			     #extension = im.split('.')[1]
			     mime = 'image/'+extension
			     mainimagefile = open(slidepath+im, 'r')
			     mainimage = mainimagefile.read()
			     SlObj.setExplanation_upload_image(mainimage, mimetype=mime)
			     SlObj.setExplanation_imagetype('image')
			     mainimagefile.close()
		     # now set the extra material: details, examples, homework/handout, alternative
		     for m in listdir(slidepath):
			     if (m == 'D'):
				     extra = 'detail'
			     elif (m == 'E'):
				     extra = 'example'
			     elif (m == 'H'):
				     extra = 'homework'
			     elif (m == 'A'):
				     extra = 'alternative'
			     else:
				     extra = 'noextra'
			     if (not(extra == 'noextra')):
				     setText(slidepath+m+'/', extra, SlObj)
			    
                     #at last set the slide reference if any
		     texttype = 'text/plain'
		     text = ''
		     try:
			     textfile = open(slidepath+'reference.tex', 'r')
			     text = textfile.read()
			     texttype = 'text/x-tex'
			     textfile.close()
			     SlObj.setSlideReference(text, mimetype=texttype)
                     except:
			     try:
				     textfile = open(slidepath+'reference.txt', 'r')
				     text = textfile.read()
				     texttype = 'text/plain'
				     textfile.close()
				     SlObj.setSlideReference(text, mimetype=texttype)
			     except:
				     text = ''
                    
                   
		     comment = 'Publishing slide content'
		     action = 'publish'
		     try:
			     workflow_tool.doActionFor(SlObj, action, comment=comment)
		     except:
			     raise TypeError('Unsupported workflow action %s for object %s.'
                           % (repr(action), repr(SlObj)))
		     SlObj.reindexObject()
		 #set the questions - r questions not implemented yet
		 for q in filter(isquestion, listdir(twpath+'/'+i+'/'+j+'/'+k)):
                     # set id, title, main, explanation text and images, reference
                     # and Details, Examples, Alternative and Handout
                     questionpath = twpath+'/'+i+'/'+j+'/'+k+'/'+q+'/'
                     question = q
                     LecObj.invokeFactory('TutorWebQuestion', question)
                     QueObj = getattr(LecObj, question)
                     maintexttype = 'text/plain'
                     explanationtexttype = 'text/plain'
		     maintext = ''
		     
                     try:
                         maintextfile = open(questionpath+'question.tex', 'r')
                         maintext = maintextfile.read()
                         maintexttype = 'text/x-tex'
                         maintextfile.close()
                     except:
                         try:
                             maintextfile = open(questionpath+'question.txt', 'r')
                             maintext = maintextfile.read()
                             maintexttype = 'text/plain'
                             maintextfile.close()

			 except:
				 try:
					 maintextfile = open(questionpath+'question.r', 'r')
					 maintext = maintextfile.read()
					 maintexttype = 'text/r'
					 maintextfile.close()
				 except:
					 maintext = ''
                     QueObj.setQuestion(maintext, mimetype=maintexttype)
		     QueObj.setPoints(1)
		     ### forgot the points and reindex????
		    
		     comment = 'Publishing question content'
		     action = 'publish'
		     try:
		         workflow_tool.doActionFor(QueObj, action, comment=comment)
		     except:
		         raise TypeError('Unsupported workflow action %s for object %s.'
                           % (repr(action), repr(QueObj)))
		     QueObj.reindexObject()
		     # Now must set the answers - presuming they are text
		     # Always have three answers (a, b, c and a i correct)
		     answers = [questionpath+'a', questionpath+'b', questionpath+'c']
		     for a in answers:
			     ans = make_uuid()
			     QueObj.invokeFactory('TutorWebAnswer', ans)
			     AnsObj = getattr(QueObj, ans)
			     answertext = ''
			     answertexttype = 'text/plain'
			     try:
				     answertextfile = open(a, 'r')
				     answertext = answertextfile.read()
				     answertexttype = 'text/plain'
				     answertextfile.close()
				     
				     
			 
		             except:
				     answertext = 'No answer found'
				     answertextype = 'text/plain'
			     AnsObj.setAnswer(answertext, mimetype=answertexttype)
			     if (a == (questionpath+'a')):
				 AnsObj.setCorrect(True)
			   
			     comment = 'Publishing answer content'
			     action = 'publish'
			     try:
				     workflow_tool.doActionFor(AnsObj, action, comment=comment)
			     except:
				     raise TypeError('Unsupported workflow action %s for object %s.'
						     % (repr(action), repr(AnsObj)))
			     AnsObj.reindexObject()
        dep = dep + i
    return 'the path is: ' + twpath + 'and ' + dep
    
