## Script (Python) "str"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=obj

#!/usr/local/bin/python

#

""" Converts objetcs into strings encoded in Plone's default character set """

if same_type(obj, '') or same_type(obj, u''):
    value = obj
else:
    value = str(obj)
    
return context.unicodeDecode(value).encode( context.getCharset() )
