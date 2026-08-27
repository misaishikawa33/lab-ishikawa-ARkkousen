import numpy as np
import datetime
import cv2
from cv2 import aruco

from OpenGL.GL import *
import glfw

from mqoloader.loadmqo import LoadMQO
from mqoloader.mqo_manager import MQOManager

import USBCamera as cam
import GLWindow
import PoseEstimation as ps
import Setting
import Marker as mkr

#
# MRアプリケーションクラス
#
class Application:
    
    # ------------------------------------------------------------------------
    # コンストラクタ
    # ------------------------------------------------------------------------
    # @param width    : 画像の横サイズ
    # @param height   : 画像の縦サイズ
    # @param deviceID : カメラ番号
    #
    def __init__(self, title, settings, use_api):
        if settings.camera_id != -1:
            self.use_camera = True
        else:
            self.use_camera = False

        self.title = title
        
        # 画像の大きさ設定
        self.width   = settings.camera_width
        self.height  = settings.camera_height
        self.channel = 3
        self.use_api = use_api
        
        # カメラの設定
        if self.use_camera:
            self.camera = cam.USBCamera (settings.camera_id,
                                         self.width,
                                         self.height,
                                         use_api)
        #
        # GLウィンドウの設定
        # 
        self.glwindow = GLWindow.GLWindow(title,
                                          self.width,
                                          self.height,
                                          self.display_func,
                                          self.keyboard_func)
        #
        # カメラの内部パラメータ
        #
        self.focus = settings.camera_focal_length
        self.u0    = self.width / 2.0
        self.v0    = self.height / 2.0

        #
        # OpenGLの表示パラメータ
        #
        scale = 0.01
        self.viewport_horizontal = self.u0 * scale
        self.viewport_vertical   = self.v0 * scale
        self.viewport_near       = self.focus * scale
        self.viewport_far        = self.viewport_near * 1.0e+6
        self.modelview           = (GLfloat * 16)()
        self.draw_axis           = True
        self.use_normal          = False

        #
        # カメラ姿勢を推定するクラス変数
        #
        self.estimator = ps.PoseEstimation(self.focus, self.u0, self.v0)

        # ファイル出力数のカウント用変数
        self.count = 0

        #
        # Arucoマーカーの設定
        #
        self.aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
        if hasattr(aruco, "DetectorParameters_create"):
            self.aruco_parameters = aruco.DetectorParameters_create()
        else:
            self.aruco_parameters = aruco.DetectorParameters()
        if hasattr(aruco, "ArucoDetector"):
            self.aruco_detector = aruco.ArucoDetector(self.aruco_dict,
                                                      self.aruco_parameters)
        else:
            self.aruco_detector = None
        self.ids = None
        self.corners = ()

        #
        # 3次元モデル
        #
        self.use_normal = False
        self.mqo_manager = MQOManager(10)
        self.model = []
        for n in range(len(settings.mqo_filename)):
            self.model.append (LoadMQO(settings.mqo_filename[n],
                                       settings.mqo_scale[n],
                                       self.use_normal,
                                       self.mqo_manager))
        self.nmodels = len(settings.mqo_filename)

        #
        # マーカーの設定
        #
        self.markers = []
        self.add_marker (settings.marker_file)
            
        self.settings = settings
        
    # ------------------------------------------------------------------------
    # マーカー情報の追加
    # ------------------------------------------------------------------------
    def add_marker (self, filename):
        with open(filename) as f:
            nlines = 0
            npoints = 0
            marker_id = 0
            p_t = []
            
            for line in f:
                nlines = nlines + 1
                if nlines == 1:
                    nmarkers = int(line)
                elif nlines % 5 == 2:
                    marker_id = int(line)
                else:
                    npoints = npoints + 1            
                    p_t.append(line)
                    if npoints == 4:
                        npoints = 0
                        p1_t = p_t[0].split()
                        p2_t = p_t[1].split()
                        p3_t = p_t[2].split()
                        p4_t = p_t[3].split()                

                        point_3D = np.array([[float(p1_t[0]),
                                              float(p1_t[1]),
                                              float(p1_t[2])],
                                             [float(p2_t[0]),
                                              float(p2_t[1]),
                                              float(p2_t[2])],
                                             [float(p3_t[0]),
                                              float(p3_t[1]),
                                              float(p3_t[2])],
                                             [float(p4_t[0]),
                                              float(p4_t[1]),
                                              float(p4_t[2])]])
                        self.markers.append(mkr.Marker(marker_id, point_3D))
                        p_t = []

    # ------------------------------------------------------------------------
    # カメラの内部パラメータの設定関数
    # ------------------------------------------------------------------------
    def SetCameraParam(self, focus, u0, v0):
        self.focus = focus
        self.u0    = u0
        self.v0    = v0

    # ------------------------------------------------------------------------
    # カメラ映像を表示するための関数
    #
    # ここに作成するアプリケーションの大部分の処理を書く
    # ------------------------------------------------------------------------
    def display_func(self, window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # 画像の読み込み
        success = False
        if self.use_camera:
            success, self.image = self.camera.CaptureImage()
        else:
            self.image = self.glwindow.image

        if not success:
            return

        # マーカ検出
        if self.aruco_detector is not None:
            self.corners, self.ids, _ = self.aruco_detector.detectMarkers(
                self.image)
        else:
            self.corners, self.ids, _ = aruco.detectMarkers(
                self.image,
                self.aruco_dict,
                parameters=self.aruco_parameters)

        # 画像の描画
        self.glwindow.draw_image(self.image)
            
        # カメラ姿勢推定
        if self.ids is not None:
            for n in range(len(self.ids)):
                marker_id = int(np.asarray(self.ids[n]).reshape(-1)[0])
                success = self.compute_camera_pose(self.corners[n][0],
                                                   marker_id)
                if success:
                    # 3次元モデルの描画
                    self.draw_3D_model(marker_id - 1)
                    
        glfw.swap_buffers(window)

    # ------------------------------------------------------------------------
    # キー関数
    # ------------------------------------------------------------------------
    def keyboard_func(self, window, key, scancode, action, mods):
        # Qで終了
        if key == glfw.KEY_Q:
            glfw.set_window_should_close(self.glwindow.window, GL_TRUE)

        # Sで画像の保存
        if action == glfw.PRESS and key == glfw.KEY_S:
            self.save_image(self.count)
            self.count += 1

        # Tでランドマーク表示を切り替え
        if action == glfw.PRESS and key == glfw.KEY_T:
            self.set_draw_landmark(not self.hand_detection.draw_landmark)

    # ------------------------------------------------------------------------
    # 画像を保存する関数
    # ------------------------------------------------------------------------
    def save_image(self, count):
        filename = 'output_image-%05d.png' % count
        image = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        glReadBuffer (GL_BACK)
        glReadPixels(0, 0, self.width, self.height, GL_RGB, GL_UNSIGNED_BYTE, image.data)
        image = cv2.flip (image, 0)
        image = cv2.cvtColor (image, cv2.COLOR_BGR2RGB)
        cv2.imwrite(filename, image)

    # ------------------------------------------------------------------------
    # カメラ姿勢を推定する関数
    # ------------------------------------------------------------------------
    def compute_camera_pose(self, c, id):
        x1, x2, x3, x4 = c[:,0]
        y1, y2, y3, y4 = c[:,1]
        
        point_2D = np.array([(x1, y1), (x2, y2), (x3, y3), (x4, y4)],
                            dtype = "double")

        # カメラ姿勢を計算
        for n in range(len(self.markers)):
            success = False
            if id == self.markers[n].id:
                success, R, t = self.estimator.compute_camera_pose(self.markers[n].point_3D, point_2D)
                break

        if success:
            # 世界座標系に対するカメラ位置を計算
            #     この位置を照明位置として使用
            if self.use_normal:
                pos = -R.transpose().dot(t)
                self.camera_pos = np.array([pos[0], pos[1], pos[2], 1.0], dtype="double")
            # OpenGLで使用するモデルビュー行列を生成
            self.modelview[0] = R[0][0]
            self.modelview[1] = R[1][0]
            self.modelview[2] = R[2][0]
            self.modelview[3] = 0.0
            self.modelview[4] = R[0][1]
            self.modelview[5] = R[1][1]
            self.modelview[6] = R[2][1]
            self.modelview[7] = 0.0
            self.modelview[8] = R[0][2]
            self.modelview[9] = R[1][2]
            self.modelview[10] = R[2][2]
            self.modelview[11] = 0.0
            self.modelview[12] = t[0]
            self.modelview[13] = t[1]
            self.modelview[14] = t[2]
            self.modelview[15] = 1.0

        return success
    
    # ------------------------------------------------------------------------
    # カメラ姿勢を推定する関数
    # ------------------------------------------------------------------------
    def draw_3D_model(self, id):

        if id > self.nmodels - 1:
            return

        self.glwindow.push_GL_setting()
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()            
        glFrustum(-self.viewport_horizontal, self.viewport_horizontal, -self.viewport_vertical, self.viewport_vertical, self.viewport_near, self.viewport_far)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glLoadMatrixf(self.modelview)

        # 証明をオン
        if self.use_normal:
            glLightfv(GL_LIGHT0, GL_POSITION, self.camera_pos)
            glEnable(GL_LIGHTING)
            glEnable(GL_LIGHT0)

        glTranslatef (self.settings.mqo_position_x[id],
                      self.settings.mqo_position_y[id],
                      self.settings.mqo_position_z[id])
        glRotatef (self.settings.mqo_angle[id],
                   self.settings.mqo_rotation_x[id],
                   self.settings.mqo_rotation_y[id],
                   self.settings.mqo_rotation_z[id])
        glScalef(self.model[id].scale, self.model[id].scale, self.model[id].scale)
        self.model[id].draw()

        self.glwindow.pop_GL_setting()
                
        # 証明をオフ
        if self.use_normal:                
            glDisable(GL_LIGHTING)
            glDisable(GL_LIGHT0)
