#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Standard library imports
import datetime
import re
import sys
import os
import csv

# Project module imports

# Secondary package imports
import requests

# global variables
# 读取系统时间，将当天的日期改成yyyy-mm-dd格式
today = datetime.datetime.now()
today_yyyy_mm_dd = today.strftime('%Y-%m-%d')
today_yyyymmdd = today.strftime('%Y%m%d')

# 一年前的日期
one_year_ago = today - datetime.timedelta(days=365)
one_year_ago_yyyy_mm_dd = one_year_ago.strftime('%Y-%m-%d')

# 天天基金网基金近三月排行，股票型基金ft=gp，sc=3yzf是近三个月数据。前50支pn=50，降序st=desc，起始日期sd，终止日期ed。
ttjj_stockfund_ranking_url = f"https://fund.eastmoney.com/data/rankhandler.aspx?op=ph&dt=kf&ft=gp&rs=&gs=0&sc=3yzf&st=desc&sd={one_year_ago_yyyy_mm_dd}&ed={today_yyyy_mm_dd}&qdii=&tabSubtype=,,,,,&pi=1&pn=50&dx=1&v=0.36344957940512745"
#print(ttjj_stockfund_ranking_url)

# 伪装请求头。没有这个Header，请求会返回“无访问权限”
headers = {
    "Cookie": "ASP.NET_SessionId=qsywrmwfzruooubl2rngfrek; st_si=67956171174611; st_asi=delete; _adsame_fullscreen_18503=1; qgqp_b_id=8022511200f54c35ddbe3f525fc7a6a3; st_nvi=fdxLDASvatu3c_kqqupepa937; nid=01841d79e3583ae5c958e1841af0ec21; nid_create_time=1754901055233; gvi=KH3hDP_0IsbnybsdtS7tK88b4; gvi_create_time=1754901055234; nid_id=551190771; fullscreengg=1; fullscreengg2=1; EMFUND0=08-11%2016%3A52%3A36@%23%24%u8DEF%u535A%u8FC8%u8D44%u6E90%u7CBE%u9009%u80A1%u7968%u53D1%u8D77C@%23%24021876; EMFUND1=08-11%2016%3A53%3A57@%23%24%u8DEF%u535A%u8FC8%u8D44%u6E90%u7CBE%u9009%u80A1%u7968%u53D1%u8D77A@%23%24021875; EMFUND2=08-11%2016%3A57%3A13@%23%24%u5E73%u5B89%u5148%u8FDB%u5236%u9020%u4E3B%u9898%u80A1%u7968%u53D1%u8D77C@%23%24019458; EMFUND3=08-11%2017%3A12%3A45@%23%24%u6C38%u8D62%u533B%u836F%u5065%u5EB7A@%23%24008618; EMFUND4=08-11%2017%3A06%3A49@%23%24%u5609%u5B9E%u4E92%u878D%u7CBE%u9009%u80A1%u7968A@%23%24006603; EMFUND5=08-11%2017%3A09%3A27@%23%24%u5BCC%u56FD%u533B%u836F%u521B%u65B0%u80A1%u7968A@%23%24019916; EMFUND6=08-11%2017%3A11%3A04@%23%24%u94F6%u534E%u6570%u5B57%u7ECF%u6D4E%u80A1%u7968%u53D1%u8D77%u5F0FA@%23%24015641; EMFUND7=08-11%2017%3A08%3A27@%23%24%u534E%u590F%u667A%u80DC%u65B0%u9510%u80A1%u7968A@%23%24018728; EMFUND8=08-11%2017%3A10%3A09@%23%24%u4E2D%u94F6%u5927%u5065%u5EB7%u80A1%u7968A@%23%24009414; EMFUND9=08-11 17:14:07@#$%u8D22%u901A%u96C6%u6210%u7535%u8DEF%u4EA7%u4E1A%u80A1%u7968A@%23%24006502; st_pvi=82407436480486; st_sp=2025-08-11%2016%3A12%3A41; st_inirUrl=https%3A%2F%2Ffund.eastmoney.com%2F; st_sn=26; st_psi=20250811171407553-112200305282-5017702856",
    "Host": "fund.eastmoney.com",
    "Referer": "https://fund.eastmoney.com/data/fundranking.html",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0",
}

# 检查并创建workspace工作目录
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
from global_settings import workspace
if not os.path.exists(workspace):
    os.makedirs(workspace)

# 初始化result
result = []


def main():
    # 1. 发送请求
    response = requests.get(url=ttjj_stockfund_ranking_url, headers=headers)
    if response.status_code != 200:
        print("ERROR, 请求失败，状态码：", response.status_code)
        sys.exit()
    if not response.text:
        print("ERROR, 请求失败，返回内容为空")
        sys.exit()
    if "无访问权限" in response.text:
        print(response.text)
        print("ERROR, 请求头Header无效，请联系开发更新header")
        sys.exit()

    # 2. 获取数据
    data = response.text
    # print(data)

    # 3. 正则匹配数据
    data_string = re.findall('\[(.*?)\]', data)[0]
    # print(data_string)

    # 4. 保存数据到本地csv文件
    tuple_data = eval(data_string)
    data_header = ["基金代码","基金简称","基金缩写","日期","单位净值","累计净值","日增长率","近1周","近1月","近3月","近6月","近1年","近2年","近3年","今年来","成立来","成立日","基金类型","unknown","购买手续费","打折手续费","打折率","打折手续费1","y","z"]
    # print(tuple_data)
    with open(os.path.join(workspace, f'top50_stockfund_ranking_{today_yyyymmdd}.csv'), 'w', encoding='utf-8') as f:
        csv_writer = csv.writer(f)
        for row in tuple_data:
            row_list = row.split(',')
            csv_writer.writerow(row_list)

if __name__ == "__main__":
    main()

