# improved_car_numberlabeling
기존의 번호판 인식 알고리즘을 개선 하고 소스 모듈화로 바로 적용할 수 있게 바꾼 소스입니다

수정 내용 리뷰 : https://blog.naver.com/bjjy1113/222677131195

using langauge : Python

개선 내용
- 번호판 이미지 전처리시 번호판에서 노이즈가 나타나는 현상
- 한국의 규격에 맞게 번호판 인식 글자 수 제한
- 두개의 함수로 압축하여 필요시 간단하게 이식하여 사용 가능 합니다. (input image, output car_number)


refered site :
1. https://maxtime1004.tistory.com/38
2. https://velog.io/@mactto3487/%ED%94%84%EB%A1%9C%EC%A0%9D%ED%8A%B8-OpenCV-%EC%9E%90%EB%8F%99%EC%B0%A8-%EB%B2%88%ED%98%B8%ED%8C%90-%EC%9D%B8%EC%8B%9D
3. https://github.com/Mactto/License_Plate_Recognition
