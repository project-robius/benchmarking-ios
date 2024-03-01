# step 2
# Example: > ./extract.sh makepad_taobao

xcrun xctrace export --input $1-ActivityMonitor.trace --xpath '/trace-toc/run[@number="1"]/data/table[@schema="sysmon-process"]' --output $1-ActivityMonitor-sysmon-process.xml

# FPS
xcrun xctrace export --input $1-GamePerformance.trace --xpath '/trace-toc/run[@number="1"]/data/table[@schema="displayed-surfaces-per-second"]' --output $1-GamePerformance-surfaces-per-second.xml

# Thermal State
xcrun xctrace export --input $1-GamePerformance.trace --xpath '/trace-toc/run[@number="1"]/data/table[@schema="device-thermal-state-intervals"]' --output $1-GamePerformance-device-thermal-state-intervals.xml
