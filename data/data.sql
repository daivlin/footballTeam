/*
数据表：
(赛程)schedule:id,match_time,teams,location,clothes,match_type,match_result
(球队信息)team_infor:infor,rules,team_name,slogan
(成员)member:id,name,age,height,tel,ability,grade,gravatar
(日志)team_log:id,title,content,scan,create_time
(评论)log_comment:id,log_id,username,create_time
(出勤)attendance:id,member_id,attend,late,ask_leave,absence
*/

create table if not exists schedule(
    id integer primary key autoincrement,
    match_time varchar(30),
    teams varchar(30),
    location varchar(30),
    clothes varchar(20),
    match_type varchar(20),
    match_result varchar(10)
);
create table if not exists team_infor(
    infor text,
    rules text,
    team_name varchar(20),
    slogan varchar(40)
);
create table if not exists member(
    id integer primary key autoincrement,
    name varchar(20),
    age integer,
    height integer,
    tel integer,
    ability varchar(50),
    grade integer,
    gravatar varchar(40)
);
create table if not exists team_log(
    id integer primary key autoincrement,
    title varchar(30),
    content text,
    scan integer,
    create_time varchar(50)
);
create table if not exists log_comment(
    id integer primary key autoincrement,
    member_id integer,
    username varchar(50),
    create_time varchar(50)
);
create table if not exists attendance(
    id integer primary key autoincrement,
    log_id integer,
    attend integer,
    late integer,
    ask_leave integer,
    absence integer
);
create trigger if not exists del_team_log
after delete on team_log
for each row
begin
    delete from log_comment where log_id = old.id;
end;

