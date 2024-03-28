"""xcperf-v2 automation

## Features
Today it creates the csv of the following tables:
    - sysmon-process
    - core-animation-fps-estimate
    - device-thermal-state-intervals
    - displayed-surfaces-per-second

## Usage
1. Compile and start the application, exit other processes
2. Execute xcrun xctrace list devices to obtain the device UDID

run: `python3 xcperf-v2.py <device_id> <process_id>`
eg: `python3 xcperf-v2.py 00008101-001575C92E90801E makepad_comp_demo`
"""

import os
import subprocess
import sys
from xml2csv import xml_to_csv

def main():
    device_id = sys.argv[1]
    process_id = sys.argv[2]

    activity_monitor_template = "Activity Monitor" 
    game_performance_template = "Game Performance" 
    metal_system_template = "Metal System Trace"

    activity_monitor_tables = ["sysmon-process"]
    game_performance_tables = ["displayed-surfaces-per-second", "device-thermal-state-intervals"]
    metal_system_tables = ["core-animation-fps-estimate"]

    activity_monitor_trace_file = xcrun_record_template(device_id, process_id, activity_monitor_template)
    game_performance_trace_file = xcrun_record_template(device_id, process_id, game_performance_template)
    metal_system_trace_file = xcrun_record_template(device_id, process_id, metal_system_template, instrument="Core Animation FPS", windowed=False)

    for table in activity_monitor_tables:
        exported_table_file = xcrun_export_trace_file_table(activity_monitor_trace_file, table)
        xml_to_csv(exported_table_file)

    for table in game_performance_tables:
        exported_table_file = xcrun_export_trace_file_table(game_performance_trace_file, table)
        xml_to_csv(exported_table_file)

    for table in metal_system_tables:
        exported_table_file = xcrun_export_trace_file_table(metal_system_trace_file, table)
        xml_to_csv(exported_table_file)


def xcrun_record_template(device_id, process_id, template_name, instrument="", windowed=True):
    output_file_name = process_id + "-" + template_name.replace(" ", "") + ".trace"

    command = ["xcrun", "xctrace", "record"]
    options = [f"--output={output_file_name}", f"--template={template_name}", f"--device={device_id}", "--time-limit=10s", f"--attach={process_id}"]

    if instrument:
        options.append("--instrument=" + instrument)
    if windowed:
        options.append("--window=10s")

    final_command = command + options

    result = subprocess.run(final_command)
    if result.returncode == 0:
        return output_file_name
    else:
        raise Exception(f'Could not record template "{template_name}" in device "{device_id}" in process "{process_id}"/nRun Command: "{" ".join(final_command)}"')

def xcrun_export_trace_file(input_trace_file_name):
    # TODO: stop using the > and shell=True, save the output of the command run with subprocess.run()
    # and store it in a file

    output_file_name = input_trace_file_name.replace(".trace", "") + ".xml"

    command = ["xcrun", "xctrace", "export"]
    options = ["--input", input_trace_file_name, "--toc", ">", output_file_name]

    final_command = command + options

    process = subprocess.Popen(final_command, shell=True)
    process.communicate()
    
    if process.returncode == 0:
        return output_file_name
    else:
        raise Exception(f'Could not export trace file {input_trace_file_name}/nRun Command: "{" ".join(final_command)}"')

def xcrun_export_trace_file_table(input_trace_file_name, table_name):
    output_file_name = input_trace_file_name.replace(".trace", "") + "-" + table_name + ".xml"

    command = ["xcrun", "xctrace", "export"]
    options = ["--input", input_trace_file_name, "--xpath", f'/trace-toc/run[@number="1"]/data/table[@schema="{table_name}"]', "--output", output_file_name]
     
    final_command = command + options

    result = subprocess.run(final_command)
    if result.returncode == 0:
        return output_file_name
    else:
        raise Exception(f'Could not export table "{table_name}" from trace file {input_trace_file_name}/nRun Command: "{" ".join(final_command)}"')

if __name__ == "__main__":
    main()