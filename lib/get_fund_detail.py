#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Standard Library import
import os
import sys
import json
import datetime
from pprint import pprint

# Project Module import


# Secondary packages import
import requests
from bs4 import BeautifulSoup


# 读取系统时间，将当天的日期改成yyyy-mm-dd格式
today = datetime.datetime.now()
today_yyyy_mm_dd = today.strftime('%Y-%m-%d')
today_yyyymmdd = today.strftime('%Y%m%d')

# 检查并创建workspace工作目录
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
from global_settings import workspace
if not os.path.isdir(workspace):
    os.makedirs(workspace)

# 检查基金排行榜文件是否存在
top50_fund_csv_path = os.path.join(workspace, f"top50_stockfund_ranking_{today_yyyymmdd}.csv")
if not os.path.isfile(top50_fund_csv_path):
    print("近3月的50支最高收益率基金排行榜数据不存在。请先运行get_top50_fund.py获取数据后再运行")
    sys.exit(1)


# 相同基金有A和C之分，需要去重。去除成立不满3年的基金。
def remove_duplicate_fund(top50_fund_csv_path, code_and_name_json_path):
    code_and_name = {}
    with open(top50_fund_csv_path, 'r',encoding='utf-8') as f:
        lines = f.readlines()
        # 无表头
        for line in lines:
            duplicate_flag = False
            row_list = line.split(',')
            # 基金成立不满3年的，即数据中没有近3年收益率，则去除这支基金。
            if not row_list[13]:
                # print(row_list[1])
                continue
            if not code_and_name:
                # 结果为空，则写入第一行
                code_and_name[row_list[0]] = row_list[1]
            else:
                # 若基金名称以A或C结尾，需要与结果中已有基金名称核对，若一致则去掉。
                if row_list[1].endswith('A') or row_list[1].endswith('C'):
                    # 去掉基金名称末尾的A或C，与code_and_name中已有基金名称一致的基金去重
                    fund_original_name = row_list[1].rstrip('A').rstrip('C')
                    for name in code_and_name.values():
                        if name.startswith(fund_original_name):
                            duplicate_flag = True
                            break
                    if not duplicate_flag:
                        code_and_name[row_list[0]] = row_list[1]
                    else:
                        continue
                else:
                    code_and_name[row_list[0]] = row_list[1]
    if not code_and_name:
        print("去除掉成立不满3年的基金后，无可用基金代码")
        sys.exit(1)
    # 写入json文件
    with open(code_and_name_json_path, 'w+',encoding='utf-8') as f:
        json.dump(code_and_name, f, ensure_ascii=False, indent=4)

# 根据基金代码字符串，从天天基金网爬取基金
def get_fund_detail_by_code(code:str)->dict:
    # 010434
    fund_detail_url = f"https://fund.eastmoney.com/{code}.html"
    response = requests.get(fund_detail_url)
    response.raise_for_status() 
    response.encoding = "utf-8"
    # 解析html
    soup = BeautifulSoup(response.text, 'html.parser')
    # 定位到持仓信息区域
    position_shares = soup.find('li', {'id': 'position_shares', 'class': 'position_shares'})
    if not position_shares:
            raise ValueError("未找到持仓信息区域")
    # 持仓发布的截止日期
    date_element = position_shares.find('span', class_='end_date')
    date = date_element.text.replace("持仓截止日期: ", "") if date_element else "未知日期"
    # 提取持仓表格
    table = position_shares.find('table', class_='ui-table-hover')
    holdings = []
        
    if table:
    # 跳过表头行
        for row in table.find_all('tr')[1:]:
            cols = row.find_all('td')
            if len(cols) >= 3:
                # 提取股票名称
                stock_name = cols[0].get_text(strip=True)
                
                # 提取持仓占比
                holding_ratio = cols[1].get_text(strip=True)
                
                # 提取涨跌幅
                change_percent = cols[2].find('span').get_text(strip=True) if cols[2].find('span') else ""
                
                holdings.append({
                    "stock_name": stock_name,
                    "holding_ratio": holding_ratio,
                    "change_percent": change_percent
                })
    # 计算总持仓占比
        
    return {
        "publish_date": date,
        "total_ratio": holding_ratio,
        "holdings": holdings
    }

def main():
    remove_duplicate_fund_json_path = os.path.join(workspace, f"remove_duplicate_fund_{today_yyyymmdd}.json")
    remove_duplicate_fund(top50_fund_csv_path,remove_duplicate_fund_json_path)
    # 读取删选后的基金代码+名称json文件
    with open(remove_duplicate_fund_json_path, 'r',encoding='utf-8') as f:
        code_and_name = json.load(f)
    # 遍历基金代码，爬取基金详情
    fund_details = {}
    for code, name in code_and_name.items():
        try:
            fund_detail = get_fund_detail_by_code(code)
            fund_details[code] = fund_detail
        except Exception as e:
            print(f"获取基金{code}({name})详情失败：{e}")
    # 写入json文件
    fund_details_json_path = os.path.join(workspace, f"fund_details_{today_yyyymmdd}.json")
    with open(fund_details_json_path, 'w+',encoding='utf-8') as f:
        json.dump(fund_details, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main()
