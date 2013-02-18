#-*- coding: UTF-8 -*-

""" Global constants for the"""

import os
from OFS.PropertyManager import PropertyManager
from Products.CMFCore.utils import getToolByName
import Products
from OFS.Application import get_folder_permissions, get_products

def makeTypeList(relativeDir):
    """ Returns a sequence of all the python files in a directory 
        specified by "relativeDir".
    """
    ret = os.listdir(os.path.dirname(__file__)+'/'+ relativeDir)
    ret = [type[:-3] for type in ret
           if type.endswith('.py') and (not type.startswith('__'))]
    return ret

GLOBALS = globals()


# define dependencies
DEPENDENCIES = ['DataGridField']

# GS profile name
EXTENSION_PROFILES = ('Products.TutorWeb:default',)

# The name of the Product
PROJECTNAME = 'TutorWeb'
DEBUG = False
try: 
    # Plone 4 and higher
 
    import plone.app.upgrade 
    PLONE_VERSION = 4 
except ImportError: 
    PLONE_VERSION = 3
try:
    import numpy
    NUMPY = True
except:
    NUMPY = False
products = get_products()
for priority, name, index, productDir in get_products():
    if (name == PROJECTNAME):
        productdir = productDir+'/'+name
        bindir = productdir+'/bin'
EXPLANATION_FIG = True
ECMCR_WORKFLOW_ID    = 'tutorweb_result_workflow'
ECMCR_WORKFLOW_TITLE = 'Result Workflow [TutorWeb]'

ECMCT_WORKFLOW_ID    = 'tutorweb_quiz_workflow'
ECMCT_WORKFLOW_TITLE = 'Test Workflow [TutorWeb]'

ECMCE_WORKFLOW_ID    = 'tutorweb_element_workflow'
ECMCE_WORKFLOW_TITLE = 'Element Workflow [TutorWeb]'

SKINS_DIR = 'skins'



def addSiteProperties(portal):
    """adds site_properties in portal_properties"""
    id = PROJECTNAME.lower()+'_properties'
    title = 'Site wide properties'
    p=PropertyManager('id')
    if id not in portal.portal_properties.objectIds():
        portal.portal_properties.addPropertySheet(id, title, p)
    p=getattr(portal.portal_properties, id)

