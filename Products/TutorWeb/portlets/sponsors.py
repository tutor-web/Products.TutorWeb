"""Define a portlet used to show tutor-web sponsors. This follows the patterns from
plone.app.portlets.portlets. Note that we also need a portlet.xml in the
GenericSetup extension profile to tell Plone about our new portlet.
"""

import random

from zope import schema
from zope.component import getMultiAdapter
from zope.formlib import form
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider

from DateTime import DateTime
from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName

#from optilux.cinemacontent.interfaces import IPromotion
#from optilux.cinemacontent.interfaces import IBannerProvider
#from optilux.cinemacontent import CinemaMessageFactory as _
#from Products.TutorWeb import PloneMessageFactory as _
from Products.CMFPlone import PloneMessageFactory as _ 
# This interface defines the configurable options (if any) for the portlet.
# It will be used to generate add and edit forms.
from Acquisition import aq_parent

class ISponsorsPortlet(IPortletDataProvider):

    count = schema.Int(title=_(u'Number of promotions to display'),
                       description=_(u'Maximum number of promotions to be shown'),
                       required=True,
                       default=5)
                       
    randomize = schema.Bool(title=_(u"Randomize promotions"),
                            description=_(u"If enabled, promotions to show will be picked randomly. "
                                            "If disabled, newer promotions will be preferred."),
                            default=False)
                            
    sitewide = schema.Bool(title=_(u"Sitewide promotions"),
                            description=_(u"If enabled, promotions from across the site will be found. "
                                           "If disabled, only promotions in this folder and its "
                                           "subfolders are eligible."),
                            default=False)

# The assignment is a persistent object used to store the configuration of
# a particular instantiation of the portlet.

class Assignment(base.Assignment):
    implements(ISponsorsPortlet)

    def __init__(self, count=5, randomize=False, sitewide=False):
        self.count = count
        self.randomize = randomize
        self.sitewide = sitewide

    @property
    def title(self):
        return _(u"Sponsors")
        #return 'Sponsors'
# The renderer is like a view (in fact, like a content provider/viewlet). The
# item self.data will typically be the assignment (although it is possible
# that the assignment chooses to return a different object - see 
# base.Assignment).

class Renderer(base.Renderer):

    # render() will be called to render the portlet
    
    render = ViewPageTemplateFile('sponsors.pt')
       
    # The 'available' property is used to determine if the portlet should
    # be shown.
        
    @property
    def available(self):
        return len(self._data()) > 0

    # To make the view template as simple as possible, we return dicts with
    # only the necessary information.

    def sponsors(self):
        for brain in self._data():
            promotion = brain.getObject()
            #banner_provider = IBannerProvider(promotion)
            yield dict(title=promotion.getTitle(),
                       sponsorurl=promotion.getSponsorurl(),
                       url=brain.getURL(),
                       sponsortext=promotion.getRawSponsortext(),
                       sponsorlogo=promotion.getSponsorlogo())
        
    # By using the @memoize decorator, the return value of the function will
    # be cached. Thus, calling it again does not result in another query.
    # See the plone.memoize package for more.
        
    @memoize
    def _data(self):
        context = aq_inner(self.context)
        limit = self.data.count
        mytype = context.Type()
        #query = dict(object_provides = IPromotion.__identifier__)
        query = {}
        query['Type'] = 'Sponsor'
        if not self.data.sitewide:
            pathlevel=1
            if (mytype == 'Lecture'):
                tut = aq_parent(context)
                basepath = '/'.join(tut.getPhysicalPath())
            elif (mytype == 'Slide'):
                lec = aq_parent(context)
                tut = aq_parent(lec)
                basepath = '/'.join(tut.getPhysicalPath())
            #elif (mytype == 'Course'):
            #    dep = aq_parent(context)
            #    basepath = '/'.join(dep.getPhysicalPath())
            else:
                basepath = '/'.join(context.getPhysicalPath())
            query['path'] = {'query' : basepath, 'depth' : pathlevel}
        if not self.data.randomize:
            query['sort_on'] = 'modified'
            query['sort_order'] = 'reverse'
            query['sort_limit'] = limit
        
        # Ensure that we only get active objects, even if the user would
        # normally have the rights to view inactive objects (as an
        # administrator would)
        #query['effectiveRange'] = DateTime()
        
        catalog = getToolByName(context, 'portal_catalog')
        if (mytype == 'Course'):
            '''Find all sponsors in tutorials which belong to the course, be careful not to repeat them'''
            tutorials = context.getTutorials()
            results = []
            urls = []
            for tut in tutorials:
                basepath = '/'.join(tut.getPhysicalPath())
                query['path'] = {'query' : basepath, 'depth' : 1}
                tutresults = catalog(query)
                for res in tutresults:
                    sponsor = res.getObject()
                    sponsorurl = sponsor.getSponsorurl()
                    if (sponsorurl not in urls):
                        urls.append(sponsorurl)
                        results.append(res)
                
                
        else:
            results = catalog(query)
        
        promotions = []
        if self.data.randomize:
            promotions = list(results)
            promotions.sort(lambda x,y: cmp(random.randint(0,200),100))
            promotions = promotions[:limit]
        else:
            promotions = results[:limit]
        
        return promotions

# Define the add forms and edit forms, based on zope.formlib. These use
# the interface to determine which fields to render.

class AddForm(base.AddForm):
    form_fields = form.Fields(ISponsorsPortlet)
    label = _(u"Add Sponsor portlet")
    #label = "Add Sponsor portlet"
    description = _(u"This portlet displays tutor-web sponsors.")
    #description = "this portlet displays tutor-web sponsor."
    # This method must be implemented to actually construct the object.
    # The 'data' parameter is a dictionary, containing the values entered
    # by the user.

    def create(self, data):
        assignment = Assignment()
        form.applyChanges(assignment, self.form_fields, data)
        return assignment

class EditForm(base.EditForm):
    form_fields = form.Fields(ISponsorsPortlet)
    label = _(u"Edit Sponsor portlet")
    #label = "Edit Sponsor portlet"
    description = _(u"This portlet displays tutor-web sponsors.")
    #description = "This portlet displays tutor-web sponsors."
