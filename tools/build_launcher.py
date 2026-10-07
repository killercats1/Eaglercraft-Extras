"""Build launcher.html: a single, self-contained VOXEL-SANDBOX launcher file.

Run from the repo root after changing a client list in assets/json/:

    python3 tools/build_launcher.py

The launcher embeds the site's fonts, images and client lists, so it opens
from a downloaded file. Clients themselves are played from (or downloaded
from) the GitHub Pages site, and when online the launcher refreshes its
client lists from the site so it never goes stale.
"""

import base64
import json
import pathlib

SITE = "https://killercats1.github.io/VOXEL-SANDBOX/"
ROOT = pathlib.Path(__file__).resolve().parent.parent
CATEGORIES = [
    ("classic", "Classic"),
    ("beta", "Beta"),
    ("1.3", "1.3"),
    ("1.5", "1.5"),
    ("1.8", "1.8"),
    ("1.9", "1.9"),
    ("1.11", "1.11"),
    ("1.12", "1.12"),
]
MIME = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".webp": "image/webp",
    ".woff2": "font/woff2",
    ".otf": "font/otf",
}


def data_uri(rel):
    path = ROOT / rel
    return "data:%s;base64,%s" % (
        MIME[path.suffix],
        base64.b64encode(path.read_bytes()).decode(),
    )


def main():
    lists = {}
    for key, _ in CATEGORIES:
        lists[key] = json.loads((ROOT / "assets/json" / f"{key}.json").read_text("utf-8"))

    html = TEMPLATE
    for name, value in {
        "__SITE__": SITE,
        "__CATEGORIES__": json.dumps(CATEGORIES),
        "__LISTS__": json.dumps(lists),
        "__FONT__": data_uri("assets/Minecraft.woff2"),
        "__FONT_BOLD__": data_uri("assets/mcbold.otf"),
        "__BTN__": data_uri("assets/btn-minecraft.png"),
        "__BTN_HOVER__": data_uri("assets/btn-minecraft-hover.png"),
        "__PANO__": data_uri("assets/pano.png"),
        "__TITLE__": data_uri("assets/title.png"),
        "__ICON__": data_uri("assets/eaglercraftx.jpg"),
    }.items():
        html = html.replace(name, value)
    (ROOT / "launcher.html").write_text(html, "utf-8")
    print("wrote launcher.html (%d KB)" % (len(html) // 1024))


TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>VOXEL-SANDBOX Launcher</title>
<link rel="icon" href="__ICON__" />
<style>
  @font-face { font-family: mc; src: url("__FONT__"); }
  @font-face { font-family: mcbold; src: url("__FONT_BOLD__"); }
  * { box-sizing: border-box; font-family: mc, monospace; }
  html, body {
    margin: 0;
    min-height: 100%;
    color: white;
    background: #1d1d1d url("__PANO__") repeat-x fixed;
    background-size: cover;
    animation: pano 95s linear infinite;
  }
  @keyframes pano { from { background-position: 0; } to { background-position: calc(100vh / 144 * -820); } }
  body::before {
    content: ""; position: fixed; inset: 0; z-index: -1;
    backdrop-filter: blur(6px); background: rgba(0, 0, 0, 0.25);
  }
  main { max-width: 900px; margin: 0 auto; padding: 0 16px 48px; text-align: center; }
  .logo { width: min(560px, 100%); margin: -40px 0 -70px; }
  .note { color: yellow; text-shadow: 2px 2px 2px black; margin: 0 0 16px; }
  .note a { color: yellow; }
  h1 { font-family: mcbold, mc; font-weight: normal; text-shadow: 2px 2px 2px black; }
  .btn {
    display: inline-block; border: none; cursor: pointer; color: white;
    font-size: 18px; padding: 10px 20px; text-decoration: none;
    background: url("__BTN__"); background-size: 100% 100%;
    text-shadow: 2px 2px 0 #3f3f3f;
  }
  .btn:hover { background-image: url("__BTN_HOVER__"); color: #ffffa0; }
  .btn.active { outline: 3px solid white; }
  .btn:disabled { filter: brightness(0.6); cursor: default; }
  .tabs { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; margin-bottom: 20px; }
  .tabs .btn { min-width: 90px; }
  .client {
    display: flex; align-items: center; gap: 16px; text-align: left;
    padding: 10px; margin: 8px 0; background: rgba(0, 0, 0, 0.45);
    text-shadow: 2px 2px 2px rgba(0, 0, 0, 0.6);
  }
  .client:hover { outline: 3px solid #f0f0f0; background: rgba(0, 0, 0, 0.6); }
  .client img { width: 64px; height: 64px; flex: none; }
  .client .info { flex: 1; min-width: 0; }
  .client .name { font-size: 22px; }
  .client .meta { color: lightgray; font-size: 16px; margin-top: 4px; }
  .client .actions { display: flex; gap: 8px; flex-wrap: wrap; justify-content: flex-end; }
  .status { color: lightgray; font-size: 14px; min-height: 1.2em; }
  @media (max-width: 600px) {
    .client { flex-wrap: wrap; }
    .client .actions { width: 100%; justify-content: stretch; }
    .client .actions .btn { flex: 1; text-align: center; }
  }
</style>
</head>
<body>
<main>
  <img class="logo" src="__TITLE__" alt="VOXEL-SANDBOX Extras" />
  <p class="note">
    Pick a client and press Play, or Download it to play with no internet.
    Full site: <a href="__SITE__" target="_blank">__SITE__</a>
  </p>
  <div class="tabs" id="tabs"></div>
  <h1 id="heading"></h1>
  <div id="list"></div>
  <p class="status" id="status"></p>
</main>
<script>
"use strict";
const SITE = "__SITE__";
const CATEGORIES = __CATEGORIES__;
let lists = __LISTS__;
let current = null;

const tabs = document.getElementById("tabs");
const list = document.getElementById("list");
const heading = document.getElementById("heading");
const statusLine = document.getElementById("status");

function absolute(url) {
  return /^https?:/.test(url) ? url : SITE + url.split("/").map(encodeURIComponent).join("/");
}

function fileName(url) {
  return decodeURIComponent(url.split("/").pop());
}

async function download(client, button) {
  const url = absolute(client.url);
  const label = button.textContent;
  button.disabled = true;
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error("HTTP " + res.status);
    const total = Number(res.headers.get("content-length")) || 0;
    const reader = res.body.getReader();
    const chunks = [];
    let got = 0;
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      chunks.push(value);
      got += value.length;
      button.textContent = total ? Math.floor((got / total) * 100) + "%" : Math.round(got / 1048576) + " MB";
    }
    const link = document.createElement("a");
    link.href = URL.createObjectURL(new Blob(chunks, { type: "text/html" }));
    link.download = fileName(client.url);
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(link.href), 60000);
  } catch (err) {
    statusLine.textContent = "Couldn't download " + client.name + " here, opening it instead (" + err.message + ").";
    window.open(url, "_blank");
  } finally {
    button.textContent = label;
    button.disabled = false;
  }
}

function show(key) {
  current = key;
  const [, label] = CATEGORIES.find(([k]) => k === key);
  heading.textContent = label + " Clients";
  for (const b of tabs.children) b.classList.toggle("active", b.dataset.key === key);
  list.replaceChildren();
  for (const client of lists[key] || []) {
    const row = document.createElement("div");
    row.className = "client";

    const icon = document.createElement("img");
    icon.src = "__ICON__";
    icon.alt = "";

    const info = document.createElement("div");
    info.className = "info";
    const name = document.createElement("div");
    name.className = "name";
    name.textContent = client.name;
    const meta = document.createElement("div");
    meta.className = "meta";
    meta.textContent = "Version: " + client.version + " · Author: " + client.author;
    info.append(name, meta);

    const actions = document.createElement("div");
    actions.className = "actions";
    const play = document.createElement("a");
    play.className = "btn";
    play.textContent = "Play";
    play.href = absolute(client.url);
    play.target = "_blank";
    const dl = document.createElement("button");
    dl.className = "btn";
    dl.textContent = "Download";
    dl.addEventListener("click", () => download(client, dl));
    actions.append(play, dl);

    row.append(icon, info, actions);
    list.appendChild(row);
  }
}

for (const [key, label] of CATEGORIES) {
  const b = document.createElement("button");
  b.className = "btn";
  b.textContent = label;
  b.dataset.key = key;
  b.addEventListener("click", () => show(key));
  tabs.appendChild(b);
}
show("1.8");

// refresh the client lists from the live site so a downloaded launcher stays current
Promise.all(CATEGORIES.map(([key]) =>
  fetch(SITE + "assets/json/" + key + ".json", { cache: "no-store" })
    .then((r) => (r.ok ? r.json() : null))
    .then((data) => { if (Array.isArray(data)) lists[key] = data; })
    .catch(() => {})
)).then(() => show(current));
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
