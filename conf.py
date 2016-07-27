#! /usr/bin/python2
#coding:utf-8


class Page(object):
    '''分页类'''
    def __init__(self,page_size=1,data_count=10,page_current=1):
        import math
        self.size = page_size
        self.data_count = data_count
        self.page_current = int(page_current)
        self.page_max = int(math.ceil(self.data_count * 0.1 * 10 / self.size ))

        self.page_current = 1 if self.page_current < 1 else self.page_current
        self.page_current = self.page_max if self.page_current > self.page_max else self.page_current
            
        self.offset = ( self.page_current - 1) * self.size
    def set_url(self,url=""):
        if "?" in url:
            f_url = url.split("page")[0]
            if "&" in url:
                f_url += "&"
        else:
            f_url = url + "?"
        self.url = f_url
    def get_html(self):
        self.page_pre = self.page_current - 1
        self.page_next = self.page_current + 1
        if self.page_max in (0,1) :
            html = u'''
                <ul>
                    <li class="disabled"><a>首页</a></li> 
                    <li class="disabled"><a>上一页</a></li> 
                    <li class="disabled"><a>下一页</a></li> 
                    <li class="disabled"><a>尾页</a></li>
                </ul>
            '''
        elif self.page_current <= 1:
            html = u'''
                <ul>
                    <li class="disabled"><a>首页</a></li> 
                    <li class="disabled"><a>上一页</a></li> 
                    <li><a href="{self.url}page={self.page_next}">下一页</a></li> 
                    <li><a href="{self.url}page={self.page_max}">尾页</a></li>
                </ul>
            '''.format(self=self)
        elif self.page_current >= self.page_max:
            html = u'''
                <ul>
                    <li><a href="{self.url}page=1">首页</a></li> 
                    <li><a href="{self.url}page={self.page_pre}">上一页</a></li> 
                    <li class="disabled"><a>下一页</a></li> 
                    <li class="disabled"><a>尾页</a></li>
                </ul>   
            '''.format(self=self)
        else:
            html = u'''
                <ul>
                    <li><a href="{self.url}page=1">首页</a></li> 
                    <li><a href="{self.url}page={self.page_pre}">上一页</a></li> 
                    <li><a href="{self.url}page={self.page_next}">下一页</a></li> 
                    <li><a href="{self.url}page={self.page_max}">尾页</a></li>
                </ul>
            '''.format(self=self)
        banner = u'''
                    <ul>
                        <li class="disabled">
                            <a>第<code>{self.page_current}</code>页</a>
                        </li>
                        <li class="disabled">
                            <a>共<code>{self.page_max}</code>页</a>
                        </li>
                    </ul>
                  '''.format(self=self)
        html = '<div class="pagination">%s</div>'%(html + banner)
        
        if self.data_count > self.size:
            return html
        else:
            return ""
        
class Visitor(object):
    u'''访问者类'''
    def __init__(self,data):
        self.data = data
        
    def get_visitor(self):
        if not self.data["visitor"]:
            self.data["visitor"] = 1
        else:
            self.data["visitor"] += 1
        return self.data["visitor"]
        
class Upload(object):
    u'''文件上传类，接受excel，csv文件'''
    
    def __init__(self,upfile):
        import os
        self.file = upfile
        self.file_ext = upfile.filename.split(".")[-1]
        self.file_name = upfile.filename.split(".")[-2]
        #self.file_path = upfile.filename.replace('\\','/')
    def save(self):
        '''将文件存入服务器文件夹'''
        import os,time
        if not self.file_ext in ("xlsx","xls"):
            return u"文件类型错误"
        try:
            os.mkdir(r"static/upload/file_dir/")
            save_path = r"static/upload/file_dir/"
        except:
            save_path = r"static/upload/file_dir/"
            
        now = str(time.time()).split(".")[0]

        try:
            with open(save_path+"%s"%(now+"."+self.file_ext),"wb") as f:
                f.write(self.file.file.read())
            self.filepath = save_path+"%s"%(now+"."+self.file_ext)
        except:
            pass
        
    def get_data(self):
        '''返回数据'''
        import os
        try:
            import xlrd
            wb = xlrd.open_workbook(self.filepath)
            ws = wb.sheet_by_index(0)
            data = [ws.row_values(i) for i in range(ws.nrows)][2:]
            return data
        except:
            return "xlrd is not exists!"
        finally:
            os.remove(self.filepath)

def read_excel(f):
    '''获取excel表数据'''
    import xlrd
    wb = xlrd.open_workbook(f)
        
    sheets = wb.sheet_names()
    row = []
    for i in sheets:
        ws = wb.sheet_by_name(i)
        for j in range(0,ws.nrows):
            row.append(ws.row_values(j))
    return row
    
    
    
