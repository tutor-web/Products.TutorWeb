## Script (Python) "download_tutorial"
##title=Download a file keeping the original uploaded filename
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
bla = context.getTutorial_pdf()


#bla = context.getRawPdf()
#if traverse_subpath:
#    field = context.getWrappedField(traverse_subpath[0])
#else:
#    field = context.getPrimaryField()
field = context.getWrappedField('LatexLog')
return field.download(context)
#file = field.get(context, raw=True)
#from OFS.Image import Image as BaseImage
#return BaseImage.index_html(bla)
#return bla
