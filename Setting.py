import numpy
import cv2

class Setting:
    def __init__(self, filename, verbose):
        self.mqo_filename = []
        self.mqo_scale = []
        self.mqo_position_x = []
        self.mqo_position_y = []
        self.mqo_position_z = []
        self.mqo_rotation_x = []
        self.mqo_rotation_y = []
        self.mqo_rotation_z = []                
        self.mqo_angle = []
        with open(filename) as f:
            for line in f:
                splitted_text = line.split()
                label = splitted_text[0]
                if label == 'cameraID:':
                    self.camera_id = int(splitted_text[1])
                elif label == 'cameraSize:':
                    self.camera_width  = int(splitted_text[1])
                    self.camera_height = int(splitted_text[2])
                elif label == 'focalLength:':
                    self.camera_focal_length = int(splitted_text[1])
                elif label == 'markerFile:':
                    self.marker_file = splitted_text[1]
                elif label == 'mqoModel:':
                    self.mqo_filename.append (splitted_text[1])
                    self.mqo_scale.append (float(splitted_text[2]))
                elif label == 'mqoPose:':
                    self.mqo_position_x.append (float(splitted_text[1]))
                    self.mqo_position_y.append (float(splitted_text[2]))
                    self.mqo_position_z.append (float(splitted_text[3]))
                    self.mqo_rotation_x.append (float(splitted_text[4]))
                    self.mqo_rotation_y.append (float(splitted_text[5]))
                    self.mqo_rotation_z.append (float(splitted_text[6]))
                    self.mqo_angle.append (float(splitted_text[7]))
