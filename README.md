# mobile_parking_control_system
사전 결제를 제공하며,레이저 OCR을 사용하지 않고 카메라를 이용한 모바일 사전 결제 시스템  
## Presentation
![image](https://user-images.githubusercontent.com/83262616/172036757-4e7e12db-2038-48a2-8529-f84e40c26f15.png)
![image](https://user-images.githubusercontent.com/83262616/172036759-f99dee8d-0360-4de5-aa71-4d6348ebf430.png)

# Release Note
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
캡쳐된 객체를 효율적으로 관리하기 위한 processing class 추가 (image 모듈)  
DB Connection, cursor 클래스화  
Classification.py 코드 일부 processing class merge 및 삭제  
불필요한 기능 일부 제거  
## 구현
Python3 (opencv, numpy, matplotlib, etc..)  
MySQL 8.0.2(DB)  
Android Studio(APP)  
참고 링크 : https://blog.naver.com/bjjy1113/222758599048  
# 프로젝트 총평  
## 아쉬운점
1. 프로젝트 특성상 임베디드와 연동 하지 않은 것에 대한 것, 라즈베리 파이, 캠을 이용하였으면 더 완성도 높을거라 생각.  
2. 일부 코드의 경우 C++ pybind를 이용하여 최적화가 가능한 부분이 있다고 생각함.  
3. 전기차 번호판 인식의 경우 threshold 구간이 하나밖에 없어 정확도가 떨어지는 점, RGB에서 B차원을 이용하여 upper, lower 범위를 이용했으면 더 정확한 계산이 가능하지 않았나 라는 생각이 든다.
# 프로젝트 실행 예시
**전기차 번호판 인식결과**   
<img src="https://user-images.githubusercontent.com/83262616/169675812-2309952e-2c1a-4f84-af01-2913b52b4b64.PNG" width="500">
<img src="https://user-images.githubusercontent.com/83262616/169675880-ab998337-db8f-41c8-9714-01cbd280036e.png" width="500">
**APP 실행 화면**  
<img src="https://user-images.githubusercontent.com/83262616/169682395-2f9d785e-9dac-4f14-b2e3-334f04eca5b0.jpg" width="400">
<img src="https://user-images.githubusercontent.com/83262616/169682397-30068b4f-2fe3-42cd-b09e-3c1a185e0ede.jpg" width="400">
