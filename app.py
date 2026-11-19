"""Simple task-list app (JSON API plus browser UI) used as a sample DevOps workload."""
import os
from itertools import count

from flask import Flask, jsonify, render_template, request

APP_VERSION = os.environ.get("APP_VERSION", "0.1.0")


def create_app() -> Flask:
    app = Flask(__name__)
    tasks: dict[int, dict] = {}
    ids = count(1)

    @app.get("/")
    def index():
        return render_template("index.html", version=APP_VERSION)

    @app.get("/health")
    def health():
        return jsonify(status="ok")

    @app.get("/version")
    def version():
        return jsonify(version=APP_VERSION)

    @app.get("/tasks")
    def list_tasks():
        return jsonify(list(tasks.values()))

    @app.post("/tasks")
    def create_task():
        data = request.get_json(silent=True) or {}
        title = str(data.get("title", "")).strip()
        if not title:
            return jsonify(error="title is required"), 400
        task_id = next(ids)
        tasks[task_id] = {"id": task_id, "title": title, "done": False}
        return jsonify(tasks[task_id]), 201

    @app.patch("/tasks/<int:task_id>")
    def complete_task(task_id: int):
        task = tasks.get(task_id)
        if task is None:
            return jsonify(error="not found"), 404
        task["done"] = True
        return jsonify(task)

    @app.delete("/tasks/<int:task_id>")
    def delete_task(task_id: int):
        if tasks.pop(task_id, None) is None:
            return jsonify(error="not found"), 404
        return "", 204

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))