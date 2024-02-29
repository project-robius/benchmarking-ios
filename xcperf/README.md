# xcperf
Automatic performance benchmark for Xcode project

## Prerequisites
- Xcode 15 installed
- Python3 installed
- Target process running on simulator / paired iDevice

## Steps
- Build & run your Xcode project
- Keep process running in the foreground
- Kill other process running in the background.(Otherwise it will take really long time to parse the xml later)
- Run the xcperf script with device_id, attach_process and time_limit.

## Troubleshooting
- If you are prompted for device-related error, please run `xcrun xctrace list devices` and make sure device_id appears in the list.
- If you are prompted with a process-related error, please check that you have specified the correct Process Name or PID. The Process Name should be the final executable file name and not the project name.
- Export xctrace result may failed, retry is all you need.
- If you are prompted with `Cannot find process matching name` or `trace trap`, run the script again.
- It may throw `Export failed: Document Missing Template Error` in some cases, like `--template 'Activity Monitor' --instrument 'Display'`

## Known Issues
- [Energy Diagnostic](https://developer.apple.com/library/archive/documentation/Performance/Conceptual/EnergyGuide-iOS/MonitorEnergyWithInstruments.html) template had removed from lates Xcode.
- [CPU Profiler](https://forums.developer.apple.com/forums/thread/702557) CPU Cycles failed with `no allocated PMI` error.
- [Automating xctrace stuck on "Stopping recording..."](https://stackoverflow.com/questions/76438218/automating-xctrace-stuck-on-stopping-recording)
- The frequency of `GPU Memory` records is very low. Only 1 record within 10 seconds, which is difficult to use as a statistical basis.
- Some field will present `sentinel` which means no data (filled with `N/A`)

## Analytics

### Mock Taobao

- % CPU (Activity Monitor, sysmon-process): 28.4% Max, 19.78% Avg
- Memory (Activity Monitor, sysmon-process): 88.77MiB Max, 81.96MiB Avg
- FPS Count (Game Performance, displayed-surfaces-per-second): 57 Max, 50.8 Avg
- Current Allocated Size(Game Performance, metal-gpu-current-allocated-size): 
- Percent Value (Metal Application, metal-gpu-counter-intervals):
- Thermal State (Game Performance, device-thermal-state-intervals): Nominal Max, Nominal Avg

### Makepad Taobao

- % CPU (Activity Monitor, sysmon-process): 72% Max, 43.24% Avg
- Memory (Activity Monitor, sysmon-process): 151.55 MiB Max, 149.21 MiB Avg
- FPS Count (Game Performance, displayed-surfaces-per-second): 60 Max, 58.18 Avg
- Current Allocated Size(Game Performance, metal-gpu-current-allocated-size): 
- Percent Value (Metal Application, metal-gpu-counter-intervals):
- Thermal State (Game Performance, device-thermal-state-intervals): Nominal Max, Nominal Avg

