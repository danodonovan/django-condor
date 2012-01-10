"""
django-condor
-------------

django-condor is a Python based Django application for managing and
running Condor jobs on a grid through the Django web-framework.

Using django-condor
```````````````````

::

    from condor import CondorHost, CondorJob, GB

    # create a condor host object
    h = CondorHost( hostname="my.host",
                    username="myname", )
                    remotedir="/path/to/data")
    h.env={"PATH":"/path/to/condor/bin",
      "CONDOR_CONFIG":"/path/to/config"}
    h.save()

    # create a condor job object
    j = CondorJob( host=h )
    j.name("testJob")
    j.timeout(1800)
    j.exec("test_executable")
    j.args(["foo","bar",42])
    j.ram_min(2048 * GB)
    j.save()

    ...

    # retrieve that job elsewhere
    j = CondorJob.objects.get(name="testJob")

    # submit the job to the scheduler
    j.submit()
    # wait some time for remote job submission
    j.update_status()


Links
`````

* `website <https://portal.sbgrid.org/>`_
* `documentation <http://tbd>`_
* `development version
  <http://github.com/danodonovan/django-condor>`_
"""
import os
from distutils.core import setup

VERSION = '0.2'

setup(
    name='django-condor',
    version=VERSION,
    description='A simple bridge between Condor and django',
    long_description=file(
        os.path.join(os.path.dirname(__file__), 'README.md')
    ).read(),
    author="Daniel O'Donovan",
    author_email='odonovan@hkl.hms.harvard.edu',
    license='BSD',
    url='http://github.com/danodonovan/django-condor',
    classifiers=[
        'Development Status :: %s - Alpha' % VERSION,
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
    },
    install_requires=[
        'Django>=1.2',
    ],
)



