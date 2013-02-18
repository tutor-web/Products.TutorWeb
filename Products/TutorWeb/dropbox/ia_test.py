#
##################################################################
#
# test the item selection schemes
#
##################################################################
#
# Run these with
#execfile("ia_test.py")
from numpy import *
import random
execfile("item_allocation.py")
# evaluate the pdf generated
I=25
#numansvec=zeros(I)
#corransvec=zeros(I)
numansvec=array([7.,9.,14.,6.,12.,3.,1.,13.,5.,5.,8.,9.,11.,9.,8.,10.,9.,9.,5.,7.,5.,9.,5.,10.,8.])
corransvec=array([4.,5.,3.,2.,3.,0.,0.,6.,2.,3.,2.,4.,4.,2.,5.,1.,3.,3.,4.,2.,1.,3.,1.,5.,3.])

grade=1
# a - simple call
selectedindex = item_allocation(numansvec,corransvec,grade)
# b - check that we get the right histogram
B=10000
freq=zeros(I)
b=0
while b<B:
  freq[item_allocation(numansvec,corransvec,grade)]+=1
  b+=1
print 'Relative frequency from B=',
print B,
print 'simulations'
print freq/sum(freq)


#
##################################################################
#
# test the pdf computations
#
##################################################################
#
#execfile("ia_pdf.py")
#pdf=ia_pdf(25.,-0.5,0.5)
#print 'I=25 g=-0.5 q=0.5:'
#print pdf 
#pdf=ia_pdf(25.,0.0,0.5)
#print 'I=25 g=0 q=0.5:'
#print pdf 
#pdf=ia_pdf(25.,0.5,0.5)
#print 'I=25 g=0.5 q=0.5:'
#print pdf 
