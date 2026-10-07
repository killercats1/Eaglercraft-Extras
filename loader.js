/*
client json loader
(c) 2025: x8r and the eaglercraft extras team
modified 2026 by killercats1
licensed under gnu gpl v3

https://www.gnu.org/licenses/gpl-3.0.en.html
https://github.com/killercats1/VOXEL-SANDBOX
*/

// set up globals
let res;
let data;

// get doms
const clientsList = document.getElementById("clients");

// get json
async function getJSON(v) {
  res = await fetch(`assets/json/${v}.json`);
  data = await res.json();
}

// now load clients and append children
function loadClients(v) {
  getJSON(v)
    .then(() => {
      console.log(`Array: ${data}`);
    })
    .then(() => {
      data.forEach((data) => {
        // create new elements
        const newClient = document.createElement("li");
        const newTitle = document.createElement("h1");
        const newVersion = document.createElement("p");
        const newLink = document.createElement("a");
        const newIcon = document.createElement("img");
        const newPlaybtn = document.createElement("img");
        const newAuthor = document.createElement("p");

        // set attributes
        newClient.setAttribute("id", "client");
        newTitle.setAttribute("id", "title");
        newVersion.setAttribute("id", "ver");
        newLink.setAttribute("id", "link");
        newIcon.setAttribute("id", "icon");
        newPlaybtn.setAttribute("id", "playbtn");
        newAuthor.setAttribute("id", "ver");

        // update content
        newTitle.textContent = data.name;
        newVersion.textContent = `Version: ${data.version}`;
        newAuthor.textContent = `Author: ${data.author}`;
        newLink.href = data.url;
        newIcon.src = data.icon;

        // move elements into list
        clientsList.appendChild(newClient);
        newClient.appendChild(newIcon);
        newClient.appendChild(newTitle);
        newClient.appendChild(newVersion);
        newClient.appendChild(newAuthor);
        newIcon.appendChild(newLink);
        newClient.appendChild(newLink);
        newLink.appendChild(newPlaybtn);
      });
    });
}

// pick the client list from the page name, e.g. 1.12.html -> 1.12
const page = window.location.pathname.split("/").pop().replace(".html", "");
loadClients(/^(1\.\d+|classic|beta)$/.test(page) ? page : "1.3");
