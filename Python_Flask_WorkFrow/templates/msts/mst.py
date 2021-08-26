# -*- coding: utf-8 -*-
"""
 Using SQLAlchemy and Flask get db record.(GET)

"""

###################################################################################
#基本イベントのインポート                                                         #
###################################################################################
#requestsをここでimportしないとpost時に「NameError: name 'request' is not defined」エラーになる。sysは何も処理しない場合に処理を抜ける場合に使う
from flask import Flask, render_template, url_for, request, redirect, flash
###################################################################################
#DB関連のインポート                                                               #
###################################################################################
#DBテーブル
from flaski.models import M_Syain                                           
from flaski.models import M_Shinsei_Root
from flaski.models import Shinsei_JNL
from flaski.models import Shinsei_No_Management
from flaski.models import M_Busyo
from flaski.models import M_Msg
#その他
from flaski.database import Base
from datetime import datetime
import datetime
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_       #or条件
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
M_MST = Blueprint('mst', __name__)


#########################################################################################
##社員マスタ                                                                            #
#########################################################################################
@M_MST.route('/m_syain_admin', methods=['POST', 'GET']) #blueprintを使う場合、ここは「app.route」ではないので注意！自分の定義したモジュール名を書くこと！
def MST_SYAIN():
    
    getid = request.args.get('id')
    getmode = request.args.get('mode')
    
    #M_SYAIN.htmlでapp.pyの値を受け取るときは「Empstr.Emp1.id」のように、、
    #結合テーブル名.取得元のテーブル名.取得元のテーブルの項目名と3段階で記述する(ex.<td>{{ Empstr.Emp1.id }}</td>)
     
    Empstr_Admin =session.query(M_Syain, M_Busyo).filter(M_Syain.busyo == M_Busyo.busyoid).all()
    session.close()
    return render_template('msts/m_syain_admin.html', Syainstr=Empstr_Admin,ID=getid,TITLE='社員マスタ')

#########################################################################################
##社員マスタ(管理者権限以外のマスタメンテ                                               #
#########################################################################################
@M_MST.route('/m_syain', methods=['POST', 'GET']) #blueprintを使う場合、ここは「app.route」ではないので注意！自分の定義したモジュール名を書くこと！
def MST_SYAIN_NOT_ADMIN():
    
    #「更新」ボタン押下時のメソッド
    if request.method == 'POST':

        #Javascriptのダイアログの「はい」「いいえ」のどっちを選択したか格納
        select_yesno = request.form.get('flg_yes_no')
        
        getid = request.form['syain_no']
        url = "/m_syain?id={0}".format(getid)
        
        #注意：SJNL = Shinsei_JNL.query.filter～のような書き方ではUPDATEされないので注意する!##
        Syain=session.query(M_Syain).filter(M_Syain.id == getid).first()
        
        #社員マスタ(UPDATE)
        Syain.password = request.form['password']
        Syain.mail = request.form['mail']        
        Syain.path_doc = request.form['doc_path']
        
        if select_yesno == 'YES':    #Javascriptで表示した確認ダイアログで「はい」を選択した場合   
           #コミット：UPDATEの場合は、commitのみでOK。session.addはINSERTの時に記述する
           try:
              session.commit()                    
           except:
              flash('DB更新中にエラーが発生しました(社員マスタ)。更新する項目をチェックしてください')
              return redirect(url)
           finally:
              session.close()
           
           return redirect(url)
           
        else:    #キャンセルの場合
           #キャンセルの場合は何もしない。何もしない方法はJavascriptでreturn falseを返し、該当する.pyファイルのロジックに「pass」を書く
           pass
    else:
        #URLの「href="m_syain?id={{ ID }}」の「id=」以降の値を取得する(今回の場合、社員番号)
        getid = request.args.get('id')
        
        #権限を取得
        Syain = M_Syain.query.filter(M_Syain.id==getid).first()
        print('取得した権限は' + str(Syain.authority))
        
        if Syain.authority == 9:    #Admin権限
           print('権限9のページ')
           url = "/m_syain_admin?id={0}".format(getid)
           return redirect(url)
        else:
           print('権限9以外のページ')           
           #TBL結合(join)の場合、「.all」で抜き出す
           #M_SYAIN.htmlでapp.pyの値を受け取るときは「Empstr.M_Syain.id」のように結合TBL名.取得元のTBL名.取得元TBL項目名と3段階で記述する(ex.<td>{{ Empstr.M_Syain.id }}</td>)
           Empstr =session.query(M_Syain, M_Busyo).filter(M_Syain.busyo == M_Busyo.busyoid).filter(M_Syain.id==getid).all()
           session.close()
           return render_template('msts/m_syain.html', Syainstr=Empstr,ID=getid,TITLE='社員マスタ')
           
#########################################################################################
##社員マスタ(Admin権限による編集、新規追加)                                          
#########################################################################################
@M_MST.route('/m_syain_edit/<id>/<to_id>/<mode>', methods=['POST', 'GET']) #blueprintを使う場合、ここは「app.route」ではないので注意！自分の定義したモジュール名を書くこと！
def MST_SYAIN_EDIT(id,to_id,mode):
    
    if request.method == 'POST':
    
        #Javascriptで表示したYES/NOダイアログの値をここで取得
        select_yesno = request.form.get('flg_yes_no')
        userid = id   #ログインユーザのID
        getid = to_id  #更新削除対象者
        getmode = mode
        syainid =id
        url = "/m_syain?id={0}".format(syainid)

        if getmode == 'add':
           #社員マスタ(INSERT)
           Syain = M_Syain()
           Syain.id = request.form['syain_no']
           Syain.name = request.form['syain_name']
           Syain.password = request.form['password']
           strbusyo = request.form['ddl_busyo']
           Syain.busyo = strbusyo[0:5]
           Syain.authority = request.form['ddl_kyoka']
           Syain.mail = request.form['mail']
           Syain.path_folder = request.form['folder_path']
           Syain.path_doc = request.form['doc_path']
           Syain.torokud = datetime.datetime.now()
           Syain.koshind = datetime.datetime.now()

           #申請番号管理マスタ(INSERT)
           SNManage = Shinsei_No_Management()
           SNManage.id = request.form['syain_no']
           SNManage.no = 0

           if select_yesno == 'YES':    #Javascriptで表示した確認ダイアログで「はい」を選択した場合   
              #コミット：UPDATEの場合は、commitのみでOK。session.addはINSERTの時に記述する
              try:
                 db.session.add(Syain)
                 db.session.add(SNManage)
                 db.session.commit()                    
              except:
                 flash('DB更新中にエラーが発生しました(社員マスタ)。キー重複、禁止文字が含まれないかをチェックしてください')
                 #元のページにリダイレクトする
                 return redirect(url)
              finally:
                 session.close()
              
              #元のページにリダイレクトする
              Empstr_Admin =session.query(M_Syain, M_Busyo).filter(M_Syain.busyo == M_Busyo.busyoid).all()
              session.close()
              return redirect(url)
              
           else:    #キャンセルの場合
              #キャンセルの場合は何もしない。何もしない方法はJavascriptでreturn falseを返し、該当する.pyファイルのロジックに「pass」を書く
              pass
        else:
           if getmode == 'edit':    #修正モード
              print('EDITモード')
              #社員マスタ(UPDATE)
              Syain = session.query(M_Syain).filter(M_Syain.id==getid).first()
              Syain.name = request.form['syain_name']
              Syain.password = request.form['password']              
              strbusyo = request.form['ddl_busyo']
              Syain.busyo = strbusyo[0:5]
              Syain.authority = request.form['ddl_kyoka']
              Syain.mail = request.form['mail']
              Syain.path_folder = request.form['folder_path']
              Syain.path_doc = request.form['doc_path']
              Syain.koshind = datetime.datetime.now()
              
              if select_yesno == 'YES':    #Javascriptで表示した確認ダイアログで「はい」を選択した場合   
                 #コミット：UPDATEの場合は、commitのみでOK。session.addはINSERTの時に記述する
                 try:
                    session.commit()
                 except:
                    flash('DB更新中にエラーが発生しました(社員マスタ)。更新する項目をチェックしてください')
                    return redirect(url)
                 finally:
                    session.close()
                 #元のページにリダイレクトする
                 return redirect(url)
              else:    #キャンセルの場合
                 #キャンセルの場合は何もしない。何もしない方法はJavascriptでreturn falseを返し、該当する.pyファイルのロジックに「pass」を書く
                 pass
           
           else:      #削除モード
           
                 Del_Syain =  session.query(M_Syain).filter(M_Syain.id==getid).first()
                 
                 if select_yesno == 'YES':    #Javascriptで表示した確認ダイアログで「はい」を選択した場合   
                    try:
                        session.delete(Del_Syain)
                        session.commit()
                    except:
                        flash('DB更新中にエラーが発生しました(社員マスタ)')
                        return redirect(url)
                    finally:
                        session.close()
                            
                    Empstr_Admin =session.query(M_Syain, M_Busyo).filter(M_Syain.busyo == M_Busyo.busyoid).all()
                    session.close()
                    return render_template('msts/m_syain_admin.html', Syainstr=Empstr_Admin,ID=userid,TITLE='社員マスタ')
                    
                 else:    #キャンセルの場合
                    #キャンセルの場合は何もしない。何もしない方法はJavascriptでreturn falseを返し、該当する.pyファイルのロジックに「pass」を書く
                    pass
    else:
        getid = id
        getmode = mode
        get_toid=to_id
        
        Busyo = M_Busyo.query.all()
        
        if getmode=='add':
           #M_SYAIN.htmlでapp.pyの値を受け取るときは「Empstr.Emp1.id」のように、、
           #結合テーブル名.取得元のテーブル名.取得元のテーブルの項目名と3段階で記述する(ex.<td>{{ Empstr.Emp1.id }}</td>)
           return render_template('msts/m_syain_edit.html', Busyostr=Busyo, ID=getid,TOID='new',MODE=getmode,TITLE='社員マスタ')
        else:
           Empstr_Admin =session.query(M_Syain, M_Busyo).filter(M_Syain.busyo == M_Busyo.busyoid).filter(M_Syain.id==get_toid).all()
           session.close()
           return render_template('msts/m_syain_edit.html', Syainstr=Empstr_Admin,ID=getid,TOID=get_toid,MODE=getmode,Busyostr=Busyo,TITLE='社員マスタ')

#########################################################################################
##申請ルートマスタ                                                                      #
#########################################################################################
@M_MST.route('/m_shinsei_root', methods=['POST', 'GET']) #blueprintを使う場合、ここは「app.route」ではないので注意！自分の定義したモジュール名を書くこと！
def SHINSEI_ROOT():

    if request.method == 'POST':

        getid = request.form['cont_id']
        url = "/m_shinsei_root?id={0}".format(getid)

        ###「新規追加」ボタン押下時のメソッド###
        #申請ルートマスタ(INSERT)
        SinseiRoot = M_Shinsei_Root()
        SinseiRoot.root_id = request.form['root_id']
        SinseiRoot.rootname = request.form['root_name']
        
        #ドロップダウンリストの中で社員番号のみ取得する。社員番号は登録時必ず6桁で登録されるようシステム上チェックしている。
        substr_root1 = request.form['root_1']
        substr_root2 = request.form['root_2']
        substr_root3 = request.form['root_3']        
        SinseiRoot.shinsei_root1_id = substr_root1[0:6]
        SinseiRoot.shinsei_root2_id = substr_root2[0:6]
        SinseiRoot.shinsei_root3_id = substr_root3[0:6]
        
        #最終承認者は、承認者1～3の中で最後にNOt NULLだった人を編集する。承認者2がNULLで承認者3がNOt NULL の場合はエラーを返す
        if SinseiRoot.shinsei_root2_id == '' and SinseiRoot.shinsei_root3_id != '':
           return render_template('msts/m_shinsei_root.html',Msg="※承認者2を選択してください", Root=Shins_root, Syainstr=Empstr,TITLE='申請ルートマスタ')
        else:
            if SinseiRoot.shinsei_root2_id == '':
               SinseiRoot.last_approval_id = substr_root1[0:6]
            else:
               if SinseiRoot.shinsei_root3_id == '':
                  SinseiRoot.last_approval_id = substr_root2[0:6]
               else:
                  SinseiRoot.last_approval_id = substr_root3[0:6]
       
        SinseiRoot.torokud = datetime.datetime.now()
        
        #TBLに追加
        try:
            db.session.add(SinseiRoot)
            db.session.commit()
        except:
            flash('DB更新中にエラーが発生しました(申請ルートマスタ)。キー重複、禁止文字が含まれないかをチェックしてください')
            return redirect(url)

        #TBLを更新した状態で元画面へ戻る
        session.close()
        return redirect(url)
    else:
        Shins_root =M_Shinsei_Root.query.all()
        #申請許可権限を持つ者のみ抽出
        Empstr = session.query(M_Syain).filter(M_Syain.authority=='1').all()
        
        #URLの「XXXXm_syain?id={{ ID }}」の「id=」以降の値を取得する(今回の場合、社員番号)
        getid = request.args.get('id')
        session.close()        
        return render_template('msts/m_shinsei_root.html', Root=Shins_root, Syainstr=Empstr,ID=getid,TITLE='申請ルートマスタ')

#########################################################################################
##申請ルートマスタ(削除)                                                                #
#########################################################################################
@M_MST.route('/m_shinsei_root/delete/<rootid>/<id>') #blueprintを使う場合、ここは「app.route」ではないので注意！自分の定義したモジュール名を書くこと！
def SHINSEI_ROOT_DELETE(rootid,id):
    
    Root_Count = session.query(Shinsei_JNL).filter(Shinsei_JNL.root_id==rootid,Shinsei_JNL.shinsei_result!='1').count()

    getid = id        
    
    if Root_Count == 0:
       root_to_delete = session.query(M_Shinsei_Root).filter(M_Shinsei_Root.root_id==rootid).first()
       try:
          session.delete(root_to_delete)
          session.commit()
       except:
          return 'There was an problem deleting that task'
       finally:
          session.close()
       url = "/m_shinsei_root?id={0}".format(getid)
       return redirect(url)
    else:        
        session.close()
        url = "/m_shinsei_root?id={0}".format(getid)
        #flashメッセージ
        flash('この申請ルートは使用中のため削除できません')
        return redirect(url)
        
#########################################################################################
##部署マスタ                                                                            #
#########################################################################################
@M_MST.route('/m_busyo', methods=['POST', 'GET']) #blueprintを使う場合、ここは「app.route」ではないので注意！自分の定義したモジュール名を書くこと！
def MST_BUSYO():
    
    if request.method == 'POST':
    
           getid = request.form['syainid']
           url = "/m_busyo?id={0}".format(getid)
           
           #社員マスタ(INSERT)
           Busyo = M_Busyo()
           Busyo.busyoid = request.form['busyo_id']
           Busyo.busyoname = request.form['busyo_name']
           
           try:
              db.session.add(Busyo)
              db.session.commit()                    
           except:
              #flashメッセージ
              flash('DB更新中にエラーが発生しました(部署マスタ)。キー重複、禁止文字が含まれないかをチェックしてください')
              url = "/m_busyo?id={0}".format(getid)
              return redirect(url)
           finally:
              session.close()
           
           #元のページにリダイレクトする
           session.close()
           return redirect(url)
    else:
        getid = request.args.get('id')
        Busyo = M_Busyo.query.all()
        session.close()
        return render_template('msts/m_busyo.html',ID=getid,Busyostr=Busyo,TITLE='部署マスタ')
        
#########################################################################################
##部署マスタ(削除ボタン押下時)                                                          #
#########################################################################################
@M_MST.route('/m_busyo/delete/<busyoid>/<id>') #blueprintを使う場合、ここは「app.route」ではないので注意！自分の定義したモジュール名を書くこと！
def BUSYO_DELETE(busyoid,id):
    
    getid=id
    url = "/m_busyo?id={0}".format(getid)
    print('社員番号は：'+ str(id))    
    print('部署IDは：'+ str(busyoid))    
    Syain =  session.query(M_Syain).filter(M_Syain.id == getid).first()

    if Syain.authority == 9:

       busyo_to_delete = session.query(M_Busyo).filter(M_Busyo.busyoid==busyoid).first()
       
       try:
          session.delete(busyo_to_delete)
          session.commit()
       except:
          flash('DB更新中にエラーが発生しました(部署マスタ)')
          return redirect(url)
       finally:
          session.close()

       return redirect(url)
    else:
       flash('権限不足です。削除できません')
       return redirect(url)

###################################################################################
##アプリを起動する定型文2(ファイルの1番最後に記述する)                             #
###################################################################################
if __name__ == "__main__":
    # サーバーの起動
    app.run()
