## Script (Python) "deleteResults"
##title=
##

#!/usr/local/bin/python

REQUEST  = context.REQUEST

if not REQUEST.has_key('ids'):
    msg = context.translate(
        msgid   = 'select_item_delete',
        default = 'Please select one or more items to delete first.')
else:
    ids = REQUEST['ids']
    context.deleteResultsById(ids)
    if len(ids) == 1:
        msg = context.translate(
            msgid   = 'item_deleted',
            default = 'Item deleted.')
    else:
        msg = context.translate(
            msgid   = 'items_deleted',
            default = 'Items deleted.')

target = context.getActionInfo('object/results')['url']
context.redirect('%s?portal_status_message=%s' % (target, msg))
