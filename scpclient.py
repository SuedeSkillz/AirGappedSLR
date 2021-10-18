from termcolor import colored
from paramiko import SSHClient
from paramiko import AutoAddPolicy
from paramiko.ssh_exception import AuthenticationException
from paramiko.ssh_exception import SSHException
from paramiko.ssh_exception import BadHostKeyException
from scp import SCPClient
from getpass import getpass
import sys
# function to scp a file to a remote system
def ssh_scp_files(ssh_host, ssh_user, ssh_password, source_file, destination_file):
    try:
# open ssh session
        ssh = SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        ssh.connect(ssh_host, username=ssh_user, password=ssh_password, look_for_keys=False)

# use scp as the transport
        with SCPClient(ssh.get_transport()) as scp:
# copy the file to the remote system
            scp.put(source_file, recursive=True, remote_path=destination_file)
# handle the exceptions
    except AuthenticationException:
        print(colored("Authentication failed, please verify your credentials", 'red'))
        raise
    except SSHException as sshException:
        print(colored("Unable to establish SSH connection: %s" % sshException, 'red'))
        raise
    except BadHostKeyException as badHostKeyException:
        print(colored("Unable to verify server's host key: %s" % badHostKeyException, 'red'))
        raise
    finally:
        ssh.close()

def get_scp_passwd():
    try:
        # get scp username and password
        user = input("Enter scp server username: ")
        passw = getpass(prompt="Enter scp server password):")
        return(user, passw)
    except KeyboardInterrupt:
        exit()
    except:
        print(colored(sys.exc_info()[0], 'red'))
        print(colored(sys.exc_info()[1], 'red'))
        exit()
