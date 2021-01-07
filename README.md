### 代码数量的统计

## 已经完成的功能和特性

1. 不指定日期统计当前年的1月1号到当前时间的记录
2. 指定日期则从指定日起开始查询记录
3. 兼容py2和py3
```python
# 主要是str和bytes的转换处理问题
   def py2py3(self, str):
        py_verison = sys.version_info.major
        if py_verison > 2:
            str = self.str2bytes(str)
        return str

    def str2bytes(self, str):
        return str.encode(encoding='utf-8')
```
4. Terminal彩色输出　信息标识
5. 无任何第三方依赖
