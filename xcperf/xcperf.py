import subprocess
import logging
import os
import re
import csv
import xml.etree.ElementTree as ET
import configparser
import shutil
from collections import defaultdict

# 配置日志记录器
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAX_RETRIES = 3

# 全局变量保存用户输入的测试设备 UDID 和测试程序进程名称
test_device_udid = None
test_process_name = None
# 全局变量保存所有 table schema
table_schemas = set()

# 获取当前目录下的配置文件路径
config_file_path = os.path.join(os.path.dirname(__file__), 'config.ini')

def load_config():
    global test_device_udid, test_process_name
    config = configparser.ConfigParser()
    config.read(config_file_path)
    if 'TestConfig' in config:
        if 'test_device_udid' in config['TestConfig']:
            test_device_udid = config['TestConfig']['test_device_udid']
        if 'test_process_name' in config['TestConfig']:
            test_process_name = config['TestConfig']['test_process_name']

def save_config():
    global test_device_udid, test_process_name
    config = configparser.ConfigParser()
    config['TestConfig'] = {
        'test_device_udid': test_device_udid,
        'test_process_name': test_process_name
    }
    with open(config_file_path, 'w') as configfile:
        config.write(configfile)

def get_supported_instruments():
    try:
        # 执行 xcrun xctrace list instruments 命令
        output = subprocess.check_output(['xcrun', 'xctrace', 'list', 'instruments'], stderr=subprocess.STDOUT, universal_newlines=True)
        # 解析输出，将每一行保存到一个数组中（除了第一行标题）
        instruments = output.strip().split('\n')[1:]
        return instruments
    except subprocess.CalledProcessError as e:
        # 如果命令执行失败，输出错误信息
        error_output = e.output.strip()
        logger.error("错误: %s", error_output)
        return []

def get_supported_templates():
    try:
        # 执行 xcrun xctrace list templates 命令
        output = subprocess.check_output(['xcrun', 'xctrace', 'list', 'templates'], stderr=subprocess.STDOUT, universal_newlines=True)
        # 解析输出，将每一行保存到一个数组中（除了第一行标题）
        templates = output.strip().split('\n')[1:]
        return templates
    except subprocess.CalledProcessError as e:
        # 如果命令执行失败，输出错误信息
        error_output = e.output.strip()
        logger.error("错误: %s", error_output)
        return []

def get_paired_devices():
    try:
        # 执行 xcrun xctrace list devices 命令
        output = subprocess.check_output(['xcrun', 'xctrace', 'list', 'devices'], stderr=subprocess.STDOUT, universal_newlines=True)
        # 解析输出，将每一行保存到一个数组中（除了第一行标题）
        devices = output.strip().split('\n')[1:]
        return devices
    except subprocess.CalledProcessError as e:
        # 如果命令执行失败，输出错误信息
        error_output = e.output.strip()
        logger.error("错误: %s", error_output)
        return []

def check_xctrace_version():
    try:
        # 执行 xcrun xctrace version 命令
        output = subprocess.check_output(['xcrun', 'xctrace', 'version'], stderr=subprocess.STDOUT, universal_newlines=True)
        # 解析输出，获取版本号
        version = output.strip()
        logger.info("已安装 xctrace 版本号: %s", version)
        return True
    except subprocess.CalledProcessError as e:
        # 如果命令执行失败，输出错误信息
        error_output = e.output.strip()
        logger.error("错误: %s", error_output)
        return False

def get_test_device_udid():
    global test_device_udid
    test_device_udid = input("请输入测试设备的 UDID: ")

def get_test_process_name():
    global test_process_name
    test_process_name = input("请输入测试程序的进程名称: ")

def prompt_user_to_check_foreground_process():
    logger.warn("请确保测试进程在前台，并且清除其他多任务后按回车键继续...")

def record_performance_data(instrument):
    # 生成输出文件名
    output_file = f"{test_process_name}_{replace_special_chars(instrument)}.trace"
    # 替换命令中的参数值
    record_command = [
        'xcrun', 'xctrace', 'record',
        '--output', output_file,
        '--template', "'Activity Monitor'",
        '--instrument', f"'{instrument}'",
        '--device', test_device_udid,
        '--time-limit', '10s',
        '--attach', test_process_name
    ]
    # 执行录制命令
    for retry in range(MAX_RETRIES):
        proc = subprocess.Popen(record_command, shell=True)
        logger.info(' '.join(record_command))
        try:
            logger.info("开始录制 %s 的性能测试数据...", instrument)
            proc.wait()
            logger.info("录制 %s 的性能测试数据完成", instrument)
            break
        except subprocess.CalledProcessError as e:
            logger.error("录制 %s 的性能测试数据失败", instrument)
            # 删除失败任务生成的文件
            if os.path.exists(output_file):
                shutil.rmtree(output_file)
            logger.info("正在重试录制 %s 的性能测试数据... (%s/%s)", instrument, retry, MAX_RETRIES)
    else:
        logger.error("连续重试3次录制 %s 的性能测试数据失败，请检查并重试", instrument)

def export_test_results(instrument):
    # 生成输入和输出文件名
    input_file = f"{test_process_name}_{replace_special_chars(instrument)}.trace"
    output_file = f"{test_process_name}_{replace_special_chars(instrument)}_toc.xml"
    # 替换命令中的参数值
    export_command = [
        'xcrun', 'xctrace', 'export',
        '--input', input_file,
        '--toc',
        '>>', output_file
    ]
    # 执行输出命令
    for retry in range(MAX_RETRIES):
        proc = subprocess.Popen(export_command, shell=True)
        logger.info(' '.join(export_command))
        try:
            logger.info("开始导出 %s 的性能测试结果...", instrument)
            proc.wait()
            logger.info("导出 %s 的性能测试结果完成", instrument)
            break
        except subprocess.CalledProcessError as e:
            logger.error("导出 %s 的性能测试结果失败", instrument)
            logger.info("正在重试导出 %s 的性能测试结果... (%s/%s)", instrument, retry, MAX_RETRIES)
    else:
        logger.error("连续重试3次导出 %s 的性能测试结果失败，请检查并重试", instrument)

def extract_table_schemas_from_toc(instrument):
    # 生成 toc 文件名
    toc_file = f"{test_process_name}_{replace_special_chars(instrument)}_toc.xml"
    try:
        # 解析 toc 文件
        tree = ET.parse(toc_file)
        root = tree.getroot()
        # 遍历节点，提取 table schema
        for table in root.findall('.//table'):
            schema = table.get('schema')
            if schema:
                table_schemas.add(schema)
    except ET.ParseError as e:
        logger.error("解析 %s 的 toc 文件失败", instrument)

def parse_table_schema(schema, instrument):
    # 生成输入和输出文件名
    input_file = f"{test_process_name}_{replace_special_chars(instrument)}.trace"
    output_file = f"{test_process_name}_{replace_special_chars(instrument)}_{schema}.xml"
    # 替换命令中的参数值
    parse_command = [
        'xcrun', 'xctrace', 'export',
        '--input', input_file,
        '--xpath', f'\'/trace-toc/run[@number="1"]/data/table[@schema="{schema}"]\'',
        '--output', output_file
    ]
    # 执行解析命令
    for retry in range(MAX_RETRIES):
        proc = subprocess.Popen(parse_command, shell=True)
        logger.info(' '.join(parse_command))
        try:
            logger.info("开始解析 %s 的 %s 数据...", instrument, schema)
            proc.wait()
            logger.info("解析 %s 的 %s 数据完成", instrument, schema)
            break
        except subprocess.CalledProcessError as e:
            logger.error("解析 %s 的 %s 数据失败", instrument, schema)
            logger.info("正在重试解析 %s 的 %s 数据...  (%s/%s)", instrument, schema, retry, MAX_RETRIES)
    else:
        logger.error("连续重试3次解析 %s 的 %s 数据失败，请检查并重试", instrument, schema)

def replace_special_chars(string):
    # 替换特殊字符为连字符
    symbols = [' ', '/', '\\', ':', '*', '?', '"', '<', '>', '|']
    pattern = '|'.join(map(re.escape, symbols))
    return re.sub(pattern, '-', string)

def xml_to_csv(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    schema_name = root.find('.//schema').attrib['name']
    print('schema_name', schema_name)
    csv_file = f"{schema_name}.csv"

    # 打开CSV文件进行写入
    with open(csv_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        print(root.find('.//col'))
        # 获取表格模式（schema）的列名
        columns = [col.find('name').text for col in root.findall('.//col')]
        print('columns', columns)
        # 写入表头
        writer.writerow(columns)
        # 遍历XML中的每个节点

        rows = root.findall('.//row')
        print('len(rows)', len(rows))
        for row in rows:
            # 提取每行数据
            print('node.tag', row.tag, 'node.text', row.text)
            data = []
            for child in row:
                print('child.tag', child.tag, 'child.text', child.text)
                # 替换ref值为对应id的实际值
                if 'ref' in child.attrib:
                    ref_id = child.attrib['ref']
                    ref_xpath = f".//{child.tag}[@id='{ref_id}']"
                    ref_node = root.find(ref_xpath)
                    ref_data = node_to_data(ref_node)
                    print('ref_id', ref_id, 'ref_xpath', ref_xpath, 'ref_node', ref_node)
                    data.append(ref_data)
                else:
                    txt = node_to_data(child)
                    data.append(txt)
            # 将数据写入CSV文件
            writer.writerow(data)

def node_to_data(node):
    if 'fmt' in node.attrib:
        return node.attrib['fmt']
    elif node.text is not None:
        return node.text
    else:
        return 'N/A'

def analytic_csv(file, field):
    columns = defaultdict(list)
    with open(file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            for (k,v) in row.items():
                columns[k].append(v)
    values = [int(val) for val in columns[field]]
    logger.info("Analytic %s: %s Max, %s Avg", field, max(values), mean(values))

def main():
    global table_schemas, test_device_udid, test_process_name
    logger.info("检查是否安装 xctrace 工具链...")
    if check_xctrace_version() is False:
        # 如果未安装工具链，提示用户安装
        logger.error("请安装 xctrace 工具链，运行以下命令:")
        logger.error("xcode-select --install")
        return
    # 加载配置文件中的值
    load_config()
    if test_device_udid:
        choice = input("检测到已保存的测试设备 UDID ，是否使用？(y/n): ")
        if choice.lower() != 'n':
            logger.info("使用已保存的测试设备 UDID: %s", test_device_udid)
        else:
            get_test_device_udid()
            save_config()
            logger.info("您输入的测试设备的 UDID 是: %s", test_device_udid)
            
    if test_process_name:
        choice = input("检测到已保存的测试程序进程名称，是否使用？(y/n): ")
        if choice.lower() != 'n':
            logger.info("使用已保存的测试程序进程名称: %s", test_process_name)
        else:
            get_test_process_name()
            save_config()
            logger.info("您输入的测试程序的进程名称是: %s", test_process_name)

    # 提示用户检查测试进程是否在前台，并清除其他多任务
    prompt_user_to_check_foreground_process()
    
    # 获取支持的 Instruments 列表
    logger.info("正在获取支持的 Instruments 列表...")
    supported_instruments = get_supported_instruments()
    if supported_instruments is None or len(supported_instruments) == 0:
        logger.error("无法获取支持的 Instruments 列表，请检查命令是否正确。")
        return

    logger.info("以下是支持的 Instruments:")
    for instrument in supported_instruments:
        record_performance_data(instrument)
        export_test_results(instrument)
        extract_table_schemas_from_toc(instrument)
        for schema in table_schemas:
            parse_table_schema(schema, instrument)
            # TODO: xml_to_csv
            # TODO: analytic_csv
        
if __name__ == "__main__":
    main()
