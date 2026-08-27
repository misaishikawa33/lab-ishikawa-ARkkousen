import sys
import numpy as np
import cv2
import glfw
import Setting
import Application

# アプリケーションで使用するパラメータ
#
settings = Setting.Setting('settings.txt', True)

#use_api = cv2.CAP_DSHOW # Windowsで使用する場合こちらを使う
use_api = 0             # Linuxで使用する場合はこちらを使う 

# アプリケーション設定
#
app = Application.Application('Aruco marker AR', settings, use_api)

# アプリケーションのメインループ
#
while not app.glwindow.window_should_close():
    app.display_func(app.glwindow.window)    
    glfw.poll_events()

glfw.terminate()


