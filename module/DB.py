'''
Mobile Parking Control System
DB.py
'''
# mySQL connect
# 데이터베이스의 연결 정보를 저장
# sql_connection 클래스를 이용하여 conn, cursor로 관리
# 생성자 단위에서 connection, cursor 생성
import pymysql

class sql_connection :
    def __init__(self) :
        self.conn = self.connection()   
        self.cursor = self.make_cursor(self.conn)
    def connection(self) :
        conn = pymysql.connect(host='localhost',
                        user='root', 
                        password='자기 비밀번호',
                        db='parking_service', 
                        charset='utf8')   
        return conn
    def make_cursor(self, conn):
        cur = conn.cursor()
        return cur
