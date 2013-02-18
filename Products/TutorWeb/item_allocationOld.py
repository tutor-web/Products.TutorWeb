#
##################################################################
#
# This is item_allocation.py
# Collection of python scripts for allocating quiz items to students
#
##################################################################
#
#
##################################################################
#
# item_allocation: the entry routine for item allocation
# calling method:
#      selectedindex = item_allocation(numansvec,corransvec,grade)
#
# arguments: numansvec=vector of tot num ans to ea lecture
#            corransvec=vector of num correct ans to ea lecture
#            grade=student's current grade
#            q=a probability parameter (0<q<1 - strict ineq)
# output: index of the chosen item
#
##################################################################
#
import random
from config import NUMPY
if NUMPY:
  from numpy import *

import os

def item_allocation(numansvec,corransvec,grade, tex_fd="tempfile", debug=False):
  qparam=0.925                            # a fundamental parameter
  numquestions=len(numansvec)
  difficulty=zeros(numquestions)     # becomes index of difficulty
  for qindex in arange(0,len(numansvec)):
   if numansvec[qindex] >5:            # be sensible even if few answers
     difficulty[qindex]=1.-float(corransvec[qindex])/numansvec[qindex]
   else:
     if grade<0.:                      # make sure low-n items gets placed at extremes
       difficulty[qindex]=(numansvec[qindex]-corransvec[qindex]/2.+random.uniform(0.,1.))/100.
     else:
       difficulty[qindex]=1.-(numansvec[qindex]-corransvec[qindex]/2.+random.uniform(0.,1.))/100.
  ranks=ia_ranking(difficulty)
  pdf=ia_pdf(numquestions,grade,qparam)
  probvec=pdf[ranks]                    # reorder pdf to lecture order
#  print numansvec
#  print corransvec
#  print difficulty
#  print pdf
#  print ranks
#  print probvec
  utmp=random.uniform(0, 1)
  selectedindex=ia_inverse_cdf(probvec,utmp)
  if (debug):
    os.write(tex_fd, '########################################\n')
    os.write(tex_fd, 'output from item_allocation\n')
    os.write(tex_fd, 'selected index: ' + str(selectedindex) + '\n')
    os.write(tex_fd, 'grade is: ' + str(grade) + '\n')
    os.write(tex_fd, 'utmp: ' + str(utmp) + '\n')
    counter = 0
    os.write(tex_fd, 'index\tnumrequested\tnumcorrect\n')
    for i in numansvec:
      os.write(tex_fd, str(counter) + '\t') 
      os.write(tex_fd, str(i) + '\t')
      os.write(tex_fd, str(corransvec[counter]) + '\n')
      counter = counter + 1
    os.write(tex_fd, 'end output from item_allocation\n')
#  print(utmp,selectedindex)
  return(selectedindex)
# item_allocation -- a placeholder
#def item_allocation(numansvec,corransvec,grade):
#  selectedindex = random.randint(0, (len(numansvec)-1))
#  return(selectedindex)
#
# find the inverse cdf for a given pdf and given u=F(x)
#
def ia_inverse_cdf(pdf,u):
  i = 0
  cumsum=pdf[0]
  while u>cumsum:
    i+=1
    cumsum+=pdf[i]
  return(i)
# a simple ranking method
def ia_ranking(vector):
    return ia_ordering(ia_ordering(vector))
# a simple ordering method
def ia_ordering(vector):
    return sorted(range(len(vector)), key=vector.__getitem__)
#
#
##################################################################
#
# ia_pdf: a simple *dynamic* item allocation pdf
# arguments: I=number of items
#            g=student's current grade
#            q=a probability parameter (0<q<1 - strict ineq)
# output: pdf for each item, according to rank 0 to I-1 (or 1 to I)
#
##################################################################
#
def ia_pdf(I,g,q):
  qrankvec=arange(0,I)   # possible Q-ranks
  pdf0=ones(I)/I         # define uniform pdf
  pdf1=zeros(I)          # from numpy
  pdf2=zeros(I)          # from numpy
  pdf=zeros(I)           # from numpy
  a=(-2.*g)              # 1 at -1/2, 0 at 0
  b1=(2.*(g+1./2.))      # 0 at -1/2, 1 at 0
  b2=(1.-g)              # 1 at 0, 0 at 1
  c=g                    # 0 at 0, 1 at 1
  pdf1=q**qrankvec       # hi wt on easy
  pdf2=q**(I-1.-qrankvec) # reverse
  pdf1=pdf1/sum(pdf1)    # scale to be a pdf
  pdf2=pdf2/sum(pdf2)  
#  for i in rank_vec:
#     print i,
#     if g<0.:
#      pdf[i]=pdf1[i]*a + pdf0[i]*b1
#     else:
#       pdf[i]=pdf0[i]*b2 + pdf2[i]*c
  if g<0.:
    pdf=pdf1*a + pdf0*b1
  else:
    pdf=pdf0*b2 + pdf2*c
#     pdfsum=pdfsum+pdf[i]
#  print pdf0
#  print pdf1
#  print pdf2
#  print pdf
#  for i in rank_vec:
#     pdf[i]=pdf[i]/pdfsum # this breaks - why?
  return(pdf)

