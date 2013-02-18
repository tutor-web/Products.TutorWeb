## Script (Python) "unicodeDecode"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=string, defaultCharSet=None

#!/usr/local/bin/python

    
if(same_type(string, u'')):
    return string
elif(not same_type(string, '')):
    string = str(string)
    
charSetList = []
if defaultCharSet:
    charSetList += [defaultCharSet]
# Get Plone's 'default_charset' (The 'getCharset()' method is either inherited
# from Products.Archetypes.BaseObject or is acquired from the 'getCharset' 
# script (Python) in Archetypes/skins/archetypes/getCharset.py)
siteCharSet = context.getCharset()
        
if siteCharSet:
    charSetList += [siteCharSet]
charSetList += ['latin-1', 'utf-8', 'cp850', 'cp437', 'cp1252']
for charSet in charSetList:
    try:
        return unicode(string, charSet)
    except UnicodeError:
        pass
raise UnicodeError('Unable to decode %s' % string)
