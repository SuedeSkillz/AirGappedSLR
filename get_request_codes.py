from termcolor import colored
from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoTimeoutException
from paramiko.ssh_exception import SSHException
from netmiko.ssh_exception import AuthenticationException
from get_router_passwd import get_router_passwd
import sys
import csv
import os
from valid_ip import validIPAddress

user, passw = get_router_passwd()

# Define device CLI commands
req_token_command = ["license smart reservation", "end", "license smart reservation request local"]
req_udi_command = ["end", "sh license tech support | i Entitlement|Count"]
dlc_conversion_command = "show license data conversion | i conversion_string"

# Initialize device
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
        if validIPAddress(row['DevicesToLicense']):
            print('Getting request code for ' + row['DevicesToLicense'])
            device["host"] = row['DevicesToLicense']
            try:
                net_connect = ConnectHandler(**device)
                device_prompt = net_connect.find_prompt()
                print(" Starting CLI configuration process on device: {}".format(device_prompt))
                if device_prompt:
                    req_code_output = net_connect.send_config_set(config_commands=req_token_command, delay_factor=0.1)
                    req_udi_output = net_connect.send_config_set(config_commands=req_udi_command, delay_factor=0.1)
                else:
                    print("Not able to get device prompt for ip address: {}".format(device["host"]))
                net_connect.disconnect()
            except AuthenticationException:
                print(colored('Authentication Failure: ' + device["host"] + '\n', 'red'))
                row['ReqCode'] = 'ERROR'
                csv_writer.writerow(row)
                continue
            except NetMikoTimeoutException:
                print(colored('Timeout to device: ' + device["host"] + '\n', 'red'))
                row['ReqCode'] = 'ERROR'
                csv_writer.writerow(row)
                continue
            except SSHException:
                print(colored('SSH might not be enabled: ' + device["host"] + '\n', 'red'))
                row['ReqCode'] = 'ERROR'
                csv_writer.writerow(row)
                continue
            except EOFError:
                print(colored('End of attempting device: ' + device["host"] + '\n', 'red'))
                row['ReqCode'] = 'ERROR'
                csv_writer.writerow(row)
                continue
            except KeyboardInterrupt:
                row['ReqCode'] = 'ERROR'
                csv_writer.writerow(row)
                exit()
            except unknown_error:
                print(colored('Some other error: ' + str(unknown_error) + '\n', 'red'))
                row['ReqCode'] = 'ERROR'
                csv_writer.writerow(row)
                continue
            except:
                print(colored('Unexpected error:', sys.exc_info()[0] + '\n', 'red'))
                print(colored('Unexpected error:', sys.exc_info()[1] + '\n', 'red'))
                row['ReqCode'] = 'ERROR'
                csv_writer.writerow(row)
                continue
            # Extract request code
            req_code = req_code_output.split('\n')[-2]
            if req_code.find("Request code:") != -1:
                data = req_code.split("code: ")
                req_code = data[1]
            # Split entitlement and count information
            udi = (req_udi_output.split('\n'))
            # Initialize entitlement search
            first = 1
            first_count = 1
            licenses = ''

            # Run through entitlement command output line by line
            for entitlement_tag in udi:
                # If I have an entitlement tag ...
                if "Entitlement Tag:" in entitlement_tag:
                    # ... and its the first tag in the list
                    if first:
                        # save the entitlement tag in a temp variable
                        temp_licenses = '{"entitlementTag":"' + entitlement_tag.split(":")[-1].replace(" ", "") + '",'
                        # Not the first anymore
                        first = 0
                    else:
                        # ... and its not the first tag in the list, save the entitlement tag and all other entitlements (in licenses) in a temp variable
                        temp_licenses = licenses + ',{"entitlementTag":"' + entitlement_tag.split(":")[-1].replace(" ", "") + '",'
                # If i have a Count tag...
                if "Count:" in entitlement_tag and int(entitlement_tag.split(":")[-1].replace(" ", "")) > 0:
                    # ... add the count value to the end of the entitlement(s) (stored in the temp variable)
                    licenses = temp_licenses + '"quantity":"' + entitlement_tag.split(":")[-1].replace(" ",
                                                                                                       "") + '","precedence":"SHORTEST_TERM_FIRST"}'
            # ... Complete the licenses JSON
            licenses = '{ "reservationRequests":[ { "reservationCode":"' + req_code + '","reservationType":"SPECIFIC", "licenses":[' + licenses + ']}]}'
            # Save the license information to the csv
            row['ReqCode'] = licenses
            csv_writer.writerow(row)
            # If the IP address is not valid print and error and save ERROR for the request code in the csv
        else:
            print(colored(row['DevicesToLicense'] + ' is an invalid IP address\n', 'red'))
            row['ReqCode'] = 'ERROR'
            csv_writer.writerow(row)

csv_file.close()
temp_csv_file.close()
os.replace('input/temp.csv', 'input/DevicesToLicense.csv')
