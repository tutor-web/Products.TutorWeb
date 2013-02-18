from kss.core import KSSView, kssaction
from kss.core import force_unicode
from kss.core.ttwapi import startKSSCommands
from kss.core.ttwapi import getKSSCommandSet
from kss.core.ttwapi import renderKSSCommands

from plone.app.kss.plonekssview import PloneKSSView
from plone.app.kss.interfaces import IPloneKSSView
from plone.app.kss.interfaces import IPortalObject

from plone.locking.interfaces import ILockable

from zope.interface import implements
from zope import lifecycleevent, event
from zope.publisher.interfaces.browser import IBrowserView

from Acquisition import aq_inner
from Products.Archetypes.event import ObjectEditedEvent
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.CMFCore.utils import getToolByName

from zope.deprecation import deprecated
import tempfile
import re
import os
import time

#import events
#from utils import get_econtext


from datetime import datetime
from zope.interface import implements
#from plonekssview import PloneKSSView
#from kss.core import force_unicode, kssaction
#from interfaces import IPloneKSSView

class DemoView(KSSView):
    implements(IPloneKSSView)
    @kssaction
   
    def response2(self):
        # KSS specific calls
        ksscore = self.getCommandSet('core')
        zopecommands = self.getCommandSet('zope')
        plonecommands = self.getCommandSet('plone')
        instance = aq_inner(self.context)
        imagevalue = instance.getSlideImageFormat()
        explanationvalue = instance.getExplanationImageFormat()
        if (imagevalue == 'image'):
            ksscore.setStyle(ksscore.getHtmlIdSelector('archetypes-fieldname-SlideImageText'), 'display', 'none')
            ksscore.setStyle(ksscore.getHtmlIdSelector('archetypes-fieldname-SlideImage'), 'display', 'block')
        elif (imagevalue == 'none'):
            ksscore.setStyle(ksscore.getHtmlIdSelector('archetypes-fieldname-SlideImageText'), 'display', 'none')
            ksscore.setStyle(ksscore.getHtmlIdSelector('archetypes-fieldname-SlideImage'), 'display', 'none')
        else:
            ksscore.setStyle(ksscore.getHtmlIdSelector('archetypes-fieldname-SlideImageText'), 'display', 'block')
            ksscore.setStyle(ksscore.getHtmlIdSelector('archetypes-fieldname-SlideImage'), 'display', 'none')

        if (explanationvalue == 'image'):
            ksscore.setStyle(ksscore.getHtmlIdSelector('archetypes-fieldname-ExplanationImageText'), 'display', 'none')
            ksscore.setStyle(ksscore.getHtmlIdSelector('archetypes-fieldname-ExplanationImage'), 'display', 'block')
        elif (explanationvalue == 'none'):
            ksscore.setStyle(ksscore.getHtmlIdSelector('archetypes-fieldname-ExplanationImageText'), 'display', 'none')
            ksscore.setStyle(ksscore.getHtmlIdSelector('archetypes-fieldname-ExplanationImage'), 'display', 'none')
        else:
            ksscore.setStyle(ksscore.getHtmlIdSelector('archetypes-fieldname-ExplanationImageText'), 'display', 'block')
            ksscore.setStyle(ksscore.getHtmlIdSelector('archetypes-fieldname-ExplanationImage'), 'display', 'none') 
    def response1(self, value='default value', imagefield=None, textimagefield=None):
        
        # build HTML
        value = force_unicode(value, 'utf')
        #value = fieldname
        #value = value + 'and templadeId is ' + str(templateId) + ' and macro is ' + str(macro) + ' and uid is ' + str(uid) + ' and target is: ' + str(target) + ' and edit is ' + str(edit) + ' and value is ' + value
        date = str(datetime.now())
        
        
        val = 'Value is:' + str(value) + ' imagefield is ' + str(imagefield) + ' textimagefield is ' + str(textimagefield)
        txt = '<span>value=<b>"%s"</b>' % (val, )
        #content = content % (mymessage, date)

        # KSS specific calls
        ksscore = self.getCommandSet('core')
        zopecommands = self.getCommandSet('zope')
        plonecommands = self.getCommandSet('plone')
        ksscore.replaceInnerHTML('#portal-siteactions', txt)
               
        instance = aq_inner(self.context)
        if (value == 'no value'):
            value = 'none'
        if (value == 'image'):
            ksscore.setStyle(ksscore.getHtmlIdSelector(textimagefield), 'display', 'none')
            ksscore.setStyle(ksscore.getHtmlIdSelector(imagefield), 'display', 'block')
        elif (value == 'none'):
            ksscore.setStyle(ksscore.getHtmlIdSelector(textimagefield), 'display', 'none')
            ksscore.setStyle(ksscore.getHtmlIdSelector(imagefield), 'display', 'none')    
        else:
            ksscore.setStyle(ksscore.getHtmlIdSelector(textimagefield), 'display', 'block')
            ksscore.setStyle(ksscore.getHtmlIdSelector(imagefield), 'display', 'none')
           
        return self.render()
    def response3(self, bla='bla', value='bla', pulldownfield=None):
        # KSS specific calls
        form_data={} 
        nullVal = ['I_DONT_KNOW']
        ksscore = self.getCommandSet('core')
        zopecommands = self.getCommandSet('zope')
        plonecommands = self.getCommandSet('plone')
        instance = aq_inner(self.context)
        ch = instance.getChanged()
        if (ch==True):
            instance.setChanged(False)
        else:
            instance.setChanged(True)
        
         
       
        instance.setSelectedAnswerInResult(value)
        selector = ksscore.getHtmlIdSelector('tutorwebanswerselection1')
        
       
        zopecommands.refreshViewlet(selector,  manager='plone.belowcontenttitle', 
                                    name='tutorweb.questionandanswer')
        #ksscore.setStyle(selector, 'display', 'none')
        return self.render()
       
    def response4(self):
        # KSS specific calls
        #ksscore = self.getCommandSet('core')
        #zopecommands = self.getCommandSet('zope')
        #plonecommands = self.getCommandSet('plone')
        instance = aq_inner(self.context)
        #torender = instance.getSlideImageFormat()
        #if (instance.UpdateSlideText):
        instance.transformSlideText()
            # should render slidetextview!!!
        return self.render()

    def response5(self, value='bla'):
        '''bla bla'''
        # KSS specific calls
        ksscore = self.getCommandSet('core')
        zopecommands = self.getCommandSet('zope')
        #plonecommands = self.getCommandSet('plone')
        instance = aq_inner(self.context)
        #instance.setUpdateSlideText(1)
        #instance.setSlideTextView('bla')
        #instance.setExplanationView('bla')
        #instance.setUpdateSlideText(0)
        #torender = instance.getSlideImageFormat()
        #if (instance.UpdateSlideText):
        #ksscore = self.getCommandSet('core')
        #zopecommands = self.getCommandSet('zope')
        #plonecommands = self.getCommandSet('plone')
        #instance.updateTransformableText()
            # should render slidetextview!!!
        tmp = instance.setSlideTextView1('bla sa da')
        #instance.setSlideTextView2('second time now')
        #instance.setSlideTextView3('bla')
        #time.sleep(10)
        #if (tmp == 'success'):
        selector = ksscore.getHtmlIdSelector('tutorwebtext_view1')
        zopecommands.refreshViewlet(selector,  manager='plone.belowcontenttitle', 
                                    name='tutorweb.SlideView')
        instance.setSlideTextChanged(1)
        return self.render()
    def response6(self, value='bla'):
        '''bla bla'''
        # KSS specific calls
        ksscore = self.getCommandSet('core')
        zopecommands = self.getCommandSet('zope')
        #plonecommands = self.getCommandSet('plone')
        instance = aq_inner(self.context)
        if (instance.SlideTextChanged):
            selector = ksscore.getHtmlIdSelector('tutorwebtext_view1')
            zopecommands.refreshViewlet(selector,  manager='plone.belowcontenttitle', 
                                    name='tutorweb.SlideView')
            instance.setSlideTextChanged(0)
        return self.render()

    def response7(self, value='bla'):
        '''bla bla'''
        # KSS specific calls
        ksscore = self.getCommandSet('core')
        zopecommands = self.getCommandSet('zope')
        #plonecommands = self.getCommandSet('plone')
        instance = aq_inner(self.context)
        tmp = instance.setSlideTextView1('bla sa da')
        selector = ksscore.getHtmlIdSelector('teacher_view1')
        zopecommands.refreshViewlet(selector,  manager='plone.abovecontentbody', 
                                    name='tutorweb.TeacherView')
        instance.setSlideTextChanged(1)
        return self.render()

    def response8(self, value='bla'):
        '''bla bla'''
        # KSS specific calls
        ksscore = self.getCommandSet('core')
        zopecommands = self.getCommandSet('zope')
        #plonecommands = self.getCommandSet('plone')
        instance = aq_inner(self.context)
        if (instance.SlideTextChanged):
            selector = ksscore.getHtmlIdSelector('teacher_view1')
            zopecommands.refreshViewlet(selector,  manager='plone.abovecontentbody', 
                                    name='tutorweb.TeacherView')
            instance.setSlideTextChanged(0)
        return self.render()
