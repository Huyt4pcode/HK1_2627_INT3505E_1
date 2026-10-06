# LAB 2: Error handler trả về problem+json

## Mục tiêu

Viết một Flask `error handler` để trả về lỗi theo chuẩn `application/problem+json` thay vì HTML mặc định của Flask.

## Yêu cầu

- Định nghĩa `ProblemError(Exception)`
- Dùng decorator `@app.errorhandler(ProblemError)`
- Dùng decorator `@app.errorhandler(HTTPException)`
- Dùng decorator `@app.errorhandler(Exception)` cho lỗi không dự đoán trước
- Trả về response JSON có các trường:
  - `type`
  - `title`
  - `detail`
  - `status`
  - `instance`
- Không lộ `stack trace` cho client
- Log error ở server-side bằng `app.logger.exception(...)`

---

## Ý nghĩa của chuẩn problem+json

`problem+json` là một định dạng chuẩn để mô tả lỗi của API theo kiểu:

```json
{
  "type": "about:blank",
  "title": "Resource not found",
  "detail": "Resource 999 does not exist.",
  "status": 404,
  "instance": "/resources/999"
}
```

Điều này rất hữu ích cho client (web, mobile, frontend) vì API trả về dữ liệu lỗi có cấu trúc rõ ràng, dễ parse.

---

## Ví dụ route

```python
@app.get("/resources/<int:resource_id>")
def get_resource(resource_id: int):
    resource = RESOURCES.get(resource_id)
    if resource is None:
        raise ProblemError(
            404,
            "Resource not found",
            f"Resource {resource_id} does not exist.",
            request.path,
        )
    return jsonify(resource)
```

Khi gọi:

```bash
curl localhost:5000/resources/999
```

Kết quả sẽ là:

```http
HTTP/1.1 404 NOT FOUND
Content-Type: application/problem+json
```

```json
{
  "type": "about:blank",
  "title": "Resource not found",
  "detail": "Resource 999 does not exist.",
  "status": 404,
  "instance": "/resources/999"
}
```

---

## Kiến thức liên quan

### 1. Flask error handler

```python
@app.errorhandler(ProblemError)
def handle_problem_error(error):
    return error.to_response()
```

Dùng để bắt các exception do ta định nghĩa.

### 2. HTTPException

`HTTPException` là lỗi chuẩn của Flask/Werkzeug dùng cho 404, 400, 405, ...

```python
@app.errorhandler(HTTPException)
def handle_http_exception(error):
    return make_problem_response(
        error.code or 500,
        error.name,
        error.description or "An error occurred.",
        request.path,
    )
```

### 3. Custom exception

```python
class ProblemError(Exception):
    pass
```

Ta có thể bổ sung các thuộc tính như `status`, `title`, `detail`, `instance` để tạo JSON phản hồi.

### 4. Logging

```python
app.logger.exception("Unhandled exception: %s", error)
```

Dùng để ghi lỗi ở server, nhưng không trả stack trace cho client.

---

## Kết luận

Lab 2 tập trung vào việc xây dựng API error handling theo chuẩn professional:

- truyền thông tin lỗi bằng JSON
- giữ đúng HTTP status code
- chuẩn hóa response cho client
- không làm lộ stack trace
- dễ mở rộng và quản lý trong dự án thực tế
