xcrun xctrace record --output $2-ActivityMonitor.trace --template 'Activity Monitor' --device $1 --time-limit 10s  --window 10s --attach $2
