import sys
from os import listdir
import re
from Products.Archetypes.utils import make_uuid
from Products.CMFCore.utils import getToolByName
import tempfile
import os
from htmlentitydefs import entitydefs

#########################
## REMEMBEr
## must import acknowledgetment data !!!
## must import extra data for lectures such as base.r and...
## must make course public
## must change how course is set, check if already there with same id
## the method now is good if importing department not tutorial
## must check if should put the acknowledgement thingies public or ok for anonymous
## ********************************************************
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

# search strings used to locate different tutor-web content
# from directory - using regular expressions
# this should be changed to endswith
isdep_re = re.compile('(.*)\.dep')
def isdep(s):
	return isdep_re.match(s) is not None
isack_re = re.compile('(^sponsor)(.*)(\.(png|jpg|gif|url|txt))$')
def isacknowledgement(s):
	return isack_re.match(s) is not None
istut_re = re.compile('\d{3}(.*)')
def istut(s):
	return istut_re.match(s) is not None
islect_re = re.compile('lecture\d{2}')
def islect(s):
	return islect_re.match(s) is not None
isslide_re = re.compile('sl\d{2}')
def isslide(s):
	return isslide_re.match(s) is not None

# need to find all files which end with *.r and *.dat and *.ind but
# are not base.r and expln.r
# must have at least two digits after Q, will reject Q1
isquestion_re = re.compile('Q\d{2}')

# regular expressions to find <pre>, * or space
#ishtml_re = re.compile('<([A-Z][A-Z0-9]*)\b[^>]*>(.*?)</\1>')(.*)>(.*)<\/(.*)>'
# this is a bit crude!!!
#ishtml_re = re.compile('<(.*)>(.*)<\/(.*)>')
#ishtml_re = re.compile('<\/?[^>]+>')
ishtml_re = re.compile('<pre>')
startwith_re = re.compile('^\*')
isstruct_re = re.compile('^\*|\n\*|\n\s\*')
hasSpace_re = re.compile('^\*\s')

# functions which return true or false depending on the regular expresision
# gathered from the above functions
def isquestion(q):
	return isquestion_re.match(q) is not None
def isanswer(a):
	if (a == 'a' or a == 'b' or a == 'c' or a == 'd.true' or a=='d.false'):
		return True
	else:
		return False
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
		extension = isTextImage(i)
		if (extension):
			return i, extension, 'text'
	for i in images:
		extension = isImage(i)
		if (extension):
			return i, extension, 'image'
	return 0, 0, 0
		    
# return true if im has extension png, jpg or gif format else false
# x.png, x.jpg, x.gif
def isImage(im):
	extension = im.split('.')[1]
	if (extension == 'png' or extension == 'gif' or extension == 'jpg'):
		return extension
	else:
		return 0
# return true if im has fig, r, gnuplot or plt as and extension else false.
# x.fig, x.r, x.gnuplot, x.plt
def isTextImage(im):
	ext = im.split('.')
	if (len(ext) > 1):
		extension = ext[1]
		if (extension == 'fig' or extension == 'r' or extension == 'gnuplot' or extension == 'plt'):
			if (extension == 'plt'):
				extension = 'gnuplot'
			return extension
		else:
			return 0
	else:
		return 0


# if contains <pre> return true else false
def hasHtml(inputtext):
	return ishtml_re.search(inputtext) is not None	
	
# if starts with * return tru else false
def hasStructured(inputtext):
	return isstruct_re.search(inputtext) is not None	

# format text as structured	
def setStructuredText(inputtext):
    
    lines = inputtext.split('\n')
    tempstr = ''
    
    for l in lines:
        if (startwith_re.search(l) != None):
		if ((hasSpace_re.search(l) == None)):
                   if (len(l) > 1):
			   l = '\n' + l[0] + ' ' + l[1:] + '\n'
		   else:
			   l = '\n' + l[0] + ' ' + '\n'
                else:
                   l = '\n' + l + '\n'
	tempstr = tempstr + l + '\n'
    return tempstr
        
# set content from file: extrapath/filename depending on which format
# file.tex, file.txt and set correct content type such as
# latex, structureed or plain text
def setText(extrapath, filename, obj):
	texttype = 'text/latex'
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
			# check if text containts html or *
			if (hasStructured(text)):
                                text = setStructuredText(text)
				texttype = 'text/structured'
			elif (hasHtml(text)):
				texttype = 'text/structured'
			
			else:	
				texttype = 'text/plain'
			textfile.close()
		except:
			text = ''
	if not isinstance(text, unicode):
            text1 = text.decode('latin-1').encode('utf-8')
	else:
            text1 = text.encode('utf-8')
	setContent(obj, text1, filename, texttype)

# set appropriate content depending on:
# detailo, example, homework, alternative
def setContent(obj, text, contenttype, texttype):
	if (contenttype == 'detail'):
		if (text == 'No details exist for this slide\n'):
			text = ''
                obj.setDetails(text, mimetype=texttype)
	elif (contenttype == 'example'):
		if (text == 'No examples exist for this slide\n'):
			text = ''
		obj.setExamples(text, mimetype=texttype)
	elif (contenttype == 'homework'):
		if (text == 'No homework exist for this slide\n'):
			text = ''
		obj.setHandout(text, mimetype=texttype)
	elif (contenttype == 'alternative'):
		if (text == 'No alternative slides exist for this slide\n'):
			text = ''
		obj.setAlternative(text, mimetype=texttype)
	else:
		'''do nothing'''
# try to set workflow-action = action for object=obj
def tryWorkflowAction(obj, action, ignoreErrors=False, comment=None):
    wtool = obj.portal_workflow
    wf = wtool.getWorkflowsFor(obj)[0]
    if wf.isActionSupported(self, action):
        if comment is None:
            #userId = getSecurityManager().getUser().getId()
            comment = 'State changed' 
	wtool.doActionFor(obj, action, comment=comment)
    elif not ignoreErrors:
        raise TypeError('Unsupported workflow action %s for object %s.'
                            % (repr(action), repr(obj)))  
# create a new object in obj with type
def createNewObject(type, obj):
    """Create a new object of type = type and initialize it."""
        
    typeName = 'type'
    id=obj.generateUniqueId(typeName)
    if obj.portal_factory.getFactoryTypes().has_key(typeName):
        o = obj.restrictedTraverse('portal_factory/' + typeName + '/' + id)
    else:
        newId = obj.invokeFactory(id=id, type_name=typeName)
	if newId is None or newId == '':
            newId = id
	o=getattr(obj, newId, None)
	id = newId
    
    if o is None:
        raise Exception
       
    o = obj.portal_factory.doCreate(o, id)
    
    tryWorkflowAction(o, "publish", ignoreErrors=True)
    o.reindexObject()

# find extra data which should be of type ExtraDataFile and add then to object
def addFiles(object, path, text, extrafiles, logfile):
    for f in listdir(path):
        if (f in text and (not(os.path.isdir(path+f)))):
            '''should add file to extra data'''
	    if (f in extrafiles):
                '''object already contains f'''
		os.write(logfile, 'trying to add extra data file to lecture which is already there ' + path + '/' + f + '\n')
	    else:
                extrafiles.append(f)
		try:
                    extrafile = open(path+f, 'r')
		    filetext = extrafile.read()
		    extrafile.close()
		    try:
                        object.invokeFactory('ExtraDataFile', f)
		    except:
                        os.write(logfile, 'could not invoke factory for file object in lecture ' + path + '\n')
		    try:
                        FileObj = getattr(object, f)
		    except:
                        os.write(logfile, 'could not getattr for fileobj in lecture ' + path + '\n')
		    try:
                        FileObj.setTitle(f)
		    except: 
                        os.write(logfile, 'could not settitle for fileobj in lecture ' + path + '\n')
		    try:
                        FileObj.setFile(filetext)
		    except:
			    os.write(logfile, 'could not set text for fileobj in lecture ' + path + '\n')
		    FileObj.reindexObject()
		    os.write(logfile, 'added extra data file ' + f + ' to lecture ' + path + '\n')
		    try:
                        extrafiles = addFiles(object, path, filetext, extrafiles, logfile)
		    except:
                        os.write(logfile, 'failed to call function addFiles for file ' + path+f + '\n')
     	 
		except:
                    '''what to do'''
		    os.write(logfile, 'failed to find file, ' +path+f+' in lecture\n')
    return extrafiles

# The main migrate function
# by default files are used from path = twpath
def twmigrate(self, twpath='/home/audbjorg/tutor-web/twmigrate/tutorials'):
    # for publishing new content
    workflow_tool = getToolByName(self, 'portal_workflow')
    container = self
    dep = 'Tutorials: '
    # create a tempfile for logging
    # careful this file is not automatically removed
    logdir = twpath + '/log'
    if (not (os.path.exists(logdir))):
        os.mkdir(logdir)
    tex_fd, tex_absname = tempfile.mkstemp(dir=logdir, suffix='.twmigrate_tutorial')
    
    
    #start by setting the courses
    	# id [xxxx][shorttitle]
	# tutidPattern = re.compile(r'^(\d*)(.*)')
	# tutidPattern.search(j).groups(),  tutidPattern[0] = leading digits
	#                                   tutidPattern[1] = rest of string
    tutidPattern = re.compile(r'^(\d*)(.*)')  # finds the first digits and the rest of the string
    courseids1 = container.getFolderContents(contentFilter={"portal_type": "Course"})
    twdepartment = (container.getCode()).lower()
    os.write(tex_fd, 'Adding a course and tutorial to department ' + twdepartment + '\n')
    courseids = []
    if (len(courseids1) < 1):
	os.write(tex_fd, 'no courses present in department\n') 
    else:
	os.write(tex_fd, 'department ' + twdepartment + 'contains courses with id:\n')
	for cid in courseids1:
            c = cid.getObject()
	    courseids.append(c.getId())
	    os.write(tex_fd, c.Title() + ', ')
        os.write(tex_fd, '\n')
    for j in filter(istut,listdir(twpath)):
        # set id, title, author, lang, courseno, reference and trailer
	tutorialpath = twpath+'/'+j+'/'
	try:
            titlefile = open(tutorialpath+'/course/titleline.txt', 'r')
	    title = titlefile.read()
	    title = title.strip()
	    titlefile.close()
	except:
            title = 'no title found'
	# id [xxxx][shorttitle]
	tutorialid = tutidPattern.search(j).groups()
	digits = tutorialid[0]
	shorttitle = tutorialid[1]
	tutid = twdepartment + j
	# it is not clear how the id for course and tutorial are separated
	# using the first - 1 digits for course id and the last digit for tutorial???
	if (len(digits) < 1):
            # does not start with digits
            # error
            return 'Error in tutorial id: ' + tutid + ' tutorial ids should start with digits. got ' + digits + ' and ' + shorttitle
	elif (len(digits) == 1):
            numdigits = 1
	else:
            numdigits = len(digits) - 1
	courseid = twdepartment + digits[0:numdigits]
	if (not(courseid in courseids)):
            # should create course with courseid
            # title, Tutorials, Students, Code, 
            courseids.append(courseid)
            container.invokeFactory('Course', courseid)
	    CourseObj = getattr(container, courseid)
	    # set same title as tutorials - to start with
	    CourseObj.setTitle(unicode(title, 'latin-1'))
	    CourseObj.setCode(digits[0:numdigits])
	    comment = 'Publishing tutorial content'
	    action = 'publish'
	    os.write(tex_fd, 'added course with id ' + courseid + ' and title ' + title + '\n')
	    try:
                workflow_tool.doActionFor(CourseObj, action, comment=comment)
	    except:
                raise TypeError('Unsupported workflow action %s for object %s.'
                           % (repr(action), repr(CourseObj)))
	    # no student info available
	else:
            CourseObj = getattr(container, courseid)
	container.invokeFactory('Tutorial', tutid)
        TutObj = getattr(container, tutid)
        # don't update pdf every time add new tutorial/lecture/slide
	#TutObj.setMigrateTutorial(1)
	TutObj.setTitle(unicode(title, 'latin-1'))
	os.write(tex_fd, 'added tutorial with id ' + tutid + ' and title ' + title + '\n')
	try:
	     authorfile = open(tutorialpath+'course/author.txt', 'r')
	     author = authorfile.read()
	     author = author.strip()
	     author = unicode(author,'latin-1')
	     authorfile.close()
	except:
	     author = ''
	     os.write(tex_fd, 'could not determine author from author.txt, no author set for ' + tutid + '\n')
	TutObj.setAuthor(author)
	info = ''
        try:
	     infofile = open(tutorialpath+'course/tutorial.info.txt', 'r')
	     #tutorial.info.txt
	     # EN%Statistical analysis of fisheries data%FISH %5%13%
	     # Lang & Title & Dep & numlecs & numcredits
	     info = infofile.read()
	     info = info.split("%")
	     lang = info[0]
	     infofile.close()
        except:
             lang = 'EN'
	     os.write(tex_fd, 'could not determine tutorial language from tutorial.info.txt, English set as default ' + tutid + '\n')
        courseno=tutid[0:3] + '.' + tutid[3]
	# try to set language correctly
        TutObj.setTutorialLanguage(lang.lower())
	# must set ShortTitle, NumberCode, Credits, TutorialReference, pdfpreamble,pdfpostamble,  (DepartmentCourse)
	# TutObj.setShortTitle(?), TutObj.setNumberCode(?), TutObj.setPdfPreamble(?)course/preamble.tex
	tempnum = len(digits) + 1
	# would normally be only one digit?
	TutObj.setNumberCode(digits[numdigits:tempnum])
	TutObj.setShortTitle(shorttitle)
	TutObj.setDepartmentCourse(CourseObj)
	# FIXME, overwrite tutorials which are already part of course
	#CourseObj.setTutorials(TutObj)
	coursetutorials = CourseObj.getTutorials()
	coursetutorials.append(TutObj)
	CourseObj.setTutorials(coursetutorials)
	# credits are not set
	try:
             trailerfile = open(tutorialpath+'course/trailer.tex', 'r')
             trailer = trailerfile.read()
	     trailer = trailer.strip()
	     trailerfile.close()
        except:
             trailer = ''
	TutObj.setPdfPostamble(trailer, mimetype='text/x-tex')
	try:
             preamblefile = open(tutorialpath+'course/preamble.tex', 'r')
             preamble = preamblefile.read()
	     preamble = preamble.strip()
	     preamblefile.close()
        except:
             preamble = ''
	TutObj.setPdfPreamble(preamble, mimetype='text/x-tex')
        try:
             referencefile = open(tutorialpath+'course/references.txt', 'r')
             reference = referencefile.read()
             reference = reference.strip()
             referencefile.close()
        except:
             reference = ''
	if not isinstance(reference, unicode):
            reference1 = reference.decode('latin-1').encode('utf-8')
	else:
            reference1 = reference.encode('utf-8')
        TutObj.setTutorialReference(reference1, mimetype='text/plain')
            
           
	comment = 'Publishing tutorial content'
	action = 'publish'
	try:
	     workflow_tool.doActionFor(TutObj, action, comment=comment)
	except:
	     raise TypeError('Unsupported workflow action %s for object %s.'
                           % (repr(action), repr(TutObj)))
        TutObj.reindexObject()
	#TutObj.at_post_create_script()
	TutObj.initializeObject()
	# now the extra data dir should have been created - must set extra data if any
	#extradata = TutObj.getAcknowledgementFolder()
	# depricated, don't use special acknowledgement folder anymore
	if (True):
            sponsorlist = filter(isacknowledgement,listdir(tutorialpath+'/course'))
            temp = sponsorlist.sort()
	    tempd = {}
	    for u in sponsorlist:
                tempd[u[7:-4]] = []
	    for u in sponsorlist:
                tempd[u[7:-4]].append(u)
	    for sponsor in tempd:
                '''set acknowledgement data'''
		# create a new sponsor:
		try:
                    #extradata.invokeFactory('File', ex)
                    TutObj.invokeFactory('Sponsor', sponsor)
		except:
                    os.write(tex_fd, 'could not create sponsor object ' + sponsor + '\n')
		try:
                    #FileObj = getattr(extradata, ex)
                    FileObj = getattr(TutObj, sponsor)
		except:
                    os.write(tex_fd, 'could not getattr for sponsorobj ' + sponsor + '\n')
		try:
                    FileObj.setTitle(sponsor)
		except: 
                    os.write(tex_fd, 'could not settitle for sponsorobj ' + ex + '\n')
		# for all files which belong to sponsor:
		for ex in tempd[sponsor]:
                    # does this really work for image files as well????
		    try:
                        titlefile = open(tutorialpath+'/course/'+ex, 'r')
		        textdata = titlefile.read()
		        if not isinstance(textdata, unicode):
                            textdata1 = textdata.decode('latin-1').encode('utf-8')
		        else:
                            textdata1 = textdata.encode('utf-8')
                        titlefile.close()
		    
                    except:
                        '''what to do'''
		        os.write(tex_fd, 'failed to find file ' + tutorialpath + '/course/'+ex + '\n')
		    if (ex.endswith('png') or ex.endswith('jpg') or ex.endswith('gif')):
		        #set logo
                        try:
                            FileObj.setSponsorlogo(textdata)
			except:
                            os.write(tex_fd, 'could not set sponsorlogo for fileobj ' + ex + '\n')   
		    elif (ex.endswith('url')):
                        # set url
			try:
                            FileObj.setSponsorurl(textdata1)
			except:
                            os.write(tex_fd, 'could not set sponsorurl for fileobj ' + ex + '\n')       
		    elif (ex.endswith('txt')):
			# set text
                        try:
                            FileObj.setSponsortext(textdata1)
			except:
                            os.write(tex_fd, 'could not set sponsortex for fileobj ' + ex + '\n')           
                    else:
			os.write(tex_fd, 'got incorrect ending for sponsor ' + ex + '\n')	 
		    
		FileObj.reindexObject()
		os.write(tex_fd, 'added sponsor  ' + sponsor + 'to tutorial '+ tutid + '\n')
		    
                
		
        for k in filter(islect,listdir(twpath+'/'+j)):
             # set id, title, reference 
             lecturepath = twpath+'/'+j+'/'+k+'/'
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
                 referencefile = open(lecturepath+'general/references.txt', 'r')
                 reference = referencefile.read()
                 reference = reference.strip()
                 referencefile.close()
             except:
                 reference = ''
	     if not isinstance(reference, unicode):
                 reference1 = reference.decode('latin-1').encode('utf-8')
	     else:
                 reference1 = reference.encode('utf-8')
             LecObj.setLectureReference(reference1, mimetype='text/plain')
                
	     comment = 'Publishing lecture content'
	     action = 'publish'
	     try:
		 workflow_tool.doActionFor(LecObj, action, comment=comment)
	     except:
		 raise TypeError('Unsupported workflow action %s for object %s.'
                           % (repr(action), repr(LecObj)))
	    
	     #LecObj.at_post_create_script()
	     LecObj.initializeObject()
	     LecObj.reindexObject()
	     os.write(tex_fd, 'added lecture ' + lecid + ' with title ' + title + '\n')
	
	     # set the slides
             for l in filter(isslide, listdir(twpath+'/'+j+'/'+k)):
                 # set id, title, main, explanation text and images, reference
                 # and Details, Examples, Alternative and Handout
                 slidepath = twpath+'/'+j+'/'+k+'/'+l+'/'
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
		 SlObj.setUpdateSlideText(True)
		 os.write(tex_fd, 'added slide ' + slid + ' with title ' + title + '\n')
		 os.write(tex_fd, 'update ' + str(SlObj.UpdateSlideText) + '\n')
                 maintexttype = 'text/latex'
                 explanationtexttype = 'text/latex'
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
				     
			 # check for <pre>     
                             
			 if (hasStructured(maintext)):
                             maintext = setStructuredText(maintext)
			     maintexttype = 'text/structured'
			 elif (hasHtml(maintext)):
			     maintexttype = 'text/structured'
			 else:	
			     maintexttype = 'text/plain'
                         maintextfile.close()
                     except:
                         maintext = ''
		 if not isinstance(maintext, unicode):
                     maintext1 = maintext.decode('latin-1').encode('utf-8')
		 else:
                     maintext1 = maintext.encode('utf-8')
                 SlObj.setSlideText(maintext1, mimetype=maintexttype)
                 try:
                     explanationtextfile = open(slidepath+'expln.tex', 'r')
                     explanationtext = explanationtextfile.read()
                     explanationtexttype = 'text/x-tex'
                     explanationtextfile.close()   
                 except:
                     try:
                         explanationtextfile = open(slidepath+'expln.txt', 'r')
                         explanationtext = explanationtextfile.read()
			 if (hasStructured(maintext)):
                             maintext = setStructuredText(maintext)
			     maintexttype = 'text/structured'
			 elif (hasHtml(explanationtext)):
			     explanationtexttype = 'text/structured'
			 else:	
			     explanationtexttype = 'text/plain'
                         explanationtextfile.close()
                     except:
                         explanationtext = ''
                     ##   maintext = ''   
		 if not isinstance(explanationtext, unicode):
                     explanationtext1 = explanationtext.decode('latin-1').encode('utf-8')
		 else:
                     explanationtext1 = explanationtext.encode('utf-8')    
                 SlObj.setExplanation(explanationtext1, mimetype=explanationtexttype)
		 
		 extradata = True
		 extras = LecObj.getAllExtraFilesIds()
                 # now set the images if any
		 im, extension, imtype = hasImage(listdir(slidepath), 'base.')
		 if (im):
		     if (imtype == 'text'):
			 #has base image with format: plt, fig, r, gnuplot
			 # imagetype: fig,gnuplot, r
			 SlObj.setSlideImageFormat(extension)
		     	 mainimagefile = open(slidepath+im, 'r')
			 mainimage = mainimagefile.read()
			 SlObj.setSlideImageText(mainimage, mimetype='text/plain')
			 mainimagefile.close()
			 
			 if (extradata):
			     extras = addFiles(LecObj, slidepath, mainimage, extras, tex_fd)
				 
		     else:
			 # has a base image with format: png, gif or jpg
			 #extension = im.split('.')[1]
			 mime = 'image/'+extension    
			 mainimagefile = open(slidepath+im, 'r')    
			 mainimage = mainimagefile.read()
			 try:
			     SlObj.setSlideImage(mainimage, mimetype=mime)
			 except:
                             os.write(tex_fd, 'could not set main slide image for slide ' + slidepath+im + '\n')
			     #return('could not set slide ' + slidepath + '\n')
			 SlObj.setSlideImageFormat('image')
			 mainimagefile.close()    	  


				  
			    
		 im, extension, imtype = hasImage(listdir(slidepath), 'expln.')
		 if (im):
		     if (imtype == 'text'):
			 #has base image with format: plt, fig, r, gnuplot
			 # imagetype: fig,gnuplot, r
			 SlObj.setExplanationImageFormat(extension)
			 mainimagefile = open(slidepath+im, 'r')
			 mainimage = mainimagefile.read()
			 SlObj.setExplanationImageText(mainimage, mimetype='text/plain')
			 mainimagefile.close()
			 if (extradata):
                             extras = addFiles(LecObj, slidepath, mainimage, extras, tex_fd)		 
			    
		     else:
			 # has a base image with format: png, gif or jpg
			 #extension = im.split('.')[1]
			 mime = 'image/'+extension
			 mainimagefile = open(slidepath+im, 'r')
			 mainimage = mainimagefile.read()
			 try:
                             SlObj.setExplanationImage(mainimage, mimetype=mime)
			 except:
                             os.write(tex_fd, 'could not add explanation image to slide ' + slidepath+im + '\n')
			 SlObj.setExplanationImageFormat('image')
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
		 #set captions if any
		 texttype = 'text/plain'
		 text = ''
		 try:
		     textfile = open(slidepath+'baseptr.txt', 'r')
		     text = textfile.read()
		     textfile.close()
		     if not isinstance(text, unicode):
                         text1 = text.decode('latin-1').encode('utf-8')
		     else:
                         text1 = text.encode('utf-8')
		     SlObj.setSlideImageCaption(text1, mimetype=texttype)
                 except:
                     ''' nothing to do'''
		 try:
		     textfile = open(slidepath+'explnptr.txt', 'r')
		     text = textfile.read()
		     textfile.close()
		     if not isinstance(text, unicode):
                         text1 = text.decode('latin-1').encode('utf-8')
		     else:
                         text1 = text.encode('utf-8')
		     SlObj.setExplanationImageCaption(text1, mimetype=texttype)
                 except:
                     ''' nothing to do'''    
                 #at last set the slide reference if any
		 texttype = 'text/plain'
		 text = ''
		 try:
		     textfile = open(slidepath+'references.tex', 'r')
		     text = textfile.read()
		     texttype = 'text/x-tex'
		     textfile.close()
		     if not isinstance(text, unicode):
                         text1 = text.decode('latin-1').encode('utf-8')
		     else:
                         text1 = text.encode('utf-8')
		     SlObj.setSlideReference(text1, mimetype=texttype)
                 except:
		     try:
			 textfile = open(slidepath+'references.txt', 'r')
			 text = textfile.read()
			 if (hasHtml(text)):
			     texttype = 'text/structured'
			 else:	
			     texttype = 'text/plain'
			     textfile.close()
			 if not isinstance(text, unicode):
                             text1 = text.decode('latin-1').encode('utf-8')
		         else:
                             text1 = text.encode('utf-8')
			 SlObj.setSlideReference(text1, mimetype=texttype)
		     except:
			 text = ''
                    
                 # update slide text
		 SlObj.setUpdateSlideText(True)
		 SlObj.setSlideTextChanged(False)
		 comment = 'Publishing slide content'
		 action = 'publish'
		 try:
		     workflow_tool.doActionFor(SlObj, action, comment=comment)
		 except:
		     raise TypeError('Unsupported workflow action %s for object %s.'
                           % (repr(action), repr(SlObj)))
		 SlObj.initializeObject()
	     #set the questions -
	     for q in filter(isquestion, listdir(twpath+'/'+j+'/'+k)):
                 # set question text 
                 questionpath = twpath+'/'+j+'/'+k+'/'+q+'/'
                 question = q
                 LecObj.invokeFactory('TutorWebQuestion', question)
                 QueObj = getattr(LecObj, question)
		 os.write(tex_fd, 'added question ' + QueObj.getId() + ' with title ' + '\n')
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
			 if (hasStructured(maintext)):
                             maintext = setStructuredText(maintext)
			     maintexttype = 'text/structured'
                         elif (hasHtml(maintext)):
			     maintexttype = 'text/structured'
			 else:	
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
	         # FIXME
	         # Remember r-latex questions if there
		 if not isinstance(maintext, unicode):
                 #    maintext = unicode(maintext, 'utf-8', 'replace')
		 #    os.write(tex_fd, 'is not unicode')
		 #    os.write(tex_fd, maintext + '\n')
                     maintext1 = maintext.decode('latin-1').encode('utf-8')
		 else:
                     maintext1 = maintext.encode('utf-8')
		 #maintext1 = maintext.encode('utf-8')
		 #os.write(tex_fd, 'after utf-8 ' + maintext1 + '\n')
                 QueObj.setQuestion(maintext1, mimetype=maintexttype)
		 QueObj.setPoints(1)
		    
		 comment = 'Publishing question content'
		 action = 'publish'
		 try:
		     workflow_tool.doActionFor(QueObj, action, comment=comment)
		 except:
		     raise TypeError('Unsupported workflow action %s for object %s.'
                           % (repr(action), repr(QueObj)))
		 
		 # Now must set the answers - presuming they are text
		 # Always have three answers (a, b, c and a i correct)
		 #answers = [questionpath+'a', questionpath+'b', questionpath+'c']
		 answers = filter(isanswer, listdir(questionpath))
		 # maybe should sort answers
		 # to get them in same order, a, b, c, d
		 tmp = answers.sort()
		 mutated = []
		 answertexttype = 'text/plain'
		 for a in answers:
                     row = {}
		     row['answertext'] = ''
		     row['correct'] = ''
		     row['randomize'] = ''
		     
		     answertext = ''
		     answertexttype = 'text/plain'
		     try:
			 answertextfile = open(questionpath+a, 'r')
			 answertext = answertextfile.read()
			 if (hasStructured(answertext)):
			     answertext = setStructuredText(answertext)
			     answertexttype = 'text/structured'
			 elif (hasHtml(answertext)):
			     answertexttype = 'text/structured'
			 else:	
			     answertexttype = 'text/plain'
			 answertextfile.close()
				     
				     
			 
		     except:
			 answertext = 'No answer found'
			 answertextype = 'text/plain'
		     #AnsObj.setAnswer(answertext, mimetype=answertexttype)
		      
		     if not isinstance(answertext, unicode):
                         answertext1 = answertext.decode('latin-1').encode('utf-8')
		     else:
                         answertext1 = answertext.encode('utf-8')
		     row['answertext'] = answertext1	 
	     
		      
		     if ('d.true' in answers and a == 'd.true'):
                         row['correct'] =  '1'
		     elif (a == 'a' and 'd.true' not in answers):
			 row['correct'] =  '1'    
		     else:
                         ''' what to do'''

		     if (a == 'd.true' or a == 'd.false'):
                         #AnsObj.setRandomize(False)
                         row['randomize'] =  ''
		     else:
                         '''should randomize'''

			 row['randomize'] =  '1'
		     mutated.append(row)	     
		 QueObj.setAnswerList(mutated)
		 # this is based on the last answer read!!
		 # all answers must have the same text format
		 QueObj.setAnswerFormat(answertexttype)
                     
		 QueObj.reindexObject()
		 QueObj.initializeObject()
             # order slides according to id
	     LecObj.orderObjects("id")
	     LecObj.plone_utils.reindexOnReorder(LecObj)
	     LecObj.setTitle_pdf()
	     LecObj.reindexObject()
		 
	TutObj.setTitle_pdf()
	#order lectures according to id
	TutObj.orderObjects("id")
	TutObj.plone_utils.reindexOnReorder(TutObj)
	
	
	dep = dep + j
    return 'finished uploading ' + dep + ' from ' + twpath
    
