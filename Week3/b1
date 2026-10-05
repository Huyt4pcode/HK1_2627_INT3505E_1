from __future__ import annotations

from flask import Flask, jsonify, request

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

posts = [
    {
        "id": 1,
        "title": "Giới thiệu về b1",
        "content": "Một blog cho phép người dùng đăng bài viết và bình luận.",
        "author_id": 1,
        "tags": ["api", "blog"],
    },
    {
        "id": 2,
        "title": "RESTful design cho resource",
        "content": "Tách resource thành collection, item và sub-resource để dễ mở rộng.",
        "author_id": 2,
        "tags": ["rest", "design"],
    },
]

comments = {
    1: [
        {"id": 1, "post_id": 1, "author_id": 2, "message": "Bài viết rất rõ ràng."},
        {"id": 2, "post_id": 1, "author_id": 3, "message": "Cảm ơn bạn đã chia sẻ."},
    ],
    2: [{"id": 1, "post_id": 2, "author_id": 1, "message": "Mô hình này rất dễ triển khai."}],
}

users = {
    1: {"id": 1, "name": "Alice"},
    2: {"id": 2, "name": "Bob"},
    3: {"id": 3, "name": "Carol"},
}


def get_post_by_id(post_id):
    for post in posts:
        if post["id"] == post_id:
            return post
    return None


def get_comment_by_id(post_id, comment_id):
    for comment in comments.get(post_id, []):
        if comment["id"] == comment_id:
            return comment
    return None


@app.get("/")
def home():
    return jsonify({
        "message": "b1 is running",
        "version": "v1",
        "resources": [
            "/api/v1/posts",
            "/api/v1/posts/<post_id>",
            "/api/v1/posts/<post_id>/comments",
            "/api/v1/users/<user_id>/posts",
            "/api/v1/tags/<tag>/posts",
        ],
    })


@app.get("/api/v1/posts")
def get_posts():
    payload = []
    for post in posts:
        payload.append({
            "id": post["id"],
            "title": post["title"],
            "content": post["content"],
            "author": users.get(post["author_id"]),
            "tags": post["tags"],
            "comments": comments.get(post["id"], []),
        })
    return jsonify(payload)


@app.post("/api/v1/posts")
def create_post():
    data = request.get_json(silent=True) or {}
    title = data.get("title")
    content = data.get("content")
    author_id = data.get("author_id")
    tags = data.get("tags", [])

    if not title or not content or not author_id:
        return jsonify({"error": "title, content and author_id are required"}), 400

    new_post = {
        "id": max((post["id"] for post in posts), default=0) + 1,
        "title": title,
        "content": content,
        "author_id": author_id,
        "tags": tags,
    }
    posts.append(new_post)
    comments.setdefault(new_post["id"], [])
    return jsonify({
        "id": new_post["id"],
        "title": new_post["title"],
        "content": new_post["content"],
        "author": users.get(author_id),
        "tags": new_post["tags"],
    }), 201


@app.get("/api/v1/posts/<int:post_id>")
def get_post(post_id):
    post = get_post_by_id(post_id)
    if post is None:
        return jsonify({"error": "Post not found"}), 404

    return jsonify({
        "id": post["id"],
        "title": post["title"],
        "content": post["content"],
        "author": users.get(post["author_id"]),
        "tags": post["tags"],
        "comments": comments.get(post_id, []),
    })


@app.put("/api/v1/posts/<int:post_id>")
def update_post(post_id):
    post = get_post_by_id(post_id)
    if post is None:
        return jsonify({"error": "Post not found"}), 404

    data = request.get_json(silent=True) or {}
    post["title"] = data.get("title", post["title"])
    post["content"] = data.get("content", post["content"])
    post["author_id"] = data.get("author_id", post["author_id"])
    post["tags"] = data.get("tags", post["tags"])
    return jsonify(post)


@app.patch("/api/v1/posts/<int:post_id>")
def patch_post(post_id):
    post = get_post_by_id(post_id)
    if post is None:
        return jsonify({"error": "Post not found"}), 404

    data = request.get_json(silent=True) or {}
    for key in ["title", "content", "author_id", "tags"]:
        if key in data:
            post[key] = data[key]
    return jsonify(post)


@app.delete("/api/v1/posts/<int:post_id>")
def delete_post(post_id):
    post = get_post_by_id(post_id)
    if post is None:
        return jsonify({"error": "Post not found"}), 404

    posts[:] = [item for item in posts if item["id"] != post_id]
    comments.pop(post_id, None)
    return jsonify({"message": f"Post {post_id} deleted"})


@app.get("/api/v1/posts/<int:post_id>/comments")
def get_comments(post_id):
    if get_post_by_id(post_id) is None:
        return jsonify({"error": "Post not found"}), 404
    return jsonify(comments.get(post_id, []))


@app.post("/api/v1/posts/<int:post_id>/comments")
def create_comment(post_id):
    post = get_post_by_id(post_id)
    if post is None:
        return jsonify({"error": "Post not found"}), 404

    data = request.get_json(silent=True) or {}
    author_id = data.get("author_id")
    message = data.get("message")
    if not author_id or not message:
        return jsonify({"error": "author_id and message are required"}), 400

    comment_list = comments.setdefault(post_id, [])
    new_comment = {
        "id": max((item["id"] for item in comment_list), default=0) + 1,
        "post_id": post_id,
        "author_id": author_id,
        "message": message,
    }
    comment_list.append(new_comment)
    return jsonify(new_comment), 201


@app.get("/api/v1/posts/<int:post_id>/comments/<int:comment_id>")
def get_comment(post_id, comment_id):
    if get_post_by_id(post_id) is None:
        return jsonify({"error": "Post not found"}), 404

    comment = get_comment_by_id(post_id, comment_id)
    if comment is None:
        return jsonify({"error": "Comment not found"}), 404
    return jsonify(comment)


@app.get("/api/v1/users/<int:user_id>/posts")
def get_user_posts(user_id):
    if user_id not in users:
        return jsonify({"error": "User not found"}), 404

    user_posts = [post for post in posts if post["author_id"] == user_id]
    return jsonify(user_posts)


@app.get("/api/v1/tags/<string:tag>/posts")
def get_tag_posts(tag):
    tag_posts = [post for post in posts if tag.lower() in [item.lower() for item in post["tags"]]]
    return jsonify(tag_posts)


if __name__ == "__main__":
    app.run(debug=True)
