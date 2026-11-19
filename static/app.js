"use strict";

const list = document.getElementById("list");
const form = document.getElementById("add-form");
const input = document.getElementById("title");
const summary = document.getElementById("summary");
const empty = document.getElementById("empty");
const message = document.getElementById("message");

function showMessage(text) {
  message.textContent = text;
  message.hidden = !text;
}

async function request(path, options) {
  const response = await fetch(path, options);
  if (!response.ok) {
    let detail = "Request failed (" + response.status + ").";
    try {
      const body = await response.json();
      if (body.error) detail = body.error.charAt(0).toUpperCase() + body.error.slice(1) + ".";
    } catch (_) {
      /* response had no JSON body */
    }
    throw new Error(detail);
  }
  return response.status === 204 ? null : response.json();
}

function renderTask(task) {
  const item = document.createElement("li");
  item.className = "task" + (task.done ? " done" : "");

  const check = document.createElement("button");
  check.type = "button";
  check.className = "check";
  check.disabled = task.done;
  check.textContent = task.done ? "\u2713" : "";
  check.setAttribute("aria-label", "Mark \"" + task.title + "\" as done");
  check.addEventListener("click", () => run(() => request("/tasks/" + task.id, { method: "PATCH" })));

  const title = document.createElement("span");
  title.className = "title";
  title.textContent = task.title;

  const remove = document.createElement("button");
  remove.type = "button";
  remove.className = "remove";
  remove.textContent = "Delete";
  remove.setAttribute("aria-label", "Delete \"" + task.title + "\"");
  remove.addEventListener("click", () => run(() => request("/tasks/" + task.id, { method: "DELETE" })));

  item.append(check, title, remove);
  return item;
}

async function refresh() {
  const tasks = await request("/tasks");
  list.replaceChildren(...tasks.map(renderTask));
  const done = tasks.filter((t) => t.done).length;
  summary.textContent = tasks.length ? done + " of " + tasks.length + " done" : "";
  empty.hidden = tasks.length > 0;
}

async function run(action) {
  try {
    showMessage("");
    await action();
    await refresh();
  } catch (err) {
    showMessage(err.message);
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const title = input.value.trim();
  if (!title) {
    showMessage("Enter a task title.");
    return;
  }
  run(async () => {
    await request("/tasks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title }),
    });
    input.value = "";
    input.focus();
  });
});

run(refresh);
