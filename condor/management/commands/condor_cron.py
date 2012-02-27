import os
from optparse import make_option
import logging

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from condor.models import CondorDagJob

logger = logging.getLogger('django_debug')

class Command(BaseCommand):

    help = """
    Run this as a cron every X minutes - for every condor DAG in the queue, this
    will:
        Submit the DAG (if it is queued and there are N other dags running)
        # extra tasks to be added as needed
    Apparently running too many condor jobs will flatten the Glidein so this 
    handles them and submits using some dumb priority level.
    """

    option_list = BaseCommand.option_list + (
        make_option('--dummy', action='store_false', dest='dummy',
                help="Run command, but don't actually submit DAG job"),
        )

    def handle(self, *args, **options):
        """ 
        Cron job: submit DAG if queued and time available
        """

        logger.debug('running %s' % __file__)

        self.check_and_submit()

    def check_and_submit(self):
        """ 
        Checks job queue and submits job if there is one to be submitted
        """

        logger.debug('check_and_submit')

        running_tasks = CondorDagJob.objects.filter(status='Running').count()
        if running_tasks < settings.CONDOR_SETTINGS['n_running_dags']:
            self.submit_oldest_dag()
    
    def submit_oldest_dag(self):
        """
        Submits the DAG that has been held in the django-condor queue for the longest time
        """
        logger.debug('submit_oldest_dag')
        oldest_dag = CondorDagJob.objects.filter(status__exact='Not Submitted').latest('created')
        logger.debug('oldest_dag %s' % oldest_dag)

        oldest_dag.submit()
        logger.debug('%s submitted' % oldest_dag)

