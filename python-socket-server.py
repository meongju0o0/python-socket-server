import os
import socket
import re
from datetime import datetime

class SocketServer:
    def __init__(self):
        self.bufsize = 1024  # 버퍼 크기 설정
        self.DIR_PATH = './request'
        self.createDir(self.DIR_PATH)

        # 응답 파일 읽기 (응답 파일이 없을 경우 기본 메시지 설정)
        try:
            with open('./response.bin', 'rb') as file:
                self.RESPONSE = file.read()
        except FileNotFoundError:
            self.RESPONSE = b"HTTP/1.1 200 OK\r\nServer: socket server v0.1\r\nContent-Type: text/html\r\nContent-Length: 96\r\n\r\n<html><head><title>socket server</title></head><body>I've got your message</body></html>"

    def createDir(self, path):
        """디렉토리 생성"""
        try:
            if not os.path.exists(path):
                os.makedirs(path)
        except OSError:
            print("Error: Failed to create the directory.")

    def save_request(self, data):
        """클라이언트 요청을 파일로 저장"""
        now = datetime.now()
        filename = now.strftime("%Y-%m-%d-%H-%M-%S") + ".bin"
        filepath = os.path.join(self.DIR_PATH, filename)
        
        # 요청 데이터를 파일로 저장
        with open(filepath, 'wb') as file:
            file.write(data)
        print(f"Request saved as {filepath}")

    def save_image(self, content):
        """이미지 데이터 추출 및 저장"""
        image_data_pattern = b'Content-Type: image/(jpeg|png|jpg)\r\n\r\n(.*?)\r\n--'
        image_match = re.search(image_data_pattern, content, re.DOTALL)

        if image_match:
            image_data = image_match.group(2)
            image_filename = f"image_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
            image_path = os.path.join(self.DIR_PATH, image_filename)

            # 이미지 파일 저장
            with open(image_path, 'wb') as img_file:
                img_file.write(image_data)

            print(f"Image saved as {image_path}")
            return image_path
        return None

    def handle_request(self, clnt_sock):
        """클라이언트 요청 처리"""
        data = b""
        while True:
            try:
                chunk = clnt_sock.recv(self.bufsize)
                if not chunk:
                    break
                data += chunk
            except socket.timeout:
                print("Socket timeout. Ending connection.")
                break

        # 요청 데이터 파일로 저장
        self.save_request(data)

        # 요청 데이터에서 이미지 추출 및 저장
        saved_image_path = self.save_image(data)
        if saved_image_path:
            print(f"Saved image at: {saved_image_path}")

        return data

    def run(self, ip, port):
        """서버 실행"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((ip, port))
        self.sock.listen(10)
        print("Start the socket server...")
        print("\"Ctrl+C\" for stopping the server!\r\n")

        try:
            while True:
                # 클라이언트의 요청 대기
                clnt_sock, req_addr = self.sock.accept()
                clnt_sock.settimeout(5.0)  # 타임아웃 설정 (5초)
                print(f"Request from {req_addr}")

                # 클라이언트의 요청 처리
                request_data = self.handle_request(clnt_sock)

                # 응답 헤더에 Content-Length 설정
                response_with_length = self.RESPONSE
                if b'Content-Length' not in self.RESPONSE:
                    response_body_length = len(response_with_length.split(b'\r\n\r\n')[1])  # 헤더와 바디 분리
                    response_header = b"HTTP/1.1 200 OK\r\nServer: socket server v0.1\r\nContent-Type: text/html\r\n"
                    response_header += f"Content-Length: {response_body_length}\r\n\r\n".encode()
                    response_with_length = response_header + response_with_length.split(b'\r\n\r\n')[1]

                # 응답 전송
                clnt_sock.sendall(response_with_length)
                
                # 서버 소켓 닫기
                clnt_sock.close()
        except KeyboardInterrupt:
            print("\r\nStop the server...")
            self.sock.close()
        except Exception as e:
            print(f"An error occurred: {e}")
            self.sock.close()

if __name__ == "__main__":
    server = SocketServer()
    server.run("127.0.0.1", 8000)
