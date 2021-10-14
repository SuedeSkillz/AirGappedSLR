from termcolor import colored
import sys
from getpass import getpass
# function to get router username and password
def get_CSSM_passwd():
    try:
        # get CSSM username and password
        user = input("Enter CSSM username: ")
        passw = getpass(prompt="Enter CSSM password:")
        return(user, passw)
    except KeyboardInterrupt:
        exit()
    except:
        print(colored('Unexpected error:', sys.exc_info()[0], 'red'))
        print(colored('Unexpected error:', sys.exc_info()[1], 'red'))
        exit()