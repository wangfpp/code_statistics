# coding: utf8
# 代码数量统计

import subprocess as sup
import os
import re as r
import sys
from datetime import datetime, date
from argparse import ArgumentParser
import calendar





class StatiCode:
    def __init__(self, kwargs):
        '''
            这里的函数初始化的参数应该在外部处理  处理函数不负责参数 应该只接受正确的参数进行逻辑处理
        '''
        print(kwargs)
        self.enter_bytes = self.getEnterBytes()
        if not kwargs.git_name:
            self.git_name = self.getGitUserName()
        else:
            self.git_name = kwargs.git_name

        if len(kwargs.branchs) <= 0:
            self.branchs = self.getAllBranchs()
        else:
            self.branchs = kwargs.branchs
        self.start_date = kwargs.start_date
        self.mode = kwargs.mode
        self.gitCount = {}
        '''
            {
                master: {
                    1: 2000,
                    2: 3000,
                    3: 400
                },
                datachannel: {

                }
            }
        # '''
    
    def main_f(self):
        '''主函数'''
        start_date, now_date, total_month = self.dateAbout()
        self.start_date = start_date
        self.now_date = now_date
        self.total_month = total_month
        self.branchsFn()
        self.count = {}
        for branch in self.gitCount:
            self.count[branch] = {
                "add": 0,
                "delete": 0,
                "nums": 0
            }
            for date_key in self.gitCount[branch]:
                self.count[branch]["add"] += self.gitCount[branch][date_key]["add"]
                self.count[branch]["delete"] += self.gitCount[branch][date_key]["delete"]
                self.count[branch]["nums"] += self.gitCount[branch][date_key]["nums"]
        print(self.count)

    def getGitUserName(self):
        '''
            查询本机的git config user.name
        '''
        try:
            git_name = sup.check_output("git config user.name", shell=True)
            git_name = git_name.strip() # strip 移除字符串头尾指定的字符 默认是空格或换行符
            if type(git_name) == bytes:
                git_name = self.byte2str(git_name)
            return git_name
        except sup.CalledProcessError as err:
            print("\033[0;31;40m {} \033[0m".format("查询本机的git username异常"))
            print("\033[0;31;40m {} \033[0m".format(err))
            exit(2)
        print("\033[0;34;40""\033[0m")

    def getAllBranchs(self):
        '''
            获取所有的分支(你操作过的分支 执行过git checkout)
        '''
        cmd = "git branch"
        try:
            project_branchs = sup.check_output(cmd, shell=True)
            project_branchs = project_branchs.split(self.enter_bytes)
            return project_branchs
        except sup.CalledProcessError as err:
            print("\033[0;31;40m {} \033[0m".format(err))
            exit(2)

    def getEnterBytes(self):
        # 不同平台的回车字符
        enter_bytes = b"\n"
        if(os.name == "nt"):
            enter_bytes = b"\r\n"
            if b"true" in self.crlf():
                enter_bytes = b"\n"
        # 判断python版本号　a bytes-like object is required, not 'str'
        return enter_bytes
    def crlf(self):
        '''
            查看是否开启了CRLF
        '''
        cmd = "git config core.autocrlf"
        try:
            crlf_val = sup.check_output(cmd, shell=True)
            return crlf_val
        except sup.CalledProcessError as err:
            print("\033[0;31;40m {} \033[0m".format(err))
            exit(2)

    def py2py3(self, str):
        py_verison = sys.version_info.major
        if py_verison > 2:
            str = self.byte2str(str)
        return str

    def byte2str(self, str):
        return str.decode(encoding='utf-8')

    def str2bytes(self, str):
        return str.encode(encoding='utf-8')

    def dateAbout(self):
        '''计算日期相关的函数体　返回开始和结束日期以及相差的月数'''
        now_date = datetime.now()
        now_year = now_date.year
        now_month = now_date.month
        _start_date = self.start_date
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

    def branchsFn(self):
        for branch in self.branchs:
            if type(branch) == bytes:
                branch = self.byte2str(branch)
            if branch != "":
                # 以*开头的是当前分支　可以直接进行log查询　其他分支需要checkout
                # print("\033[0;36;40m===================当前分支为:{}  ========================\033[0m".format(branch))
                # m_patt = self.py2py3() 
                pattern = r'^\*'
                if r.match(pattern, branch):
                    self.yearCodeNum(branch)
                else:
                    try:
                        switch_branch_cmd = "git checkout {}".format(branch)
                        switch_result = sup.check_output(switch_branch_cmd, shell=True)
                        self.yearCodeNum(branch)
                    except sup.CalledProcessError as err:
                        print("\033[31m {} \033[0m".format(err))

    def yearCodeNum(self, branch):
        ''''
        　统计当前分支下一定日期内的日志
        '''
        if branch not in self.gitCount:
            self.gitCount[branch] = {}
        for i in range(0, self.total_month):
            start_date = self.addMonths(self.start_date, i)
            next_date = self.addMonths(self.start_date, i+1)
            start_date = start_date.strftime("%Y-%m-%d")
            next_date = next_date.strftime("%Y-%m-%d")
            date_key = "{}:{}".format(start_date, next_date)
            if date_key not in self.gitCount[branch]:
                self.gitCount[branch][date_key] = {}
            self.monthCodeNum(start_date, next_date, branch, date_key)

    
    def logPretty(self, start_date, end_date):
        '''
        查询某期间的日志格式化输出
        '''
        cmd = "git log --author={} --since={} --until={}  --pretty=tformat: --shortstat".format(self.git_name, start_date, end_date)
        try:
            pretty_commit_log = sup.check_output(cmd, shell=True)
        except sup.CalledProcessError as err:
            pretty_commit_log = ""
            print("\033[0;31;40m {} \033[0m".format(err))
            # os.system("")
            exit(1)
        return pretty_commit_log.split(self.enter_bytes)

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
            c
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
    def monthCodeNum(self, start_date, next_date, branch, date_key):
        log_list = self.logPretty(start_date, next_date)
        month_code = {
            "file": 0,
            "add": 0,
            "delete": 0,
            "nums": 0
        }
        if(len(log_list) > 0):
            for log_item in log_list:
                code_num = self.praseLog(log_item)
                month_code["file"] += code_num["file"]
                month_code["add"] += code_num["add"]
                month_code["delete"] += code_num["delete"]
                month_code["nums"] += 1
            # print("\033[0;35;40m{}至{}期间您　共有:{}个文件变动 \r\n新增code:{}行 \r\n删除code:{}行 \r\n总计:{}行 \033[4m".format(
            #         start_date,
            #         next_date,
            #         month_code["file"],
            #         month_code["add"],
            #         month_code["delete"],
            #         month_code["add"]-month_code["delete"]
            #         ))
        else:
            pass
            # print("无提交记录")
        # print("\033[0;34;40""\033[0m")
        self.gitCount[branch][date_key]["add"] = month_code["add"]
        self.gitCount[branch][date_key]["delete"] = month_code["delete"]
        self.gitCount[branch][date_key]["nums"] = month_code["nums"]

if __name__ == "__main__":
    now_date = datetime.now()
    now_year_start = "{}-01-01".format(now_date.year)
    parse = ArgumentParser(description="查询某人某项目一定时间内的代码提交量")
    parse.add_argument("-mode", "--mode", choices=["default", "detail", "slient"], type=str, default="default", help="是否输出详细信息")
    parse.add_argument("-name", "--git_name", type=str, help="您的git config user.name")
    parse.add_argument("-branchs", "--branchs", nargs="+", help="要查询的分支列表", default=[])
    parse.add_argument("-st", "--start_date", type=str, default=now_year_start, help="查询的起始日期默认当前年的一月一号")
    
    arguments = parse.parse_args()
    mat = r.match(r"(\d{4}-\d{2}-\d{2})",arguments.start_date)
    if not mat:
        print("\033[0;31;40m {} \033[0m".format("输入的日期格式必须是 YYYY-MM-dd"))
        exit(1)
    main = StatiCode(arguments)
    main.main_f()
  
    '''
        退出的状态码 
            1 参数错误
            2 异常情况
    '''
    