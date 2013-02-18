import transaction
from Products.CMFCore.utils import getToolByName

from Products.TutorWeb.config import *

from StringIO import StringIO
from types import InstanceType
from Products.TutorWeb.mimetypes import LaTeX, R, RLaTeX


def registerTransform(self, out, name, module):
    transforms = getToolByName(self, 'portal_transforms')
    transforms.manage_addTransform(name, module)
    print >> out, "Registered transform", name

def unregisterTransform(self, out, name):
    transforms = getToolByName(self, 'portal_transforms')
    try:
        transforms.unregisterTransform(name)
        print >> out, "Removed transform", name
    except AttributeError:
        print >> out, "Could not remove transform", name, "(not found)"

def registerMimeType(self, out, mimetype):
    if type(mimetype) != InstanceType:
        mimetype = mimetype()
    mimetypes_registry = getToolByName(self, 'mimetypes_registry')
    mimetypes_registry.register(mimetype)
    print >> out, "Registered mimetype", mimetype

def unregisterMimeType(self, out, mimetype):
    if type(mimetype) != InstanceType:
        mimetype = mimetype()
    mimetypes_registry = getToolByName(self, 'mimetypes_registry')
    mimetypes_registry.unregister(mimetype)
    print >> out, "Unregistered mimetype", mimetype

def install(self, reinstall=False):
    """Install a set of products (which themselves may either use Install.py
    or GenericSetup extension profiles for their configuration) and then
    install a set of extension profiles.
    
    One of the extension profiles we install is that of this product. This
    works because an Install.py installation script (such as this one) takes
    precedence over extension profiles for the same product in portal_quickinstaller.
    
    We do this because it is not possible to install other products during
    the execution of an extension profile (i.e. we cannot do this during
    the importVarious step for this profile).
    """
   
    portal_quickinstaller = getToolByName(self, 'portal_quickinstaller')
    portal_setup = getToolByName(self, 'portal_setup')

    for product in DEPENDENCIES:
        if reinstall and portal_quickinstaller.isProductInstalled(product):
            portal_quickinstaller.reinstallProducts([product])
            transaction.savepoint()
        elif not portal_quickinstaller.isProductInstalled(product):
            portal_quickinstaller.installProduct(product)
            transaction.savepoint()
   
    for extension_id in EXTENSION_PROFILES:
        portal_setup.runAllImportStepsFromProfile('profile-%s' % extension_id, purge_old=False)
        product_name = extension_id.split(':')[0]
        portal_quickinstaller.notifyInstalled(product_name)
        transaction.savepoint()
    out = StringIO()

    print >> out, "Installing tex/html transform"


    
    
    # Register mimetype
    registerMimeType(self, out, LaTeX)
    registerMimeType(self, out, R)
    registerMimeType(self, out, RLaTeX)
    # Register transforms
    registerTransform(self, out, 'tex_to_html', 'Products.TutorWeb.tex_to_html')
    return out.getvalue()

def uninstall(self):

    out = StringIO()

    # Remove transforms
    unregisterTransform(self, out, 'tex_to_html')
    

    # Remove mimetype
    unregisterMimeType(self, out, LaTeX)
    # Remove mimetype
    unregisterMimeType(self, out, R)
    # Remove mimetype
    unregisterMimeType(self, out, RLaTeX)
    
    
    return out.getvalue()
