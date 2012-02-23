import datetime
from django.db import models

from condor import CONDOR_RAM_GB, condorBinaryUpload, condorScriptUpload
from condor.fields import JSONField
from condor.condor_tools import condor_status, condor_submit, condor_classad_template, condor_rm

class CondorHost(models.Model):
    """ Hold details for the condor host """

    hostname = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    port = models.PositiveIntegerField(default=22)
    env = JSONField(blank=True)
    remotedir = models.CharField(max_length=255)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return '<condor host %d : %s>' % (self.hostname, self.username)

class AbstractJobBaseClass(models.Model):
    """ Abstract Base Class for a condor job
    """
    pid = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=32, default='Not Submitted')
    update = models.DateTimeField(auto_now_add=True)

    history = models.TextField()

    host = models.ForeignKey('CondorHost', null=True)

    name = models.CharField(max_length=255, blank=True)
    timeout = models.IntegerField(default=1800)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return '<condor %d : %s>' % (self.pid, self.name)

    def update_status(self):
        """ Update the job status for the given pid """
        changed = False
        if not self.pid: return changed

        prevStatus = self.status

        if not self.host:
            self.status = condor_status(self.pid)
        else:
            h = self.host
            self.status = condor_status(self.pid,
                hostname=h.hostname, username=h.username, password=h.password,
                port=h.port, env=h.env, remotedir=h.remotedir)

        self.update = datetime.datetime.now()
        self.store_history()
        self.save()

        if self.status is not prevStatus:
            changed = False
        
        return changed

    def store_history(self, save=False):
        """ store update in history """
        if not self.history:
            self.history = repr({self.update:self.status})
            return
        history = eval(self.history)
        if not history.has_key(self.update):
            history[self.update] = self.status
        self.history = repr(history)
        if save: self.save()

    def submit(self, dag=False):
        """ submit a condor job """
        if self.pid: return
        if not self.submit_script: return

        if not self.host:
            self.pid = condor_submit(self.submit_script, dag=dag)
        else:
            h = self.host
            self.pid = condor_submit(self.submit_script,
                hostname=h.hostname, username=h.username, password=h.password,
                port=h.port, env=h.env, remotedir=h.remotedir, dag=dag)

        self.save()
        self.update_status()


    def rm(self):
        """ kill a condor job """
        if not self.pid: return

        if not self.host:
            success = condor_rm(self.pid)
        else:
            h = self.host
            success = condor_rm(self.pid,
                hostname=h.hostname, username=h.username, password=h.password,
                port=h.port, env=h.env, remotedir=h.remotedir)

        self.save()
        self.update_status()

    class Meta:
        abstract = True

class CondorJob( AbstractJobBaseClass ):
    """ CondorJob - a model to control and track a single condor job defined by
            values given through django.
    """
    # these values job classAds
    Arguments               = JSONField()
    Output                  = models.CharField(max_length=255, blank=True)
    Error                   = models.CharField(max_length=255, blank=True)
    Log                     = models.CharField(max_length=255, blank=True)
    Should_transfer_files   = models.CharField(max_length=255, blank=True)
    When_to_transfer_output = models.CharField(max_length=255, blank=True)
    Transfer_output_files   = models.CharField(max_length=255, blank=True)
    Notification            = models.CharField(max_length=255, blank=True)
    Priority                = models.CharField(max_length=255, blank=True)
    Requirements            = models.CharField(max_length=255, blank=True)
    Periodic_remove         = models.CharField(max_length=255, blank=True)
    X509userproxy           = models.CharField(max_length=255, blank=True)
    Universe                = models.CharField(max_length=255, blank=True)

    ram_min = models.CharField(max_length=255, default='2048 * %s' % CONDOR_RAM_GB)

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

class CondorDagJob(AbstractJobBaseClass):
    """ CondorDagJob - a model to control and track a single condor dag job - submitted locally
        or on a remote scheduler. A DAG owns and submits multiple individual condor jobs that
        are not traked by django condor
    """
    submit_script = models.FileField(upload_to='condor_jobs', blank=False)
    executable = models.FileField(upload_to='condor_exec', blank=True)

    def submit(self, **kwargs):
        super(CondorDagJob, self).submit(dag=True, **kwargs)

