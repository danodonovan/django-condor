import datetime
from django.db import models

from condor import condorBinaryUpload, condorScriptUpload
import condor.fields as custom_fields
from condor.condor_tools import condor_status, condor_submit, condor_classad_template

class CondorHost( models.Model ):
    """ Hold details for the condor host """
    hostname = models.CharField( max_length=256 )
    username = models.CharField( max_length=256 )
    password = models.CharField( max_length=256 )
    port     = models.PositiveIntegerField( default=22 )
    env      = models.TextField( blank=True )
    remotedir= models.CharField( max_length=256 )

    class Meta:
        verbose_name_plural = 'CondorHosts'

class AbstractJobBaseClass( models.Model ):
    """ Abstract Base Class for a condor job
    """
    pid     = models.PositiveIntegerField( default=0 )
    name    = models.CharField( blank=True )

    status  = models.CharField( max_length=32, default='Not Submitted' )
    update  = models.DateTimeField( auto_now_add=True )

    history = models.TextField()

    host    = models.ForeignKey( 'CondorHost', null=True )

    executable    = models.FileField( upload_to=condorBinaryUpload, blank=True )

    # if this isn't set by CondorScriptedJob it is created by CondorJob
    classAd = models.FileField( upload_to=condorScriptUpload, blank=False )

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

class CondorScriptedJob( AbstractJobBaseClass ):
    """ CondorScriptedJob - a model to control and track a single condor job defined by
            a script. Submitted locally or on a remote scheduler.
    """

    class Meta:
        verbose_name_plural = 'CondorScriptedJobs'

def CondorJob( AbstractJobBaseClass ):
    """ CondorJob - a model to control and track a single condor job defined by
            values given through django.
    """
    # these values job classAds
    Arguments               = custom_fields.DictionaryField()
    Output                  = models.CharField( blank=True )
    Error                   = models.CharField( blank=True )
    Log                     = models.CharField( blank=True )
    Should_transfer_files   = models.CharField( blank=True )
    When_to_transfer_output = models.CharField( blank=True )
    Transfer_output_files   = models.CharField( blank=True )
    Notification            = models.CharField( blank=True )
    Priority                = models.CharField( blank=True )
    Requirements            = models.CharField( blank=True )
    Periodic_remove         = models.CharField( blank=True )
    X509userproxy           = models.CharField( blank=True )
    Universe                = models.CharField( blank=True )



    timeout     = models.IntegerField( default=1800 )

    ram_min = models.CharField( default=2048 * GB )

    class Meta:
        verbose_name_plural = 'CondorJobs'

    def _write_classad( self ):
        # condor_classad_template
        pass

    # Arguments               = ${arguments}
    # Output                  = ${stdoutFile}
    # Error                   = ${stderrFile}
    # Log                     = ${logFile}
    # Should_transfer_files   = ${transferYesNoBool}
    # When_to_transfer_output = ${whenTransfer}
    # Transfer_output_files   = ${outputFilesList}
    # Notification            = ${notification}
    # Priority                = ${priority}
    # Requirements            = ${requirements}
    # Periodic_remove         = ${periodicRemove}
    # ${X509userproxy}
    # Universe                = ${universe}
    #
    # Queue




















