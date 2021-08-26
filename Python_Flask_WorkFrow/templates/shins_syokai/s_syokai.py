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
from sqlalchemy import or_
from sqlalchemy import desc
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

#画像を埋め込む用の設定
from reportlab.pdfgen import canvas
from PIL import Image
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
Shinsei_S = Blueprint('s_syokai', __name__)


#########################################################################################
##申請照会                                                                              #
#########################################################################################
#申請照会画面
@Shinsei_S.route('/shinsei_syokai', methods=['POST', 'GET'])            #blueprintを使う場合、ここは「app.route」ではないので注意！自分の定義したモジュール名を書くこと！
def SHINSEI_SYOKAI():

    if request.method == 'POST':

        getshinseid_from = request.form['shinseid_from']
        if getshinseid_from =='':
           getshinseid_from = '2019-01-01'
        
        getshinseid_to = request.form['shinseid_to']
        if getshinseid_to =='':
           getshinseid_to = '9999-99-99'
           
        #ドロップダウンで選択した条件で抽出
        getmode = request.form['filter_mode']
        getid = request.form['cont_id']
        
        if getmode == '全て':
           print('全て')
           #SJNL =Shinsei_JNL.query.filter(Shinsei_JNL.shinsei_syainno==getid).order_by(desc(Shinsei_JNL.shinsei_no)).all()
           SJNL =Shinsei_JNL.query.filter(Shinsei_JNL.shinsei_syainno==getid).filter(Shinsei_JNL.shinseid.between(getshinseid_from, getshinseid_to)).order_by(desc(Shinsei_JNL.shinseid)).limit(100).all()
           #htmlファイルはtemplatesフォルダからの相対パスで書く
           return render_template('shins_syokai/shinsei_syokai.html',shinseistr =SJNL,ID=getid,MODE=getmode,id=getid,DATE_FROM=getshinseid_from,DATE_TO=getshinseid_to,TITLE='申請照会')
        else:   
           if getmode == '申請中':
              print('申請中')
              SJNL =Shinsei_JNL.query.filter(Shinsei_JNL.shinsei_syainno==getid,Shinsei_JNL.shinsei_result=='0').filter(Shinsei_JNL.shinseid.between(getshinseid_from, getshinseid_to)).order_by(desc(Shinsei_JNL.shinseid)).limit(100).all() 
              #htmlファイルはtemplatesフォルダからの相対パスで書く
              return render_template('shins_syokai/shinsei_syokai.html',shinseistr =SJNL,ID=getid,MODE=getmode,DATE_FROM=getshinseid_from,DATE_TO=getshinseid_to,TITLE='申請照会')
           else:   
              if getmode == '許可済':
                 print('許可済')
                 SJNL =Shinsei_JNL.query.filter(Shinsei_JNL.shinsei_syainno==getid,Shinsei_JNL.shinsei_result=='1').filter(Shinsei_JNL.shinseid.between(getshinseid_from, getshinseid_to)).order_by(desc(Shinsei_JNL.shinseid)).limit(100).all() 
                 return render_template('shins_syokai/shinsei_syokai.html',shinseistr =SJNL,ID=getid,MODE=getmode,DATE_FROM=getshinseid_from,DATE_TO=getshinseid_to,TITLE='申請照会')
              else:   
                 if getmode == '下書き':
                    print('下書き')
                    SJNL =Shinsei_JNL.query.filter(Shinsei_JNL.shinsei_syainno==getid,Shinsei_JNL.shinsei_result==None).filter(Shinsei_JNL.shinseid.between(getshinseid_from, getshinseid_to)).order_by(desc(Shinsei_JNL.shinseid)).limit(100).all() 
                    return render_template('shins_syokai/shinsei_syokai.html',shinseistr =SJNL,ID=getid,MODE=getmode,DATE_FROM=getshinseid_from,DATE_TO=getshinseid_to,TITLE='申請照会')
                 else:   
                    if getmode == '不許可':
                       print('不許可')
                       SJNL =Shinsei_JNL.query.filter(Shinsei_JNL.shinsei_syainno==getid,Shinsei_JNL.shinsei_result=='2').filter(Shinsei_JNL.shinseid.between(getshinseid_from, getshinseid_to)).order_by(desc(Shinsei_JNL.shinseid)).limit(100).all() 
                       return render_template('shins_syokai/shinsei_syokai.html',shinseistr =SJNL,ID=getid,MODE=getmode,DATE_FROM=getshinseid_from,DATE_TO=getshinseid_to,TITLE='申請照会')
    else:
        #URLの「href="m_syain?id={{ ID }}」の「id=」以降の値を取得する(今回の場合、社員番号)
        getid = request.args.get('id')
    
        getshinseid_fr = '2019-01-01'  #登録のない日を設定
        getshinseid_t = datetime.date.today()  
    
        SJNL =Shinsei_JNL.query.filter(Shinsei_JNL.shinsei_syainno==getid).order_by(desc(Shinsei_JNL.shinseid)).limit(100).all() 
        
        #htmlファイルはtemplatesフォルダからの相対パスで書く
        return render_template('shins_syokai/shinsei_syokai.html',shinseistr =SJNL,ID=getid,MODE='全て',DATE_FROM=getshinseid_fr,DATE_TO=getshinseid_t,TITLE='申請照会')
    
#########################################################################################
##申請照会詳細                                                                          #
#########################################################################################
#申請照会画面
@Shinsei_S.route('/shinsei_syokai_detail', methods=['POST', 'GET'])
def SHINSEI_SYOKAI_DETAIL():

    if request.method == 'POST':
            
           #Javascriptで表示したYES/NOダイアログの値をここで取得
           select_yesno = request.form.get('flg_yes_no')

           if select_yesno == 'YES':    #Javascriptで表示した確認ダイアログで「はい」を選択した場合   
            
              #編集項目の取得
              get_syainno = request.form['syain_no']
              get_syainid = request.form['syain_id']
              get_no = request.form['shinsei_no']
              get_shinsei_detail = request.form['shinsei_detail'] 
              get_busyo = request.form['busyo']
              get_title = request.form['shinsei_title']
              get_shinseid = request.form['shinseid']
              get_kesaid = request.form['kesaid']
              get_root = request.form['root_id']
              
              #sp = get_shinsei_detail.split("\n")
              sp = get_shinsei_detail.splitlines()
              sp_len = len(sp)           
              
              print(sp_len)
              print(sp[-1])
              
              #Pythonのreportlabを使ってPDF出力する
              tstr = datetime.datetime.now()   
              tdatetime = tstr.strftime('%Y%m%d%H%M%S')  
              
              doc_shinsei = request.form['doc_shinseisya']
              
              pdfFile = canvas.Canvas(doc_shinsei + '/' + get_no + '_' + str(tdatetime)+'.pdf')
              
              pdfFile.saveState()
               
              pdfFile.setAuthor(get_syainno)
              pdfFile.setTitle('PDF生成')
              pdfFile.setSubject('サンプル')
               
              # A4
              pdfFile.setPageSize((21.0*cm, 29.7*cm))
              # B5
              # pdfFile.setPageSize((18.2*cm, 25.7*cm))
               
              pdfFile.setFillColorRGB(0, 0, 100)
              
              #文字フォント、カラー設定
              pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))
              #pdfFile.setFont('HeiseiKakuGo-W5', 12)
              #pdfFile.drawString(5*cm, 25*cm, 'あいうえおー')
              pdfFile.setFillColorRGB(0, 0, 0)
              
              pdfFile.setFont('HeiseiKakuGo-W5', 12)
              pdfFile.drawString(9.5*cm, 28.5*cm, '稟議書')
              
              pdfFile.setFont('HeiseiKakuGo-W5', 8)

              #pdfFile.setFont('HeiseiKakuGo-W5', 5)
              
              ###四角を描画(描画は左下を起点として何センチか、で指定する。rect(A,B,C,D)：A:左下からの横の幅(座標位置)、B:左下からの高さ(座標位置)、C:横の長さ描画,D:縦の長さ描画###    
              #申請者ハンコ欄
              pdfFile.rect(10*cm, 27*cm, 2*cm, 0.5*cm)   #見出し
              pdfFile.rect(10*cm, 25*cm, 2*cm, 2*cm)     #ハンコ部分
              pdfFile.drawString(10.6*cm, 27.1*cm, '申請者') #見出しタイトル
              
              #画像埋め込み
              stmp_shinsei = request.form['stamp_shinseisya']
              image =Image.open(stmp_shinsei)
              pdfFile.drawInlineImage(image,10.5*cm,25.5*cm,width=1*cm, height=1*cm)
              
              #項目名についてはdrawStringで描画する。drawString(A,B,'文字名')  A:左下の端からの位置、B:そこからの下からの高さ
              #承認者ハンコ欄
              pdfFile.rect(13*cm, 27*cm, 6*cm, 0.5*cm)   #見出し   
              pdfFile.rect(13*cm, 25*cm, 2*cm, 2*cm)     #ハンコ部分
              pdfFile.rect(15*cm, 25*cm, 2*cm, 2*cm)     #ハンコ部分
              pdfFile.rect(17*cm, 25*cm, 2*cm, 2*cm)     #ハンコ部分
              pdfFile.drawString(15.5*cm, 27.1*cm, '承認者')  #見出しタイトル
              #許可印取得部
              stmp_syain1 = request.form['stamp_syain1']
              stmp_syain2 = request.form['stamp_syain2']
              stmp_syain3 = request.form['stamp_syain3']
              
              image1 =Image.open(stmp_syain1)
              pdfFile.drawInlineImage(image1,13.5*cm,25.5*cm,width=1*cm, height=1*cm)
              
              if stmp_syain2 != '':
                 image2 =Image.open(stmp_syain2)
                 pdfFile.drawInlineImage(image2,15.5*cm,25.5*cm,width=1*cm, height=1*cm)
                 
              if stmp_syain3 != '':
                 image3 =Image.open(stmp_syain3)
                 pdfFile.drawInlineImage(image3,17.5*cm,25.5*cm,width=1*cm, height=1*cm)
              
              #申請者
              pdfFile.rect(2*cm, 23*cm, 3*cm, 0.5*cm)   #見出し
              pdfFile.rect(2*cm, 22*cm, 17*cm, 1*cm)     #ハンコ部分
              pdfFile.drawString(2.2*cm, 23.1*cm, '申請者') #見出しタイトル
              pdfFile.drawString(2.1*cm, 22.3*cm, get_syainno) #編集部
               
              #部署
              #pdfFile.rect(10.5*cm, 23*cm, 3*cm, 0.5*cm)   #見出し
              #pdfFile.rect(10.5*cm, 22*cm, 8.5*cm, 1*cm)     #ハンコ部分
              #pdfFile.drawString(10.7*cm, 23.1*cm, '部署') #見出しタイトル
              #pdfFile.drawString(10.7*cm, 22.3*cm, get_busyo) #編集部
              
              #部署
              pdfFile.rect(2*cm, 21*cm, 3*cm, 0.5*cm)   #見出し
              pdfFile.rect(2*cm, 20*cm, 17*cm, 1*cm)     #ハンコ部分
              pdfFile.drawString(2.2*cm, 21.1*cm, '部署') #見出しタイトル
              pdfFile.drawString(2.1*cm, 20.3*cm, get_busyo) #編集部
              
              ###四角を描画(描画は左下を起点として何センチか、で指定する。rect(A,B,C,D)：A:左下からの横の幅(座標位置)、B:左下からの高さ(座標位置)、C:横の長さ描画,D:縦の長さ描画###    
              #標題
              pdfFile.rect(2*cm, 19*cm, 3*cm, 0.5*cm)   #見出し
              pdfFile.rect(2*cm, 18*cm, 17*cm, 1*cm)     #ハンコ部分
              pdfFile.drawString(2.2*cm, 19.1*cm, '標題') #見出しタイトル
              pdfFile.drawString(2.1*cm, 18.4*cm, get_title) #編集部
              
              #内容
              pdfFile.rect(2*cm, 17*cm, 3*cm, 0.5*cm)   #見出し
              pdfFile.rect(2*cm, 5*cm, 17*cm, 12*cm)     #ハンコ部分
              pdfFile.drawString(2.2*cm, 17.1*cm, '内容') #見出しタイトル
              
              #for sp_list in sp:
              for i in range(sp_len):
                    print('i='+ str(i)+':'+sp[i])
                    #print('位置=' + str(13+i))
                    
                    #【内容】の印字位置を調整。5mm間隔で行を改行
                    num = (16.5 - (i*0.5))
                    print('num=' + str(num))
                    pdfFile.drawString(2*cm, num*cm, sp[i].encode('utf-8'))
              
              #申請日
              pdfFile.rect(10*cm, 4*cm, 2*cm, 0.5*cm)   #見出し
              pdfFile.rect(10*cm, 3*cm, 4*cm, 1*cm)     #ハンコ部分
              pdfFile.drawString(10.2*cm, 4.1*cm, '申請日') #見出しタイトル
              pdfFile.drawString(10.2*cm, 3.5*cm, get_shinseid) #編集部
              
              #承認日
              pdfFile.rect(15*cm, 4*cm, 2*cm, 0.5*cm)   #見出し
              pdfFile.rect(15*cm, 3*cm, 4*cm, 1*cm)     #ハンコ部分
              pdfFile.drawString(15.2*cm, 4.1*cm, '承認日') #見出しタイトル
              pdfFile.drawString(15.2*cm, 3.5*cm, get_kesaid) #編集部
              
              #lineは縦線。書き方：line(A,B,C,D) A:左下、B:Aからの下からの高さ、C:直線の長さ、D:Cの長さをどの位置から引くか B=Dにしておかないと真っすぐ引けない
              pdfFile.line(2*cm, 26.5*cm, 7*cm, 26.5*cm)  #アンダーライン
              pdfFile.drawString(2*cm, 27.3*cm, '申請番号') #見出しタイトル
              pdfFile.drawString(2*cm, 26.7*cm, get_no) #編集部
              
              pdfFile.line(2*cm, 25*cm, 7*cm, 25*cm)  #アンダーライン
              pdfFile.drawString(2*cm, 25.8*cm, '申請ルート') #見出しタイトル
              pdfFile.drawString(2*cm, 25.2*cm, get_root) #編集部
              
              pdfFile.setLineWidth(1)
              pdfFile.restoreState()
              pdfFile.save()
              
              #元のページにリダイレクトする
              url = "/shinsei_syokai_detail?id={0}&no={1}".format(get_syainid,get_no)
              return redirect(url)    

           else:    #キャンセルの場合
              #キャンセルの場合は何もしない。何もしない方法はJavascriptでreturn falseを返し、該当する.pyファイルのロジックに「pass」を書く
              pass

    else:
           getid = request.args.get('id') 
           getno = request.args.get('no')

           SJNL = session.query(Shinsei_JNL, M_Syain ,M_Busyo ,M_Shinsei_Root).filter(Shinsei_JNL.shinsei_syainno == M_Syain.id, M_Syain.busyo==M_Busyo.busyoid, Shinsei_JNL.root_id==M_Shinsei_Root.root_id).filter(Shinsei_JNL.shinsei_no==getno).all()     
           
           #許可印のディレクトリをここで取得しておく
           SJNL2 = session.query(Shinsei_JNL).filter(Shinsei_JNL.shinsei_no==getno).first()
           SJNL_syain1 = SJNL2.shinsei_syain1
           SJNL_syain2 = SJNL2.shinsei_syain2
           SJNL_syain3 = SJNL2.shinsei_syain3
           SJNL_shinseisya = SJNL2.shinsei_syainno
           Syain1 = session.query(M_Syain).filter(M_Syain.id== SJNL_syain1).first()
           Syain2 = session.query(M_Syain).filter(M_Syain.id== SJNL_syain2).first()
           Syain3 = session.query(M_Syain).filter(M_Syain.id== SJNL_syain3).first()
           Shinseisya = session.query(M_Syain).filter(M_Syain.id== SJNL_shinseisya).first()
                                 
           session.close()
           return render_template('shins_syokai/shinsei_syokai_detail.html', shinseistr =SJNL,ID=getid,SYAIN1=Syain1,SYAIN2=Syain2,SYAIN3=Syain3,SHINSEISYA=Shinseisya,TITLE='申請照会')

#########################################################################################
##申請照会(削除モード)                                                                    
#########################################################################################
# 削除画面
@Shinsei_S.route('/shinsei_syokai_delete', methods=['POST', 'GET'])
def SHINSEI_SYOKAI_DELETE():

    if request.method == 'POST':
    
         #Javascriptで表示したYES/NOダイアログの値をここで取得
         select_yesno = request.form.get('flg_yes_no')
         
         get_syainno = request.form['syain_no']
         get_shinseino = request.form['shinsei_no']

         url = "/shinsei_syokai?id={0}".format(get_syainno)
         
         #メッセージマスタに登録があるかチェックs
         Cnt_Msg =  session.query(M_Msg).filter(M_Msg.shinsei_no==get_shinseino).count()
         print('メッセージマスタの登録件数は:' + str(Cnt_Msg))
    
         if Cnt_Msg == 1:
            #メッセージマスタを削除する。
            Del_Msg =  session.query(M_Msg).filter(M_Msg.shinsei_no==get_shinseino).first()
            if select_yesno == 'YES':    #Javascriptで表示した確認ダイアログで「はい」を選択した場合
               #コミット
               try:
                  session.delete(Del_Msg)
                  session.commit()
                  print('メッセージマスタ削除完了')
               except:
                  flash('DB更新中にエラーが発生しました(メッセージマスタ)')
                  return redirect(url)
               finally:
                  session.close()
            else:                          #キャンセルの場合、元のページに留まる
                  pass
         
         #クエリ作成 申請番号で1意になるが念のため社員番号も抽出条件に含める
         Del_SJNL =  session.query(Shinsei_JNL).filter(Shinsei_JNL.shinsei_syainno==get_syainno ,Shinsei_JNL.shinsei_no==get_shinseino).first()
         
         if select_yesno == 'YES':      #削除する場合
             try:
                 session.delete(Del_SJNL)
                 session.commit()
                 print('SJNL削除完了')
             except:
                 return 'There was an problem deleting that task'
             finally:
                 session.close()
             #申請照会画面に戻る
             url = "/shinsei_syokai?id={0}".format(get_syainno)
             return redirect(url)
         else:                          #キャンセルの場合
             session.close()
             return redirect(url)
    else:
         getid = request.args.get('id') 
         getno = request.args.get('no')

         SJNL = Shinsei_JNL.query.filter(Shinsei_JNL.shinsei_no==getno).all()     
         session.close()
         return render_template('shins_syokai/shinsei_syokai_delete.html', shinseistr =SJNL,ID=getid,TITLE='申請照会')

###################################################################################
##アプリを起動する定型文2(ファイルの1番最後に記述する)                            #
###################################################################################
if __name__ == "__main__":
    # サーバーの起動
    app.run()
