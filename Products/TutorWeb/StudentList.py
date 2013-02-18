from AccessControl import ClassSecurityInfo, getSecurityManager
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.public import Schema, BaseSchema, BaseContent, \
     ObjectField, IntegerField, StringField, DateTimeField, BooleanField
from Products.Archetypes.Widget import TypesWidget, StringWidget, \
     BooleanWidget
from Products.ATContentTypes.content.base import ATCTContent
from Products.ATContentTypes.content.schemata import ATContentTypeSchema

from Products.DataGridField import DataGridField, DataGridWidget
from Products.DataGridField.Column import Column
from Products.DataGridField.SelectColumn import SelectColumn
from Products.DataGridField.RadioColumn import RadioColumn
from Products.DataGridField.CheckboxColumn import CheckboxColumn
from Products.DataGridField.FixedColumn import FixedColumn
from Products.DataGridField.DataGridField import FixedRow
from Products.DataGridField.HelpColumn import HelpColumn

from config import *
from permissions import *
from tools import *
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.Archetypes.public import BaseSchema, Schema, BooleanField, \
     StringField, TextField, SelectionWidget, TextAreaWidget, RichWidget, \
     BaseContent
from Products.Archetypes.Widget import TypesWidget, IntegerWidget, \
     BooleanWidget, StringWidget
from Products.Archetypes.utils import DisplayList
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.folder import ATFolderSchema
from Products.Archetypes import atapi
import tempfile
from Products.CMFCore.utils import getToolByName
from random import random
import shutil

if PLONE_VERSION == 4:
    from Products.Archetypes import atapi
    from config import PROJECTNAME
   
class StudentList(ATCTContent, HistoryAwareMixin):
    """Keeps a unique id for each student."""

    
    
    schema = ATContentTypeSchema.copy() + Schema((
        
       
        DataGridField('StudentIdList',
                searchable=True, # One unit tests checks whether text search works
                widget = DataGridWidget(label='StudentIds',
                     columns= {
                    "studentid" : Column("Student Id"),
                    "randomnumber" : Column("Random id number"),
                    "email": Column("Student email"),
                }
                    ),
                               
                columns=('studentid', 'randomnumber', 'email'),
                
            ),             
        ))
    def getAllList(self):
        return self.getStudentIdList()
    def addStudent(self, studid):
        
        grid = self.getWrappedField('StudentIdList')
        rowrandom = grid.search(self, studentid=studid)
        #newgrid = self.getStudentIdList()
        #for g in newgrid:
        #    tempid = g['studentid']
        #    member = self.portal_membership.getMemberById(tempid)
        #    studentemail = member.getProperty('email', None)
        #    g['email'] = studentemail
            
        if (len(rowrandom) <=0):
            ''' add new student to list'''
            # generate a random number
            
            randnum = str(random())[2:]
            rowrandom = grid.search(self, randomnumber=randnum)
            while(len(rowrandom) > 0):
                randnum = str(random())[2:]
                rowrandom = grid.search(self, randomnumber=randnum)
            # find student e-mail
            member = self.portal_membership.getMemberById(studid)
            studentemail = member.getProperty('email', None)
            rows = []
            temprow = {}
            temprow['studentid'] = studid
            temprow['randomnumber'] = randnum
            temprow['email'] = studentemail
            rows.append(temprow)
            original = self.getStudentIdList()
            list = original + tuple(rows)
            self.setStudentIdList(list)
            return randnum
        else:
            return rowrandom[0]['randomnumber']
    
    def getStudentIdNumber(self, studid):
        
        grid = self.getWrappedField('StudentIdList')
        rowrandom = grid.search(self, studentid=studid)
        
        if (len(rowrandom) <= 0):
            
            return self.addStudent(studid)
        else:
            return rowrandom[0]['randomnumber']   
        
       
if PLONE_VERSION == 3:
    registerATCTLogged(StudentList)
else:
    atapi.registerType(StudentList, PROJECTNAME)
