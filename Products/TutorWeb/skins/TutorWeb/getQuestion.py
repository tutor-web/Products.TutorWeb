## Script (Python) "maybe_make_result"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=return the question object.
##
#quiz = context.getQuiz()
result = context.maybeMakeNewResult()
return result.getChosenQuestion()
