## Script (Python) "transformslidedata"
##bind container=container
##bind context=context
##
REQUEST = container.REQUEST
trform = context.updateTransformableText()
context.redirect('teacher_view')
