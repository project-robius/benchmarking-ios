# step 3
# Example: > ./convert.sh makepad_taobao

python3 xml2csv.py $1-ActivityMonitor-sysmon-process.xml
python3 xml2csv.py $1-GamePerformance-surfaces-per-second.xml
python3 xml2csv.py $1-GamePerformance-device-thermal-state-intervals.xml