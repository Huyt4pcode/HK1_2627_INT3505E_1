# LAB 1: Thiết kế Resource cho Blog API

## 1. Xác định resources trong miền

- `users`
- `posts`
- `comments`
- `tags`
- `profile`
- `following`
- `followers`

---

## 2. Phân loại collection / item / sub-resource

### 2.1. Collection

```
/users
/posts
/tags
```

### 2.2. Item

```
/users/{user_id}
/posts/{post_id}
/tags/{tag_id}
```

### 2.3. Sub-resource

```
/users/{user_id}/profile
/users/{user_id}/posts
/users/{user_id}/following
/users/{user_id}/followers

/posts/{post_id}/comments
/posts/{post_id}/comments/{comment_id}
/posts/{post_id}/tags

/tags/{tag_id}/posts
```

---

## 3. Vẽ sơ đồ cây endpoint và quyết định version segment

### 3.1. Version segment

```
/api/v1
```

Ví dụ:

```
/api/v1/users
/api/v1/posts
/api/v1/tags
```

### 3.2. Cây endpoint

```
/api/v1
│
├── /users
│   │
│   ├── GET
│   ├── POST
│   │
│   └── /{user_id}
│       │
│       ├── GET
│       ├── PUT
│       ├── PATCH
│       ├── DELETE
│       │
│       ├── /profile
│       │   ├── GET
│       │   └── PATCH
│       │
│       ├── /posts
│       │   └── GET
│       │
│       ├── /following
│       │   └── GET
│       │
│       └── /followers
│           └── GET
│
├── /posts
│   │
│   ├── GET
│   ├── POST
│   │
│   └── /{post_id}
│       │
│       ├── GET
│       ├── PUT
│       ├── PATCH
│       ├── DELETE
│       │
│       ├── /comments
│       │   │
│       │   ├── GET
│       │   ├── POST
│       │   │
│       │   └── /{comment_id}
│       │       ├── GET
│       │       ├── PATCH
│       │       └── DELETE
│       │
│       └── /tags
│           ├── GET
│           └── POST
│
└── /tags
    │
    ├── GET
    ├── POST
    │
    └── /{tag_id}
        │
        ├── GET
        └── /posts
            └── GET
```

---

## 4. Gợi ý thiết kế API

- Dùng tiền tố `/api/v1` để đảm bảo versioning rõ ràng.
- Collection dùng để lấy danh sách hoặc tạo mới.
- Item dùng để thao tác với một đối tượng cụ thể.
- Sub-resource dùng để tách chức năng phụ thuộc vào resource gốc.
- Việc tách rõ resource giúp API dễ mở rộng và dễ bảo trì.
