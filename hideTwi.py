#-------------------------------------------------------------------------------
# Name:        hideTwi
# Purpose:     こっそりTwitterを楽しみたい、画像ハッシュタグの自動保存を行いたい方向け
#
# Author:      T
#
# Created:     24/12/2020
# Copyright:   (c) T 2020
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import json, config #標準のjsonモジュールとconfig.pyの読み込み
from requests_oauthlib import OAuth1Session #OAuthのライブラリの読み込み
from urllib.parse import parse_qsl
import requests
import codecs
import os
import sys
from time import sleep
import urllib.request as urlreq
import datetime
import threading
import base64
import webbrowser

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import sip
import ast

#アクセスURLのエンドポイント設定
url1 = "https://api.twitter.com/1.1/statuses/home_timeline.json" #タイムライン取得エンドポイント
url2 = "https://api.twitter.com/1.1/statuses/update.json" #ツイートポストエンドポイント
url3 = "https://api.twitter.com/1.1/favorites/create.json"
url4 = "https://upload.twitter.com/1.1/media/upload.json" #画像投稿
url5 = "https://api.twitter.com/oauth/request_token"
url6 = "https://api.twitter.com/oauth/authenticate"
url7 = "https://api.twitter.com/oauth/access_token"

#httpリクエストのための設定
CK = ""
CS = ""
AT = ""
ATS = ""
twitter = ""

image_list = []
delete_index = []
image_num = 0

alpha_rate = config.MAIN_ALPHA
image_alpha_rate = config.IMAGE_ALPHA
tl_alpha_rate = config.TL_ALPHA
theme_alpha_rate = config.THEME_ALPHA
image_color = config.DEFAULT_IMAGE_COLOR
phonto_color = config.DEFAULT_PHONT_COLOR

if config.DEFAULT_THEME == "dark":
    image_color = config.DARK_IMAGE_COLOR
    phonto_color = config.DARK_PHONT_COLOR
elif config.DEFAULT_THEME == "light":
    image_color = config.LIGHT_IMAGE_COLOR
    phonto_color = config.LIGHT_PHONT_COLOR

class ThemeWindow(QWidget):
    def __init__(self, parent=None):
        super(ThemeWindow, self).__init__(parent)

        #メインウィンドウの設定
        self.w = 1280
        self.h = 720
        self.resize(self.w, self.h)
        self.setMinimumSize(self.w/2, self.h/2)
        self.widthFactor  = 1
        self.heightFactor = 1
        self.setWindowTitle('テーマ変更するよ')
        self.setStyleSheet("background-color: " + image_color + ";")
        self.setWindowOpacity(theme_alpha_rate)

        self.theme_display()

    def theme_display(self):
        global image_color
        # opening color dialog
        color = QColorDialog.getColor()

        image_color = color.name()

        main_window.update_theme_color()

class TLWindow(QWidget):
    def __init__(self, parent=None):
        super(TLWindow, self).__init__(parent)

        #メインウィンドウの設定
        self.w = 1280
        self.h = 720
        self.resize(self.w, self.h)
        self.setMinimumSize(self.w/2, self.h/2)
        self.widthFactor  = 1
        self.heightFactor = 1
        self.setWindowTitle('TL表示するよ')
        self.setStyleSheet("background-color: " + image_color + ";")
        self.setWindowOpacity(tl_alpha_rate)

        self.tl_display()

    def tl_display(self):
        pass


class ImageWindow(QWidget):
    def __init__(self, parent=None):
        super(ImageWindow, self).__init__(parent)

        #メインウィンドウの設定
        self.w = 1150
        self.h = 500
        self.resize(self.w, self.h)
        self.setMinimumSize(self.w/2, self.h/2)
        self.widthFactor  = 1
        self.heightFactor = 1
        self.setWindowTitle('画像一覧')
        self.setStyleSheet("background-color: " + image_color + ";")
        self.setWindowOpacity(image_alpha_rate)
        self.label_list = []
        self.button_list = []
        self.piclabel_list = []
        self.image_display()

    def image_display(self):
        if len(image_list) == 0:
            return

        for i in range(len(image_list)):
            #画像ラベルの追加
            self.label_list.append(QLabel(self))
            self.label_list[i].move(50 , 120 * (i + 1) - 60)
            self.label_list[i].setText('<p><font size="4" color="' + phonto_color + '">' + image_list[i] + '</font></p>')

            #削除ボタンの追加
            self.button_list.append(QPushButton('削除', self))

            if i == 0:
                self.button_list[i].clicked.connect(lambda: self.delete_image(0))
            elif i == 1:
                self.button_list[i].clicked.connect(lambda: self.delete_image(1))
            elif i == 2:
                self.button_list[i].clicked.connect(lambda: self.delete_image(2))
            elif i == 3:
                self.button_list[i].clicked.connect(lambda: self.delete_image(3))

            self.button_list[i].resize(100, 30)
            self.button_list[i].setStyleSheet("background-color: #FFFFFF;")
            self.button_list[i].move(1030, 120 * (i + 1) - 60)

            self.piclabel_list.append(QLabel(self))

            pixmap = QPixmap(image_list[i])
            pixmap2 = pixmap.scaled(100, 100)
            self.piclabel_list[i].setPixmap(pixmap2)
            self.piclabel_list[i].move(900,120 * (i + 1) - 100)

    def delete_image(self, index:int):
        global image_num
        global image_list
        #print(index)

        minus_index = 0

        if index == 0:
            minus_index = 0

        elif index == 1:
            if 0 in delete_index:
                minus_index += 1

        elif index == 2:
            if 0 in delete_index:
                minus_index += 1

            if 1 in delete_index:
                minus_index += 1

        elif index == 3:
            if 0 in delete_index:
                minus_index += 1

            if 1 in delete_index:
                minus_index += 1

            if 2 in delete_index:
                minus_index += 1

        image_list.pop(index - minus_index )
        delete_index.append(index)
        image_num -= 1

        self.label_list[index].hide()
        self.button_list[index].hide()
        self.piclabel_list[index].hide()

        main_window.update_image_num()

class MainWindow(QWidget):
    progressChanged = pyqtSignal(int)
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.get_key()
        self.oauth()
        self.theme_status = config.DEFAULT_THEME

        #メインウィンドウの設定
        self.w = 1280
        self.h = 300
        self.resize(self.w, self.h)
        self.setMinimumSize(self.w/2, self.h/2)
        self.widthFactor  = 1
        self.heightFactor = 1
        self.setWindowTitle('ついったーするやつ')
        self.setStyleSheet("background-color: " + image_color + ";")
        self.setWindowOpacity(alpha_rate)

        #ツイート関連の表示ウィジェットの設定
        self.tweet_init()

        #ハッシュタグ保存機能の表示ウィジェットの設定
        self.hash_init()

        #透過率変更機能ウィジェットの設定
        self.alpha_change_init()

        #TL表示ボタンの設定
        self.timeline_init()

        self.menu_init()

    def get_key(self):
        global CK
        global CS
        self.get_response = requests.get('https://mythos.pythonanywhere.com/twitter/request_key')
        key_token = ast.literal_eval(self.get_response.content.decode("utf-8"))

        CK = key_token["CK"]
        CS = key_token["CS"]

    def oauth(self):

        self.request_response = requests.get('https://mythos.pythonanywhere.com/twitter/request_token?oauth_callback=https://mythos.pythonanywhere.com/twitter/access_token')
        request_token = ast.literal_eval(self.request_response.content.decode("utf-8"))
        authenticate_endpoint = "https://api.twitter.com/oauth/authenticate?oauth_token=" + request_token["oauth_token"]

        webbrowser.open(authenticate_endpoint)

    def get_AT(self):
        global AT
        global ATS
        self.oauth_response = requests.get('https://mythos.pythonanywhere.com/twitter/oauth')
        request_token = ast.literal_eval(self.oauth_response.content.decode("utf-8"))
        AT = request_token["AT"]
        ATS = request_token["ATS"]

    def tweet_init(self):
        #Tweetラベルの追加
        self.lbl = QLabel(self)
        self.lbl.move(50, 30)
        self.lbl.setText('<p><font size="4" color="' + phonto_color + '">呟く内容を書けよ</font></p>')

        # ツイートTextBoxの追加
        self.textbox = QTextEdit(self)
        self.textbox.move(40, 60)
        self.textbox.setStyleSheet("background-color: #FFFFFF;")

        # ツイートボタンの追加
        self.tweetbutton = QPushButton('tweet', self)
        self.tweetbutton.clicked.connect(self.tweet)
        self.tweetbutton.resize(100, 30)
        self.tweetbutton.setStyleSheet("background-color: #FFFFFF;")

        # 画像添付ボタンの追加
        self.imagebutton = QPushButton('画像添付', self)
        self.imagebutton.clicked.connect(self.add_image)
        self.imagebutton.resize(100, 30)
        self.imagebutton.setStyleSheet("background-color: #FFFFFF;")

        # 添付画像ラベルの追加
        self.imagelbl = QLabel(self)
        self.imagelbl.move(50, 145)
        self.imagelbl.setText('<p><font size="4" color="' + phonto_color + '">添付画像数 : ' + str(image_num) + '</font></p>')

        # 画像一覧ボタンの追加
        self.listbutton = QPushButton('画像一覧', self)
        self.listbutton.clicked.connect(self.list_image)
        self.listbutton.resize(100, 30)
        self.listbutton.move(180, 138)
        self.listbutton.setStyleSheet("background-color: #FFFFFF;")


    def hash_init(self):
        #ハッシュタグラベルの追加
        self.hashlbl = QLabel(self)
        self.hashlbl.move(50, 190)
        self.hashlbl.setText('<p><font size="4" color="' + phonto_color + '">保存したい画像のハッシュタグを書けよ</font></p>')

        #保存時ふぁぼ機能チェックボックスの追加
        self.hashcheckbox = QCheckBox("ふぁぼりてぇCheckBox", self)
        self.hashcheckbox.move(340, 190)
        self.hashcheckbox.setChecked(False)

        # ハッシュタグTextBoxの追加
        self.hashbox = QLineEdit(self)
        self.hashbox.move(40, 220)
        self.hashbox.setStyleSheet("background-color: #FFFFFF;")

        # 保存ボタンの追加
        self.savebutton = QPushButton('保存', self)
        self.savebutton.clicked.connect(self.save_hash)
        self.savebutton.resize(100, 30)
        self.savebutton.setStyleSheet("background-color: #FFFFFF;")

        #保存件数表示ラベルの追加
        self.savelbl = QLabel(self)
        self.savelbl.move(50, 260)
        self.savelbl.setText('<p><font size="4" color="' + phonto_color + '">保存件数 : </font></p>')
        self.savelbl.setVisible(False);

        self.progressChanged.connect(self.visible_hash)

    def timeline_init(self):
        # 保存ボタンの追加
        self.TLbutton = QPushButton('TimeLine', self)
        self.TLbutton.clicked.connect(self.timeline)
        self.TLbutton.resize(100, 30)
        self.TLbutton.setStyleSheet("background-color: #FFFFFF;")

    def menu_init(self):
        #メニューバーの作成
        self.menubar = QMenuBar(self)

        #Fileメニュ-の作成
        self.fileMenu = self.menubar.addMenu('&File')

        #Ctrl + Qで終了
        self.exitAction = QAction('&Exit', self)
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.setStatusTip('Exit application')
        self.exitAction.triggered.connect(qApp.quit)
        self.fileMenu.addAction(self.exitAction)

        #Ctrl + Wでテーマカラー変更
        self.themeColorAction = QAction('&Configuration', self)
        self.themeColorAction.setShortcut('Ctrl+W')
        self.themeColorAction.setStatusTip('Theme color change')
        self.themeColorAction.triggered.connect(self.configuration_window)
        self.fileMenu.addAction(self.themeColorAction)

        #テーマカラー変更
        self.themeMenu = self.fileMenu.addMenu('&Theme Change')
        self.themedefaultAction = QAction('&Default', self)
        #self.themeAction.setShortcut('Ctrl+D')
        self.themedefaultAction.setStatusTip('Theme change to default')
        self.themedefaultAction.triggered.connect(self.theme_default_change)
        self.themeMenu.addAction(self.themedefaultAction)

        self.themelightAction = QAction('&light', self)
        #self.themeAction.setShortcut('Ctrl+l')
        self.themelightAction.setStatusTip('Theme change to light')
        self.themelightAction.triggered.connect(self.theme_light_change)
        self.themeMenu.addAction(self.themelightAction)

        self.themedarkAction = QAction('&dark', self)
        #self.themeAction.setShortcut('Ctrl+T')
        self.themedarkAction.setStatusTip('Theme change to dark')
        self.themedarkAction.triggered.connect(self.theme_dark_change)
        self.themeMenu.addAction(self.themedarkAction)

    def update_theme_color(self):
        #print(vars(image_color))
        self.setStyleSheet("background-color: " + image_color + ";")

    def configuration_window(self):
        theme_window = ThemeWindow()
        theme_window.show()

    def theme_default_change(self):
        image_color = config.DEFAULT_IMAGE_COLOR
        phonto_color = config.DEFAULT_PHONT_COLOR
        self.set_theme()

    def theme_light_change(self):
        image_color = config.LIGHT_IMAGE_COLOR
        phonto_color = config.LIGHT_PHONT_COLOR
        self.set_theme()

    def theme_dark_change(self):
        image_color = config.DARK_IMAGE_COLOR
        phonto_color = config.DARK_PHONT_COLOR
        self.set_theme()

    def set_theme(self):
        self.setStyleSheet("background-color: " + image_color + ";")
        self.lbl.setText('<p><font size="4" color="' + ph + '">呟く内容を書けよ</font></p>')


    def timeline(self):
        timeline_window = TLWindow()
        timeline_window.show()

    def visible_hash(self, count):
        self.savelbl.setText('<p><font size="4" color="' + phonto_color + '">保存件数 :' + str(count) + ' 件 </font></p>')
        self.savelbl.setVisible(True);

        t=threading.Thread(target=self.invisible_hash)
        t.start()

    def invisible_hash(self):
        sleep(5)
        self.savelbl.setVisible(False);

    def alpha_change_init(self):
        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setFocusPolicy(Qt.NoFocus)
        self.slider.valueChanged[int].connect(self.alpha_change)

    def alpha_change(self, value):
        global alpha_rate
        alpha_rate = 0.2 + value / 100 * 0.8
        image_alpha_rate = 0.2 + value / 100 * 0.8
        self.setWindowOpacity(alpha_rate)

    def resizeEvent(self, event):
        self.widthFactor  = self.rect().width() / 1280
        self.heightFactor = self.rect().height()/ 300

        #ツイート機能ウィジェットの自動調整
        self.textbox.resize(self.w*self.widthFactor*0.85, 70)
        self.tweetbutton.move(40 + 30 + self.w*self.widthFactor*0.85, 100)
        self.imagebutton.move(40 + 30 + self.w*self.widthFactor*0.85, 60)

        #ハッシュタグ機能ウィジェットの自動調整
        self.hashbox.resize(self.w*self.widthFactor*0.85,30)
        self.savebutton.move(40 + 30 + self.w*self.widthFactor*0.85,  220)

        #透過率調整つまみの自動調整
        self.slider.move(self.w*self.widthFactor - 130,  self.h*self.heightFactor - 40)

        #TL表示ボタンの自動調整
        self.TLbutton.move(20, self.h*self.heightFactor - 40)

        super(MainWindow, self).resizeEvent(event)

    def tweet(self):
        global image_num
        global image_list
        image_res_list = []
        media_id_list = []
        self.get_AT()
        twitter = OAuth1Session(CK, CS, AT, ATS) #認証処理
        tweet = self.textbox.toPlainText()

        if image_num != 0:
            for i in range(len(image_list)):

                b64 = base64.encodestring(open(image_list[i], 'rb').read())

                #画像投稿
                files = {"media" : b64}
                res_image = twitter.post(url4, params = files) #post送信

                if res_image.status_code != 200:
                    print ("画像をアップロードできませんでした。: ", res_image.status_code, res_image.text )
                else:
                    image_res_list.append(res_image)


        for i in range(len(image_res_list)):
            media_id_list.append(json.loads(image_res_list[i].text)['media_id'])

        if image_num != 0:
            if len(image_res_list) == 0:
                print("画像投稿失敗")
                image_list
                return
            else:
                params = {"status" : tweet, "media_ids": media_id_list}

        else:
            params = {"status" : tweet}

        res = twitter.post(url2, params = params) #post送信

        if res.status_code == 200: #正常投稿出来た場合
            print("tweet success")
            self.textbox.setText("")
        else: #正常投稿出来なかった場合
            print("Failed. : %d"% res.status_code)

        image_list.clear()
        image_num = 0
        self.update_image_num()

    def add_image(self):

        global image_num

        if image_num > 3:
            return

        path = os.getcwd()


        input_image_path = QFileDialog.getOpenFileName(
        QFileDialog(), caption="入力画像", directory=path, filter="*.png *.jpg")[0]

        if input_image_path != "":
            image_list.append(input_image_path)
            image_num += 1
            self.imagelbl.setText('<p><font size="4" color="' + phonto_color + '">添付画像数 : ' + str(image_num) + '</font></p>')

            if image_num > 3:
                self.imagelbl.setText('<p><font size="4" color="' + phonto_color + '">添付画像数 : ' + str(image_num) + ' (MAX) </font></p>')

    def list_image(self):
        image_window = ImageWindow()
        image_window.show()

    def update_image_num(self):
        self.imagelbl.setText('<p><font size="4" color="' + phonto_color + '">添付画像数 : ' + str(image_num) + '</font></p>')




    #ハッシュタグを自動保存する
    def save_hash(self):
        self.get_AT()
        twitter = OAuth1Session(CK, CS, AT, ATS)
        hash = self.hashbox.text()
        hash = hash.strip()
        t=threading.Thread(target=self.save_hash_thread,args = (hash,))
        t.start()

    def save_hash_thread(self, hash):
        if hash[:1] != "#":
            hash = "#" + hash

        query = hash + ' filter:images min_faves:0 exclude:retweets'

        hash = hash[1:]

        if config.IMAGE_DIRECTORY == "":
            save_dir = "./" + hash
        else:
            if not os.path.exists(config.IMAGE_DIRECTORY):
                print("指定したディレクトリは存在しません。")
                return
            else:
                save_dir = config.IMAGE_DIRECTORY + "\\" + hash

        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        params = {"q": query, "count": 200}

        url = 'https://api.twitter.com/1.1/search/tweets.json'
        twitter = OAuth1Session(CK, CS, AT, ATS) #認証処理
        req = twitter.get(url, params=params)

        result = []
        if req.status_code == 200:
            tweets = json.loads(req.text)
            result = tweets['statuses']

        else:
            print("ERROR!: %d" % req.status_code)
            return;

        save_count = 0
        for tweet in result:
            name = tweet['user']['screen_name']
            date = tweet['created_at']
            date = date.replace(" +0000","")
            date = date.replace(" ","-")
            date = date.replace(":",".")
            count = 0
            try:
                media_list = tweet['extended_entities']['media']
                for img in media_list:
                    count += 1
                    img_url = img['media_url']
                    path = save_dir + "/[" + str(name) + "]_" + str(date) + "_" + str(count) + ".jpg"
                    print(path)
                    if os.path.exists(path):
                        print("重複のため保存しませんでした")
                    else:
                        tweet_id = tweet["id"]
                        params = {"id": tweet_id}
                        #print("id取得" + str(tweet_id))
                        if self.hashcheckbox.isChecked():
                            res = twitter.post(url3, params=params) #ふぁぼ
                            if res.status_code == 200: #正常投稿出来た場合
                                print("Favorite Success.")
                            else: #正常投稿出来なかった場合
                                print("Failed. : %d"% res.status_code)

                        urlreq.urlretrieve(img_url, path)
                        print("画像を保存しました", img_url)
                        save_count += 1
                    print("-・"*30)
            except Exception as e:
                print("画像を取得できませんでした")
                print(e)
                print("-・"*30)

        self.progressChanged.emit(save_count)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
