"""
Uses the http://sf.net/projects/pdftohtml bin to do its handy work

"""
from Products.PortalTransforms.interfaces import itransform
from Products.PortalTransforms.libtransforms.utils import bin_search, sansext
from Products.PortalTransforms.libtransforms.commandtransform import commandtransform
from Products.PortalTransforms.libtransforms.commandtransform import popentransform
from Products.CMFDefault.utils import bodyfinder
import os
import re
import os
import shutil
import tempfile

#productdir = '/opt/Plone-3.0.2/zinstance/Products/TutorWeb'
#productdir = '/opt/Plone-3.1/zeocluster/parts/client1/Products/TutorWeb'
from Products.TutorWeb import productdir

class tex_to_html(commandtransform):
    __implements__ = itransform

    __name__ = "tex_to_html"
    #inputs   = ('application/pdf',)
    inputs = ('text/latex', 'text/x-tex',)
    output  = 'text/html'
    output_encoding = 'utf-8'

    #binaryName = "pdftohtml"
    #binaryArgs = "-noframes -enc UTF-8"
    binaryName = 'latex2html'
    binaryArgs = '-debug -nonavigation -notop_navigation -nobottom_navigation ' + \
                        '-noinfo ' + \
                        '-image_type png -html_version 4.0 -no_math ' + \
                          '-noparbox_images -math -math_parsing ' + \
                          '-antialias_text -antialias -transparent -white ' + \
                          '-noaddress ' 
    #binaryName = 
    def __init__(self):
        commandtransform.__init__(self, binary=self.binaryName)

    def convert(self, data, cache, **kwargs):
        kwargs['filename'] = 'unknown.pdf'

        ## tmpdir, fullname = self.initialize_tmpdir(data, **kwargs)
        if (len(data) > 0):
            tmpdir, fullname, tex_fd = self.initialize_tmpdir()
            html = self.invokeCommand(data, tmpdir, fullname, tex_fd)
            htmldir = fullname[:-4]+'/'
            path, images = self.subObjects(htmldir)
            objects = {}
            if images:
                self.fixImages(path, images, objects)
            #remove temporary files    
            self.cleanDir(tmpdir)
            cache.setData(bodyfinder(html))
            cache.setSubObjects(objects)
        return cache

    def invokeCommand(self, text, tmpdir, fullname, tex_fd):
        ## if os.name=='posix':
##             cmd = 'cd "%s" && %s %s "%s" 2>error_log 1>/dev/null' % (
##                    tmpdir, self.binary, self.binaryArgs, fullname)
##         else:
##             cmd = 'cd "%s" && %s %s "%s"' % (
##                   tmpdir, self.binary, self.binaryArgs, fullname)
##         os.system(cmd)
##         try:
##             htmlfilename = os.path.join(tmpdir, sansext(fullname) + '.html')
##             htmlfile = open(htmlfilename, 'r')
##             html = htmlfile.read()
##             htmlfile.close()
##         except:
##             try:
##                 return open("%s/error_log" % tmpdir, 'r').read()
##             except:
##                 return "transform failed while running %s (maybe this pdf file doesn't support transform)" % cmd
        htmldir = fullname[:-4]+'/'
        htmlfilename = htmldir+'index.html'
        try:

                #f = open(productdir+'/twtext_preamble.tex','r')
                #os.write(tex_fd,f.read())
                os.write(tex_fd, text)
                #f.close()

                f = open(productdir+'/twtext_postamble.tex','r')
                os.write(tex_fd,f.read())
                f.close()
                os.close(tex_fd)
        except OSError, (errno, strerror):
                print "_twlatex: IOError[%s]: %s" % (errno, strerror)
        try:
            #sh -c '(echo "q" |latex2html stuff.tex)' >&/dev/null
            os.system('echo \\x03 | latex2html -debug -nonavigation -notop_navigation -nobottom_navigation ' + \
                        '-noinfo ' + \
                        '-image_type png -html_version 4.0,latin1,unicode -no_math ' + \
                          '-noparbox_images -math -math_parsing ' + \
                          '-antialias_text -antialias -transparent -white ' + \
                          '-noaddress ' + fullname)
            #os.system('latex2html -nonavigation -notop_navigation -nobottom_navigation ' + \
            #            '-noinfo ' + \
            #            '-image_type png -html_version 4.0 -no_math ' + \
            #              '-noparbox_images -math -math_parsing ' + \
             #             '-antialias_text -antialias -transparent -white ' + \
             #             '-noaddress ' + fullname)
            #code = os.system ("ulimit -t <secs> ; ...") #              
            #os.system('ulimit -t <60>; latex2html -nonavigation -notop_navigation -nobottom_navigation ' + \
            #            '-noinfo ' + \
            #            '-image_type png -html_version 4.0 -no_math ' + \
            #              '-noparbox_images -math -math_parsing ' + \
            #              '-antialias_text -antialias -transparent -white ' + \
            #              '-noaddress ' + fullname)
        except:
            print "error could not run latex2html"
        html = file(htmlfilename).read()
        return html
    def initialize_tmpdir(self):
        try:
            tmpout = tempfile.mkdtemp()
	

            tex_fd, tex_absname = tempfile.mkstemp(dir=tmpout, suffix='.tex')
            return tmpout, tex_absname, tex_fd
        except:
            ''' what to do'''
def register():
    return tex_to_html()
