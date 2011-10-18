import datetime
from django.db import models

from condor.condor_tools import condor_status, condor_submit

class CondorHost( models.Model ):
    """ Hold details for the condor host """
    hostname = models.CharField( max_length=256 )
    username = models.CharField( max_length=256 )
    password = models.CharField( max_length=256 )
    port     = models.PositiveIntegerField( default=22 )
    env      = models.TextField( blank=True )
    remotedir= models.CharField( max_length=256 )

class AbstractJobBaseClass( models.Model ):
    """ Abstract Base Class for a condor job
    """
    pid     = models.PositiveIntegerField( default=0 )

    status  = models.CharField( max_length=32, default='Not Submitted' )
    update  = models.DateTimeField( auto_now_add=True )

    history = models.TextField()

    host    = models.ForeignKey( 'CondorHost', null=True )

    name    = models.CharField( blank=True )
    timeout = models.IntegerField( default=1800 )

    ram_min = models.CharField( default='2048 * GB')

    def update_status( self ):
        """ Update the job status for the given pid """
        if not self.pid: return

        if not self.host:
            self.status = condor_status( self.pid )
        else:
            h = self.host
            self.status = condor_status( self.pid,
                hostname=h.hostname, username=h.username, password=h.password,
                port=h.port, env=h.env, remotedir=h.remotedir )

        self.update = datetime.datetime.now()
        self.store_history()
        self.save()

    def store_history( self, save=False ):
        """ store update in history """
        if not self.history:
            self.history = repr( {self.update:self.status} )
            return
        history = eval( self.history )
        if not history.has_key( self.update ):
            history[ self.update ] = self.status
        self.history = repr( history )
        if save: self.save()

    def submit( self ):
        """ submit a condor job """
        if self.pid: return
        if not self.submit_script: return

        if not self.host:
            self.pid = condor_submit( self.submit_script )
        else:
            h = self.host
            self.pid = condor_submit( self.submit_script,
                hostname=h.hostname, username=h.username, password=h.password,
                port=h.port, env=h.env, remotedir=h.remotedir )

        self.save()
        self.update_status()


    class Meta:
        abstract = True

class CondorJobs( AbstractJobBaseClass ):
    """ CondorJobs - a model to control and track a single condor job - submitted locally
        or on a remote scheduler.
    """
    submit_script = models.FileField( upload_to='condor_jobs', blank=False )
    executable    = models.FileField( upload_to='condor_exec', blank=True )


