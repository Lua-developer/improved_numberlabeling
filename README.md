# mobile_parking_control_system
해당 프로젝트는 영남대학교 정보통신공학과 2022년 1학기 종합설계및과제 과목에 의해 개발되었습니다.  

# Release Note
프로젝트 명을 모바일 주차 관제 시스템으로 명명  
데이터베이스 구조 설계 및 테이블 정의  
차량 인식을 위한 tensorflow-hub Object Detection 모델 적용(main.py)  
데이터베이스에 필요한 데이터 삽입  
번호판 프로세스 소스 생성 (number.py)  
파이썬 DB 연동 (DB.py)  
입,출차 프로세스 추가 (Classification.py)   
number.py 소스 모듈화  
차량 인식 1차 개선 (일정 거리 도달 시 인식, 차량 외 더미 박스를 추가하여 프레임 드랍 Fix)  
number.py 소스 1차 개선 (차량 이미지 전처리 알고리즘 개선)  
차량 번호 라벨링 과정에서 contour가 충돌하던 현상 Fix  
차량이 두번 이상 인식 될때 번호판이 뭉개지는 현상 Fix  
전기차 판별 알고리즘 추가 (isElectric)  
경차 판별 모델 추가 (isCompact)  


# Develop Enviornment
**DataBase :MySQL Workbench 8.0.2  
Main Programming : Python 3  
Library : numpy, matplotlib.pyplot, opencv, pymysql, tensorflow, keras, pandas, etc..**  

# 프로젝트 실행 예시

**전기차 번호판 인식결과**   
<img src="https://user-images.githubusercontent.com/83262616/169675812-2309952e-2c1a-4f84-af01-2913b52b4b64.PNG" width="500">
<img src="https://user-images.githubusercontent.com/83262616/169675880-ab998337-db8f-41c8-9714-01cbd280036e.png" width="500">
**APP 실행 화면**  
<img src="https://user-images.githubusercontent.com/83262616/169682395-2f9d785e-9dac-4f14-b2e3-334f04eca5b0.jpg" width="400">
<img src="https://user-images.githubusercontent.com/83262616/169682397-30068b4f-2fe3-42cd-b09e-3c1a185e0ede.jpg" width="400">
