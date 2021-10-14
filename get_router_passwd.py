from termcolor import colored
import sys
from getpass import getpass
# function to get router username and password
def get_router_passwd():
    try:
        # get router username and password
        user = input("Enter router username (level 15): ")
        passw = getpass(prompt="Enter router password (level 15):")
        return(user, passw)
    except KeyboardInterrupt:
        exit()
    except:
        print(colored('Unexpected error:', sys.exc_info()[0], 'red'))
        print(colored('Unexpected error:', sys.exc_info()[1], 'red'))
        exit()