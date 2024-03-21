# step 1.2
# Example: > ./record2.sh makepad_taobao 00008110-001029521A13801E

xcrun xctrace record --output $2-GamePerformance.trace --template 'Game Performance' --device $1 --time-limit 10s  --window 10s --attach $2
