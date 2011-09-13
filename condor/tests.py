"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

import time

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
        env = s.GRID_ENV['osg']
        (out, err) = call_condor( 'condor_q', hostname='shell.nebiogrid.org', env=env )
        self.assertIn( '-- Submitter:', out )


class CondorJobTest(TestCase):
    """ """

    def test_simple_job(self):
        """ """
        j = CondorJobs()
        j.submit_script = 'test_scripts/test.sh'
        j.save()

        j.update_status()

        self.assertEqual( 'Not Submitted', j.status )

        # 'call_condor error cmd: condor_submit test_scripts/test.sh'
        with self.assertRaises(CondorError):
            j.submit()

    def test_host(self):

        h = CondorHost( hostname='shell.nebiogrid.org', username='odonovan' )
        h.save()

    def test_remote_host_no_env(self):

        h = CondorHost( hostname='shell.nebiogrid.org', username='odonovan' )
        h.save()

        self.assertEqual( 'shell.nebiogrid.org', h.hostname )
        self.assertEqual( 'odonovan', h.username )

        j = CondorJobs( host=h, submit_script='test_scripts/test.sh' )
        j.save()

        self.assertEqual( 'Not Submitted', j.status )
        self.assertEqual( 'shell.nebiogrid.org', j.host.hostname )
        self.assertEqual( 'odonovan', j.host.username )

        with self.assertRaises(CondorError):
            j.submit()

    def test_remote_host_with_env(self):

        h = CondorHost( hostname='shell.nebiogrid.org', username='odonovan',
            env=s.GRID_ENV['osg'] )
        h.save()

        self.assertEqual( 'shell.nebiogrid.org', h.hostname )
        self.assertEqual( 'odonovan', h.username )

        j = CondorJobs( host=h, submit_script='test_scripts/test.sh' )
        j.save()

        self.assertEqual( 'Not Submitted', j.status )
        self.assertEqual( 'shell.nebiogrid.org', j.host.hostname )
        self.assertEqual( 'odonovan', j.host.username )

        with self.assertRaises(CondorError):
            j.submit()

    def test_remote_host_with_env_and_remote_file(self):

        h = CondorHost( hostname='shell.nebiogrid.org', username='odonovan',
            env=s.GRID_ENV['osg'], remotedir='/home/odonovan/sandbox/projects/py_condor/tests' )
        h.save()

        self.assertEqual( 'shell.nebiogrid.org', h.hostname )
        self.assertEqual( 'odonovan', h.username )

        j = CondorJobs( host=h, submit_script='test.submit' )
        j.save()

        self.assertEqual( 'Not Submitted', j.status )
        self.assertEqual( 'shell.nebiogrid.org', j.host.hostname )
        self.assertEqual( 'odonovan', j.host.username )

        j.submit()

        while j.status[0] != 'Completed':
            time.sleep( 4 )
            j.update_status()








