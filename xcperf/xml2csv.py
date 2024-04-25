import csv
import os
import sys
import xml.etree.ElementTree as ET

def xml_to_csv(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    schema_name = root.find('.//schema').attrib['name']
    print('schema_name', schema_name)

    path, _ = os.path.splitext(xml_file)
    csv_file = path.split("/")[-1] + ".csv"

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
        if len(rows) == 0:
            print('没有对应的数据，导出失败')
            return
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

def main():
    argv = sys.argv
    if len(argv) > 1:
        for xml in argv[1:]:
            xml_to_csv(xml)

if __name__ == '__main__':
    main()
