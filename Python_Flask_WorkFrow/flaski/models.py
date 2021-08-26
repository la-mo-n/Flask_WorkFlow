# -*- coding: utf-8 -*-
#テーブルの定義部分
from sqlalchemy import Column, Integer, String, Text, DateTime
from flaski.database import Base
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey



class M_Syain(Base):
    __tablename__ = 'M_Syain'
    id = Column(String(6), nullable=False, primary_key=True)
    name = Column(String(40), nullable=False)
    busyo = Column(String(6))
    password = Column(String(40), nullable=False)
    authority = Column(Integer)
    mail = Column(String(100))
    path_folder = Column(String(250))
    path_doc = Column(String(250))
    torokud = Column(DateTime, default=datetime.now())
    koshind = Column(DateTime, default=datetime.now())


class M_Shinsei_Root(Base):
    __tablename__ = 'M_Shinsei_Root'
    root_id = Column(String(5), nullable=False, primary_key=True)
    rootname = Column(String(40))
    shinsei_root1_id = Column(String(6))
    shinsei_root2_id = Column(String(6))
    shinsei_root3_id = Column(String(6))
    last_approval_id = Column(String(6))
    torokud = Column(DateTime, default=datetime.now())


class Shinsei_JNL(Base):
    __tablename__ = 'Shinsei_JNL'
    shinsei_no = Column(String(12), nullable=False, primary_key=True)
    shinseid = Column(String(10))
    shinsei_syainno = Column(String(6))
    root_id = Column(String(5))
    shinseisaki_syainno = Column(String(6))
    shinsei_title = Column(String(200))
    shinsei_detail = Column(String(1000))
    shinsei_syain1 = Column(String(6))
    shinsei_cond1 = Column(String(1))
    shinsei_syain2 = Column(String(6))
    shinsei_cond2 = Column(String(1))
    shinsei_syain3 = Column(String(6))
    shinsei_cond3 = Column(String(1))    
    shinsei_result = Column(String(1))
    reason_denied = Column(String(200))
    torokud = Column(DateTime, default=datetime.now())
    koshind = Column(DateTime, default=datetime.now())


class Shinsei_No_Management(Base):
    __tablename__ = 'Shinsei_No_Management'
    id = Column(String(6), nullable=False, primary_key=True)
    no = Column(Integer)


class M_Busyo(Base):
    __tablename__ = 'M_Busyo'
    busyoid = Column(String(5), nullable=False, primary_key=True)
    busyoname = Column(String(60))



class M_Msg(Base):
    __tablename__ = 'M_Msg'
    shinsei_no = Column(String(12), nullable=False, primary_key=True)
    from_syainno = Column(String(6))
    from_syain_msg_close = Column(Integer)
    to_syainno = Column(String(6))
    to_syain_msg_close = Column(Integer)
    detail = Column(String(150))
    #torokud  = Column(DateTime, default=datetime.now())
    torokud  =Column(String(19))


def __init__M_Syain(self, id =None, name =None ,busyo =None , password =None, authority =None, mail =None, path_folder =None,path_doc =None, torokud =None,koshind =None):
        self.id = id
        self.name = name
        self.busyo = busyo
        self.password = password
        self.authority = authority
        self.mail = mail
        self.path_folder = path_folder
        self.path_doc = path_doc
        self.torokud = torokud
        self.koshind = koshind


def __init__M_Shinsei_Root(self, root_id =None, rootname =None, shinsei_root1_id =None, shinsei_root2_id =None, shinsei_root3_id =None, last_approval_id =None, torokud =None):
        self.root_id = root_id
        self.rootname = rootname
        self.shinsei_root1_id = shinsei_root1_id
        self.shinsei_root2_id = shinsei_root2_id
        self.shinsei_root3_id = shinsei_root3_id
        self.last_approval_id = last_approval_id
        self.torokud = torokud


def __init__Shinsei_JNL(self, shinsei_no=None, shinseid=None, shinsei_syainno=None, root_id=None, shinseisaki_syainno=None, shinsei_title=None, shinsei_detail=None, shinsei_syain1=None,shinsei_cond1=None,shinsei_syain2=None,shinsei_cond2=None,shinsei_syain3=None,shinsei_cond3=None,shinsei_result=None,reason_denied=None,torokud =None,koshind =None
):
        self.shinsei_no = shinsei_no 
        self.shinseid = shinseid
        self.shinsei_syainno = shinsei_syainno
        self.root_id = root_id
        self.shinseisaki_syainno = shinseisaki_syain
        self.shinsei_title = shinsei_title
        self.shinsei_detail = shinsei_detail
        self.shinsei_syain1 = shinsei_syain1
        self.shinsei_cond1 = shinsei_cond1
        self.shinsei_syain2 = shinsei_syain2
        self.shinsei_cond2 = shinsei_cond2
        self.shinsei_syain3 = shinsei_syain3
        self.shinsei_cond3 = shinsei_cond3
        self.shinsei_result = shinsei_result
        self.reason_denied = reason_denied
        self.torokud = torokud
        self.koshind = koshind

        
        
def __init__Shinsei_No_Management(self,id=None, no=None):
        self.id = id
        self.no = no


def __init__M_Busyo(self,busyoid=None, busyoname=None):
        self.busyoid = busyoid
        self.busyoname = busyoname


def __init__M_Msg(self,shinsei_no=None,from_syainno=None,from_syain_msg_close=None,to_syainno=None,to_syain_msg_close=None,detail=None,torokud=None):
        self.shinsei_no = shinsei_no
        self.from_syainno = from_syainno
        self.from_syain_msg_close = from_syain_msg_close
        self.to_syainno = to_syainno
        self.to_syain_msg_close = to_syain_msg_close
        self.detail = detail
        self.torokud  = torokud
        


def __repr__(self):
        return '<ID %r>' % (self.id)
        return '<NO %r>' % (self.no)









