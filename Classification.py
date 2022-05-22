'''
Mobile Parking Control System
Classification.py
'''
import cv2
import time as time
from datetime import datetime
import tensorflow as tf
import keras
import DB as db
import matplotlib.pyplot as plt
import numpy as np
# 경차 이미지 넣고 아웃풋 반환하는 함수 하나 생성
# classification model class 하나 만들기


# 차량 인식 후 번호판 추출에 불필요한 배경을 제거하는 함수입니다.
def Crop_and_save(xmin, xmax, ymin, ymax, img) :
    crop_img = img[ymin:ymin+ymax, xmin:xmin+xmax]
    # 크롭된 이미지를 저장합니다, 파일 명은 현재 시간으로 저장
    file_name = datetime.today().strftime('%Y-%m-%d-%H-%M-%S')
    cv2.imwrite("Capture/"+ file_name + ".png", crop_img)
    return file_name
# 입차 프로세스를 담당하는 함수
def entrance_car(result_char, location, isDiscount) :
    conn = db.con_and_make_cursor()
    cursor = conn.cursor()
    # 분단위로 자를거기에 분단위까지만 저장
    times = time.strftime('%m-%d %H:%M')
    print("차량 입차 정보")
    select = "SELECT * FROM parking_lot as PL WHERE PL.park_id = %s"
    cursor.execute(select, location)
    result = cursor.fetchall()
    print("입차 시간 : ", times, "차량 번호 : ", result_char, "주차장 정보 :", result[0][1], "10분당 요금 :", result[0][4])
    times = time.strftime('%Y-%m-%d %H:%M')
    # 입차 로그 업데이트
    update = "UPDATE car SET entry_time = %s, park_id = %s WHERE license_plate_number = %s"
    cursor.execute(update,(times, location ,result_char))
    conn.commit()
# 사전 결제차량 구분 후 사전 결제 차량일 시 출차
# 미결제 차량이라면 차주의 포인트를 차감후 출차(I PARKING Parking Pass 모방)
def exit_car(result_char, location) :
    conn = db.con_and_make_cursor()
    cursor = conn.cursor()
    times = time.strftime('%m-%d %H:%M')
    print("차량 출차 정보")
    select = "SELECT * FROM car WHERE license_plate_number = %s"
    cursor.execute(select, result_char)
    result = cursor.fetchall()
    # 사전 결제 조회
    if result[0][4] == 0 :
        print("미 사전결제 차량")
        return 0
        # result = order(result_char, location)
        # if result == 0 :
        #     print("포인트가 부족합니다! 포인트를 충전 해 주세요.")
        # else :
        #     print("포인트 결제 완료")
    else :
        print("사전 정산 차량")
        times = time.strftime('%Y-%m-%d %H:%M:%S')
        update = "UPDATE car SET departure_time = %s WHERE license_plate_number = %s"
        cursor.execute(update,(times, result_char))
        # 출차된 차량은 시간 초기화
        update_time = "UPDATE car SET entry_time = %s, departure_time = %s, pre_order = %s WHERE license_plate_number = %s"
        cursor.execute(update_time, (None, times, 0, result_char))
        conn.commit()
        return 1
def isCompactCar(img) :
    compact_model ='compactcar.h5'
    model = keras.models.load_model(compact_model, compile=False, custom_objects={'tf': tf})
    # 먼저 들어온 이미지 정규화
    preprocessed = preprocessing(img)
    # 분류
    prediction = model.predict(preprocessed)
    # 첫번째 라벨은 경차 두번째라벨은 Ohter
    if prediction[0,0] > prediction[0,1] :
        print("할인 대상 차량 : 경차")
        return 1
    else :
        return 0

def preprocessing(img):
    
    size = (224, 224)
    frame_resized = cv2.resize(img, size, interpolation=cv2.INTER_AREA)
    
    # 이미지 정규화
    # astype : 속성
    frame_normalized = (frame_resized.astype(np.float32) / 127.0) - 1

    # 이미지 차원 재조정 - 예측을 위해 reshape 해줍니다.
    # keras 모델에 공급할 올바른 모양의 배열 생성
    frame_reshaped = frame_normalized.reshape((1, 224, 224, 3))
    #print(frame_reshaped)
    return frame_reshaped

def isElectric(info, img) :
    '''
    일반 번호판은 바탕이 하얀색, 전기차 번호판은 하늘색
    차량 번호는 둘다 검은색이고, 차지하는 비중이 비슷하므로 배경 판별에는 큰 영향을 주지 않기에 신경쓰지 않음
    R,G,B 각각의 채널에서 전기차가 아닌 경우 B 채널의 밝기값이 0에 밀집됨
    전기차인 경우 B채널의 밝기값이 255에 밀집되어 있음
    번호판을 땃을 때 밝기값이 어두운쪽으로 몰빵 되어 있는 현상을 해결 하기 위해 히스토그램 평활화를 적용하여 밝기값을 골고루 분포되게 변경
    일반 번호판은 흰색이기 때문에 평활화로 인해 B채널의 값이 증가하지만 미미한 수준
    전기차 번호판은 파란색이기 때문에 압도적으로 파란 밝기가 높아지는 것을 확인 함
    '''
    img = img[info['y']:info['y']+info['h'], info['x']:info['x']+info['w']]
    cv2.imshow("test", img)
    img_yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
    img_yuv[:,:,0] = cv2.equalizeHist(img_yuv[:,:,0])
    img_output = cv2.cvtColor(img_yuv, cv2.COLOR_YCR_CB2BGR)
    colors = ['b']
    bgr_planes = cv2.split(img_output)
# R,G,B 중 B채널의 밝기값을 histogram 계산
    for (p, c) in zip(bgr_planes, colors):
        hist = cv2.calcHist([p], [0], None, [256], [0, 256])
        plt.plot(hist, color=c)
        plt.show()
    max = hist.argmax()
    # B채널의 밝기 값 중 가장 집중된 부분을 뽑아낸다
    if max == 255 :
        print("주차 할인 대상 차량 : 전기차")
        return 1
    else :
        print("일반 차량")
        return 0

def order(result_char, location) :
    conn = db.con_and_make_cursor()
    cursor = conn.cursor()
    # 포인트 결제 프로세스
    # 출차 시간 저장
    update = "UPDATE car SET departure_time = %s WHERE license_plate_number = %s"
    d_times = time.strftime('%Y-%m-%d %H:%M')
    cursor.execute(update,(d_times, result_char))
    conn.commit()
    print("결제 모듈을 실행합니다.")
    print("차량 번호 : ", result_char)
    print("회원의 주차 시간과 포인트를 조회합니다")
    # payment 테이블 업데이트를 위해 user id를 가져온다
    # 조인 걸어서 car 테이블 동시에 조회
    select_join = "SELECT * FROM user, car WHERE user.license_plate_number = %s AND car.license_plate_number = %s"
    cursor.execute(select_join, (result_char, result_char))
    result = cursor.fetchall()
    select_park_fee = "SELECT parking_lot.fee_per_10min FROM parking_lot, car WHERE parking_lot.park_id = %s AND car.park_id = %s"
    cursor.execute(select_park_fee, (location, location)) 
    fee = cursor.fetchall()
    print(result)
    # 입차, 출차, 잔여 포인트, 10분당 요금
    id, entry, d_times, n_point, t_fee = result[0][0], result[0][7], result[0][8], result[0][5], int(fee[0][0])
    # 시간 차이를 분 단위로 계산
    minutes = int(divmod((d_times - entry).total_seconds(), 60)[0] / 10)
    total_fee = t_fee * minutes
    # 최대 15000원
    if total_fee > 15000 :
        total_fee = 15000
    # 포인트 차감된 잔여 포인트 업데이트
    n_point = n_point - total_fee
    update = "UPDATE user SET points = %s WHERE license_plate_number = %s"
    cursor.execute(update,(n_point, result_char))
    conn.commit()
    # payment table 업데이트
    payment_t = time.strftime('%Y-%m-%d %H:%M')
    insert_payment = "INSERT INTO payment VALUES (%s, %s, %s, %s)"
    p_id = n_point / 10 + 201231
    cursor.execute(insert_payment, (p_id, payment_t, total_fee, str(id)))
    conn.commit()
    # 결제 모듈 종료
    print("포인트로 결제가 완료 되었습니다.")
    