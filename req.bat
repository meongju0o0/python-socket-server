@Echo off

curl -v -F "author=1" ^
-F "title=curl 테스트" ^
-F "text=API curl로 작성된 AP 테스트 입력 입니다." ^
-F "created_date=2024-10-11T10:17:00+09:00" ^
-F "published_date=2024-10-11T10:17:00+09:00" ^
-F "image=@C:\Users\bl4an\Documents\college_lectures\모바일웹서비스프로젝트\python-socket-server\apple.jpg" ^
http://127.0.0.1:8000/api_root/Post/

pause