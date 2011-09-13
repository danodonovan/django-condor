import datetime
from django.db import models

from condor.condor_tools import condor_status, condor_submit

# class CondorTasks( models.Model ):
#     """
#     CondorTasks class
#         This class is the highest level class for managing all lower tasks
#     """
#
#     name = models.CharField( max_length=256 )
#
#     condor_dags = models.ManyToManyField( 'CondorDags' )
#     condor_jobs = models.ManyToManyField( 'CondorJobs' )


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

    class Meta:
        abstract = True

class CondorJobs( AbstractJobBaseClass ):
    """
    """
    submit_script = models.FileField( upload_to='condor_jobs', blank=False )

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


# class CondorDags( AbstractJobBaseClass ):
#     """ A condor DAG is a special type of condor job
#     """
#     condor_jobs = models.ManyToManyField( 'CondorJobs' )



## History models - for keeping track of past job status
# class AbstractHistoryBaseClass( models.Model ):
#     """ Abstract Base Class for HistoryJob and HistoryJob
#         This is simply a table of the results of every status update - also tracking
#         the job / dag which was updated and the time of the update.
#     """
#     update = models.DateTimeField()
#     status = models.CharField( max_length=32 )
#
#     class Meta:
#         abstract = True
#         ordering = ['update']
#
# class HistoryJob( AbstractHistoryBaseClass ):
#     """ Track the history of a job
#     """
#     job = models.ForeignKey( 'CondorJobs' )
#
# class HistoryDag( AbstractHistoryBaseClass ):
#     """ Track the history of a DAG
#     """
#     dag = models.ForeignKey( 'CondorDags' )
