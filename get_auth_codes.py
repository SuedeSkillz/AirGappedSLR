from termcolor import colored
import sys
import csv
import os
import requests
from requests.exceptions import HTTPError
from get_CSSM_passwd import get_CSSM_passwd
import configparser

# Get config information
config = configparser.ConfigParser()
config.read('input/config.ini')

try:
    ClientID = config.get("application", "client_id")
    ClientSecret = config.get("application", "client_secret")
    SmartAccount = config.get("application", "smart_account_domain")
    VirtualAccount = config.get("application", "virtual_account")
except configparser.NoSectionError:
    print(colored("No section 'application'", 'red'))
    exit()
except configparser.ConfigParser.NoOptionError:
    print(colored('config.ini is not formatted appropriately', 'red'))
    exit()
except:
    print(colored('Unexpected Error', 'red'))
    exit()

user, passw = get_CSSM_passwd()

# Get token using client id, client secret, username and password
try:
    url = "https://cloudsso.cisco.com/as/token.oauth2"
    payload = 'client_id=' + ClientID + '&client_secret=' + ClientSecret + '&grant_type=password&username=' + user + '&password=' + passw
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.request("POST", url, headers=headers, data=payload)
    token = response.json()["access_token"]
except KeyError:
    print(colored('Invalid username, password or API client/secret', 'red'))
    exit()
except KeyboardInterrupt:
    exit()
except:
    print(colored('Unexpected error:', sys.exc_info()[0], 'red'))
    print(colored('Unexpected error:', sys.exc_info()[1], 'red'))
    exit()

print(token)

# Set url using SmartAccount and VirtualAccount and header using bearer token
url = "https://swapi.cisco.com//services/api/smart-accounts-and-licensing/v1/accounts/" + SmartAccount + "/virtual-accounts/" + VirtualAccount + "/reserve-licenses"
headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + str(token)}

# Run thru all of the IP addresses in the csv
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
            row['AuthCode'] = 'ERROR'
            csv_writer.writerow(row)
            continue
        try:
            # Get license request information for this device from the csv
            print('Getting request code for ' + row['DevicesToLicense'])
            licenses = row['ReqCode']
            # Call API to get authorization codes from software.cisco.com
            response = requests.request("POST", url, headers=headers, data=licenses)
            # Raise exceptions if the return code is 4xx
            response.raise_for_status()
            # Reformat the authorization code response
            authorization_code = '<smartLicense>' + response.json()["authorizationCodes"][0][
                "authorizationCode"] + '</smartLicense>'
            # Write the authorization code to the csv
            row['AuthCode'] = authorization_code
            csv_writer.writerow(row)
        except HTTPError:
            print(colored(response.json(), 'red'))
            row['AuthCode'] = 'ERROR'
            csv_writer.writerow(row)
            continue
        except KeyboardInterrupt:
            exit()
        except:
            print(colored('Unexpected error:', sys.exc_info()[0], 'red'))
            print(colored('Unexpected error:', sys.exc_info()[1], 'red'))
            continue

# Save the csv
csv_file.close()
temp_csv_file.close()
os.replace('input/temp.csv', 'input/DevicesToLicense.csv')
