"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

import time

from django.test import TestCase
from django.conf import settings as s

<<<<<<< HEAD
from condor.models import CondorJob, CondorHost
=======
from condor.models import CondorScriptedJob, CondorHost
>>>>>>> master
from condor.condor_tools import call_condor, CondorError


## get TEST_CONDOR_INFO settings - or DEFAULT
try:
    CONDOR_INFO = s.TEST_CONDOR_INFO
except AttributeError:
    testHostname = 'localhost'
    testUsername = 'none'
    testPassword = 'none'
    testRemotedir = 'none'
    testSubmitScript = 'none'
else:
    testHostname = s.TEST_CONDOR_INFO.get('hostname', 'localhost')
    testUsername = s.TEST_CONDOR_INFO.get('username', 'none')
    testPassword = s.TEST_CONDOR_INFO.get('password', 'none')
    testRemotedir = s.TEST_CONDOR_INFO.get('remotedir', 'none')
    testSubmitScript = s.TEST_CONDOR_INFO.get('submit_script', 'none')

try:
    GRID_ENV = s.GRID_ENV
except AttributeError:
    GRID_ENV = None
else:
    GRID_ENV = s.GRID_ENV.get('default', None)

class ToolTest(TestCase):
    """ Testing the condor cli communicate tools """

    def test_nonsense_call_condor(self):
        """ Make sure that nonsense test fails """
        with self.assertRaises(CondorError):
            (out, err) = call_condor('this', 'is', 'a', 'test')

    def test_connection_call_condor(self):
        """ Make sure that nonsense test fails """
        # assert that this doesn't raise an error
        (out, err) = call_condor('ls',  hostname=testHostname )

    def test_remote_hostname_call_condor(self):
        """ Test that the machine being connected to is itself - may fail! """

        (out, err) = call_condor('hostname', hostname=testHostname, env=None)
        self.assertEqual(out.strip(), testHostname)

    def test_remote_call_condor(self):
        """ Test condor on established grid """
        (out, err) = call_condor('condor_q', hostname=testHostname, env=GRID_ENV)
        self.assertIn('-- Submitter:', out)

class CondorScriptedJobTest(TestCase):
    """ Testing for the Condor django models """

    def test_simple_job(self):
        """ """

        j = CondorJob()
        j.submit_script = testSubmitScript
        j.save()

        j.update_status()

        self.assertEqual('Not Submitted', j.status)

        # 'call_condor error cmd: condor_submit test_scripts/test.sh'
        with self.assertRaises(CondorError):
            j.submit()

    def test_host(self):


        h = CondorHost(hostname=testHostname, username=testUsername)
        h.save()

    def test_remote_host_no_env(self):


        h = CondorHost(hostname=testHostname, username=testUsername)
        h.save()

        self.assertEqual(testHostname, h.hostname)
        self.assertEqual(testUsername, h.username)

        j = CondorJob(host=h, submit_script=testSubmitScript)
        j.save()

        self.assertEqual('Not Submitted', j.status)
        self.assertEqual(testHostname, j.host.hostname)
        self.assertEqual(testUsername, j.host.username)

        with self.assertRaises(CondorError):
            j.submit()

    def test_remote_host_with_env(self):

        h = CondorHost(hostname=testHostname, username=testUsername,
            env=s.GRID_ENV['osg'])
        h.save()

        self.assertEqual(testHostname, h.hostname)
        self.assertEqual(testUsername, h.username)

        j = CondorJob(host=h, submit_script=testSubmitScript)
        j.save()

        self.assertEqual('Not Submitted', j.status)
        self.assertEqual(testHostname, j.host.hostname)
        self.assertEqual(testUsername, j.host.username)

        with self.assertRaises(CondorError):
            j.submit()

    def test_remote_host_with_env_and_remote_file(self):

        h = CondorHost(hostname=testHostname, username=testUsername,
            env=s.GRID_ENV['osg'], remotedir=testRemotedir)
        h.save()

        self.assertEqual(testHostname, h.hostname)
        self.assertEqual(testUsername, h.username)


        j = CondorJob(host=h, submit_script=testSubmitScript)
        j.save()

        self.assertEqual('Not Submitted', j.status)
        self.assertEqual(testHostname, j.host.hostname)
        self.assertEqual(testUsername, j.host.username)

        j.submit()

        nsecs, maxsecs = 0, 60 * 2
        while j.status[0] != 'Completed' and nsecs < maxsecs:
            j.update_status()

            # add time control
            time.sleep(4)
            nsecs += 4

        # check that we didn't time out
        self.assertEqual(j.status[0], 'Completed')







