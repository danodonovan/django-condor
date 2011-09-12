"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.conf import settings as s

from condor.models import CondorJobs, CondorHost
from condor.condor_tools import call_condor, CondorError

class ToolTest(TestCase):
    """ Testing the condor cli communicate tools """

    def test_nonsense_call_condor( self ):
        """ Make sure that nonsense test fails """
        with self.assertRaises(CondorError):
            (out, err) = call_condor( 'this', 'is', 'a', 'test' )

    def test_connection_call_condor( self ):
        """ Make sure that nonsense test fails """
        (out, err) = call_condor( 'ls',  hostname='shell.nebiogrid.org'  )

    def test_remote_no_env_call_condor( self ):
        with self.assertRaises(CondorError):
            (out, err) = call_condor( 'condor_q', hostname='shell.nebiogrid.org' )

    def test_remote_hostname_call_condor( self ):
        (out, err) = call_condor( 'hostname', hostname='shell.nebiogrid.org', env=None )
        self.assertEqual( out.strip(), 'shell.nebiogrid.org' )

    def test_remote_call_condor( self ):
        env = s.OSG_CLUSTER_ENV
        (out, err) = call_condor( 'condor_q', hostname='shell.nebiogrid.org', env=env )
        self.assertIn( '-- Submitter:', out )


class CondorJobTest(TestCase):
    """ """

    def test_simple_job(self):
        """ """
        j = CondorJobs()
        j.submit_script = 'test_scripts/test.sh'
        j.save()

        j.update()

        self.assertEqual( 'Not Submitted', j.status )

    def test_host(self):
        # with self.assertRaises(
        h = CondorHost()
        h.save()

    def test_remote_job(self):
        pass

