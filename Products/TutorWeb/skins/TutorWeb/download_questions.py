## Script (Python) "download_questions"
##title=Download a file keeping the original uploaded filename
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath

bla = context.getQuestion_pdf()
if (not bla):
    return 'You need to login to view this file'
else:
    field = context.getWrappedField('QuestionFile')
    return field.download(context)
#bla = context.getRawPdf()
#if traverse_subpath:
#    field = context.getWrappedField(traverse_subpath[0])
#else:
#    field = context.getPrimaryField()
#field = context.getWrappedField('Pdf')
#return field.download(context)
#file = field.get(context, raw=True)
#from OFS.Image import Image as BaseImage
#return BaseImage.index_html(bla)
#return bla
