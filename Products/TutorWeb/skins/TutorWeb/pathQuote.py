## Script (Python) "pathQuote"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=string=''
##title=
##

#!/usr/local/bin/python

SPACE_REPLACER = '_'
# Replace any character not in [a-zA-Z0-9_-] with SPACE_REPLACER
ALLOWED_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-'
ret = ''
for c in string:
    if c in ALLOWED_CHARS:
        ret += c
    else:
        ret += SPACE_REPLACER
return ret
