import cv2
import time as time
from datetime import datetime
import DB as db
import numpy as np

# 차량 인식 후 번호판 추출에 불필요한 배경을 제거하는 함수입니다.
def Crop_and_save(xmin, xmax, ymin, ymax, img) :
    crop_img = img[ymin:ymin+ymax-150, xmin:xmin+xmax-350]
    crop_img = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
    # 크롭된 이미지를 저장합니다, 파일 명은 현재 시간으로 저장
    file_name = datetime.today().strftime('%Y-%m-%d-%H-%M-%S')
    cv2.imwrite("Capture/"+ file_name + ".png", crop_img)
    # 파일 이름을 반환(string)
    return file_name
# 현재 들어온 차량의 번호를 데이터베이스에서 조회합니다.
# 차량이 있다면 true를 없다면 False 를 반환합니다.
def isValidNumber(result_char) :
    conn = db.mySql_Connection()
    cur = conn.cursor()
    # isValid = "SELECT * FROM 입차내역 WHERE id == 'result_char'"
    # cur.execute(isValid)
# 인자로는 차량 번호를 받습니다.
def income_car(result_char) :
    #conn = db.mySql_Connection()
    #cur = conn.cursor()
    now = datetime.now()
    # 분단위로 자를거기에 분단위까지만 저장
    # isValidNumber(result_char)
    current_time = now.strftime("%H:%M:%S")
    print("차량 입차 정보")
    print("입차 시간 : ", current_time, "차량 번호 : ", result_char, "주차장 정보 : 영남대학교 기계관 학생주차장")
    # 데이터베이스 입차 정보 저장
    #insert_infomation = "INSERT INTO car VALUE(result_char, current_time, '',100)"
    # 실행
    #cur.execute(insert_infomation)
    '''
    if 실패시 자기 자신 재호출(3번) 3번 이상 실패하면 입차 프로세스 실패 
    '''
# 크롭 후 전처리된 번호판에서 번호를 추출 후 출차 조건에 맞는 경우 해당 함수를 호출합니다.
# 출차 프로세스 실행
def exit_car(exit_num) :
    return 0