from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint


app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes


SWAGGER_URL = "/api/docs"
API_URL = "/static/masterblog.json"

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={"app_name": "Masterblog API"}
)

app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)


POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


@app.route('/api/posts', methods=['GET'])
def get_posts():
    sort_field = request.args.get("sort")      # "title" or "content"
    direction = request.args.get("direction")  # "asc" or "desc"

    # No sorting params -> behave exactly like before
    if not sort_field and not direction:
        return jsonify(POSTS), 200

    # Validate
    if sort_field not in ("title", "content"):
        return jsonify({"error": "Invalid sort field. Use 'title' or 'content'."}), 400
    if direction not in ("asc", "desc"):
        return jsonify({"error": "Invalid direction. Use 'asc' or 'desc'."}), 400

    reverse = (direction == "desc")

    sorted_posts = sorted(
        POSTS,
        key=lambda p: (p.get(sort_field) or "").lower(),
        reverse=reverse
    )

    return jsonify(sorted_posts), 200


@app.route('/api/posts', methods=['POST'])
def add_post():
    data = request.get_json(silent=True) or {}

    missing = []
    if not data.get("title"):
        missing.append("title")
    if not data.get("content"):
        missing.append("content")

    if missing:
        return jsonify({
            "error": "Missing required fields",
            "missing": missing
        }), 400

    new_id = max((p["id"] for p in POSTS), default=0) + 1
    new_post = {
        "id": int(new_id),
        "title": data["title"],
        "content": data["content"]
    }

    POSTS.append(new_post)
    return jsonify(new_post), 201


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    title_q = (request.args.get("title") or "").strip().lower()
    content_q = (request.args.get("content") or "").strip().lower()

    results = []
    for post in POSTS:
        title_text = (post.get("title") or "").lower()
        content_text = (post.get("content") or "").lower()

        title_ok = True if not title_q else (title_q in title_text)
        content_ok = True if not content_q else (content_q in content_text)

        if title_ok and content_ok:
            results.append(post)

    return jsonify(results), 200


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    for i, post in enumerate(POSTS):
        if post["id"] == post_id:
            POSTS.pop(i)
            return jsonify({
                "message": f"Post with id {post_id} has been deleted successfully."
            }), 200

    return jsonify({
        "error": "Post not found",
        "message": f"No post with id {post_id} was found."
    }), 404


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    data = request.get_json(silent=True) or {}

    for post in POSTS:
        if post["id"] == post_id:
            # both optional: keep old values if not provided
            if "title" in data and data["title"] is not None:
                post["title"] = data["title"]
            if "content" in data and data["content"] is not None:
                post["content"] = data["content"]

            return jsonify(post), 200

    return jsonify({
        "error": "Post not found",
        "message": f"No post with id {post_id} was found."
    }), 404


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
