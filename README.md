<div align="center">
VIETNAM NATIONAL UNIVERSITY, HO CHI MINH CITY
<br />
UNIVERSITY OF TECHNOLOGY
<br />
FACULTY OF COMPUTER SCIENCE AND ENGINEERING
<br />
<br />

[![N|Solid](https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/HCMUT_official_logo.png/238px-HCMUT_official_logo.png)](https://www.hcmut.edu.vn/vi)
<br />
<br />

**Computer Network / Semester 211**
<br/>
**Group 1**

</div>

# Project: VIDEO STREAMING APPLICATION

## Team members

| No. | Name             | Student ID | Email                          | Contact                                                                                                                                                                                                                     |
| :-: | ---------------- | :--------: | ------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|  1  | Võ Minh Toàn     |  1915570   | toan.vo4121@gmail.com          | [<img src="https://cdn-icons-png.flaticon.com/512/20/20673.png" align="left" width=20px/>][fb1] [<img src="https://cdn-icons-png.flaticon.com/512/733/733609.png" align="left" width=20px style="margin-left:5px" />][git1] |
|  2  | Đặng Hùng Cường  |  1912817   | cuong.danghcmut@hcmut.edu.vn   | [<img src="https://cdn-icons-png.flaticon.com/512/20/20673.png" align="left" width=20px/>][fb2] [<img src="https://cdn-icons-png.flaticon.com/512/733/733609.png" align="left" width=20px style="margin-left:5px" />][git2] |
|  3  | Nguyễn Đình Hiếu |  1913341   | hieu.nguyen190125@hcmut.edu.vn | [<img src="https://cdn-icons-png.flaticon.com/512/20/20673.png" align="left" width=20px/>][fb3] [<img src="https://cdn-icons-png.flaticon.com/512/733/733609.png" align="left" width=20px style="margin-left:5px" />][git3] |
|  4  | Nguyễn Hải Linh  |  1913944   | linh.nguyen1505@hcmut.edu.vn   | [<img src="https://cdn-icons-png.flaticon.com/512/20/20673.png" align="left" width=20px/>][fb4] [<img src="https://cdn-icons-png.flaticon.com/512/733/733609.png" align="left" width=20px style="margin-left:5px" />][git4] |

## Requirements
Đề bài được mô tả chi tiết trong file <>

## Languages & Tools

<img src="https://cdn4.iconfinder.com/data/icons/logos-and-brands/512/267_Python_logo-256.png" align="center" style="margin-left:10px;margin-bottom:5px;" width=70px/>

## Specification

### Description

- **Client.launcher**: Khởi chạy Client và giao diện application nơi ta gửi RTSP request và dùng để xem video
- **Client**: Hiện thực các button SETUP, PLAY, PAUSE, TEARDOWN cho application, giao tiếp với Server thông qua giao thức RTSP
- **Client2**: Tương tự như Client nhưng thêm các chức năng Extend như: DESCRIBE, STOP, thể hiện total time và remaining time của video, FORWARD, BACKWARD, tính toán các chỉ số gói tin.
- **Server**: Khởi tạo Server
- **ServerWorker**: Xử lý các Request từ Client gửi đến và phản hồi lại
- **RTPPacket**: Xử lý gói tin RTP
- **VideoStream**: Bao gồm các thông tin về video stream từ phía server tới client và xử lý video stream

### How to run

- Đầu tiên, khởi chạy Server với command sau:

```python
python Server.py <server_port>
```

với <server_port> là port để Server thiết lập RTSP connections. Port RTSP tiêu chuẩn là 554 nhưng trong Assignment này, ta cần dùng port lớn hơn 1024

- Sau đó, tạo một cửa sổ terminal mới và khởi chạy Client với command sau:

```python
python ClientLauncher.py <server_host> <server_port> <rtp_port> <video_file>
```

với <server_host> là địa chỉ IP của máy chạy Server, <server_port> trùng với command trước đó, <rtp_port> là port nhận RTP_packet, <video_file> là tên file video ta muốn xem (ví dụ trong Project là file movie.Mjpeg)

## Report
Báo cáo chi tiết project ở file <>

[fb1]: https://www.facebook.com/toanvo4121/
[fb2]: https://www.facebook.com/Cuongflorid/
[fb3]: https://www.facebook.com/kazami190125/
[fb4]: https://www.facebook.com/hailinh.nguyen.359126/
[git1]: https://github.com/toanvo4121
[git2]: https://github.com/CuongFlodric
[git3]: https://github.com/HandsOfGoddest
[git4]: https://github.com/Halee1505
