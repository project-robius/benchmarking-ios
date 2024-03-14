import subprocess
import logging
import os
import re
import csv
import asyncio
import xml.etree.ElementTree as ET
import configparser
import shutil
from collections import defaultdict
from statistics import mean 

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

def load_config(title="default"):
    global test_device_udid, test_process_name
    parser = configparser.ConfigParser()
    parser.read(config_file_path)
    if title not in parser:
        logger.error("找不到匹配的配置文件 %s", title)
        return
    
    config = parser[title]
    if 'test_device_udid' in config:
        test_device_udid = config['test_device_udid']
    if 'test_process_name' in config:
        test_process_name = config['test_process_name']

def save_config(title="default"):
    global test_device_udid, test_process_name
    parser = configparser.ConfigParser()
    config = {}
    if test_device_udid is not None:
        config.update({'test_device_udid': test_device_udid})
    if test_process_name is not None:
        config.update({'test_process_name': test_process_name})
    parser[title] = config

    with open(config_file_path, 'w') as configfile:
        parser.write(configfile)

async def run_shell_command(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    print(f'[{cmd!r} exited with {proc.returncode}]')
    if stdout:
        print(f'[stdout]\n{stdout.decode()}')
    if stderr:
        print(f'[stderr]\n{stderr.decode()}')

def get_supported_instruments():
    try:
        output = subprocess.check_output(['xcrun', 'xctrace', 'list', 'instruments'], stderr=subprocess.PIPE, universal_newlines=True)
        instruments = set(output.strip().split('\n')[1:])
        return instruments
    except subprocess.CalledProcessError as e:
        error_output = e.output.strip()
        logger.error("错误: %s", error_output)
        return set()
    
def get_preferred_instruments():
    return {'Activity Monitor'}

def get_supported_templates():
    try:
        output = subprocess.check_output(['xcrun', 'xctrace', 'list', 'templates'], stderr=subprocess.PIPE, universal_newlines=True)
        templates = set(output.strip().split('\n')[1:])
        return templates
    except subprocess.CalledProcessError as e:
        error_output = e.output.strip()
        logger.error("错误: %s", error_output)
        return set()

def get_preferred_templates():
    return {'Activity Monitor', 'Game Performance'}

def get_paired_devices():
    try:
        output = subprocess.check_output(['xcrun', 'xctrace', 'list', 'devices'], stderr=subprocess.PIPE, universal_newlines=True)
        devices = set(output.strip().split('\n')[1:])
        return devices
    except subprocess.CalledProcessError as e:
        error_output = e.output.strip()
        logger.error("错误: %s", error_output)
        return set()

def check_xctrace_version():
    try:
        output = subprocess.check_output(['xcrun', 'xctrace', 'version'], stderr=subprocess.PIPE, universal_newlines=True)
        version = output.strip()
        logger.info("已安装 xctrace 版本号: %s", version)
        return True
    except subprocess.CalledProcessError as e:
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

def record_performance_data(template, instrument):
    # 生成输出文件名
    output_file = f"{test_process_name}_{replace_special_chars(template)}_{replace_special_chars(instrument)}.trace"
    # 替换命令中的参数值
    record_command = [
        'xcrun', 'xctrace', 'record',
        '--output', output_file,
        '--template', template,
        '--instrument', instrument,
        '--device', test_device_udid,
        '--time-limit', '10s',
        '--window', '10s',
        '--attach', test_process_name
    ]
    # 执行录制命令
    for retry in range(MAX_RETRIES):
        logger.info(' '.join(record_command))
        proc = subprocess.Popen(record_command)
        try:
            logger.info("开始录制 %s %s 的性能测试数据... (%s/%s)", template, instrument, retry, MAX_RETRIES)
            proc.wait()
            logger.info("录制 %s %s 的性能测试数据完成", template, instrument)
            return
        except subprocess.CalledProcessError as e:
            logger.error("录制 %s %s 的性能测试数据失败 (%s/%s)", template, instrument, retry, MAX_RETRIES)
            # 删除失败任务生成的文件
            if os.path.exists(output_file):
                shutil.rmtree(output_file)

def export_test_results(template, instrument):
    # 生成输入和输出文件名
    input_file = f"{test_process_name}_{replace_special_chars(template)}_{replace_special_chars(instrument)}.trace"
    output_file = f"{test_process_name}_{replace_special_chars(template)}_{replace_special_chars(instrument)}_toc.xml"
    # 替换命令中的参数值
    export_command = [
        'xcrun', 'xctrace', 'export',
        '--input', input_file,
        '--output', output_file,
        '--toc'
    ]
    # 执行输出命令
    for retry in range(MAX_RETRIES):
        logger.info(' '.join(export_command))
        proc = subprocess.Popen(export_command)
        try:
            logger.info("开始导出 %s %s 的性能测试结果... (%s/%s)", template, instrument, retry, MAX_RETRIES)
            proc.wait()
            logger.info("导出 %s %s 的性能测试结果完成", template, instrument)
            return
        except subprocess.CalledProcessError as e:
            logger.error("导出 %s %s 的性能测试结果失败 (%s/%s)", template, instrument, retry, MAX_RETRIES)
            # 删除失败任务生成的文件
            if os.path.exists(output_file):
                shutil.rmtree(output_file)

def export_schmeas_toc(template, instrument):
    # 生成 toc 文件名
    toc_file = f"{test_process_name}_{replace_special_chars(template)}_{replace_special_chars(instrument)}_toc.xml"
    for retry in range(MAX_RETRIES):
        try:
            # 解析 toc 文件
            tree = ET.parse(toc_file)
            root = tree.getroot()
            table_schemas.clear()
            # 遍历节点，提取 table schema
            for table in root.findall('.//table'):
                schema = table.get('schema')
                if schema:
                    table_schemas.add(schema)
                else:
                    logger.info("没有找到 %s %s 的 %s 信息", template, instrument, schema)
        except ET.ParseError as e:
            logger.error("解析 %s %s 的 toc 文件失败 (%s/%s)", template, instrument, retry, MAX_RETRIES)

def export_table_schema(template, instrument, schema):
    # 生成输入和输出文件名
    input_file = f"{test_process_name}_{replace_special_chars(template)}_{replace_special_chars(instrument)}.trace"
    output_file = f"{test_process_name}_{replace_special_chars(template)}_{replace_special_chars(instrument)}_{schema}.xml"
    # 替换命令中的参数值
    parse_command = [
        'xcrun', 'xctrace', 'export',
        '--input', input_file,
        '--output', output_file,
        '--xpath', f'\'/trace-toc/run[@number="1"]/data/table[@schema="{schema}"]\''
    ]
    # 执行解析命令
    for retry in range(MAX_RETRIES):
        logger.info(' '.join(parse_command))
        proc = subprocess.Popen(parse_command)
        try:
            logger.info("开始解析 %s %s 的 %s 数据... (%s/%s)", template, instrument, schema, retry, MAX_RETRIES)
            proc.wait()
            logger.info("解析 %s %s 的 %s 数据完成", template, instrument, schema)
            return
        except subprocess.CalledProcessError as e:
            logger.error("解析 %s %s 的 %s 数据失败 (%s/%s)", template, instrument, schema, retry, MAX_RETRIES)
            # 删除失败任务生成的文件
            if os.path.exists(output_file):
                shutil.rmtree(output_file)

def replace_special_chars(string):
    # 替换特殊字符为连字符
    symbols = [' ', '/', '\\', ':', '*', '?', '"', '<', '>', '|']
    pattern = '|'.join(map(re.escape, symbols))
    return re.sub(pattern, '-', string)

def convert_csv(template, instrument, schema):
    input_file = f"{test_process_name}_{replace_special_chars(template)}_{replace_special_chars(instrument)}_{schema}.xml"
    output_file = f"{test_process_name}_{replace_special_chars(template)}_{replace_special_chars(instrument)}_{schema}.csv"
    try:
        tree = ET.parse(input_file)
        root = tree.getroot()
        schema_node = root.find('.//schema')
        if schema_node is None:
            logger.error("%s 数据为空，无法转换。", input_file)
            return
        schema_name = schema_node.attrib['name']
        print('schema_name', schema_name)
    except ET.ParseError as e:
        logger.error("无法解析 %s 的内容", input_file)


    # 打开CSV文件进行写入
    with open(output_file, 'w', newline='') as csvfile:
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

def analytic_csv(template, instrument, schema, field):
    input_file = f"{test_process_name}_{replace_special_chars(template)}_{replace_special_chars(instrument)}_{schema}.csv"
    columns = defaultdict(list)
    with open(input_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            for (k,v) in row.items():
                columns[k].append(v)
    values = [int(val) for val in columns[field]]
    logger.info("Analytic %s: %s Max, %s Avg", field, max(values), mean(values))

def main():
    global table_schemas, test_device_udid, test_process_name
    if check_xctrace_version() is False:
        logger.error("请安装 xctrace 工具链，运行以下命令: xcode-select --install")
        return
    
    # 加载配置文件中的值
    load_config()
    value_availabilities = [
        (test_device_udid, "检测到已保存的测试设备 UDID ，是否使用？(y/n):", get_test_device_udid),
        (test_process_name, "检测到已保存的测试程序进程名称，是否使用？(y/n):", get_test_process_name)
    ]
    for value, prompt, action in value_availabilities:
        if value is not None and input(prompt).lower() != 'n':
            logger.info("使用已保存的配置: %s。", value)
        else:
            action()
            save_config()
            logger.info("已保存新的配置: %s。", value)

    # 提示用户检查测试进程是否在前台，并清除其他多任务
    prompt_user_to_check_foreground_process()
    
    # 获取支持的 Instruments 列表
    supported_instruments = get_supported_instruments()
    preferred_instruments = get_preferred_instruments()
    if supported_instruments is None or len(supported_instruments) == 0:
        logger.error("无法获取支持的 Instruments 列表，请检查命令是否正确。")
        return
    
    supported_templates = get_supported_templates()
    preferred_templates = get_preferred_templates()
    if supported_templates is None or len(supported_templates) == 0:
        logger.error("无法获取支持的 Templates 列表，请检查命令是否正确。")
        return

    for template in supported_templates & preferred_templates:
        for instrument in supported_instruments & preferred_instruments:
            logger.info("========== %s, %s ==========", template, instrument)
            record_performance_data(template, instrument)
            export_test_results(template, instrument)
            export_schmeas_toc(template, instrument)
            for schema in table_schemas:
                export_table_schema(template, instrument, schema)
                convert_csv(template, instrument, schema)
                # TODO: analytic_csv
        
if __name__ == "__main__":
    main()
