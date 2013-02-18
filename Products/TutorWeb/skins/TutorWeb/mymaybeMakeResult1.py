## Script (Python) "maybe_make_result"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=usern
##title=Create a new result object.
##
quiz = context.getQuiz()
return quiz.maybeMakeNewTest(usern)
