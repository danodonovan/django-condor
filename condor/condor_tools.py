import os, sys
import subprocess, shlex

class CondorError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    def __repr__(self):
        return 'CondorError(%s)' % (self.value)

condor_status = {
    '0':'?',
    '1':'Idle',
    '2':'Running',
    '3':'Removed',
    '4':'Completed',
    '5':'Held',
}


def call_condor( *args, **kwargs ):
    """ Generic function for calling condor on `host` machine
            Note - if password free ssh is not setup, a hardcoded passphrase will
            need to be sent in the open.
    """

    hostname = kwargs['hostname'] if kwargs.has_key( 'hostname' ) else None
    port     = kwargs['port']     if kwargs.has_key( 'port' )     else 22
    username = kwargs['username'] if kwargs.has_key( 'username' ) else None
    password = kwargs['password'] if kwargs.has_key( 'password' ) else None

    env = kwargs['env'] if kwargs.has_key( 'env' ) else None

    command = ' '.join( args )

    if not hostname:
        # simple system call to local machine
        (stdout, stderr) = _call( command, env )
        stdout = stdout[0]
    else:
        # more complex call using paramiko
        (stdout, stderr) = _connect_call( command, env, hostname, port, username, password )

    # sh not kicking up an OSError when command not found
    if stderr.__contains__( ': command not found' ):
        raise CondorError( 'call_condor error cmd not found: %s' % command )

    return (stdout, stderr)

def _call( command, env ):
    """ Internal local call command """
    try:
        p = subprocess.Popen( command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env )
    except OSError:
        raise CondorError( 'call_condor error cmd: %s' % command )

    stdout, stderr = p.stdout.readlines(), p.stderr.read()

def _connect_call( command, env, hostname, port, username, password):
    """ Internal remote call command """
    try:
        import paramiko
    except ImportError:
        raise ImportError( 'To call a remote host python module paramiko must be installed' )

    # pretty nasty, but paramiko doesn't support env sending
    if env:
        command = ' '.join(['%s=%s' % (k,v) for k,v in env.items()]) + ' ' + command

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.WarningPolicy)

    client.connect(hostname, port, username, password)

    try:
        stdin_fo, stdout_fo, stderr_fo = client.exec_command( command )

        stdout = '\n'.join( line for line in stdout_fo )
        stderr = '\n'.join( line for line in stderr_fo )
    except:
        raise CondorError( 'Error executing "%s" on remote host %s' % (command, hostname) )

    client.close()

    return (stdout, stderr)

def condor_status( pid, **kwargs ):
    """ Run condor_status for job pid """

    (stdout, stderr) = call_condor( [ 'condor_q', '-format', '%s JobStatus', '%f' % pid], **kwargs )

    if stderr:
        raise CondorError( 'condor_status error: %s' % stderr )

    if not stdout:  job_status = ('Completed', None )
    else:           job_status = (status[stdout], stdout)

    return job_status
