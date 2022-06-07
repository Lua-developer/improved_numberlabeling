# mobile_parking_payment_system
사전 결제를 제공하며,레이저 OCR을 사용하지 않고 한대의 카메라를 이용한 모바일 사전 결제 시스템  
한대의 카메라로 입차와 출차가 가능(한 주차장당 출차 인식용, 입차 인식용 두대 사용)  
경제성과 편리함을 동시에 잡아 사업성이 매우 유망합니다.
APP 디자인 제공 : 용기의 흰불꽃  

## Presentation
![image](https://user-images.githubusercontent.com/83262616/172036757-4e7e12db-2038-48a2-8529-f84e40c26f15.png)
![image](https://user-images.githubusercontent.com/83262616/172036759-f99dee8d-0360-4de5-aa71-4d6348ebf430.png)

# Release Note
프로젝트 명을 모바일 주차 관제 시스템으로 명명  
프로젝트 명을 모바일 주차 결제 시스템으로 수정  
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
사전 결제를 위한 안드로이드 어플리케이션 개발 및 디자인   
입차, 출차 중 데이터베이스가 업데이트 되지 않는 현상 Fix  
전기차 판별 알고리즘 개선  
## 실행 방법
아래에 작성한 모든 환경은 모두 설정이 되어 있어야합니다.  
php 서버 실행 방법 : https://blog.naver.com/bjjy1113/222758599048  

# Develop Enviornment
**DataBase :MySQL Workbench 8.0.2  
Web Server : XAMPP
Main Programming : Python 3, Tool : VS code
Library : numpy, matplotlib.pyplot, opencv, pymysql, tensorflow, keras, pandas, etc..**  

# 프로젝트 실행 예시
**전기차 번호판 인식결과**   
<img src="https://user-images.githubusercontent.com/83262616/169675812-2309952e-2c1a-4f84-af01-2913b52b4b64.PNG" width="500">
<img src="https://user-images.githubusercontent.com/83262616/169675880-ab998337-db8f-41c8-9714-01cbd280036e.png" width="500">
**APP 실행 화면**  
<img src="https://user-images.githubusercontent.com/83262616/169682395-2f9d785e-9dac-4f14-b2e3-334f04eca5b0.jpg" width="400">
<img src="https://user-images.githubusercontent.com/83262616/169682397-30068b4f-2fe3-42cd-b09e-3c1a185e0ede.jpg" width="400">
