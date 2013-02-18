#-*- coding: UTF-8 -*-
import tempfile
import os
from config import *

def ps2png(ps):
	"""Input: Postscript string
	   Output: PNG string"""
	tmp_fd, tmp_absname = tempfile.mkstemp(text=True)
	os.write(tmp_fd, ps)
	x = os.spawnlp(os.P_WAIT, 'pstoimg', 'pstoimg', '-type', 'png', '-flip',    
	'cw',  tmp_absname)
	os.close(tmp_fd)
	os.unlink(tmp_absname)
	if x:
	 	raise RunTimeError, "Can't convert PS to PNG"
	doojaa = tmp_absname+'.png'
	pngfile = open(doojaa) #FIXME Hvað skal gera ef þetta misheppnast?
	x = pngfile.read()
	pngfile.close()
	os.unlink(doojaa)
	return x

