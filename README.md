django-condor
=============

This is a small django app designed to ease the integration of the condor high performance
computing job submission system and django based websites.

Requires
--------

django and python, but also paramiko - but only if you need to connect to remote job
scheduling machines (roll your own ssh seems a little flaky).

Install
-------

This should be as simple as `python setup.py install`

You will need to ensure that 'condor' has been included in you INSTALLED_APPS in
settings.py Remeber to run `python manage.py syncdb' to create the correct DB entries.

Usage
-----

You will likely need to set some environment variables in order to communicate with the
condor instance on your submit node. Setting non-django environment variables from django
isn't very pleasant so django-condor provides a mechanism for you to do this - see
`CONDOR_SETTINGS` in settings.py

After installing you will need to add `condor` to your `INSTALLED_APPS` and synchronise the 
database with 
`python manage.py syncdb`

For debugging, the entire django-condor DB can be dropped with
`python manage.py reset condor`

For testing and general convenience, the settings for connecting to your condor submission
node can be held in a dict in settings.py that looks similar to:

CONDOR_SETTINGS = {
    'hostname'      : <host name or IP>,
    'username'      : <username to connect with>,
    'password'      : <password - can be None if local or password free ssh set>,
    'remotedir'     : <remote directory in which to run 'condor_submit'>,
    'submit_script' : <local submit script>,
	'env' 			: <a dictionary containg any environment variables that may need to be set>
}

Contact
-------
Written by Dan O'Donovan as part of the SBGrid portal project.
