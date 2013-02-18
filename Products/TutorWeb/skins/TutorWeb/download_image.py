## Script (Python) "download_image"
##title=Download a file keeping the original uploaded filename
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
#bla = context.getLecture_pdf()
#if traverse_subpath:
#    field = context.getWrappedField(traverse_subpath[0])
#else:
#    field = context.getPrimaryField()
#field = context.getField('Pdf')
#field = context.getPrimaryField()
#field = context.getWrappedField('SlideImage')
#return field.download(context)
#return context.getField('SlideImage')
#return field.get(context)
im = context.getImage()
#return context.getSlideImage()
#acc = field.getAccessor(context)
#return acc


#return 'bla'
return im[1]
