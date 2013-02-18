try: 
    # Plone 4 and higher 
    import plone.app.upgrade
    from Products.validation.interfaces.IValidator import IValidator
    USE_BBB_VALIDATORS = False 
except ImportError: 
    # BBB Plone 3 
    USE_BBB_VALIDATORS = True 
    from Products.validation.interfaces import ivalidator

from zope.interface import implements
#from Products.TutorWeb.Department import Department
from Acquisition import aq_parent

class SameDepartmentCodeValidator:
    '''Check if id is already in use by a different department'''
##    __implements__ = (ivalidator,)
    if USE_BBB_VALIDATORS: 
        __implements__ = (ivalidator,) 
    else: 
        implements(IValidator) 
    def __init__(self, name):
        self.name = name

    def __call__(self, value, *args, **kwargs):
        '''bla bla'''
        #return 'bla'
        instance    = kwargs.get('instance', None)
        parent = aq_parent(instance)
        dep = parent.getFolderContents(contentFilter={"portal_type": "Department"})
        myid = instance.getId()
        for d in dep:
            d = d.getObject()
            i = d.getId()
            if (i != myid):
                if (value == d.getCode()):
    
                    return value + ' is already in use by department: ' + d.getTitle() + ' , please choose a different code'
        
        return True


class SameCourseCodeValidator:
    """Check if the suggested id is alrady in use"""

    if USE_BBB_VALIDATORS: 
        __implements__ = (ivalidator,) 
    else: 
        implements(IValidator) 
    def __init__(self, name):
        self.name = name

    def __call__(self, value, *args, **kwargs):
        instance    = kwargs.get('instance', None)
        parent = aq_parent(instance)
        dep = parent.getFolderContents(contentFilter={"portal_type": "Course"})
        myid = instance.getId()
        for d in dep:
            d = d.getObject()
            i = d.getId()
            if (i != myid):
                if (value == d.getCode()):
                    return value + ' is already in use by course: ' + d.getTitle() + ' , please choose a different code'
        
        return True

class SameQuestionIdValidator:
    """Check if the suggested id is alrady in use"""
    if USE_BBB_VALIDATORS: 
        __implements__ = (ivalidator,) 
    else: 
        implements(IValidator)
 
    def __init__(self, name):
        self.name = name

    def __call__(self, value, *args, **kwargs):
        instance    = kwargs.get('instance', None)
        parent = aq_parent(instance)
        que = parent.getFolderContents(contentFilter={"portal_type": "TutorWebQuestion"})
        myid = instance.getId()
        
        for q in que:
            d = q.getObject()
            i = d.getId()
            if (i != myid):
            ##    if (value == d.getCode()):
                if value == i:
                    return value + ' is already in use by a question: ' + d.getTitle() + ' , please choose a different id'
        
        return True

class SetCorrectAnswerValidator:
    """Check if any answer has been set correct, need at least one
       correct answer"""
    if USE_BBB_VALIDATORS: 
        __implements__ = (ivalidator,) 
    else: 
        implements(IValidator)
 
    def __init__(self, name):
        self.name = name

    def __call__(self, value, *args, **kwargs):
        instance    = kwargs.get('instance', None)
        
        #parent = aq_parent(instance)
        #que = parent.getFolderContents(contentFilter={"portal_type": "TutorWebQuestion"})
        #field    = kwargs.get('field', None)
        texttype = 'bla'
        return True
        field = instance.getField('question')
        widget  = field.widget
        request = getattr(instance, 'REQUEST', None)
        if request and request.form:
            form   = request.form
            result = widget.process_form(instance, field, form)
            field = instance.getField('question')
            texttype = field.getContentType(instance)
                      
        #question = instance.REQUEST.get('question', None)
        #texttype = question.getContentType()
        #f = instance.REQUEST.getField('question')
        #texttype = f.getContentType(instance)
        return 'texttype ' + texttype
        #return True
        if (texttype == 'text/r' or texttype =='text/r-latex'):
            return 'texttype is ' + texttype
        length = len(value) - 1
        if (length < 1):
            '''need at least one answer'''
            return 'Please add at least one answer to the question'
        hassetcorrect = False
        for row in value: 
            if (row['correct'] == '1'):
                hassetcorrect = True
            
        if (hassetcorrect==True):
            return True
        else:
            return 'Please choose one answer as True'
                  
class SameSchoolNameValidator:
    '''Check if name is already in use'''
##    __implements__ = (ivalidator,)
    if USE_BBB_VALIDATORS: 
        __implements__ = (ivalidator,) 
    else: 
        implements(IValidator) 
    def __init__(self, name):
        self.name = name
    def __call__(self, value, *args, **kwargs):     
        instance    = kwargs.get('instance', None)
        parent = aq_parent(instance)
        schools = parent.getFolderContents(contentFilter={"portal_type": "School"})
        myid = instance.getId()
        if not isinstance(value, unicode):
            charset = instance.getCharset()
            v = unicode(value, charset)
        else:
            v = value
        for s in schools:
            s = s.getObject()
            i = s.getId()
            if (i != myid):
                t = s.getTitle()
                if not isinstance(t, unicode):
                    charset = instance.getCharset()
                    t = unicode(t, charset)
                if (v == t):
                    return v + ' is already in use by school: ' + t + ' , please choose a different name for the school.'
        
        return True

class SameClassNameValidator:
    '''Check if name is already in use by school'''
##    __implements__ = (ivalidator,)
    if USE_BBB_VALIDATORS: 
        __implements__ = (ivalidator,) 
    else: 
        implements(IValidator) 
    def __init__(self, name):
        self.name = name
    def __call__(self, value, *args, **kwargs):     
        instance    = kwargs.get('instance', None)
        parent = aq_parent(instance)
        classes = parent.getFolderContents(contentFilter={"portal_type": "Class"})
        # compare to a unicode value
        if not isinstance(value, unicode):
            charset = instance.getCharset()
            v = unicode(value, charset)
        else:
            v = value
        myid = instance.getId()
        
        for s in classes:
            s = s.getObject()
            i = s.getId()
            if (i != myid):
                t = s.getTitle()
                if not isinstance(t, unicode):
                    charset = instance.getCharset()
                    t = unicode(t, charset)
                if (v == t):
                    return v + ' is already in use by class: ' + t + ' , please choose a different name for the class.'
        
        return True
