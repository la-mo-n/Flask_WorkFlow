# -*- coding: utf-8 -*-
"""
 Using SQLAlchemy and Flask get db record.(GET)

"""

###################################################################################
#基本イベントのインポート                                                         #
###################################################################################
#requestsをここでimportしないとpost時に「NameError: name 'request' is not defined」エラーになる
from flask import Flask, render_template, url_for, request, redirect
###################################################################################
#DB関連のインポート                                                               #
###################################################################################
#DBテーブル
from flaski.models import M_Syain                                           
from flaski.models import M_Shinsei_Root
from flaski.models import Shinsei_JNL
from flaski.models import Shinsei_No_Management
from flaski.models import M_Msg
from flaski.models import M_Busyo
#その他
from flaski.database import Base
from datetime import datetime
import datetime
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
###################################################################################
#pdf作成ツール(reportlab)のインポート                                             #
###################################################################################
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.units import cm
###################################################################################
#アプリ分割(Blueprint)のインポート                                                #
###################################################################################
# Flaskのインポート，
from flask import Flask, Blueprint

###################################################################################
##アプリを起動する定型文1                                                         #
###################################################################################
app = Flask(__name__)

###################################################################################
# DB接続＆テーブル生成                                                            #
###################################################################################
#URIの部分でディレクトリを指定する。「sqlite:///〇〇.db」はフォルダ直下にdbファイルがある場合。
#別フォルダを作ってその中にdbファイルを格納した場合は下記のように「///」の後にフォルダを指定する
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flaski/D_SYSTEM.db'
db=SQLAlchemy(app)

engine = create_engine('sqlite:///flaski/D_SYSTEM.db')
#Base
Base = declarative_base()

# テーブルクラスのテーブルを生成
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

###################################################################################
#Blueprint_モジュールの登録                                                       #
###################################################################################
#ここにメインとなる「app.py」と関連付ける「.py」ファイルを定義する
#書き方：〇〇(app.pyで定義したモジュール名) = Blueprint('XX(pyファイルの名称)', __name__)
Shinsei_K = Blueprint('s_kyoka', __name__)


#########################################################################################
##申請許可                                                                              #
#########################################################################################
@Shinsei_K.route('/shinsei_kyoka', methods=['POST', 'GET'])  #blueprintを使う場合、ここは「app.route」ではないので注意！自分の定義したモジュール名を書くこと！
def SHINSEI_KYOKA():
          
    #URLから「?id=」以降の文字列を取得
    getid = request.args.get('id')     
    SJNL = Shinsei_JNL.query.filter(Shinsei_JNL.shinseisaki_syainno==getid).limit(100).all()     
         
    #申請JNLから自分宛の申請情報を取得
    #申請情報は申請JNL.申請先社員番号にログインした社員のIDが登録されている場合に当画面にて表示する
    #申請JNL.申請先社員番号は最終決裁者の決済後NULLになる
    #SJNL = Shinsei_JNL.query.filter(Shinsei_JNL.shinseisaki_syainno==getid,Shinsei_JNL.shinsei_cond1==0).all()
    session.close()
    return render_template('shins_kyoka/shinsei_kyoka.html',shinseistr =SJNL,ID=getid,TITLE='申請許可')

#########################################################################################
##申請許可詳細                                                                          #
#########################################################################################
@Shinsei_K.route('/shinsei_kyoka_detail', methods=['POST', 'GET'])   #blueprintを使う場合、ここは「app.route」ではないので注意！自分の定義したモジュール名を書くこと！
def SHINSEI_KYOKA_DETAIL():

    getid = request.args.get('id') 
    getno = request.args.get('no')
    
    #last_approval = Root.last_approval_id
    
    if request.method == 'POST':
        
       shinseino = request.form['shinsei_no']
       rootid = request.form['root_id']
      
       #申請ルートマスタからデータを取得
       ##注意：SJNL = Shinsei_JNL.query.filter～のような書き方ではUPDATEされないので注意する!##
       SJNL=session.query(Shinsei_JNL).filter(Shinsei_JNL.shinsei_no == shinseino).first()
       #リダイレクトするために社員番号を格納しておく
       syainno = SJNL.shinseisaki_syainno
      
       MSG=session.query(M_Msg).filter(M_Msg.shinsei_no == shinseino).first()
       MSG2=session.query(M_Msg).filter(M_Msg.shinsei_no == shinseino).count()
       print('MSG２のカウント' + str(MSG2))

       #通知用に取得
       Msg_title = SJNL.shinsei_title
       Msg_str = ''
       Msg_to_syainno=''
      
       Root = session.query(M_Shinsei_Root).filter(M_Shinsei_Root.root_id == rootid).first()

       radio_select = request.form.get('radio')

       ##1人目が申請を許可/不許可する場合##
       if SJNL.shinsei_cond1 == '0':

            #許可する場合
            if radio_select == '1':
               SJNL.shinsei_cond1 = '1'
               
               if SJNL.shinseisaki_syainno == Root.last_approval_id:
               
                  ##通知用に取得
                  Msg_to_syainno = SJNL.shinseisaki_syainno
                  Msg_str = '許可されました。この決済は完了です。'
                                 
                  SJNL.shinsei_result = '1'
                  SJNL.shinseisaki_syainno=''
                  SJNL.koshind = datetime.datetime.now()
               else:
                  SJNL.shinseisaki_syainno = Root.shinsei_root2_id
                  SJNL.shinsei_cond2 = '0'
                  SJNL.koshind = datetime.datetime.now()
                  ##通知用に取得
                  Msg_to_syainno = SJNL.shinseisaki_syainno
                  Msg_str = '許可されました。'
                    
            #不許可の場合        
            else:
               SJNL.shinsei_cond1 = '2'
               SJNL.reason_denied = request.form['cont_reason_denied']
               SJNL.shinsei_result = '2'
               ##通知用に取得
               Msg_to_syainno = SJNL.shinseisaki_syainno
               Msg_str = '不許可となりました。'
                 
               SJNL.shinseisaki_syainno=''
               SJNL.koshind = datetime.datetime.now()
       
       ##2人目が申請を許可/不許可する場合##
       else:
            if SJNL.shinsei_cond2 == '0':

                #許可する場合
                if radio_select == '1':
                   SJNL.shinsei_cond2 = '1'
                   
                   if SJNL.shinseisaki_syainno == Root.last_approval_id:
                   
                      ##通知用に取得
                      Msg_to_syainno = SJNL.shinseisaki_syainno
                      Msg_str = '許可されました。この決済は完了です。'
               
                      SJNL.shinsei_result = '1'
                      SJNL.shinseisaki_syainno=''
                      SJNL.koshind = datetime.datetime.now()
                   else:
                      SJNL.shinseisaki_syainno = Root.shinsei_root3_id
                      SJNL.shinsei_cond3 = '0'
                      SJNL.koshind = datetime.datetime.now()
                      ##通知用に取得
                      Msg_to_syainno = SJNL.shinseisaki_syainno
                      Msg_str = '許可されました。'
                
                #不許可の場合        
                else:
                   SJNL.shinsei_cond2 = '2'
                   SJNL.reason_denied = request.form['cont_reason_denied']
                   SJNL.shinsei_result = '2'
                   
                   ##通知用に取得
                   Msg_to_syainno = SJNL.shinseisaki_syainno
                   Msg_str = '不許可となりました。'
   
                   SJNL.shinseisaki_syainno=''
                   SJNL.koshind = datetime.datetime.now()

            ##3人目が申請を許可/不許可する場合##
            else:          
                #許可する場合
                if radio_select == '1':
                   SJNL.shinsei_cond3 = '1'
                   SJNL.shinsei_result = '1'
                   
                   ##通知用に取得
                   Msg_to_syainno = SJNL.shinseisaki_syainno
                   Msg_str = '許可されました。この決済は完了です。'
                   
                   SJNL.shinseisaki_syainno=''
                   SJNL.koshind = datetime.datetime.now()

                #不許可の場合        
                else:
                   SJNL.shinsei_cond3 = '2'
                   SJNL.reason_denied = request.form['cont_reason_denied']
                   SJNL.shinsei_result = '2'
                   
                   ##通知用に取得
                   Msg_to_syainno = SJNL.shinseisaki_syainno
                   Msg_str = '不許可となりました。'
                   SJNL.shinseisaki_syainno=''
                   SJNL.koshind = datetime.datetime.now()

       #メッセージマスタ(更新部)
       MSG.to_syainno = Msg_to_syainno
       MSG.detail = Msg_title + '  について ' + Msg_str
       #UPDATEの場合は、commitのみでOK。session.addはINSERTの時に記述する
       try:
          session.commit()
       except:
           return "DB更新中にエラーが発生しました(申請JNL_申請許可)"
       finally:
           db.session.close()

       #元のページにリダイレクトする
       url = "/shinsei_kyoka?id={0}".format(syainno)
       return redirect(url)    
    else:
        SJNL = Shinsei_JNL.query.filter(Shinsei_JNL.shinsei_no==getno).all()     
        session.close()
        return render_template('shins_kyoka/shinsei_kyoka_detail.html', shinseistr =SJNL,ID=getid,TITLE='申請許可')

###################################################################################
##アプリを起動する定型文2(ファイルの1番最後に記述する)                             #
###################################################################################
if __name__ == "__main__":
    # サーバーの起動
    app.run()
