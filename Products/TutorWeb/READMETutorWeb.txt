# download plone
http://plone.org/products/plone
Linux example
Unified installer
 f.x. 
Goto Plone unified directory:
cd /home/audbjorg/Plone-3.1.6-r2-UnifiedInstaller

To install:
sudo or do su
./install.sh zeo or ./install.sh standalone
Will create Plone in /opt
For more info and options see README.txt 
obtain Username: admin
  Password: wufhSDXd

Go to
/opt/Plone-3.1/zeocluster
of if one instance
/opt/Plone-3.1/zinstance

see password file
Port 8080 virkt?

efore you start Plone, you should review the settings in:

  /opt/Plone-3.1/zeocluster/buildout.cfg

Adjust the ports Plone uses before starting the site, if necessary,
and run /opt/Plone-3.1/zeocluster/bin/buildout
to apply settings.

To start Plone, issue the following command in a terminal window:

  sudo /opt/Plone-3.1/zeocluster/bin/plonectl start

To stop Plone, issue the following command in a terminal window:

  sudo /opt/Plone-3.1/zeocluster/bin/plonectl stop


Copy Data.fs ../var/

Add mime types
LaTeX, R, R-LaTeX

Copy TutorWeb, DataGridField to Products dir.

copy:
/opt/Plone-3.0.2/zinstance/Products/PortalTransforms/transforms/tex_to_html.py to transforms dir.

Fix desktop
logo
set the navigation
types

# REMEMBEr
# must change bin directories

SOFTWARE
R
fig2dev
latex2html
gnuplot
With tutor-web
txt2latex.htm
struct2latex, StructuredText

rest2latex - docutils

imgtops (not used now)
latex
dvips
ps2pdf

REMEMBER
changes in DataGridField
1. DataGridWidget.py changed
In skin:
2. datagridwidget_view_row.pt
3. datagrid_text_cell.pt
4. datagridwidget.pt
 DID NOT WORK, copied the whole thing.
5. REMEMBER changes to the CMFPlonse/skins/plone_login
join_form.cpt.metadata.orig  join_form.cpt.orig  register.cpy.orig

Check:
tutorwebanswerselection1.pt
Lot of defines are they really needed????

chow plone TutorWeb directory
HEADER = 'bitmap(file="/dev/stdout")\r\n'n 
sponsor text can't include icelandic characters!!
REM:
add and change what group teacher can do...
FIXME
