"""
Permissions used in TutorWeb
"""

from config import PROJECTNAME
from Products.CMFCore.permissions import setDefaultRoles, AddPortalContent, \
     ModifyPortalContent, View

ROLE_RESULT_GRADER = 'TutorWebResultGrader'
ROLE_RESULT_VIEWER = 'TutorWebResultViewer'

PERMISSION_INTERROGATOR        = ModifyPortalContent
PERMISSION_STUDENT             = 'TutorWeb Access Contents'
PERMISSION_RESULT_READ         = 'TutorWeb Read Result'
PERMISSION_RESULT_WRITE        = 'TutorWeb Write Result'

PERMISSION_GRADE = 'TutorWeb: Grade Assignments'
setDefaultRoles(PERMISSION_GRADE,  ('Manager',))
setDefaultRoles(PERMISSION_STUDENT, ('Manager', 'Owner', 'Authenticated',))

PERMISSION_ADD_MCTEST = 'TutorWeb: Add Quiz'
setDefaultRoles(PERMISSION_ADD_MCTEST, ('Manager', 'Owner',))

ADD_CONTENT_PERMISSIONS = {
    'TutorWeb': PERMISSION_ADD_MCTEST,
}
