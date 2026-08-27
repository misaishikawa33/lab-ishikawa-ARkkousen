import numpy as np
import cv2

# 
# 平面上の特徴点対応からカメラ姿勢を推定するクラス
#
class PoseEstimation:

    # ------------------------------------------------------------------------
    # コンストラクタ
    # ------------------------------------------------------------------------
    def __init__(self, f, u0, v0):

        # 投影行列
        self.A = np.array([[f, 0.0, u0], [0.0, f, v0], [0.0, 0.0, 1.0]], dtype = "double")

        # 歪み係数
        self.dist_coeff = np.zeros((4, 1))

    # ------------------------------------------------------------------------
    # カメラ姿勢の推定関数
    # ------------------------------------------------------------------------
    def compute_camera_pose(self, point_3D, point_2D):
        success, vec_R, t = cv2.solvePnP(point_3D,
                                         point_2D,
                                         self.A,
                                         self.dist_coeff,
                                         flags = 0)
        if not success:
            return False, None, None

        R = cv2.Rodrigues (vec_R)[0]

        # OpenGLの座標系に変換する回転行列
        R_ = np.array([[1.0, 0.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, -1.0]])
        R = np.dot(R_, R)
        t = np.dot(R_, t).reshape(3)
            
        return success, R, t

    # ------------------------------------------------------------------------
    # 3次元点をセットする関数
    # ------------------------------------------------------------------------
    def set_3D_points(self, filename):
        with open(filename) as f:
            nlines = 0
            p_t = []
            for line in f:
                nlines = nlines + 1                
                if nlines == 1 or nlines == 2:
                    continue
                p_t.append(line)


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
        self.point_3D = point_3D
        self.ready = True
