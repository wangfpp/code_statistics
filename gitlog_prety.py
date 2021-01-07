# coding: utf8
# 代码数量统计

import subprocess as sup
import os
import re as r
import sys
from datetime import datetime, date
import calendar





class StatiCode:
    def __init__(self, mode, args):
        self.mode = mode
        self.argv = args
        self.enter_bytes = self.getEnterBytes()
    
    def main_f(self):
        '''主函数'''
        start_date, now_date, total_month = self.dateAbout()
        self.start_date = start_date
        self.now_date = now_date
        self.total_month = total_month
        self.branchs()
        

    def getEnterBytes(self):
        # 不同平台的回车字符
        enter_bytes = "\n"
        if(os.name == "nt"):
            enter_bytes = "\r\n"
        # 判断python版本号　a bytes-like object is required, not 'str'
        return self.py2py3(enter_bytes)

    def py2py3(self, str):
        py_verison = sys.version_info.major
        if py_verison > 2:
            str = self.str2bytes(str)
        return str

    def str2bytes(self, str):
        return str.encode(encoding='utf-8')

    def dateAbout(self):
        '''计算日期相关的函数体　返回开始和结束日期以及相差的月数'''
        _args = self.argv
        now_date = datetime.now()
        now_year = now_date.year
        now_month = now_date.month
        _start_date = "{}-01-01".format(now_year)
        if len(_args) > 1 and _args[1] != "":
            _start_date = _args[1]
        totla_month = self.totalMonth(_start_date, now_date)
        bk_start_date = datetime.strptime(_start_date, "%Y-%m-%d")
        return [bk_start_date, now_date, totla_month]

    def addMonths(self,sourcedate,months):
        '''
            源日期加上月数后的日期
        '''
        month=sourcedate.month - 1 + months
        year=int(sourcedate.year + month/12)
        month=month%12 + 1
        day=min(sourcedate.day,calendar.monthrange(year,month)[1])
        return date(year,month,day)

    def totalMonth(self, _start_date, now_date):
        '''计算开始日期和当前日期间隔的月数'''
        start_date = datetime.strptime(_start_date, "%Y-%m-%d")
        start_year = start_date.year
        start_month = start_date.month
        now_year = now_date.year
        now_month = now_date.month
        month = 0
        if (now_year >= start_year):
            _month = (now_year - start_year) * 12
            month = _month + (now_month- start_month) + 1
        # month = addMonths(current, 1)
        return month

        
    def branchs(self):
        try:
            cmd = "git branch"
            project_branchs = sup.check_output(cmd, shell=True)
            project_branchs = project_branchs.split(self.enter_bytes)
            for branch in project_branchs:
                if branch != "":
                    # 以*开头的是当前分支　可以直接进行log查询　其他分支需要checkout
                    print("\033[0;36;40m===================当前分支为:{}  ========================\033[0m".format(branch))
                    # m_patt = self.py2py3() 
                    pattern = r'^\*'
                    if sys.version_info.major > 2:
                        pattern = r.compile(b'^\*')

                    if r.match(pattern, branch):
                        self.yearCodeNum()
                    else:
                        try:
                            switch_branch_cmd = "git checkout {}".format(branch)
                            # switch_result = sup.check_output(switch_branch_cmd, shell=True)
                            # print(switch_result)
                            self.yearCodeNum()
                        except sup.CalledProcessError as err:
                            print("\033[31m {} \033[0m".format(err))

        except sup.CalledProcessError as err:
            print("\033[0;31;40m {} \033[0m".format(err))

    def yearCodeNum(self):
        ''''
        　统计当前分支下一定日期内的日志
        '''
        for i in range(0, self.total_month):
            start_date = self.addMonths(self.start_date, i)
            next_date = self.addMonths(self.start_date, i+1)
            start_date = start_date.strftime("%Y-%m-%d")
            next_date = next_date.strftime("%Y-%m-%d")
            self.monthCodeNum(start_date, next_date)

    
    def logPretty(self, start_date, end_date):
        '''
        查询某期间的日志格式化输出
        '''
        cmd = "git log --author=wangfpp --since={} --until={}  --pretty=tformat: --shortstat".format(start_date, end_date)
        try:
            sub_process = sup.check_output(cmd, shell=True)
        except sup.CalledProcessError as err:
            sub_process = ""
            print("\033[0;31;40m {} \033[0m".format(err))
            # os.system("")
            exit(1)
        return sub_process.split(self.enter_bytes)

    '''
    格式化 log输出并计算代码提交数量
    1 file changed, 21 insertions(+), 4 deletions(-)　
    '''
    def praseLog(self, log_str):
        pattern = r'[a-z \(\)\+\-]'
        if sys.version_info.major > 2:
            pattern = r.compile(b'[a-z \(\)\+\-]')
        log_num = r.sub(pattern, b"", log_str).split(b",")
        if self.mode == "detail":
            print("\033[0;34;40 {} \033[0m".format(log_str))
        code_num = {
            "file": 0,
            "add": 0,
            "delete": 0
        }
        for i,item in enumerate(log_num, start=0):
            if item: # 有空值的情况
                item = int(float(item))
                if (i == 0):
                    code_num["file"] += item
                elif (i == 1):
                    if (item >= 1000):
                        print("\033[0;33;40m此次提交代码{} \033[0m".format(item))
                    code_num["add"] += item
                elif ( i == 2):
                    code_num["delete"] += item
                
        return code_num

    '''
    计算一段时间内的代码量
    '''
    def monthCodeNum(self, start_date, next_date):
        log_list = self.logPretty(start_date, next_date)
        month_code = {
            "file": 0,
            "add": 0,
            "delete": 0
        }
        if(len(log_list) > 0):
            for log_item in log_list:
                code_num = self.praseLog(log_item)
                month_code["file"] += code_num["file"]
                month_code["add"] += code_num["add"]
                month_code["delete"] += code_num["delete"]
            print("\033[0;35;40m{}至{}期间您　共有:{}个文件变动 \r\n新增code:{}行 \r\n删除code:{}行 \r\n总计:{}行 \033[4m".format(
                    start_date,
                    next_date,
                    month_code["file"],
                    month_code["add"],
                    month_code["delete"],
                    month_code["add"]-month_code["delete"]
                    ))
        else:
            print("无提交记录")
        print("\033[0;34;40""\033[0m")

if __name__ == "__main__":
    argvs = sys.argv
    mode = "detail"
    if (len(argvs) > 1):
        date_str = argvs[1]
        mat = r.match(r"(\d{4}-\d{2}-\d{2})",date_str)
        if (mat):
            main = StatiCode(mode, argvs)
            main.main_f()
        else:
            print("\033[0;31;40m {} \033[0m".format("输入的日期格式必须是 2020-01-01"))
    else:
        now_date = datetime.now().strftime('%Y-%m-%d')
        print("""\033[0;31;33m 
            您没有提供附属参数则从{}开始统计您的代码
            您可以提供时间则从规定时间统计例如:
            python ./gitlog_prety.py  2020-11-01 \033[3m""".format(now_date))
        main = StatiCode(mode, argvs)
        main.main_f()
    