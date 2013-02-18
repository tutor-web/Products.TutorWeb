## Script (Python) "exportResults"
##parameters=format='tab'
##title=
##

#!/usr/local/bin/python



REQUEST  = context.REQUEST
RESPONSE = REQUEST.RESPONSE

ecq_tool = context.myecq_tool

I18N_DOMAIN = context.i18n_domain

target = context.getActionInfo('object/results')['url']
REDIRECT_URL = '%s?portal_status_message=' % target

if not REQUEST.has_key('ids'):
    msg = context.translate(
        msgid   = 'select_item_export',
        default = 'Please select one or more items to export first.')
    return context.redirect(REDIRECT_URL + msg)

ERROR_FORMAT_MSG = context.translate(
    msgid   = 'unknown_format_export',
    default = 'Unknown format. Cannot export.')

if not format:
    return context.redirect(REDIRECT_URL + ERROR_FORMAT_MSG)
format = format.lower()
exportFormatList = [o for o in context.RESULTS_EXPORT_FORMATS
                    if o[0].lower() == format]
if not exportFormatList:
    return context.redirect(REDIRECT_URL + ERROR_FORMAT_MSG)

exportFormat = exportFormatList[0]
#~ fileExt      = exportFormat[0]
colDelim     = exportFormat[1]
rowDelim     = exportFormat[2]
strStart     = exportFormat[3]
strEnd       = exportFormat[4]
escapeChar   = exportFormat[5]
encoding     = 'latin-1'

def escape(string):
    escaped = ''
    for c in string:
        if c in [escapeChar, strStart, strEnd]:
            escaped += escapeChar + c
        else:
            escaped += c
    return escaped

results = context.getResultsAsList(REQUEST['ids'])
exportCols = ['user_id', 'full_name', 'state', 'grade', 'score', 'max_score',
              'time_start', 'time_finish',]
if not results[0].has_key('grade'):
    exportCols.remove('grade')

NONE_STRING = context.translate(msgid   = 'N/A',
                                default = 'N/A')

output = ''
for row_dict in results:
    row = [row_dict[key] for key in exportCols]
    maxCol = len(row) - 1
    for i in range(0, maxCol+1):
        col = row[i]
        if col is None:
            col = NONE_STRING
        
        if same_type(col, '') or same_type(col, u''):
            # output as text if the content of the cell is a string
            output += strStart + escape(context.str(col)) + strEnd
        # no string --> no output as text
        elif same_type(col, 1.1):
            # i18n of fractional numbers
            output += escape(ecq_tool.localizeNumber("%.2f", col))
        else:
            output += escape(str(col))
        # If this is the last column of the row, append the row
        # delimiter.  Else, append the column delimiter.
        output += [colDelim, rowDelim][i == maxCol]


resultsString = context.translate(
    msgid   = 'results',
    domain  = I18N_DOMAIN,
    default = 'results')
    
filename = context.mypathQuote(context.title_or_id()) + '_' + resultsString + '.' + format

RESPONSE.setHeader('Content-Disposition', 'attachment; filename=' + filename)
RESPONSE.setHeader('Content-Type', 'text/plain')

return context.unicodeDecode(output).encode(encoding)
