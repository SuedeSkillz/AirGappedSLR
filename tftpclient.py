from termcolor import colored
import tftpy
import sys
# function to tftp a file to a remote system
def tftp_put_files(tftp_host, source_file, destination_file):
    try:
# open tftp session
        client = tftpy.TftpClient(tftp_host, 69)
        client.upload(destination_file, source_file)
# handle the exceptions
    except:
        print(colored('Unexpected error:', sys.exc_info()[0], 'red'))
        print(colored('Unexpected error:', sys.exc_info()[1], 'red'))
        exit()