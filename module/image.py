from unittest import result
import cv2
import Classification as cf
import numpy as np
import matplotlib.image as img 
import matplotlib.pyplot as plt
import pytesseract
import datetime

'''
class processing
영상 객체의 파일화 및 잘라내는 클래스
'''
class processimg :
    # 생성자
    def __init__(self, img) :
        self.img = img
    # 이미지 크롭팅 함수
    def crop_img(self, img, x_min, x_max, y_min, y_max) :
        crop_img = img[y_min:y_min+y_max, x_min:x_min+x_max]
        return crop_img
    def crop_and_save(self, img, x_min, x_max, y_min, y_max) :
        crop_img = img[y_min:y_min+y_max, x_min:x_min+x_max]
        file_name = self.img_save(crop_img)
        return crop_img, file_name
    # 이미지 저장 함수, 파일명을 반환
    def img_save(self, img) :
        file_name = datetime.today().strftime('%Y-%m-%d-%H-%M-%S')
        cv2.imwrite("Capture/"+ file_name + ".png", img)
        return file_name
    # 모델 입력용 이미지 전처리 함수
    def machine_preprocessing(self, img) :
        # 객체 사이즈 축소 및 보간
        frame_resized = cv2.resize(img, [224,224], interpolation=cv2.INTER_AREA)
        # 이미지 정규화
        frame_normalized = (frame_resized.astype(np.float32) / 127.0) - 1

        # 예측을 위해 reshape.
        # 학습한 이미지와 사이즈가 동일하게 만든다.
        frame_reshaped = frame_normalized.reshape((1, 224, 224, 3))
        # 객체 반환
        self.img = frame_reshaped
