## Script (Python) "exportItemStatistics"
##parameters=format='tab'
##title=
##

#!/usr/local/bin/python
# -*- coding: iso-8859-1 -*-

REQUEST  = context.REQUEST
RESPONSE = REQUEST.RESPONSE

ecq_tool = context.myecq_tool

I18N_DOMAIN = context.i18n_domain

target = context.getActionInfo('object/statistics')['url']
REDIRECT_URL = '%s?portal_status_message=' % target

ERROR_FORMAT_MSG = context.translate(
    msgid   = 'unknown_format_export',
    domain  = I18N_DOMAIN,
    default = 'Unknown format. Cannot export.')

if not format:
    return context.redirect(REDIRECT_URL + ERROR_FORMAT_MSG)
format = format.lower()
exportFormatList = [o for o in context.RESULTS_EXPORT_FORMATS
                    if o[0].lower() == format]
if not exportFormatList:
    return context.redirect(REDIRECT_URL + ERROR_FORMAT_MSG)

exportFormat = exportFormatList[0]
colDelim     = exportFormat[1]
rowDelim     = exportFormat[2]
strStart     = exportFormat[3]
strEnd       = exportFormat[4]
escapeChar   = exportFormat[5]
encoding     = 'latin-1'

def escape(string):
    escaped = ''
    for c in string:
        if(c in [escapeChar, strStart, strEnd]):
            escaped += escapeChar + c
        else:
            escaped += c
    return escaped

results = context.getDetailedScores()

# We assume that the first row is the header of the table.  The items
# of the header may be tuples or arrays.  For CSV output, we separate
# this information in multiple rows.  For example:
#
#   [('Candidate', '', ''), ('header 1', 'foo', 'bar')]
#
# becomes
#
#   ['Candidate', 'header 1']
#   ['', 'foo']
#   ['', 'bar']

header = []

if same_type(results[0][0], ()) or same_type(results[0][0], []):
    for j in range(0, len(results[0][0])):
        hrow = []
        for col in results[0]:
            hrow.append(col[j])
        
        header.append(hrow)
else:
    header = results[0]

output = ''

for row in header + results[1:]:
    maxCol = len(row) - 1
    for i in range(0, maxCol+1):
        col = row[i]
        if(same_type(col, '') or same_type(col, u'')):
            # output as text if the content of the cell is a string
            output += strStart + escape(col) + strEnd
        # no string --> no output as text
        elif(same_type(col, 1.1)):
            # i18n of fractional numbers
            output += escape(ecq_tool.localizeNumber("%.2f", col))
        else:
            output += escape(str(col))
        # append column delimiter or row delimiter 
        # if this is the last column of the row
        output += [colDelim, rowDelim][i >= (maxCol)]


resultsString = context.translate(
    msgid   = 'statistics',
    domain  = I18N_DOMAIN,
    default = 'statistics')

filename = context.mypathQuote(context.title_or_id()) \
           + '_' + resultsString + '.' + format

RESPONSE.setHeader('Content-Disposition', 'attachment; filename=' + filename)
RESPONSE.setHeader('Content-Type', 'text/plain')
# 'unicodeDecode()' is defined in the script (Python)
# Products/ECQuiz/skins/ECQuiz/unicodeDecode.py
return context.unicodeDecode(output).encode(encoding)
