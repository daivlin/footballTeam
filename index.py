#! /usr/local/lib/python
#coding:utf-8
import sys, os

ABSPATH = os.path.dirname(__file__) 
sys.path.append('/usr/local/lib/python2.7/site-packages/') 
sys.path.append(ABSPATH) 
os.chdir(ABSPATH) 


import web
import conf
from web.contrib.template import render_jinja

#---------------config---------------#

urls = (
    r"/","Index",
    r"/about","About",
    r"/member","Member",
    r"/schedule","Schedule",
    r"/schedule_detail","Schedule_detail",
    r"/team_log","Team_log",
    r"/team_log_add","Team_log_add",
    r"/log_detail","Log_detail",
    r"/log_comment","Log_comment",
    r"/information","Information",

    r"/login","Login",
    r"/login_out","Login_out",
    r"/admin","Admin",
    r"/admin/infor","Admin",
    r"/admin/infor_edit","Admin_infor_edit",
    r"/admin/schedule","Admin_schedule",
    r"/admin/schedule_add","Admin_schedule_add",
    r"/admin/schedule_edit","Admin_schedule_edit",
    r"/admin/member","Admin_member",
    r"/admin/member_add","Admin_member_add",
    r"/admin/member_edit","Admin_member_edit",
    r"/admin/member_del","Admin_member_edit_del",
    r"/admin/picture","Admin_picture",
    r"/admin/score","Admin_score",
    r"/admin/team_log","Admin_team_log",
    r"/admin/team_log_del","Admin_team_log_del",
)


#db = web.database(dbn = "sqlite",db = os.path.join(ABSPATH,"data/data.db")) 
db = web.database(dbn = "sqlite",db = "/var/www/webpy-app/footballTeam/data/data.db") 



grade_dict = {
    1 : u"前锋",
    2 : u"中场",
    3 : u"后卫",
    4 : u"门将",
    }
grade_manage_dict = {
    u"领队" : 1,
    u"教练" : 2,
    u"队长" : 3,
    u"副队长" : 4,
    u"助理" : 5,
    }
    
def get_visitor():
    import shelve  
    s = shelve.open('data/visitor.dat') 
    try:
        count = s['count']
    except:
        s['count'] = 1
        count = s['count']
    s['count'] = count + 1
    s.close()
    return count
    
t_globals = {
            "ctx" : web.ctx,
            "team_infor" : db.select("team_infor")[0],
            "grade_dict" : grade_dict,
            "grade_manage_dict" : grade_manage_dict,
            "gravatar_dir" : r"/static/gravatar/",
            "visitor_count" : get_visitor,
        }

render = render_jinja(os.path.join(ABSPATH,"templates/"),encoding="utf-8",globals = t_globals)
render_admin = render_jinja(os.path.join(ABSPATH,"templates/admin/"),encoding="utf-8",globals = t_globals)



app = web.application(urls,globals())
application = app.wsgifunc()

store = web.session.DBStore(db, 'sessions')
sess = web.session.Session(app, store)

class Upload(object):
    
    def __init__(self,upfile):
        import os
        self.file = upfile
        self.file_ext = upfile.filename.split(".")[-1]
        self.file_name = upfile.filename.split(".")[-2]
        #self.file_path = upfile.filename.replace('\\','/')
    def save(self):
        import os,time
        if not self.file_ext in ("xlsx","xls"):
            return u"ext is not correct."

        try:
            os.mkdir(r"static/upload/")
            save_path = r"static/upload/"
        except:
            save_path = r"static/upload/"
            
        now = str(time.time()).split(".")[0]

        try:
            with open(save_path+"%s"%(now+"."+self.file_ext),"wb") as f:
                f.write(self.file.file.read())
            self.filepath = save_path+"%s"%(now+"."+self.file_ext)
        except:
            pass
        
    def get_data(self):
        import os
        try:
            import xlrd
            wb = xlrd.open_workbook(self.filepath)
            ws = wb.sheet_by_index(0)
            data = [ws.row_values(i) for i in range(ws.nrows)]
            return data
        except:
            return "xlrd is not exists!"
        finally:
            os.remove(self.filepath)


def logged():
    global sess
    if sess.get("login",0) == 1:
        return True
    else:
        return False    

def check_login():
    global sess
    if not logged():
        web.seeother("/login")
            


class Index(object):
    def GET(self):
        import random
        team_picture_dir = r"static/team_picture/"
        team_picture_list = os.listdir(os.path.join(ABSPATH,team_picture_dir))
        random.shuffle(team_picture_list) 
        schedule = db.select("schedule",order="match_time desc")
#	schedule = ""
        return render.index(locals())

class About(object):
    def GET(self):
        team_infor  =db.select("team_infor")[0]
        return render.about(locals())       

class Member(object):
    def GET(self):
    
        #grade_dict = {
        #    1 : u"1",
        #    2 : u"2",
        #    3 : u"3",
        #    4 : u"4",
        #    }
        gravatar_dir = r"static/gravatar/"
        member = db.select("member",order="grade")
        member_manage = db.select("member",where="manage <> 'none'",order="grade_manage")
        member_score = db.select("member",order="score desc")
        return render.member(locals())   
        
class Schedule(object):
    def GET(self):
        i = web.input()
        try:
		start_time = i.get("start_time","")
		end_time = i.get("end_time","")
	except:
		start_time = ""
		end_time = ""
        if not start_time or not end_time:
		schedule = db.select("schedule",order="match_time desc")

        else:
	        schedule = db.select("schedule",where="match_time > '%s' and match_time < '%s'"%(start_time,end_time))

        return render.schedule(locals())

class Schedule_detail(object):
    def GET(self):
        i = web.input()
        schedule_detail = db.select("schedule",where="id='%s'"%i.id)[0]
        return render.schedule_detail(locals()) 
        
class Team_log(object):
    def GET(self):
        i = web.input()
        
        page_size = 10        
	page_current = i.get("page",0)

        team_log_count = db.select("team_log",what="count(id) c")[0]["c"]
        page = conf.Page(page_size,team_log_count,page_current)
        page.set_url(web.ctx.fullpath)
        page_html = page.get_html()
        
        
        team_log = db.select("team_log",order="create_time desc",limit=page.size,offset=page.offset)
        return render.team_log(locals()) 
    
    def POST(self):
        import time
        now = time.strftime("%Y-%m-%d %H:%M")
        i = web.input()
        if not i.log_content.strip() or not i.log_title.strip():
            return "<script>alert('Content can not be empty!');history.go(-1);</script>"
        else:
            db.insert(
                "team_log",
                title = i.log_title.strip(),
                content = i.log_content,
                create_time = now,
                )
            return "<script>location.href='/team_log';</script>"
        
        
        
        
class Log_detail(object):
    def GET(self):
        i = web.input()
        log_id = i.log_id
        team_log_detail = db.select("team_log",where="id='%s'"%log_id)[0]
        db.update(
            "team_log",
            where="id='%s'"%log_id,
            scan = int(team_log_detail["scan"]) + 1,
            )
        
        log_comment_count = db.select("log_comment",what="count(id) c",where="log_id='%s'"%log_id)[0]["c"]
        log_comment = db.select("log_comment",where="log_id='%s'"%log_id,order="create_time desc")   
            
        return render.log_detail(locals()) 
  
class Log_comment(object)  :
    def POST(self):
        import time
        now = time.strftime("%Y-%m-%d %H:%M")
        i = web.input()
        db.insert(
            "log_comment",
            log_id = i.log_id,
            username = i.c_name,
            create_time = now,
            comment = i.c_comment,
            )
        return "ok"
        
class Information(object):
    def GET(self):
        from bs4 import BeautifulSoup as bs
        import requests as rq
        
        url = r"http://sports.sina.com.cn/global/"
        
        r = rq.get(url)
        r.encoding = "utf-8"
        html = r.text.encode("utf-8")

        soup = bs(html)
        li = soup.find(attrs={"data-sudaclick":"blk_focus_news"}).select("div ul > li a")[:20]
        content = [(i["href"],i.string) for i in li]
        
        def get_date(url):
            r = rq.get(url)
            r.encoding = "utf-8"
            html = r.text.encode("utf-8")

            soup = bs(html)
            date = soup.find("span",id="pub_date").string
            return date

        return render.information(locals()) 
        
    
class Login(object):
    def GET(self):
        if not logged():
            return render.login()
        else:
            web.seeother("/admin")
    def POST(self):
        i = web.input()
        userName = i.userName
        password = i.password
        if userName == "admin" and password == "12347890":
            sess.login = 1
            sess.name = "admin"
            web.seeother("/admin")
        else:
            return u"<script>alert('Account or password error');location.href='/login';</script>"  
class Login_out(object):
    def GET(self):
        sess.name = ""
        sess.login = 0
        sess.kill()
        web.seeother("/login")


    
        

class Admin(object):
    def GET(self):
        check_login()
        team_infor  =db.select("team_infor")[0]
        return render_admin.admin_infor(locals()) 

class Admin_infor_edit(object):
    def POST(self):
        check_login()
        i = web.input()
        db.update(
            "team_infor",
            where="id=1",
            infor = i.infor,
            rules = i.rules,
            team_name = i.team_name,
            slogan = i.slogan
        )
        return "<script>location.href='/admin';</script>"
    
class Admin_schedule(object):
    def GET(self):
        check_login()
        schedule = db.select("schedule",order="match_time desc")
        return render_admin.admin_schedule(locals())
        
class Admin_schedule_add(object):
    def GET(self):
        check_login()
        return render_admin.admin_schedule_add(locals())
    
    def POST(self):
        check_login()
        i = web.input()
        db.insert(
            "schedule",
            match_time = i.match_time,
            teams = i.teams,
            location = i.location,
            clothes = i.clothes,
            match_type = i.match_type,
            match_result = i.match_result,
            match_detail = i.match_detail,
        )
        return "<script>location.href='/admin/schedule';</script>"
        
    
class Admin_schedule_edit(object):
    def GET(self):
        check_login()
        i = web.input()
        s_id = i.s_id
        schedule = db.select("schedule",where="id='%s'"%s_id)[0]
        return render_admin.admin_schedule_edit(locals())
    
    def POST(self):
        check_login()
        i = web.input()
        db.update(
            "schedule",
            where="id='%s'"%i.s_id,
            match_time = i.match_time,
            teams = i.teams,
            location = i.location,
            clothes = i.clothes,
            match_type = i.match_type,
            match_result = i.match_result,
            match_detail = i.match_detail,
        )
        return "<script>location.href='/admin/schedule';</script>"
        
class Admin_member(object):
    def GET(self):
        check_login()
        member = db.select("member",order="number")
        return render_admin.admin_member(locals())
        
class Admin_member_add(object):
    def GET(self):
        check_login()
        return render_admin.admin_member_add(locals())
    
    def POST(self):
        check_login()
        i = web.input()
        db.insert(
            "member",
            name = i.name,
            number = i.number,
            age = i.age,
            height = i.height,
            tel = i.tel,
            ability = i.ability,
            grade = i.grade,
            manage = i.manage,
            grade_manage = i.grade_manage,
            gravatar = i.gravatar,
        )
        return "<script>location.href='/admin/member';</script>"
        
        
class Admin_member_edit(object):
    def GET(self):
        check_login()
        i = web.input()
        member = db.select("member",where="id='%s'"%i.id)[0]
        return render_admin.admin_member_edit(locals())
    
    def POST(self):
        check_login()
        i = web.input(gravatar={})

        db.update(
            "member",
            where="id='%s'"%i.id,
            name = i.name,
            header_name = i.header_name,
        )
        fx = i["gravatar"].file.read()
        if fx:
            with open("static/gravatar/%s.jpg"%i.header_name,"wb") as f:
                f.write(fx)
        return "<script>location.href='/admin/member';</script>"
       
class Admin_picture(object):
    def GET(self):
        check_login()
        return render_admin.admin_picture(locals())
        
    def POST(self):
        check_login()
        import time
        now_time = time.strftime("%Y%m%d%H%M%S")
        i = web.input(picture={})
        fx = i["picture"].file.read()
        if fx:
            with open("static/team_picture/%s.jpg"%(now_time),"wb") as f:
                f.write(fx)
        return "<script>alert('upload success!');location.href='/admin/picture';</script>"

       
class Admin_score(object):
    def GET(self):
        check_login()
        return render_admin.admin_score(locals())
        
    def POST(self):
        check_login()
    
        grade_dict = {
            u"前锋" : 1,
            u"中场" : 2,
            u"后卫" : 3,
            u"门将" : 4,
            }
    
    
        f = web.input(score={})
        
        try:
            with open("static/score_table.xlsx","wb") as fx:
                fx.write(f["score"].file.read())
            
        except:
            return "<script>alert('this file is opened!');history.go(-1);</script>"
            
        try:
            import xlrd
            wb = xlrd.open_workbook(r"static/score_table.xlsx")
            ws = wb.sheet_by_name("score")
            data = [ws.row_values(i) for i in range(ws.nrows)]
        except:
            return "xlrd is not exists!"
        t = db.transaction()
        db.query("delete from member") 
        for i in data[3:]:
            db.insert(
                "member",
                name = i[1],
                number = i[2],
                age = i[3],
                height = i[4],
                tel = i[5],
                ability = i[6],
                grade = grade_dict[i[7]],
                manage = i[8] if i[8] else "none",
                grade_manage = grade_manage_dict[i[8]] if i[8] else 0,
                company = i[9],
                score = i[10],
                
                )
        t.commit()
        return "<script>alert('Import success');location.href='/admin/score';</script>"
        
class Admin_team_log(object):
    def GET(self):
        check_login()
        i = web.input()
        
        page_size = 10 
        page_current = i.get("page",0)
        team_log_count = db.select("team_log",what="count(id) c")[0]["c"]
        page = conf.Page(page_size,team_log_count,page_current)
        page.set_url(web.ctx.fullpath)
        page_html = page.get_html()
        
        team_log = db.select("team_log",order="create_time desc",limit=page.size,offset=page.offset)
        return render_admin.admin_team_log(locals()) 
        
class Admin_team_log_del(object):
    def GET(self):
        check_login()
        i = web.input()
        db.delete(
            "team_log",
            where="id='%s'"%i.log_id,
            )
        raise web.seeother("/admin/team_log")
        
