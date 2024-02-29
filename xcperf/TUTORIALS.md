# 测试步骤
1. （可省略，仅首次需要）编译并启动应用，退出其他进程
2. （可省略，仅首次需要）执行 xcrun xctrace list devices 获取设备 UDID
3. 执行如下命令，根据终端输出提示开始操作应用.注意将进程名称（MockTaobao）和 UDID 替换为实际值。
```bash
xcrun xctrace record --output MockTaobao_ActivityMonitor.trace --template 'Activity Monitor' --device '00008110-001029521A13801E' --time-limit 10s  --window 10s --attach MockTaobao
```
看到终端提示"Output file saved as"再进入下一步。如果报错就删掉output的文件再次执行。
4. 执行如下命令，根据终端输出提示开始操作应用.注意将进程名称（MockTaobao）和 UDID 替换为实际值。
```bash
xcrun xctrace record --output MockTaobao_GamePerformance.trace --template 'Game Performance' --device '00008110-001029521A13801E' --time-limit 10s  --window 10s --attach MockTaobao
```
看到终端提示"Output file saved as"再进入下一步。如果报错就删掉output的文件再次执行。
5. （可省略，方便验证）执行如下命令，获取测试结果的目录。如果失败就重新执行。
```bash
xcrun xctrace export --input MockTaobao_ActivityMonitor.trace --toc > MockTaobao_ActivityMonitor.xml 
xcrun xctrace export --input MockTaobao_GamePerformance.trace --toc > MockTaobao_GamePerformance.xml 
```
6. 执行如下命令，导出结果的详细数据。
```bash
# % CPU, CPU Time, Memory Usage
xcrun xctrace export --input MockTaobao_ActivityMonitor.trace --xpath '/trace-toc/run[@number="1"]/data/table[@schema="sysmon-process"]' --output MockTaobao_ActivityMonitor_sysmon-process.xml
# FPS
xcrun xctrace export --input MockTaobao_GamePerformance.trace --xpath '/trace-toc/run[@number="1"]/data/table[@schema="displayed-surfaces-per-second"]' --output MockTaobao_GamePerformance_displayed-surfaces-per-second.xml
# Thermal State
xcrun xctrace export --input MockTaobao_GamePerformance.trace --xpath '/trace-toc/run[@number="1"]/data/table[@schema="device-thermal-state-intervals"]' --output MockTaobao_GamePerformance_device-thermal-state-intervals.xml
```
7. 复制已导出xml文件的路径，调用```python3 xml2csv.py __XML_FILE_PATH__```即可导出csv数据，导出后可以使用excel计算最大值和平均值。