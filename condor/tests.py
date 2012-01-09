"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

import time

from django.test import TestCase
from django.conf import settings as s

from condor.models import CondorJob, CondorHost
from condor.condor_tools import call_condor, CondorError

class ToolTest(TestCase):
    """ Testing the condor cli communicate tools """

    def test_nonsense_call_condor( self ):
        """ Make sure that nonsense test fails """
        with self.assertRaises(CondorError):
            (out, err) = call_condor( 'this', 'is', 'a', 'test' )

    def test_connection_call_condor( self ):
        """ Make sure that nonsense test fails """
        # assert that this doesn't raise an error
        (out, err) = call_condor( 'ls',  hostname=s.TEST_CONDOR_INFO['hostname']  )

    def test_remote_hostname_call_condor( self ):
        """ Test that the machine being connected to is itself - may fail! """
        (out, err) = call_condor( 'hostname', hostname=s.TEST_CONDOR_INFO['hostname'], env=None )
        self.assertEqual( out.strip(), s.TEST_CONDOR_INFO['hostname'] )

    def test_remote_call_condor( self ):
        """ Test condor on established grid """
        (out, err) = call_condor( 'condor_q', hostname=s.TEST_CONDOR_INFO['hostname'], env=s.GRID_ENV['osg'] )
        self.assertIn( '-- Submitter:', out )

class CondorJobTest(TestCase):
    """ Testing for the Condor django models """

    def test_simple_job(self):
        """ """
        j = CondorJob()
        j.submit_script = s.TEST_CONDOR_INFO['submit_script']
        j.save()

        j.update_status()

        self.assertEqual( 'Not Submitted', j.status )

        # 'call_condor error cmd: condor_submit test_scripts/test.sh'
        with self.assertRaises(CondorError):
            j.submit()

    def test_host(self):

        h = CondorHost( hostname=s.TEST_CONDOR_INFO['hostname'], username=s.TEST_CONDOR_INFO['username'] )
        h.save()

    def test_remote_host_no_env(self):

        h = CondorHost( hostname=s.TEST_CONDOR_INFO['hostname'], username=s.TEST_CONDOR_INFO['username'] )
        h.save()

        self.assertEqual( s.TEST_CONDOR_INFO['hostname'], h.hostname )
        self.assertEqual( s.TEST_CONDOR_INFO['username'], h.username )

        j = CondorJob( host=h, submit_script=s.TEST_CONDOR_INFO['submit_script'] )
        j.save()

        self.assertEqual( 'Not Submitted', j.status )
        self.assertEqual( s.TEST_CONDOR_INFO['hostname'], j.host.hostname )
        self.assertEqual( s.TEST_CONDOR_INFO['username'], j.host.username )

        with self.assertRaises(CondorError):
            j.submit()

    def test_remote_host_with_env(self):

        h = CondorHost( hostname=s.TEST_CONDOR_INFO['hostname'], username=s.TEST_CONDOR_INFO['username'],
            env=s.GRID_ENV['osg'] )
        h.save()

        self.assertEqual( s.TEST_CONDOR_INFO['hostname'], h.hostname )
        self.assertEqual( s.TEST_CONDOR_INFO['username'], h.username )

        j = CondorJob( host=h, submit_script=s.TEST_CONDOR_INFO['submit_script'] )
        j.save()

        self.assertEqual( 'Not Submitted', j.status )
        self.assertEqual( s.TEST_CONDOR_INFO['hostname'], j.host.hostname )
        self.assertEqual( s.TEST_CONDOR_INFO['username'], j.host.username )

        with self.assertRaises(CondorError):
            j.submit()

    def test_remote_host_with_env_and_remote_file(self):

        h = CondorHost( hostname=s.TEST_CONDOR_INFO['hostname'], username=s.TEST_CONDOR_INFO['username'],
            env=s.GRID_ENV['osg'], remotedir=s.TEST_CONDOR_INFO['remotedir'] )
        h.save()

        self.assertEqual( s.TEST_CONDOR_INFO['hostname'], h.hostname )
        self.assertEqual( s.TEST_CONDOR_INFO['username'], h.username )

        j = CondorJob( host=h, submit_script=s.TEST_CONDOR_INFO['submit_script'] )
        j.save()

        self.assertEqual( 'Not Submitted', j.status )
        self.assertEqual( s.TEST_CONDOR_INFO['hostname'], j.host.hostname )
        self.assertEqual( s.TEST_CONDOR_INFO['username'], j.host.username )

        j.submit()

        nsecs, maxsecs = 0, 60 * 2
        while j.status[0] != 'Completed' and nsecs < maxsecs:
            j.update_status()

            # add time control
            time.sleep( 4 )
            nsecs += 4

        # check that we didn't time out
        self.assertEqual( j.status[0], 'Completed' )







