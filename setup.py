import os
from distutils.core import setup

VERSION = '0.1'

setup(
    name='django-condor',
    version=VERSION,
    description='A simple bridge between Condor and django',
    long_description=file(
        os.path.join(os.path.dirname(__file__), 'README')
    ).read(),
    author="Daniel O'Donovan",
    author_email='odonovan@hkl.hms.harvard.edu',
    license='BSD',
    url='http://github.com/danodonovan/django-condor',
    classifiers=[
        'Development Status :: 1 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Framework :: Django',
        'Environment :: Web Environment',
    ],
    packages=[
        'condor',
    ],
    package_data={
        'condor': ['test_scripts/*']
    }
)



