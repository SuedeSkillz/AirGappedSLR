## Prerequisites
To complete an Airgapped SLR of your devices, you will require:
  - A system capable of connecting to the devices (```airgapped```)
  - A system capable of connecting to software.cisco.com (```internet```)
  - A tftp server in the airgapped environment for reservation authorization files

Docker will need to be installed on both the ```airgapped``` and ```internet``` systems (https://docs.docker.com/get-docker/).

## Docker Image installation
### internet system
Download the container image from docker hub using
```
docker pull diamondtrim/airgappedslr
```
You must download the airgappedslr docker image and manually move it to the ```airgapped``` system.  Do this using
```
docker save diamondtrim/airgappedslr | gzip > airgappedslr.tar.gz
```
Move airgappedslr.tar.gz to a working directory on the ```airgapped``` system.

### airgapped system
Use the following command to manually load the image using
```
docker load < airgappedslr.tar.gz
```

## Execution
### Step 1 - Retrieve request codes from the devices
On the ```Airgapped``` system, change directories to a working directory for the AirGappedSLR operation.  Start a container using
```
docker run -i --network=host -v "$(pwd):/AirGappedSLR/input" -t diamondtrim/airgappedslr /bin/sh
```
You are now in a shell within the container and should see ```/AirGappedSLR #``` prompt.

Update the tftp server_type (TFTP or SCP), server_ip and server_path in input/config.ini

List all devices IP addresses in input/DevicesToLicense.csv.  There should be an example entry in the file.

Execute the following command on the ```airgapped``` system to retrive the request codes from the devices and place them in the DevicesToLicense.csv file.
```
python get_request_codes.py
```
You will be asked for the device username and password.  These need to be level 15 usernames.

Once this script complete exit from the container.
```
exit
```
You can inspect DevicesToLicense.csv and see the request codes.  Devices that presented errors will be marked as ERROR in the csv file.  Once you are satisfied with the request codes, move the file to a working directory on the ```internet``` system.

### Step 2 -  Retrieve authorization codes from CSSM (software.cisco.com)
On the ```internet``` system, change directories to a working directory for the AirGappedSLR operation.  Start a container using
```
docker run -i --network=host -v "$(pwd):/AirGappedSLR/input" -t diamondtrim/airgappedslr /bin/sh
```
You are now in a shell within the container and should see ```/AirGappedSLR #``` prompt.

Update the API client ID and secret in input/config.ini.  To get your client ID and secret, you will need register your application (https://apidocs-prod.cisco.com/explore;category=6083723a25042e9035f6a753;sgroup=6083723b25042e9035f6a775)

Execute the following command on the ```internet``` system to retrive the request codes from the devices and place them in the DevicesToLicense.csv file.
```
python get_auth_codes.py
```
You will be asked for your cisco_ID and password.  This is the username that has access to the Virtual Account on software.cisco.com.
Once this script complete exit from the container.
```
exit
```
You can inspect DevicesToLicense.csv and see the authorization codes.  Devices that presented errors will be marked as ERROR in the csv file.  Once you are satisified with the authorization codes, move the file to the working directory on the ```airgapped``` system.

### Step 3 -  Apply the authorization codes to the devices
On the ```airgapped``` system change directories to a working directory for the AirGappedSLR operation.  Start a container using
```
docker run -i --network=host -v "$(pwd):/AirGappedSLR/input" -t diamondtrim/airgappedslr /bin/sh
```
You are now in a shell within the container and should see ```/AirGappedSLR #``` prompt.
Execute the following command on the ```airgapped``` system to retrive the request codes from the devices and place them in the DevicesToLicense.csv file.
```
python apply_auth_codes.py
```
You will be asked for the device username and password.  These need to be level 15 usernames.
Once this script complete exit from the container.
```
exit
```
You can inspect DevicesToLicense.csv and see the confirmation codes.  Devices that presented errors will be marked as ERROR in the csv file.
