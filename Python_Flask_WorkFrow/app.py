# -*- coding: utf-8 -*-
"""
 Using SQLAlchemy and Flask get db record.(GET)

"""
from flask import Flask, render_template, url_for, request, redirect, flash     #requestsをここでimportしないとpost時に「NameError: name 'request' is not defined」エラーになる
from flaski.database import db_session
from flaski.models import M_Syain                                            #DBのクラス名をここでimport
from flaski.models import M_Shinsei_Root
from flaski.models import Shinsei_JNL
from flaski.models import Shinsei_No_Management
from flaski.models import M_Busyo
from flaski.models import M_Msg

from flaski.database import Base
from datetime import datetime
import datetime
import os

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from sqlalchemy import and_
from sqlalchemy import desc

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle

#reportlab s
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.units import cm
#reportlab e


#アプリケーション分割
from flask import Blueprint

#別の.pyファイルを呼び出す時はメインのapp.pyからの絶対パスのディレクトリを指定する。import XXXのXXXは任意の名前を設定可
from templates.shins_syokai.s_syokai import Shinsei_S
from templates.shins_kyoka.s_kyoka import Shinsei_K
from templates.shins_nyuryoku.s_nyuryoku import Shinsei_N
from templates.msts.mst import M_MST


app = Flask(__name__)
#URIの部分でディレクトリを指定する。「sqlite:///〇〇.db」はフォルダ直下にdbファイルがある場合。
#別フォルダを作ってその中にdbファイルを格納した場合は下記のように「///」の後にフォルダを指定する
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flaski/D_SYSTEM.db'
db=SQLAlchemy(app)

#flashメッセージをセットするために設定。urandom24とはランダムの秘密鍵を生成する設定。何も指定が無ければこれでOK
app.secret_key = os.urandom(24)


# DB接続
engine = create_engine('sqlite:///flaski/D_SYSTEM.db')
Base = declarative_base()


# テーブルクラスのテーブルを生成
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


#他モジュール(.py)から呼び出す
app.register_blueprint(Shinsei_S)
app.register_blueprint(Shinsei_K)
app.register_blueprint(Shinsei_N)
app.register_blueprint(M_MST)



# 起動されたサーバーの/にアクセスした時の挙動を記述。
# @app.route("/hoge")で記述すれば、http://127.0.0.1:5000/aaでアクセスした時の挙動を記述できる。


#########################################################################################
##ログイン画面(トップページ)                                                            #
#########################################################################################
#トップページ
@app.route("/", methods=['POST', 'GET'])
def LOGIN():
    #ログインボタン押下時のアクション
    if request.method == 'POST':
        mEmp = M_Syain()
        
        #request.form[cont_XX]：htmlファイルの「name=」で指定された名称の項目の値を取得する
        login_id = request.form['cont_id']
        login_password = request.form['cont_pass']

        Emps = M_Syain.query.filter(M_Syain.id==login_id ,M_Syain.password==login_password).count()
        
        try:
            #IDとパスワードの組み合わせでCountする。存在するID+PASSの組み合わせは1意なのでCountすれば1になる。
            Emps = M_Syain.query.filter(M_Syain.id==login_id ,M_Syain.password==login_password).count()

            if Emps ==1:
             #ログイン成功の場合、社員IDを次画面へ渡す
             ###return render_template('menu_header.html',ID=login_id)
             #return render_template('top_page.html',ID=login_id)
             
             url = "/top_page?id={0}".format(login_id)
             return redirect(url)
            else:
             #ログイン失敗
             return render_template('login.html',Msg="※IDとパスワードの組み合わせが違います")
        except:
            return "フォームの送信中に問題が発生しました"
    else:
        #初めてページにアクセスした時のアクション
        return render_template('login.html')

#########################################################################################
##メニューヘッダー                                                                      #
#########################################################################################
@app.route('/menu_header', methods=['POST', 'GET'])
def MENUHEAD():
       getid = request.args.get('id')
       return render_template('menu_header.html',ID=getid)

#########################################################################################
##トップページ                                                                          #
#########################################################################################
@app.route('/top_page', methods=['POST', 'GET'])
def TOP_PAGE():

    getid = request.args.get('id')
       
    tstr = datetime.datetime.now()   
    tdatetime = tstr.strftime('%Y-%m-%d %H:%M:%S')  
    print('今の時間は' + str(tdatetime))   
       
    #or条件を使うときは「_or」をインポートして使用する。構文：or_(検索条件1,検索条件2)
    #and条件を使うときは「_and」をインポートして使用する。構文：and_(検索条件1,検索条件2)
    #昇順降順の並び替えをする場合はdesc,ascをインポートすること
    
    #orとandの複合条件で検索が可能
    #ex.)AかつBもしくはCかつD→.filter(or_((and_(A,B)),(and_(C,D)))
    
    Info = session.query(M_Msg, M_Syain).filter(M_Msg.from_syainno == M_Syain.id).filter(or_((and_(M_Msg.from_syainno==getid,M_Msg.from_syain_msg_close=='0')),(and_(M_Msg.to_syainno==getid,M_Msg.to_syain_msg_close=='0')))).order_by(desc(M_Msg.torokud)).all()
    
    session.close()
    return render_template('top_page.html',ID=getid,Infostr=Info,TITLE='TOP')
#########################################################################################
##トップページ(確認)                                                              
#########################################################################################
@app.route('/top_page/confirm/<id>/<no>/<from_id>/<to_id>', methods=['POST', 'GET'])
def TOP_PAGE_SUBMIT(id,no,from_id,to_id):

    url = ''
    #url内の引数から社員ID,申請番号取得
    syainid = id
    shinsei_no = no
    from_syain = from_id
    to_syain = to_id

    if from_syain == to_syain:
         print('第1許可者=申請者のパターン')
         url = "/shinsei_kyoka_detail?id={0}&no={1}".format(to_syain,no)
         return redirect(url)    

    if syainid == from_syain:
         print('申請者')
         url = "/shinsei_syokai_detail?id={0}&no={1}".format(from_syain,no)
         return redirect(url)    
    else:
         print('決裁者')
         url = "/shinsei_kyoka_detail?id={0}&no={1}".format(to_syain,no)
         return redirect(url)    
         
#########################################################################################
##トップページ(非表示)                                                              
#########################################################################################
@app.route('/top_page/hide/<id>/<no>/<from_id>/<to_id>', methods=['POST', 'GET'])
def TOP_PAGE_HIDE(id,no,from_id,to_id):

    url = ''
    #url内の引数から社員ID,申請番号取得
    syainid = id
    shinsei_no = no

    from_syain = from_id
    to_syain = to_id

    ##メッセージマスタ更新部(UPDATE)##
    Msg = session.query(M_Msg).filter(M_Msg.shinsei_no == no).first()
  
    if syainid == from_syain:
         print('申請者更新')
         Msg.from_syain_msg_close = '1'
    else:
         print('決裁者更新')
         Msg.to_syain_msg_close = '1'
  
    if from_syain == to_syain:
         print('FromもToも更新')
         Msg.from_syain_msg_close = '1'
         Msg.to_syain_msg_close = '1'
    try:
        session.commit()
    except:
        return "DB更新中にエラーが発生しました"
    finally:
        db.session.close()
  
    url = "/top_page?id={0}".format(syainid)
    return redirect(url) 


#########################################################################################
##最後に記述する箇所                                                              
#########################################################################################


if __name__ == "__main__":
    # サーバーの起動
    app.run()