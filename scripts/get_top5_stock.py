#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Standard Library import
import os
import sys
import json
import datetime
from pprint import pprint
from collections import defaultdict

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
fund_details_json_path = os.path.join(workspace, f"fund_details_{today_yyyymmdd}.json")
if not os.path.isfile(fund_details_json_path):
    print("近3月的基金详情数据不存在。请先运行get_fund_details.py获取详情数据后再运行")
    sys.exit(1)

# 主函数
def main():
    # 初始化结果变量
    stock_stats = defaultdict(lambda: {'total_ratio': 0, 'count': 0, 'avg_ratio': 0})
    # 读取基金详情数据
    with open(fund_details_json_path, 'r') as f:
        fund_details_data = json.load(f)
        for fund_code, fund_data in fund_details_data.items():
            for holding in fund_data['holdings']:
                stock_name = holding['stock_name']
                ratio = float(holding['holding_ratio'].strip('%'))
        
                stock_stats[stock_name]['total_ratio'] += ratio
                stock_stats[stock_name]['count'] += 1
                stock_stats[stock_name]['avg_ratio'] = stock_stats[stock_name]['total_ratio'] / stock_stats[stock_name]['count']

        # 根据total_ratio降序选出前5支股票
        top_stocks = sorted(stock_stats.items(), key=lambda x: x[1]['total_ratio'], reverse=True)[:5]

        # 4. 输出结果
        result = {}
        print("最优5支股票（总持仓占比）：")
        for stock_name, stock_data in top_stocks:
            print(f"{stock_name}: {stock_data['total_ratio']:.2f}%"+f" | 基金覆盖：{stock_data['count']}只")
            result[stock_name] = stock_data

    # 将结果写入workspace中的top5_stock.json
    top5_stock_json_path = os.path.join(workspace, f"top5_stock_{today_yyyymmdd}.json")
    with open(top5_stock_json_path, 'w+') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main()
