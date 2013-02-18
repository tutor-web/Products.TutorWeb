#from Products.MimetypesRegistry.interfaces import IClassifier
from Products.MimetypesRegistry.MimeTypeItem import MimeTypeItem
from Products.MimetypesRegistry.common import MimeTypeException

from types import InstanceType

class LaTeX(MimeTypeItem):

    __name__   = "LaTeX"
    mimetypes  = ('text/latex', 'text/x-tex',)
    extensions = ('tex',)
    binary     = 0

class R(MimeTypeItem):

    
    __name__   = "R"
    mimetypes  = ('text/r',)
    extensions = ('r',)
    binary     = 0

class RLaTeX(MimeTypeItem):

   
    __name__   = "RLaTeX"
    mimetypes  = ('text/r-latex',)
    extensions = ('r',)
    binary     = 0
