from termcolor import colored
from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoTimeoutException
from paramiko.ssh_exception import SSHException
from netmiko.ssh_exception import AuthenticationException
from get_router_passwd import get_router_passwd
import configparser
import sys
import csv
import os
from scpclient import ssh_scp_files
from scpclient import get_scp_passwd
from tftpclient import tftp_put_files

# Get config information
config = configparser.ConfigParser()
config.read('input/config.ini')

try:
    server_type = config.get("application", "server_type")
    server = config.get("application", "server_ip")
    server_path = config.get("application", "server_path")
except configparser.NoSectionError:
    print(colored("No section 'application'", 'red'))
    exit()
except configparser.ConfigParser.NoOptionError:
    print(colored('config.ini is not formatted appropriately', 'red'))
    exit()
except:
    print(colored('Unexpected Error', 'red'))
    exit()

user, passw = get_router_passwd()

if server_type == 'SCP':
    scp_user, scp_passw = get_scp_passwd()

apply_authorization_code_command = "license smart reservation install file tftp://" + server + "/"

device = {
    'device_type': 'cisco_xe',
    'host': '',
    'username': user,
    'password': passw
}

with open('input/DevicesToLicense.csv', mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    temp_csv_file = open('input/temp.csv', 'w')
    csv_writer = csv.DictWriter(temp_csv_file, fieldnames=csv_reader.fieldnames)
    csv_writer.writeheader()
    new_rows = {}
    for row in csv_reader:
        # Was the row in ERROR???
        if row['ReqCode'] == 'ERROR':
            # Print error if the IP address is not valid
            print(colored(row['DevicesToLicense'] + ' had an error while retrieving request code (STEP 1)\n', 'red'))
            row['ConfirmationCode'] = 'ERROR'
            csv_writer.writerow(row)
            continue
        print('Getting request code for ' + row['DevicesToLicense'])
        device["host"] = row['DevicesToLicense']
        authorization_code = row['AuthCode']
        authorization_file = device["host"] + '-authcode.txt'
        try:
            f = open(authorization_file, 'w')
            f.write(authorization_code)
            f.close()

            if server_type == 'SCP':
                ssh_scp_files(server, scp_user, scp_passw, authorization_file, server_path + authorization_file)
            else:
                print(server)
                print(authorization_file)
                tftp_put_files(server, authorization_file, authorization_file)
            os.remove(authorization_file)
        except KeyboardInterrupt:
            exit()
        except:
            print(colored('Unexpected error:', sys.exc_info()[0] + '\n', 'red'))
            print(colored('Unexpected error:', sys.exc_info()[1] + '\n', 'red'))
            exit()

        command = ["end", apply_authorization_code_command + authorization_file]

        try:
            net_connect = ConnectHandler(**device)
            device_prompt = net_connect.find_prompt()
            print("Starting CLI configuration process on device: {}".format(device_prompt))
            if device_prompt:
                reservation_confirmation_output = net_connect.send_config_set(config_commands=command, delay_factor=0.1)
            else:
                print("Not able to get device prompt for ip address: {}".format(device["host"]))

            net_connect.disconnect()

        except AuthenticationException:
            print(colored('Authentication Failure: ' + device["host"] + '\n', 'red'))
            row['ConfirmationCode'] = 'ERROR'
            csv_writer.writerow(row)
            continue
        except NetMikoTimeoutException:
            print(colored('Timeout to device: ' + device["host"] + '\n', 'red'))
            row['ConfirmationCode'] = 'ERROR'
            csv_writer.writerow(row)
            continue
        except SSHException:
            print(colored('SSH might not be enabled: ' + device["host"] + '\n', 'red'))
            row['ConfirmationCode'] = 'ERROR'
            csv_writer.writerow(row)
            continue
        except EOFError:
            print(colored('End of attempting device: ' + device["host"] + '\n', 'red'))
            row['ConfirmationCode'] = 'ERROR'
            csv_writer.writerow(row)
            continue
        except unknown_error:
            print(colored('Some other error: ' + str(unknown_error) + '\n', 'red'))
            row['ConfirmationCode'] = 'ERROR'
            csv_writer.writerow(row)
            continue
        except KeyboardInterrupt:
            row['ConfirmationCode'] = 'ERROR'
            csv_writer.writerow(row)
            exit()
        except:
            print(colored('Unexpected error:', sys.exc_info()[0] + '\n', 'red'))
            print(colored('Unexpected error:', sys.exc_info()[1] + '\n', 'red'))
            row['ConfirmationCode'] = 'ERROR'
            csv_writer.writerow(row)
            continue

        res_code = reservation_confirmation_output.split('\n')[-5]
        if res_code.find("Confirmation code:") != -1:
            data = res_code.split("code: ")
            res_code = data[1]
        row['ConfirmationCode'] = res_code
        csv_writer.writerow(row)

csv_file.close()
temp_csv_file.close()
os.replace('input/temp.csv', 'input/DevicesToLicense.csv')