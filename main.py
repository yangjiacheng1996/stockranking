#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import datetime
import subprocess
from pprint import pprint

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


def run_command_with_status(command_list: list) -> str:
    """
    执行系统命令并返回执行结果
    
    参数:
        command_list: 命令列表（如 ['ls', '-l']）
        
    返回:
        - 若命令执行成功（exit code=0），返回 stdout 内容
        - 若命令执行失败（exit code≠0），返回 stderr 错误信息
        - 若执行过程发生异常，返回异常描述
    """
    try:
        # 执行命令并捕获输出
        result = subprocess.run(
            command_list,
            capture_output=True,  # 捕获 stdout 和 stderr
            text=True,            # 输出转为字符串格式
            check=False            # 不自动抛出异常
        )
        
        # 检查退出状态码
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"Command failed with exit code {result.returncode}:\n{result.stderr.strip()}"
            
    except FileNotFoundError:
        return "Error: Command not found. Check if the executable exists."
    except PermissionError:
        return "Error: Permission denied. You may need elevated privileges."
    except Exception as e:
        return f"Unexpected error: {str(e)}"
    

if __name__ == '__main__':
    python_path = sys.executable
    project_root = os.path.dirname(os.path.abspath(__file__))

    get_top50_fund_script_path = os.path.join(project_root, 'get_top50_fund.py')
    get_top50_fund_result_path = os.path.join(workspace, f'top50_stockfund_ranking_{today_yyyymmdd}.csv')

    get_fund_detail_script_path = os.path.join(project_root, 'get_fund_detail.py')
    get_fund_detail_result_path = os.path.join(workspace, f'fund_details_{today_yyyymmdd}.json')

    get_top5_stock_script_path = os.path.join(project_root, 'get_top5_stock.py')
    get_top5_stock_result_path = os.path.join(workspace, f'top5_stock_{today_yyyymmdd}.json')


    # 获取基金排名
    if not os.path.isfile(get_top50_fund_result_path):
        get_top50_fund_cmd = [python_path, get_top50_fund_script_path]
        run_command_with_status(get_top50_fund_cmd)
    # 获取基金详情
    if not os.path.isfile(get_fund_detail_result_path):
        get_fund_detail_cmd = [python_path, get_fund_detail_script_path]
        run_command_with_status(get_fund_detail_result_path)
    # 获取前五股票名
    if not os.path.isfile(get_top5_stock_result_path):
        fund_rank_cmd = [python_path, get_fund_rank_path]
        run_command_with_status(fund_rank_cmd)

    # 打印结果，workspace/top5_stock_yyyymmdd.json内容
    with open(get_top5_stock_result_path, 'r') as f:
        pprint(json.load(f))
    
