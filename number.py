'''
github : https://github.com/Lua-developer
Programmed by Jung Jin Young
reference : https://github.com/Mactto/License_Plate_Recognition
'''

# 테서랙트를 이용한 number.py
# 모듈화 진행 완료
from unittest import result
import cv2
import Classification as cf
import numpy as np
import matplotlib.image as img 
import matplotlib.pyplot as plt
import pytesseract

# 번호판 출력
MAX_DIAG_MULTIPLYER = 5 # 5
MAX_ANGLE_DIFF = 12.0 # 12.0
MAX_AREA_DIFF = 0.5 # 0.5
MAX_WIDTH_DIFF = 0.8
MAX_HEIGHT_DIFF = 0.2
MIN_N_MATCHED = 3 # 3

#똑바로 돌리기
PLATE_WIDTH_PADDING = 1.3 # 1.3
PLATE_HEIGHT_PADDING = 1.5 # 1.5
MIN_PLATE_RATIO = 3
MAX_PLATE_RATIO = 10
#어떤게 번호판처럼 생겼는지?

MIN_AREA = 80
MIN_WIDTH, MIN_HEIGHT = 2, 10
MIN_RATIO, MAX_RATIO = 0.5, 1.0

def find_chars(contour_list):
    matched_result_idx = []
    
    for d1 in contour_list:
        matched_contours_idx = []
        for d2 in contour_list:
            if d1['idx'] == d2['idx']:
                continue

            dx = abs(d1['cx'] - d2['cx'])
            dy = abs(d1['cy'] - d2['cy'])

            diagonal_length1 = np.sqrt(d1['w'] ** 2 + d1['h'] ** 2)

            distance = np.linalg.norm(np.array([d1['cx'], d1['cy']]) - np.array([d2['cx'], d2['cy']]))
            if dx == 0:
                angle_diff = 90
            else:
                angle_diff = np.degrees(np.arctan(dy / dx))
            area_diff = abs(d1['w'] * d1['h'] - d2['w'] * d2['h']) / (d1['w'] * d1['h'])
            width_diff = abs(d1['w'] - d2['w']) / d1['w']
            height_diff = abs(d1['h'] - d2['h']) / d1['h']

            if distance < diagonal_length1 * MAX_DIAG_MULTIPLYER \
            and angle_diff < MAX_ANGLE_DIFF and area_diff < MAX_AREA_DIFF \
            and width_diff < MAX_WIDTH_DIFF and height_diff < MAX_HEIGHT_DIFF:
                matched_contours_idx.append(d2['idx'])

        # append this contour
        matched_contours_idx.append(d1['idx'])

        if len(matched_contours_idx) < MIN_N_MATCHED:
            continue

        matched_result_idx.append(matched_contours_idx)

        unmatched_contour_idx = []
        for d4 in contour_list:
            if d4['idx'] not in matched_contours_idx:
                unmatched_contour_idx.append(d4['idx'])

        unmatched_contour = np.take(contour_list, unmatched_contour_idx)
        
        # recursive
        recursive_contour_list = find_chars(unmatched_contour)
        
        for idx in recursive_contour_list:
            matched_result_idx.append(idx)

        break

    return matched_result_idx

# 1단계 이미지 전처리
def labeling_bulid_1(img_ori):
    try :
        height, width, channel = img_ori.shape
    except AttributeError :
        return None, None
    possible_contours = []
    '''
    1차 이미지 전처리
    이미지를 흑백조로 전환하고 모폴로지를 통해 차량 이미지에서 부풀리고 줄임으로 노이즈를 1차로 제거
    가우시안 블러링을 통해 이미지의 윤곽선을 매끄럽게 수정함
    '''
    gray = cv2.cvtColor(img_ori, cv2.COLOR_BGR2GRAY)

    structuringElement = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

    imgTopHat = cv2.morphologyEx(gray, cv2.MORPH_TOPHAT, structuringElement)
    imgBlackHat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, structuringElement)
    
    imgGrayscalePlusTopHat = cv2.add(gray, imgTopHat)
    gray = cv2.subtract(imgGrayscalePlusTopHat, imgBlackHat)
    img_blurred = cv2.GaussianBlur(gray, ksize=(5, 5), sigmaX=0)
    '''
    Edge에 대해 블러링이 된 이미지에 스레시홀드를 가하여 회색조 이미지에서 흑백 반전을 일으킴
    Adaptive Thresholding 기법중 Mean_Thresholding을 채택
    Mean_Threshold는 번호판을 흐리게 하기 보다 이미지를 매끄럽게 처리하여 OCR의 인식율이 좋아짐
    Gaussian_Thresholding 은 반대로 이미지를 더 흐리게 만들어 OCR의 인식율이 낮아짐
    '''
    img_thresh = cv2.adaptiveThreshold(
        img_blurred, 
        maxValue=255.0, 
        adaptiveMethod=cv2.ADAPTIVE_THRESH_MEAN_C, 
        thresholdType=cv2.THRESH_BINARY_INV, 
        blockSize=19, 
        C=9
        )
    contours, _ = cv2.findContours(
        img_thresh, 
        mode=cv2.RETR_LIST, 
        method=cv2.CHAIN_APPROX_SIMPLE
        )

    '''
    이미지의 특성을 이해하고 특성에 대해 수식으로 변환하기 위해 새로운 numpy array를 생성하고 제로패딩함
    컨투어로 스레시홀딩된 이미지에서 연결성이 있는 객체에 대해 바운딩 박스를 그려 표현함
    '''
    temp_result = np.zeros((height, width, channel), dtype=np.uint8)
    cv2.drawContours(temp_result, contours=contours, contourIdx=-1, color=(255, 255, 255))
    temp_result = np.zeros((height, width, channel), dtype=np.uint8)
    contours_dict = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(temp_result, pt1=(x, y), pt2=(x+w, y+h), color=(255, 255, 255), thickness=2)
    
    # insert to dict
        contours_dict.append({
            'contour': contour,
            'x': x,
            'y': y,
        'w': w,
        'h': h,
        'cx': x + (w / 2),
        'cy': y + (h / 2)
    })
    cnt = 0
    for d in contours_dict:
        area = d['w'] * d['h']
        ratio = d['w'] / d['h']
    
        if area > MIN_AREA \
        and d['w'] > MIN_WIDTH and d['h'] > MIN_HEIGHT \
        and MIN_RATIO < ratio < MAX_RATIO:
            d['idx'] = cnt
            cnt += 1
            possible_contours.append(d)
        
    temp_result = np.zeros((height, width, channel), dtype=np.uint8)

    for d in possible_contours:
        cv2.rectangle(temp_result, pt1=(d['x'], d['y']), pt2=(d['x']+d['w'], d['y']+d['h']), color=(255, 255, 255), thickness=2)
    try :
        result_idx = find_chars(possible_contours)
    except IndexError :
        return None, None
    matched_result = []
    for idx_list in result_idx:
        matched_result.append(np.take(possible_contours, idx_list))

    '''
    이미지에서 바운딩박스가 연속되는 지점에 대해 네모 박스 형태로 묶음처리를 한다.
    바운딩박스가 규칙적으로 일정하게 반복되는 구간은 차량에서 번호판에 해당이 되므로 번호판을 네모처럼 잘라내는것과 같음
    '''
    temp_result = np.zeros((height, width, channel), dtype=np.uint8)
    for r in matched_result:
        for d in r:
#         cv2.drawContours(temp_result, d['contour'], -1, (255, 255, 255))
            cv2.rectangle(temp_result, pt1=(d['x'], d['y']), pt2=(d['x']+d['w'], d['y']+d['h']), color=(255, 255, 255), thickness=2)
    plate_imgs = []
    plate_infos = []
    for i, matched_chars in enumerate(matched_result):
        sorted_chars = sorted(matched_chars, key=lambda x: x['cx'])
        plate_cx = (sorted_chars[0]['cx'] + sorted_chars[-1]['cx']) / 2
        plate_cy = (sorted_chars[0]['cy'] + sorted_chars[-1]['cy']) / 2
    
        plate_width = (sorted_chars[-1]['x'] + sorted_chars[-1]['w'] - sorted_chars[0]['x']) * PLATE_WIDTH_PADDING
        sum_height = 0
        for d in sorted_chars:
            sum_height += d['h']

        plate_height = int(sum_height / len(sorted_chars) * PLATE_HEIGHT_PADDING)
        triangle_height = sorted_chars[-1]['cy'] - sorted_chars[0]['cy']
        triangle_hypotenus = np.linalg.norm(
        np.array([sorted_chars[0]['cx'], sorted_chars[0]['cy']]) - 
        np.array([sorted_chars[-1]['cx'], sorted_chars[-1]['cy']])
    )
        '''
        해당 라인에서 연속적으로 이미지 프로세싱을 시도 할 시 오류가 있었음
        angle은 번호판이 각지거나 휘었을때 픽셀 특징을 가지고 보정을 하는 기능임
        첫번째에서는 반환되는 list의 개수가 1개 이나, 2번째 부터는 2개 이상을 반환
        보정을 위해 컨볼루션을 거치는 것으로 보임, 마지막 리스트 내의 numpy array가 보정된 번호판 위치 특성인데 이전에 연산된 특징들 까지 중복으로 적용되었음
        프로세스된 특징을 추출하고 리스트화 하여 번호판의 위치 특성을 labeling_bulid_1 함수에서 반환함
        '''
        angle = np.degrees(np.arcsin(triangle_height / triangle_hypotenus))
        rotation_matrix = cv2.getRotationMatrix2D(center=(plate_cx, plate_cy), angle=angle, scale=1.0)
        img_rotated = cv2.warpAffine(img_thresh, M=rotation_matrix, dsize=(width, height))   
        img_cropped = cv2.getRectSubPix(
        img_rotated, 
        patchSize=(int(plate_width), int(plate_height)), 
        center=(int(plate_cx), int(plate_cy))
    ) 
        if img_cropped.shape[1] / img_cropped.shape[0] < MIN_PLATE_RATIO or img_cropped.shape[1] / img_cropped.shape[0] < MIN_PLATE_RATIO > MAX_PLATE_RATIO:
            continue
    
        plate_imgs.append(img_cropped)
        plate_infos.append({
        'x': int(plate_cx - plate_width / 2),
        'y': int(plate_cy - plate_height / 2),
        'w': int(plate_width),
        'h': int(plate_height)
    })
    # plate_imgs는 번호판 위치를 보정 후 번호판의 왜곡되지 않은 특성을 numpy.array 형태로 가지게 됨
    # 만약 보정이 따로 들어가지 않았다면 해당 조건을 실행
    if plate_imgs == None :
        print("Error")
        return None, None
    if len(plate_imgs) == 1 :
        np.squeeze(plate_imgs)
        return plate_imgs, plate_infos
    # 보정이 들어갔다면 해당 조건을 실행
    # 계산된 특성을 추출하고 리스트로 매핑하여 반환
    else :
        try :
            np.squeeze(plate_imgs)
            new_plate = plate_imgs.pop()
            new_plate = [new_plate]
        except IndexError :
            return None, None
        return new_plate, plate_infos
# 여기까지 labeling_bulid_1, plate_img 라는 전처리가 완료된 이미지 객체를 labeling_bulid_2 함수로 전달
    
def labeling_bulid_2(MIN_AREA, MIN_WIDTH, MIN_HEIGHT, MIN_RATIO, MAX_RATIO, plate_imgs,plate_infos, ori_img):
    '''
    labeling_bulid_2 함수는 번호판의 특징을 수식화한 plate_imgs를 받는다
    이 이미지 특성을 담고 있는 객체는 2차적으로 전처리를 하고 각 바운딩박스에서 추출된 2차원 특징 벡터를 테서랙트 OCR과 대조한다.
    동작 방식은 MNIST의 문자 판독과 비슷한 대조 방식
    OCR에서 라벨링되어 반환된 string 문자열은 main.py 에서 최종적으로 예외처리를 거친 후 성공/실패 여부를 판단한다.
    '''
    longest_idx, longest_text = -1, 0
    plate_chars = []
    for i, plate_img in enumerate(plate_imgs):
        plate_img = cv2.resize(plate_img, dsize=(0, 0), fx=1.6, fy=1.6)
        _, plate_img = cv2.threshold(plate_img, thresh=0.0, maxval=255.0, type=cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(plate_img, mode=cv2.RETR_LIST, method=cv2.CHAIN_APPROX_SIMPLE)
    
        plate_min_x, plate_min_y = plate_img.shape[1], plate_img.shape[0]
        plate_max_x, plate_max_y = 0, 0

    # 최종적으로 번호판 좌표 찍는 부분 문제X
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
        
            area = w * h
            ratio = w / h
            
            if area > MIN_AREA \
        and w > MIN_WIDTH and h > MIN_HEIGHT \
        and MIN_RATIO < ratio < MAX_RATIO:
                if x < plate_min_x:
                    plate_min_x = x
                if y < plate_min_y:
                    plate_min_y = y
                if x + w > plate_max_x:
                    plate_max_x = x + w
                if y + h > plate_max_y:
                    plate_max_y = y + h
        '''
        미세 조정, 차량 앞 번호의 나사는 모조리 걸러냄
        카메라를 이용하여 직접 차량을 촬영 시 최적의 표준편차는 0.2
        차량을 촬영하는게 아닌 기존의 사진을 이용하여 입력 시 최적의 표준편차는 0.4~0.5 사이
        커널은 3,3 이 적당함, 표준편차를 조정하며 번호판에서 라벨링된 글자를 blurring 하여 sharp하게 만듬
        해당 소스에서 잡아내지 못한 번호판 잡음은 main 단에서 다시 한번 예외처리
        '''
        img_result = plate_img[plate_min_y:plate_max_y+5, plate_min_x:plate_max_x+10]
        try :
            img_result = cv2.GaussianBlur(img_result, ksize=(3, 3), sigmaX=0.3)
        except IndexError :
            return None, None
        _, img_result = cv2.threshold(img_result, thresh=0.0, maxval=255.0, type=cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        # 번호판 디버깅시 사용
        plt.imshow(img_result)
        plt.show()
        # 테서랙트를 불러온다
        pytesseract.pytesseract.tesseract_cmd = 'C:\\Users\\LUA\\Documents\\Tesseract-OCR\\tesseract.exe'
        chars = pytesseract.image_to_string(img_result, lang='kor', config='--psm 7 --oem 0')
        # 신형 구형 번호판 인식율 향상
        result_chars = ''
        has_digit = False
        for c in chars:
            if ord('가') <= ord(c) <= ord('힣') or c.isdigit():
                if c.isdigit() :
                    has_digit = True
                result_chars += c
        # 가장 마지막에 있는 string 이 숫자인지 아스키 코드로 판별
        if has_digit and len(plate_chars) > longest_text:
            longest_idx = i
        info = plate_infos[longest_idx]
        isDiscount = cf.isCompactCar(ori_img)
        if isDiscount != 1 :        
            isDiscount = cf.isElectric(info, ori_img)
        if len(result_chars) >= 7 or len(result_chars) <= 9 :
            return result_chars, isDiscount
        else :
            return None, None