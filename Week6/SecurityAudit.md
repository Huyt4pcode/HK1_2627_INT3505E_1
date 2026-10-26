# Kiểm toán bảo mật — API mạng xã hội

API xử lý thông tin đăng nhập, bearer token và nội dung do người dùng tạo. Bảng
dưới đây liệt kê các nguy cơ lộ dữ liệu tiềm ẩn và biện pháp kiểm soát cần áp dụng.

| # | Nguy cơ lộ dữ liệu | Rủi ro | Biện pháp kiểm soát đề xuất |
|---|---|---|---|
| 1 | Mật khẩu bị ghi lại trong log request, hệ thống tracing hoặc báo cáo lỗi của `POST /auth/login` | Kẻ tấn công chiếm quyền tài khoản nếu truy cập được log hoặc dữ liệu giám sát | Che hoặc loại bỏ trường mật khẩu trước khi ghi log; không ghi nội dung request thô của endpoint xác thực; giới hạn và kiểm tra việc truy cập log |
| 2 | Access token hoặc refresh token bị lộ trong log ứng dụng, URL, công cụ phân tích hoặc báo cáo sự cố | Kẻ tấn công có thể giả mạo người dùng cho đến khi token hết hạn hoặc bị thu hồi | Chỉ gửi token qua HTTPS trong header hoặc phần thân request; không đưa token vào URL; che token trong log; giới hạn thời hạn của access token |
| 3 | Refresh token bị sao chép hoặc sử dụng lại sau khi bị đánh cắp | Kẻ tấn công duy trì quyền truy cập và liên tục yêu cầu cấp token mới | Luân chuyển refresh token sau mỗi lần làm mới thành công; vô hiệu hóa token cũ; phát hiện việc sử dụng lại và thu hồi toàn bộ nhóm token liên quan |
| 4 | Dò tìm tài khoản thông qua khác biệt về lỗi đăng nhập hoặc thời gian phản hồi | Kẻ tấn công xác định được địa chỉ email đã đăng ký | Trả cùng một thông báo `401` chung cho email không tồn tại và mật khẩu sai; giữ hành vi phản hồi nhất quán và giới hạn tần suất thử |
| 5 | Bài đăng bị lộ do thiếu kiểm tra quyền hoặc quyền truy cập ở cấp đối tượng | Nội dung riêng tư, bị chặn hoặc bị hạn chế có thể xem được khi thay đổi `{id}` | Kiểm tra quyền và quy tắc hiển thị mỗi khi truy vấn bài đăng; trả `404` không tiết lộ thông tin đối với bài đăng người gọi không được phép xem |
| 6 | Cấp hoặc chấp nhận quá nhiều scope từ `requestedScopes` | Tài khoản hoặc ứng dụng bị xâm nhập có quyền vượt quá nhu cầu | Áp dụng nguyên tắc đặc quyền tối thiểu; chỉ cho phép scope được duyệt theo từng người dùng/ứng dụng; chỉ cấp scope được phép và trả về scope thực tế đã cấp |
| 7 | Phản hồi bài đăng hoặc lỗi chứa trường nhạy cảm của tài khoản hay hệ thống | Email, ghi chú kiểm duyệt, thông tin cơ sở dữ liệu, stack trace hoặc bí mật có thể bị lộ | Khai báo rõ schema phản hồi và danh sách trường được phép; dùng thông báo lỗi chung và mã request không nhạy cảm để tra cứu |
| 8 | Dữ liệu cá nhân và nội dung bài đăng bị lộ qua log vận hành hoặc bản sao lưu không được kiểm soát | Lượng lớn dữ liệu bị tiết lộ nếu hệ thống giám sát hoặc sao lưu bị truy cập trái phép | Thu thập ít dữ liệu nhất có thể; che hoặc giả danh hóa mã định danh và nội dung; mã hóa log và bản sao lưu; kiểm soát thời hạn lưu trữ và quyền truy cập |
| 9 | Thông tin đăng nhập hoặc token bị chặn khi truyền tải | Tài khoản và phiên đăng nhập bị xâm phạm | Bắt buộc dùng HTTPS/TLS cho mọi endpoint; từ chối HTTP không mã hóa trong môi trường production; cấu hình bảo mật truyền tải tại máy chủ biên |
| 10 | Thử đăng nhập hoặc làm mới token liên tục nhằm dò thông tin hoặc tiêu tốn tài nguyên | Tấn công nhồi thông tin đăng nhập, lạm dụng token hoặc từ chối dịch vụ | Giới hạn tần suất theo tài khoản và nguồn gửi; theo dõi hành vi đáng ngờ; trả `429` kèm giá trị `Retry-After` an toàn |

Không đưa mật khẩu, access token, refresh token hoặc dữ liệu cá nhân thật vào ví dụ,
tệp được commit, ảnh chụp màn hình hay kết quả kiểm thử.
