import os
import sys
import json
import datetime
import subprocess
from pprint import pprint
from collections import namedtuple

from global_settings import workspace

# 创建命令结果对象
CommandResult = namedtuple('CommandResult', ['success', 'output'])

def run_command_with_status(command_list: list) -> CommandResult:
    """
    增强版命令执行函数
    """
    try:
        result = subprocess.run(
            command_list,
            capture_output=True,
            text=True,
            check=True,  # 关键修改：非零退出码时抛异常
            timeout=300  # 添加5分钟超时
        )
        return CommandResult(success=True, output=result.stdout.strip())
    except subprocess.CalledProcessError as e:
        error_msg = f"""
        🚨 命令执行失败！
        命令: {e.cmd}
        退出码: {e.returncode}
        ──────────────────
        错误输出: {e.stderr.strip()}
        """
        return CommandResult(success=False, output=error_msg)
    except FileNotFoundError:
        return CommandResult(success=False, output="错误：命令不存在")
    except Exception as e:
        return CommandResult(success=False, output=f"意外错误：{str(e)}")

if __name__ == '__main__':
    python_path = sys.executable
    # 读取系统时间，将当天的日期改成yyyy-mm-dd格式
    today = datetime.datetime.now()
    today_yyyy_mm_dd = today.strftime('%Y-%m-%d')
    today_yyyymmdd = today.strftime('%Y%m%d')

    # project_root定义
    project_root = os.path.dirname(os.path.abspath(__file__)) 
    
    # 验证路径存在性
    os.makedirs(workspace, exist_ok=True)  # 自动创建缺失目录

    # 文件路径定义
    get_top50_fund_script_path = os.path.join(project_root, "scripts",'get_top50_fund.py')
    get_top50_fund_result_path = os.path.join(workspace, f'top50_stockfund_ranking_{today_yyyymmdd}.csv')

    get_fund_detail_script_path = os.path.join(project_root, "scripts",'get_fund_detail.py')
    get_fund_detail_result_path = os.path.join(workspace, f'fund_details_{today_yyyymmdd}.json')

    get_top5_stock_script_path = os.path.join(project_root, "scripts",'get_top5_stock.py')
    get_top5_stock_result_path = os.path.join(workspace, f'top5_stock_{today_yyyymmdd}.json')

    # 构造命令
    get_top50_fund_cmd = [python_path, get_top50_fund_script_path]
    get_fund_detail_cmd = [python_path, get_fund_detail_script_path]
    get_top5_stock_cmd = [python_path, get_top5_stock_script_path]

    # 执行命令
    if not os.path.isfile(get_top50_fund_result_path):
        get_top50_fund_result = run_command_with_status(get_top50_fund_cmd)
        if not get_top50_fund_result.success:
            print(get_top50_fund_result.output)
            sys.exit(1)
    if not os.path.isfile(get_fund_detail_result_path):
        get_fund_detail_result = run_command_with_status(get_fund_detail_cmd)
        if not get_fund_detail_result.success:
            print(get_fund_detail_result.output)
            sys.exit(1)
    if not os.path.isfile(get_top5_stock_result_path):
        get_top5_stock_result = run_command_with_status(get_top5_stock_cmd)
        if not get_top5_stock_result.success:
            print(get_top5_stock_result.output)
            sys.exit(1)
    # 读取结果文件    
    with open(get_top5_stock_result_path, 'r') as f:
        json_data = json.load(f)
        pprint(json_data)