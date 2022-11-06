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
    