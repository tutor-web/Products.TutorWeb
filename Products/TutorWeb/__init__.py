""" This file is needed in order to make Zope import this directory.
    All the following statements will be executed and finally 
    the 'initialize' function will be called.
"""

from Products.TutorWeb.tools import log
# mark start of Product initialization in log file

log('------------------------------------------------------------------\n')

import os, os.path

from Products.Archetypes.public import process_types, listTypes
from Products.CMFCore import utils as cmfutils
from Products.CMFCore.DirectoryView import registerDirectory
from Products.validation.validators.validator import RegexValidator
from Products.validation import validation
from validators import SameDepartmentCodeValidator, SameCourseCodeValidator, SameQuestionIdValidator, SetCorrectAnswerValidator, SameSchoolNameValidator, SameClassNameValidator 

validation.register(SameDepartmentCodeValidator("isSameDepartmentCode"))
validation.register(SameCourseCodeValidator("isSameCourseCode"))  
validation.register(SameQuestionIdValidator("isSameQuestionId"))
validation.register(SetCorrectAnswerValidator("hasSetCorrectAnswer"))
validation.register(SameSchoolNameValidator("isSameSchoolName"))
validation.register(SameClassNameValidator("isSameClassName"))
  
# some global constants (in ALL_CAPS) and functions
from Products.TutorWeb.config import *
from Products.TutorWeb.tools import *
from Products.TutorWeb.permissions import *
from Products.TutorWeb.ECQTool import ECQTool

module = ''

# register the validator 'isPositiveInt' in the Zope environment and log whether the registration worked
registerValidatorLogged(RegexValidator, 'isPositiveInt', r'^[1-9]\d*$')

# import self defined types and register them in Zope
# (the registration of the classes contained in each file
# is done via 'registerType(ClassName)' statements in the file)
try:
   
    for m in ['Department',
              'SchoolFolder',
              'School',
              'Class',
              'Course',
              'BaseQuestionSelectionParameters',
              'QuestionSelectionParameters',
              'TutorWebQuiz',
              'TutorWebQuestion',
              'StudentList',
              'InvisibleQuestion',
              'Tutorial',
              'Lecture',
              'Slide',
              'QuestionResult',
              'QuizResult',
              'Sponsor',
              'QuestionSelectionParameters',
              'ExtraDataFile',
              ]:
        module = m
        exec('import ' + module)
        log('Worked: importing module "' + module + '"\n')
except Exception, e:
     # log any errors that occurred
      log('Failed: importing module "' + module + '": ' + unicode(e) + '\n')

""" Register the skins directory (where all the page templates, the
    '.pt' files, live) (defined in Products.TutorWeb.config)
"""
registerDirectory(SKINS_DIR, GLOBALS)
 
def initialize(context):
    """ The 'initialize' function of this Product.
        It is called when Zope is restarted with these files in the Products 
        directory. (I'm not sure what it does or if it is neccessary 
        at all. Best leave it alone.)
    """
    log('Start: "initialize()"\n')

    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)
    
    cmfutils.ContentInit(
        PROJECTNAME + ' Content',
        content_types      = content_types,
        permission         = PERMISSION_ADD_MCTEST,
        extra_constructors = constructors,
        fti                = ftis,
    ).initialize(context)
    
    log('\tWorked: "ContentInit()"\n')

    # Add permissions to allow control on a per-class basis
    for i in range(0, len(content_types)):
        content_type = content_types[i].__name__
        if ADD_CONTENT_PERMISSIONS.has_key(content_type):
            context.registerClass(meta_type    = ftis[i]['meta_type'],
                                  constructors = (constructors[i],),
                                  permission   = ADD_CONTENT_PERMISSIONS[content_type])

    #~ parsers.initialize(context)
    #~ renderers.initialize(context)
    log('Worked: "initialize()"\n')

    # Mark end of Product initialization in log file.
    log('------------------------------------------------------------------\n')

# start initilizing transforms

from Products.PortalTransforms.libtransforms.utils import MissingBinary
modules = [
    'Products.TutorWeb.tex_to_html',
    ]

#g = globals()
#transforms = []
#for m in modules:
#    try:
#        ns = __import__(m, g, g, None)
#        transforms.append(ns.register())
#    except ImportError, e:
#        print "Problem importing module %s : %s" % (m, e)
#    except MissingBinary, e:
#        print e
#    except:
#        import traceback
#        traceback.print_exc()

#def initialize(engine):
#    for transform in transforms:
#        engine.registerTransform(transform)
