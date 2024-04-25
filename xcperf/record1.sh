# step 1.1
# Example: > ./record1.sh makepad_taobao 00008110-001029521A13801E

xcrun xctrace record --output $1-ActivityMonitor.trace --template 'Activity Monitor' --device $2 --time-limit 10s  --window 10s --attach $1
