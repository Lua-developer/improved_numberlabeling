'''
Mobile Parking Control System
main.py
최종 수정 시각 : 2022-11-06
변경 사항 : image 모듈 추가 및 video 1차 최적화
'''
import tensorflow_hub as hub
import cv2
import pandas as pd
import Classification as Cf
import image
from number import labeling_bulid_1
from number import labeling_bulid_2
import DB as db
import tensorflow
import os 
def main() :
    os.environ['TFHUB_CACHE_DIR'] = '/home/user/workspace/tf_cache'
    detects = hub.load("https://tfhub.dev/tensorflow/efficientdet/lite2/detection/1")
    labels = pd.read_csv('labels.csv',sep=';',index_col='ID')
    # labels.csv 파일에서 label을 numpyArray 화 하여 배열로 저장합니다
    labels = labels['OBJECT (2022 REL.)']
    scale = 30
    location = 1
    MIN_AREA = 80
    MIN_WIDTH, MIN_HEIGHT = 2, 8
    MIN_RATIO, MAX_RATIO = 0.25, 1.0
    conn = db.con_and_make_cursor()
    cursor = conn.cursor()
    select = "SELECT * FROM administrator AS admin, parking_lot as PL WHERE admin.management_park = %s = PL.park_id = %s"
    cursor.execute(select, (location, location))
    result = cursor.fetchall()
    print("관리자 명 :", result[0][2],"연락처 :", result[0][3], "10분당 주차 비용(원) :",result[0][9], "지역 :", result[0][7], "현재 주차장 정보 : ",result[0][6], "최대 주차 면적 :", result[0][8])
    max_parking_area = result[0][8]
    cap = cv2.VideoCapture(0)
    counts = 0
    while(True) :
            # 프레임을 받아온다.
            ret, frame = cap.read()
            # 줌인을 하는 함수가 아님, frame/1sec 단위로 모든 프레임을 자른다
            cv2.flip(frame, 1)
            '''
            # 현재 반영되고 있는 프레임의 가로, 세로, 컬러채널 크기를 받아온다
            height, width, channels = frame.shape
            # 중심점 탐색
            centerX,centerY=int(height/2),int(width/2)
            # radius 계산
            radiusX,radiusY= int(scale*height/100),int(scale*width/100)
            # 적용할 새로운 프레임 크기 계산
            minX,maxX=centerX-radiusX,centerX+radiusX
            minY,maxY=centerY-radiusY,centerY+radiusY
            # 프레임 크롭 및 적용
            cropped = frame[minX:maxX, minY:maxY]
            '''
            # 이건 보기 편하게 하기 위해 윈도우 사이즈 확대
            # 프레임마다 리사이즈 하게 되면 초당 60프레임 기준으로 리소스 낭비가 심함
            # 주석처리
            #frame_img = cv2.resize(frame, (1024, 640)) 
            # 들어오는 프레임을 rgb2bgr
            rgb = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        #Is optional but i recommend (float convertion and convert img to tensor image)
            rgb_tensor = tensorflow.convert_to_tensor(frame, dtype=tensorflow.uint8)
            
            
            #rgb_tensor = tensorflow.convert_to_tensor(frame_img, dtype=tensorflow.uint8)

        #Add dims to rgb_tensor
            rgb_tensor = tensorflow.expand_dims(rgb_tensor , 0)
        
            boxes, scores, classes, num_detections = detects(rgb_tensor)
        
            pred_labels = classes.numpy().astype('int')[0]
            pred_labels = [labels[i] for i in pred_labels]
            pred_boxes = boxes.numpy()[0].astype('int')
            pred_scores = scores.numpy()[0]
            # object Detection 
            # 디텍터가 돌때 프레임 다운되는 현상 해결
            # for start
            for score, (ymin,xmin,ymax,xmax), label in zip(pred_scores, pred_boxes, pred_labels):
                conn.commit()
                # 차량이 아니면 검출하지 않음
                if score < 0.6 or label != 'car' :
                # 시연때는 사진 같은거로 보여줘야 하므로 로스를 높임
                    '''
                    들어온 프레임에서 car 객체가 아닌 경우에는 box를 그리지 않음.
                    '''
                    img_boxes = cv2.rectangle(frame,(0, 0),(0, 0),(0,0,0),1)
                    # img_boxes = cv2.rectangle(frame_img,(0, 0),(0, 0),(0,0,0),1)
                else :
                    img_boxes = cv2.rectangle(frame,(xmin, ymax),(xmax, ymin),(0,0,0),1)                       
                    #img_boxes = cv2.rectangle(frame_img,(xmin, ymax),(xmax, ymin),(0,0,0),1)   
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    '''
                    2. 차량 거리 계산
                    바운딩 박스의 기준이 되는 xmax, xmin, ymax, ymin 의 값을 이용하여 탐지된 객체의 박스 넓이를 계산
                    약 계산된 사이즈가 190000이 될때 번호판 인식율이 좋음.
                    박스의 크기가 기준에 충족하지 못하면 자동차 객체라도 다음 과정으로 넘어가지 않음
                    '''
                    x, y = xmax-xmin, ymax-ymin
                    size = x * y
                    # 박스 사이즈와 위치 출력
                    cv2.putText(img_boxes,str(size),(xmin, ymin), font, 0.5, (0,0,0), 1, cv2.LINE_AA)
                    result_ck = None
                    if label == "car" :
                        if size < 190000 :
                            continue
                        else :
                            # 시작
                            print("차량이 감지되었습니다.")
                            print("차량 배경 분리 작업을 시작합니다.")
                            # processimg 클래스 생성자 호출
                            unprocess_img = image.processimg(img_boxes)
                            crop_img, file_name = unprocess_img.crop_and_save(unprocess_img, xmin, xmax, ymin, ymax)
                            # 파일 확장자 추가
                            print("차량 배경 분리 완료 파일 명 : {}.png".format(file_name))
                            print("차량 번호판 분리 및 번호 라벨링 시작")
                            '''
                            3. 번호판 추출 세션
                            '''
                            plate_img, plate_infos = labeling_bulid_1(crop_img)
                            # 이미지 객체가 None이 반환된 경우 중단하고 다시 탐지
                            if plate_img == None :
                                print("이미지 객체가 잘못되었습니다.")
                                continue
                            # 라벨링이 끝난 번호를 반환합니다
                            result_char, isDiscount = labeling_bulid_2(MIN_AREA, MIN_WIDTH, MIN_HEIGHT, MIN_RATIO, MAX_RATIO, plate_img, plate_infos, car_img)
                            if result_char == None  :
                                count = count + 1
                                print("[에러] : 차량 라벨링 실패 현재 ", count, "회 실패!")
                                # 번호판 인식이 잘못되었으므로 해당 이미지는 삭제합니다.
                                try: 
                                    os.remove("Capture/" + img_name + ".png")
                                except: pass
                                # 실패 횟수 카운팅을 하여 연달아 실패 시 잠시 대기 후 다시 라벨링을 시도함
                                if count == 3 :
                                # 운전자에게 인식이 실패했다고 알린다.
                                    Open = cv2.imread("Failed.png")
                                    cv2.imshow("Fail", Open)
                                    cv2.waitKey(3000)
                                    count = 0
                                    continue
                                continue
                            # 제일 앞 글자가 숫자가 아니라면 제일 앞 문자를 지운다.
                            # 보정
                            if result_char[0] < '0' or result_char[0] > '9' :
                                for i in range(1, 8) :
                                    try :
                                        correction_char += result_char[i]
                                    except IndexError :
                                        print("번호판 정보가 잘못됨.")
                                        result_char = None
                                        continue
                                    except TypeError :
                                        print("번호판 정보가 잘못됨.")
                                        result_char = None
                                        continue
                                result_char = None
                                result_char = correction_char
                            # 차량 앞번호가 2자리 인 경우 뒤에 4자리 외에 컷
                            # 보정
                            if result_char[2] < '0' or result_char[2] > '9' :
                                for i in range(0, 7) :
                                    try :
                                        correction_char += result_char[i]
                                    except IndexError :
                                        print("번호판 정보가 잘못됨.")
                                        result_char = None
                                        continue
                                result_char = None
                                result_char = correction_char
                            # 차량 앞번호가 3자리 인 경우 뒤에 4자리 외에 컷
                            # 보정
                            if result_char[3] < '0' or result_char[3] > '9' :
                                for i in range(0, 8) :
                                    try :
                                        correction_char += result_char[i]
                                    except IndexError :
                                        print("번호판 정보가 잘못됨.")
                                        result_char = None
                                        continue
                                    result_char = None
                                    result_char = correction_char
                            if result_char == None :
                                print("라벨링 실패 재시도")
                                continue
                            Check = "SELECT * FROM car WHERE license_plate_number = %s"
                            cursor.execute(Check, (result_char)) 
                            result_ck = cursor.fetchall()
                            if not result_ck :
                                # 데베에 없으면 차 번호 인식 X
                                print("데이터 베이스에 존재 하지 않는 번호입니다. 재인식을 시도합니다.")
                                continue
                            if result_ck[0][1] == None:
                                result_char = Cf.entrance_car(result_char, location, isDiscount)
                                max_parking_area = max_parking_area - 1
                                print("차량 번호 : ", result_char)
                                print("현재 남은 공간 : ", max_parking_area)
                                # 운전자에게 차단기가 열렸다는 신호를 준다
                                Open = cv2.imread("Opened.png")
                                cv2.imshow("Open", Open)
                                cv2.waitKey(3000)
                                cv2.destroyAllWindows()
                                continue
                        # 출차 모드 일시 출차 프로세스 실행
                            else :
                                isPay = Cf.exit_car(result_char, location)
                                if isPay == 0 :
                                    Open = cv2.imread("Not.png")
                                    cv2.imshow("NotPayment", Open)
                                    cv2.waitKey(3000)
                                    cv2.destroyAllWindows()
                                    continue
                                elif isPay == 1 :
                                    max_parking_area = max_parking_area + 1
                                # 운전자에게 차단기가 열렸다는 신호를 준다
                                    Open = cv2.imread("Opened.png")
                                    cv2.imshow("Open", Open)
                                    cv2.waitKey(3000)
                                    cv2.destroyAllWindows()
                                    continue
            # for end
            cam_name = "screen"
                # 웹캠 오픈
            cv2.imshow(cam_name, img_boxes)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__" :
    main()
