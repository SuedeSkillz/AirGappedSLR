# AirGappedSLR
Simple scripts that use csv files to perform SLR for multiple devices in air-gapped deployments.

## Prerequisites
To complete an Airgapped SLR of your devices, you will require:
  - A system capable of connecting to the devices (```airgapped```)
  - A system capable of connecting to software.cisco.com (```internet```)
  - A tfpt server in the airgapped environment for reservation authorization files

The following tool(s) will need to be installed on both systems (identified as ```airgapped``` and ```internet``` above):
  - python3.x (Required to run python scripts.  The install instructions here:  https://www.python.org)
  - Airgapped SLR package

## config.ini
### airgapped system
Update the tftp server_type (TFTP or SCP), server_ip and server_path in input/config.ini

### internet system
Update the API client ID and secret in input/config.ini.  To get your client ID and secret, you will need register your application (https://apidocs-prod.cisco.com/explore;category=6083723a25042e9035f6a753;sgroup=6083723b25042e9035f6a775)

## DevicesToLicense.csv
List all devices IP address in DevicesToLicense.csv.  Example csv in input/DevicesToLicense.csv.

##Execution
### Step 1 - Retrieve request codes from the devices
Execute the following command on the ```airgapped``` system to retrive the request codes from the devices and place them in the DevicesToLicense.csv file.
```
python get_request_codes.py
```
You will be asked for the device username and password.  These need to be level 15 usernames.

Once this script complete, you can inspect input/DevicesToLicense.csv and see the request codes.  Devices that presented errors will be marked as ERROR in the csv file.  Once you are satisified with the request codes, move the file to input/DevicesToLicense.csv on the ```internet``` system.

### Step 2 -  Retreve authorization codes from CSSM (software.cisco.com)
Execute the following command on the ```internet``` system to retrive the request codes from the devices and place them in the DevicesToLicense.csv file.
```
python get_auth_codes.py
```
You will be asked for your cisco_ID and password.  This is the username that has access to the Virtual Account on software.cisco.com.

Once this script complete, you can inspect input/DevicesToLicense.csv and see the authorization codes.  Devices that presented errors will be marked as ERROR in the csv file.  Once you are satisified with the authorization codes, move the file to input/DevicesToLicense.csv on the ```airgapped``` system.

### Step 3 -  Apply the authorization codes to the devices
Execute the following command on the ```airgapped``` system to retrive the request codes from the devices and place them in the DevicesToLicense.csv file.
```
python apply_auth_codes.py
```
You will be asked for the device username and password.  These need to be level 15 usernames.

Once this script complete, you can inspect input/DevicesToLicense.csv and see the confirmation codes.  Devices that presented errors will be marked as ERROR in the csv file.
