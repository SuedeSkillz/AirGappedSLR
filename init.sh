if [ -e 'input/DevicesToLicense.csv' ]
then
    echo "csv ok"
else
    echo "csv nok"
    cp example/DevicesToLicense.csv input/.
fi
if [ -e 'input/config.ini' ]
then
    echo "ini ok"
else
    echo "ini nok"
    cp example/config.ini input/.
fi
