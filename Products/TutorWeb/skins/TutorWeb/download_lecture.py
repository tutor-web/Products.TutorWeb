## Script (Python) "download_lecture"
##title=Download a file keeping the original uploaded filename
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
#context.portal_url.getPortalObject().ext_switchSkin(context)
bla = context.getLecture_pdf()
#return context.getLectureField_pdf()
#if traverse_subpath:
#    field = context.getWrappedField(traverse_subpath[0])
#else:
#    field = context.getPrimaryField()
#field = context.getField('Pdf')
#field = context.getPrimaryField()
pdffield = context.getWrappedField('Pdf')
return pdffield.download(context)
