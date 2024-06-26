# Manual Test Steps

The main script `xcperf.py` is supposed to do all the following steps in 1 command. However, it's still not completely stable yet, hence the following conveience steps can be used instead.

### TODO

* Combine the two templates, plus any other (such as Core Animation) into a single user defined template. This reduces the record command - and more importantly the test session into 1.
Right now for each record command, we need to run the app and manipulate the UI manually. This can introduce inconsistencies.
* Update the export commands to obtain the relevant new schema to the xml file
* Update the summarize scripts to parse the new metrics columns

## Convenient Scripts

Step 3 and 4 can be replaced with the following scripts:

```bash
./record1.sh 00008110-001029521A13801E MockTaobao
./record2.sh 00008110-001029521A13801E MockTaobao
```

Step 6 can be replaced with the following scripts:

```bash
./export.sh MockTaobao
```

Step 6 can be replaced with the following scripts:

```bash
./convert.sh MockTaobao
```

Step 7 can be replaced with the following scripts:

```bash
./summarize.sh MockTaobao
```

## Detailed Steps

1. (Can be omitted, only required for the first time) Compile and start the application, exit other processes
2. (Can be omitted, only required for the first time) Execute xcrun xctrace list devices to obtain the device UDID
3. Execute the following command and start operating the application according to the terminal output prompts. Pay attention to replacing the process name (MockTaobao) and UDID with actual values.

```bash
xcrun xctrace record --output MockTaobao-ActivityMonitor.trace --template 'Activity Monitor' --device '00008110-001029521A13801E' --time-limit 10s  --window 10s --attach MockTaobao
```

See the terminal prompt "Output file saved as" before proceeding to the next step. If an error is reported, delete the output file and execute again.

4. Execute the following command and start operating the application according to the terminal output prompts. Pay attention to replacing the process name (MockTaobao) and UDID with actual values.

```bash
xcrun xctrace record --output MockTaobao-GamePerformance.trace --template 'Game Performance' --device '00008110-001029521A13801E' --time-limit 10s  --window 10s --attach MockTaobao
```

See the terminal prompt "Output file saved as" before proceeding to the next step. If an error is reported, delete the output file and execute again.

5. (Can be omitted to facilitate verification) Execute the following command to obtain the directory of test results. If it fails, try again.

```bash
xcrun xctrace export --input MockTaobao-ActivityMonitor.trace --toc > MockTaobao-ActivityMonitor.xml
xcrun xctrace export --input MockTaobao-GamePerformance.trace --toc > MockTaobao-GamePerformance.xml
```

6. Execute the following command to export the detailed data of the results.

```bash
# % CPU, CPU Time, Memory Usage
xcrun xctrace export --input MockTaobao-ActivityMonitor.trace --xpath '/trace-toc/run[@number="1"]/data/table[@schema="sysmon-process"]' --output MockTaobao-ActivityMonitor_sysmon-process.xml
# FPS
xcrun xctrace export --input MockTaobao-GamePerformance.trace --xpath '/trace-toc/run[@number="1"]/data/table[@schema="displayed-surfaces-per-second"]' --output MockTaobao-GamePerformance_displayed-surfaces-per-second.xml
# Thermal State
xcrun xctrace export --input MockTaobao-GamePerformance.trace --xpath '/trace-toc/run[@number="1"]/data/table[@schema="device-thermal-state-intervals"]' --output MockTaobao-GamePerformance_device-thermal-state-intervals.xml
```

7. Convert the XML files into .csv format by using the script xml2csv.py. After export, you can use Excel to calculate the maximum and average values.

```bash
python3 xml2csv.py MockTaobao-ActivityMonitor-sysmon-process.xml
python3 xml2csv.py MockTaobao-GamePerformance-surfaces-per-second.xml
python3 xml2csv.py MockTaobao-AGamePerformance-device-thermal-state-intervals.xml
```

8. Summarize the average and max values from the spreadsheets.

```bash
python3 summarize2.py MockTaobao
python3 summarize.py MockTaobao
```
