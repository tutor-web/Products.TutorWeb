from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='Products.TutorWeb',
      version=version,
      description="Web-based education system",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='',
      author_email='',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*- 
          "MySQL-python",
          'collective.lead>=1.0b3,<2.0dev',
          'Products.DataGridField>=1.8a1',
	  'numpy',         
          
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
