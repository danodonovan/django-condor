import os, sys
import logging
import re, subprocess, shlex

logger = logging.getLogger('condor_debug')

class CondorError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    def __repr__(self):
        return 'CondorError(%s)' % (self.value)

condor_status_dict = {
    '0':'?',
    '1':'Idle',
    '2':'Running',
    '3':'Removed',
    '4':'Completed',
    '5':'Held',
}


def call_condor(*args, **kwargs):
    """ Generic function for calling condor on `host` machine
            Note - if password free ssh is not setup, a hardcoded passphrase will
            need to be sent in the open.
    """

    hostname = kwargs['hostname'] if kwargs.has_key('hostname') else None
    port     = kwargs['port']     if kwargs.has_key('port')     else 22
    username = kwargs['username'] if kwargs.has_key('username') else None
    password = kwargs['password'] if kwargs.has_key('password') else None
    remotedir= kwargs['remotedir']if kwargs.has_key('remotedir')else None

    env = kwargs['env'] if kwargs.has_key('env') else None
    command = ' '.join(args)

    if hostname == 'localhost':
        logger.debug('call_condor localhost')
        # simple system call to local machine
        commands = [arg.strip() for arg in args]
        (stdout, stderr) = _call(commands, env, remotedir=remotedir)
        stdout = stdout[0] if stdout else None
    else:
        # more complex call using paramiko
        logger.debug('call_condor remote %s %s %s %s %s %s %s' % \
            (command, env, hostname, port, username, password, remotedir))
        (stdout, stderr) = _connect_call(   command, env, hostname, port,
                                            username, password, remotedir )

    # sh not kicking up an OSError when command not found
    if stderr.__contains__( ': command not found' ):
        raise CondorError( 'call_condor error cmd not found: %s Full error: %s' % \
            (command, stderr) )

    if stderr.__contains__( ': Unable to read file: ' ):
        raise CondorError( 'call_condor error could not read file: %s Full error: %s' % \
            (command, stderr) )

    return (stdout, stderr)

def _call(command, env, remotedir=None):
    """ Local call command """
    if remotedir:
        logger.debug('_call remote dir %s exists' % remotedir)
        command = ['cd', '%s' % remotedir, ';'] + command

    try:
        logger.debug('_call execute: %s - %s' % (command, env))
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    except OSError:
        raise CondorError('_call call_condor error cmd: %s' % command)

    return p.stdout.readlines(), p.stderr.read()

def _connect_call(command, env, hostname, port, username, password, remotedir):
    """ Remote call command """
    try:
        import paramiko
    except ImportError:
        raise ImportError('To call a remote host python module paramiko must be installed')

    # pretty nasty, but paramiko doesn't support env sending
    pre_command = ''

    if remotedir:
        pre_command += 'cd %s; ' % remotedir

    if env and isinstance(env, dict):
        pre_command += ' '.join(['%s=%s' % (k,v) for k,v in env.items()]) + ' '
        command = pre_command + command
    elif env:
        raise CondorError('env not a dictionary %s' % env)

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ## try to connect with system host keys, but this may not work (ie on OSX)
    try:
        client.connect(hostname, int(port), username, password)
    except paramiko.PasswordRequiredException as e:
        if e.message == 'Private key file is encrypted':
            if not password:
                raise CondorError('Paramiko Error: %s - you may need to supply a password' % (e.message))
            else:
                raise CondorError('Paramiko Error: %s - your password may be incorrect' % (e.message))
    #except Exception as e:
    #    raise CondorError('Error: %s' % (e.message))

    try:
        stdin_fo, stdout_fo, stderr_fo = client.exec_command(command)

        stdout = '\n'.join(line for line in stdout_fo)
        stderr = '\n'.join(line for line in stderr_fo)
    except:
        raise CondorError('Error executing "%s" on remote host %s' % (command, hostname))

    client.close()

    return (stdout, stderr)

## this are the public facing API functions

def condor_status(pid, **kwargs):
    """ Run condor_status for job pid """

    (stdout, stderr) = call_condor('condor_q', '-format', '%s JobStatus', '%f' % pid, **kwargs)

    if stderr:
        raise CondorError('condor_status error: %s' % stderr)

    if not stdout:  job_status = 'Completed'
    else:           job_status = condor_status_dict[stdout]

    return job_status

def condor_submit(submit_script, **kwargs):
    """ Run condor_submit for job """

    submit = 'condor_submit_dag' if kwargs.has_key('dag') and kwargs['dag'] else 'condor_submit'

    logger.debug('condor_submit %s' % kwargs)

    (stdout, stderr) = call_condor(submit, '%s' % submit_script, **kwargs)

    if stderr: raise CondorError('condor_submit error: %s' % stderr)

    if not stderr and stdout:
        # return the PID for this host
        temp = re.search(r'job\(s\) submitted to cluster \d+', stdout).group()
        return int(re.search(r'\d+', temp).group())


def condor_rm(pid, **kwargs):
    """ Run condor_submit for job """

    remove = 'condor_rm'

    (stdout, stderr) = call_condor(remove, '%s' % pid, **kwargs)

    if stderr: raise CondorError('condor_rm error: %s' % stderr)

    if not stderr and stdout:
        if stdout == 'Job %d.0 marked for removal' % pid:
            return True
    return False    

condor_classad_template = """
Executable              = ${executable}
Arguments               = ${arguments}
Output                  = ${stdoutFile}
Error                   = ${stderrFile}
Log                     = ${logFile}
Should_transfer_files   = ${transferYesNoBool}
When_to_transfer_output = ${whenTransfer}
Transfer_output_files   = ${outputFilesList}
Notification            = ${notification}
Priority                = ${priority}
Requirements            = ${requirements}
Periodic_remove         = ${periodicRemove}
${X509userproxy}
Universe                = ${universe}

Queue
"""


