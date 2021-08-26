# -*- coding: utf-8 -*-
"""
 Using SQLAlchemy and Flask get db record.(GET)

"""

###################################################################################
#基本イベントのインポート                                                         #
###################################################################################
#requestsをここでimportしないとpost時に「NameError: name 'request' is not defined」エラーになる
from flask import Flask, render_template, url_for, request, redirect, flash
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
Shinsei_N = Blueprint('s_nyuryoku', __name__)


#########################################################################################
##申請入力                                                                              #
#########################################################################################
@Shinsei_N.route('/shinsei_nyuryoku', methods=['POST', 'GET']) #blueprintを使う場合、ここは「app.route」ではないので注意！自分の定義したモジュール名を書くこと！
def SHINSEI_NYUROKU():

    Shins_root =M_Shinsei_Root.query.all()

    #URLの「href="m_syain?id={{ ID }}」の「id=」以降の値を取得する(今回の場合、社員番号)

    if request.method == 'POST':
    
        #共通で使用する項目
        shinseisyain_no = request.form['syain_no']
        to_syain = ''
        ##申請番号管理マスタ更新部(UPDATE)##
        SNMng =  session.query(Shinsei_No_Management).filter(Shinsei_No_Management.id == shinseisyain_no).first()

        #request.form[cont_XX]：htmlファイルの「name=」で指定された名称の項目の値を取得する
        shins_no = int(request.form['shinseino'])
        SNMng.no = shins_no

        #UPDATEの場合は、commitのみでOK。session.addはINSERTの時に記述する
        try:
            session.commit()
        except:
            return "DB更新中にエラーが発生しました(申請番号管理)"

        ##申請ジャーナル更新部(INSERT)##
        SJNL = Shinsei_JNL()
        SJNL.shinsei_no = shinseisyain_no + '-' + request.form['shinseino']
        
        today = datetime.date.today()
        shinseid = request.form['cont_shinseid']
        if shinseid == None:
           SJNL.shinseid = today
        else:
           SJNL.shinseid = shinseid
        
        SJNL.shinsei_syainno = shinseisyain_no

        #ルートIDはドロップダウンリストから文字列切り出し
        substr_rootid = request.form['shinsei_root']
        getRootid = substr_rootid[0:5]
        SJNL.root_id = getRootid
        
        SJNL.shinsei_title =  request.form['cont_shinsei_title']        
        
        #申請内容(全16行の入力項目よりfor文でlist化し、joinでlistの内容を連結する。その際、1行ずつ改行するため、\nを指定する)
        shinsei_detail_lists = []
        for i in range(1,17):
            shinsei_detail_lists.append(request.form['cont_shinsei_detail'+ str(i) ])  

        shinsei_detail = '\n'.join(map(str, shinsei_detail_lists))
        print(shinsei_detail)
        
        SJNL.shinsei_detail = shinsei_detail
                
        SJNL.torokud =	datetime.datetime.now()
        SJNL.koshind =	datetime.datetime.now()
        
        #申請先社員番号は申請ルートマスタより取得する
        ShinsRoot =  session.query(M_Shinsei_Root).filter(M_Shinsei_Root.root_id == getRootid).first()
        SJNL.shinseisaki_syainno = ShinsRoot.shinsei_root1_id
        
        SJNL.shinsei_syain1 = ShinsRoot.shinsei_root1_id
        to_syain = ShinsRoot.shinsei_root1_id
        SJNL.shinsei_syain2 = ShinsRoot.shinsei_root2_id
        SJNL.shinsei_syain3 = ShinsRoot.shinsei_root3_id
        
        #ラジオボタンが「申請する」か「下書きとして保存」どちらかを判定
        radio_select = request.form.get('radio')
        if radio_select == '1':  #「申請する」
           SJNL.shinsei_result = '0'   
           SJNL.shinsei_cond1 = '0'
                
        #メッセージマスタ(更新部)
        Msg = M_Msg()
        Msg.shinsei_no = shinseisyain_no + '-' + request.form['shinseino']
        Msg.from_syainno = shinseisyain_no
        Msg.from_syain_msg_close = '0'
        Msg.to_syainno = to_syain
        Msg.to_syain_msg_close = '0'
        Msg.detail = request.form['cont_shinsei_title'] + '  を申請しました'
        
        tstr = datetime.datetime.now()   
        tdatetime = tstr.strftime('%Y-%m-%d %H:%M:%S')  
        Msg.torokud =tdatetime
        
		#TBLに追加
        try:
              db.session.add(SJNL)
              db.session.add(Msg)
              db.session.commit()
        except:
              return "DB更新中にエラーが発生しました111"
        finally:
              db.session.close()
        
        #元のページにリダイレクトする(その際、申請番号はカウントアップされる)
        url = "/shinsei_nyuryoku?id={0}".format(shinseisyain_no)
        return redirect(url)
    else:
        getid = request.args.get('id')
        gettoday = datetime.date.today()  

        #申請番号管理テーブルの番号を取得する
        SNManage= Shinsei_No_Management.query.filter(Shinsei_No_Management.id==getid).first()
        
        #申請番号管理テーブルの番号からカウントアップする
        new_SeqNo = SNManage.no + 1
        
        #申請時、申請番号管理テーブルを更新するため、ここで一旦セッションを閉じる
        session.close()
        
        return render_template('shins_nyuryoku/shinsei_nyuryoku.html', Seq = new_SeqNo, Root = Shins_root,ID=getid,TODAY=gettoday,TITLE='申請入力')
                   
#########################################################################################
##申請入力(修正)                                                                        #
#########################################################################################
@Shinsei_N.route('/shinsei_nyuryoku_syusei', methods=['POST', 'GET']) #blueprintを使う場合、ここは「app.route」ではないので注意！自分の定義したモジュール名を書くこと！
def SHINSEI_NYUROKU_SYUSEI():

    if request.method == 'POST':
    
        getid = request.form['cont_id']
        
        #ボタンが「下書き」「申請取り消し」どっちかを判定
        getmode = request.form['btn']
        print('getmode ゲットモード : ' + str(getmode))
        
        if getmode == '下書き・不許可':
           MSG = '下書きデータを表示しています'
           print(MSG)
           Mode = 'draft'
           SJNL_DRAFT = Shinsei_JNL.query.filter(Shinsei_JNL.shinsei_syainno==getid).filter(or_(Shinsei_JNL.shinsei_result == None,Shinsei_JNL.shinsei_result =='2')).all() 
           
           session.close()
           return render_template('shins_nyuryoku/shinsei_nyuryoku_syusei.html', shinseistr =SJNL_DRAFT,ID=getid, HMSG =MSG ,MODE=Mode,TITLE='申請入力')
           
        else:   #申請取り消し
           MSG = '申請取消可能なデータを表示しています'
           Mode = 'cancel'
           #申請取り消しの条件：申請中かつ、最初の承認者の状態が「0」、つまり申請したが誰も承認していない場合にのみ有効
           #もし誰かがすでに承認した申請を取り消したい場合は承認削除で物理削除する
           SJNL_CANCEL = Shinsei_JNL.query.filter(Shinsei_JNL.shinsei_syainno==getid,Shinsei_JNL.shinsei_cond1=='0').all()     
           session.close()
           return render_template('shins_nyuryoku/shinsei_nyuryoku_syusei.html', shinseistr =SJNL_CANCEL,ID=getid, HMSG=MSG,MODE=Mode,TITLE='申請入力')
    else:
        MSG = '下書きデータを表示しています'
        getid = request.args.get('id') 
        Mode = 'draft'
        
        #初期状態では下書きデータを表示する  
        SJNL = Shinsei_JNL.query.filter(Shinsei_JNL.shinsei_syainno==getid).filter(or_(Shinsei_JNL.shinsei_result == None,Shinsei_JNL.shinsei_result =='2')).all()   
        session.close()
        return render_template('shins_nyuryoku/shinsei_nyuryoku_syusei.html', shinseistr =SJNL,ID=getid, HMSG =MSG,MODE=Mode,TITLE='申請入力')
#########################################################################################
##申請入力(下書き)                                                                      #
#########################################################################################
@Shinsei_N.route('/shinsei_nyuryoku_draft', methods=['POST', 'GET']) #blueprintを使う場合、ここは「app.route」ではないので注意！自分の定義したモジュール名を書くこと！
def SHINSEI_NYUROKU_DRAFT():

    if request.method == 'POST':
    
        #モード選択
        getmode = request.form['cont_mode']
    
        #Javascriptで表示したYES/NOダイアログの値をここで取得
        select_yesno = request.form.get('flg_yes_no')
    
        #共通で使用する項目
        shinseisyain_no = request.form['syain_no']
        shinseino = request.form['shinseino']
        tosyain_id = ''
        radio_select = request.form.get('radio')
        url = "/shinsei_nyuryoku_syusei?id={0}".format(shinseisyain_no)
        
        ##申請ジャーナル更新部(UPDATE)##
        #注意：SJNL = Shinsei_JNL.query.filter～のような書き方ではUPDATEされないので注意する!##
        SJNL=session.query(Shinsei_JNL).filter(Shinsei_JNL.shinsei_no == shinseino).first()

        if getmode == 'cancel':
             #申請取り消しの条件：申請中かつ、最初の承認者の状態が「0」、つまり申請したが誰も承認していない場合にのみ有効
             #もし誰かがすでに承認した申請を取り消したい場合は承認削除で物理削除する
             print('取消モード')
             SJNL.shinsei_result = None   
             SJNL.shinsei_cond1 = None
             SJNL.koshind = datetime.datetime.now()
             
             if select_yesno == 'YES':    #Javascriptで表示した確認ダイアログで「はい」を選択した場合
                #コミット
                #UPDATEの場合は、commitのみでOK。session.addはINSERTの時に記述する
                try:
                   session.commit()
                except:
                   flash('DB更新中にエラーが発生しました(申請JNL)')
                   return redirect(url)
                finally:
                   session.close()
             else:                          #キャンセルの場合、元のページに留まる
                pass
             #メッセージマスタを削除する。再申請時に再発行する
             Del_Msg =  session.query(M_Msg).filter(M_Msg.shinsei_no==shinseino).first()
        
             if select_yesno == 'YES':    #Javascriptで表示した確認ダイアログで「はい」を選択した場合
                #コミット
                try:
                   session.delete(Del_Msg)
                   session.commit()
                except:
                   flash('DB更新中にエラーが発生しました(申請JNL)')
                   return redirect(url)
                finally:
                   session.close()
                
                #元のページにリダイレクトする
                url = "/shinsei_nyuryoku_syusei?id={0}".format(shinseisyain_no)
                return redirect(url)
             else:                          #キャンセルの場合、元のページに留まる
                pass
        else:    #下書きモード     
             
            #「削除する」場合  削除は不許可になったデータのみ選択可能とする        
            if  radio_select == '3':        
                get_syainno = request.form['syain_no']
                get_shinseino = request.form['shinseino']
                
                #クエリ作成 申請番号で1意になるが念のため社員番号も抽出条件に含める
                Del_SJNL =  session.query(Shinsei_JNL).filter(Shinsei_JNL.shinsei_syainno==get_syainno ,Shinsei_JNL.shinsei_no==get_shinseino).first()
                
                if select_yesno == 'YES': 
                    try:
                        session.delete(Del_SJNL)
                        session.commit()
                    except:
                        flash('DB更新中にエラーが発生しました(申請JNL)')
                        return redirect(url)
                    finally:
                        session.close()
                else:
                    pass
                                        
                #メッセージマスタを削除する。再申請時に再発行する
                Del_Msg =  session.query(M_Msg).filter(M_Msg.shinsei_no==shinseino).first()
                if select_yesno == 'YES':    #Javascriptで表示した確認ダイアログで「はい」を選択した場合
                   #コミット
                   try:
                      session.delete(Del_Msg)
                      session.commit()
                   except:
                      flash('DB更新中にエラーが発生しました(申請JNL)')
                      return redirect(url)
                   finally:
                      session.close()
                   
                   #元のページにリダイレクトする
                   url = "/shinsei_nyuryoku_syusei?id={0}".format(shinseisyain_no)
                   return redirect(url)
                else:                          #キャンセルの場合、元のページに留まる
                   pass
            else:
             
                 SJNL.shinseid = request.form['cont_shinseid']
                 
                 #ルートIDはドロップダウンリストから文字列切り出し
                 substr_rootid = request.form['shinsei_root']
                 getRootid = substr_rootid[0:5]
                 SJNL.root_id = getRootid
                 
                 #タイトル
                 SJNL.shinsei_title =  request.form['cont_shinsei_title']

                 #申請内容(全16行の入力項目よりfor文でlist化し、joinでlistの内容を連結する。その際、1行ずつ改行するため、\nを指定する)
                 shinsei_detail_lists = []
                 for i in range(1,17):
                     shinsei_detail_lists.append(request.form['cont_shinsei_detail'+ str(i) ])  
                 shinsei_detail = '\n'.join(map(str, shinsei_detail_lists))        
                 SJNL.shinsei_detail = shinsei_detail
                 
                 #更新日
                 SJNL.koshind =	datetime.datetime.now()
                 
                 #申請先社員番号は申請ルートマスタより取得する
                 ShinsRoot =  session.query(M_Shinsei_Root).filter(M_Shinsei_Root.root_id == getRootid).first()
                 SJNL.shinseisaki_syainno = ShinsRoot.shinsei_root1_id
                 
                 SJNL.shinsei_syain1 = ShinsRoot.shinsei_root1_id
                 SJNL.shinsei_syain2 = ShinsRoot.shinsei_root2_id
                 SJNL.shinsei_syain3 = ShinsRoot.shinsei_root3_id
                 tosyain_id = ShinsRoot.shinsei_root1_id
                 
                 if  radio_select == '2':        #「下書き」
                     print('下書きモード了')
                     if select_yesno == 'YES':    #Javascriptで表示した確認ダイアログで「はい」を選択した場合
                     
                        #コミット
                        #UPDATEの場合は、commitのみでOK。session.addはINSERTの時に記述する
                        try:
                           session.commit()
                        except:
                           flash('DB更新中にエラーが発生しました(申請JNL)')
                           return redirect(url)
                        finally:
                           session.close()
                        #元のページにリダイレクトする
                        url = "/shinsei_nyuryoku_syusei?id={0}".format(shinseisyain_no)
                        return redirect(url)
                     else:                          #キャンセルの場合、元のページに留まる
                        pass
                 
                 #ラジオボタンが「申請する」場合のみ、申請状態と申請結果、メッセージマスタを更新する
                 if  radio_select == '1':        #「申請する」
                     SJNL.shinsei_result = '0'   
                     SJNL.shinsei_cond1 = '0'

                     if select_yesno == 'YES':    #Javascriptで表示した確認ダイアログで「はい」を選択した場合
                        #コミット
                        #UPDATEの場合は、commitのみでOK。session.addはINSERTの時に記述する
                        print('SJNLの申請するを更新')
                        try:
                           session.commit()
                        except:
                           flash('DB更新中にエラーが発生しました(申請JNL)')
                           return redirect(url)
                        finally:
                           session.close()
                     else:                     #キャンセルの場合、元のページに留まる
                        pass
                     
                     #メッセージマスタ(更新部)
                     Msg = M_Msg()
                     Msg.shinsei_no = shinseino
                     Msg.from_syainno = shinseisyain_no
                     Msg.from_syain_msg_close = '0'
                     Msg.to_syainno = tosyain_id
                     Msg.to_syain_msg_close = '0'
                     Msg.detail = request.form['cont_shinsei_title'] + '  を申請しました'
                     tstr = datetime.datetime.now()   
                     tdatetime = tstr.strftime('%Y-%m-%d %H:%M:%S')  
                     Msg.torokud =tdatetime
                 
                     if select_yesno == 'YES':    #Javascriptで表示した確認ダイアログで「はい」を選択した場合
                        #コミット
                        #UPDATEの場合は、commitのみでOK。session.addはINSERTの時に記述する
                        print('申請するを更新')
                        try:
                           db.session.add(Msg)
                           db.session.commit()
                        except:
                           flash('DB更新中にエラーが発生しました(メッセージマスタ)')
                           return redirect(url)
                        finally:
                           session.close()
                        
                        #元のページにリダイレクトする
                        url = "/shinsei_nyuryoku_syusei?id={0}".format(shinseisyain_no)
                        return redirect(url)
                     else:                     #キャンセルの場合、元のページに留まる
                        pass

    else:
        getid = request.args.get('id')
        getno = request.args.get('no')
        getmode = request.args.get('mode')

        Shins_root =M_Shinsei_Root.query.all()
        SJNL = Shinsei_JNL.query.filter(Shinsei_JNL.shinsei_no==getno).all()
             
        session.close()
        return render_template('shins_nyuryoku/shinsei_nyuryoku_draft.html', Root=Shins_root,shinseistr =SJNL,ID=getid,MODE=getmode,TITLE='申請入力')
        
###################################################################################
##アプリを起動する定型文2(ファイルの1番最後に記述する)                             #
###################################################################################
if __name__ == "__main__":
    # サーバーの起動
    app.run()
