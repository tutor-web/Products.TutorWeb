## Script (Python) "download_lecture"
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
field = context.getWrappedField('LectureGrades')
return field.download(context)
