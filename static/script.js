const chatBox = document.getElementById("chatBox");
const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");

function addMessage(role, text, recipesData) {
  const wrap = document.createElement("div");
  wrap.className = `message ${role}`;

  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = role === "bot" ? "🍳" : "You";

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.innerHTML = text;

  if (recipesData && recipesData.length > 0) {
    const grid = document.createElement("div");
    grid.className = "recipes-grid";
    recipesData.forEach((r) => {
      const card = document.createElement("div");
      card.className = "recipe-card";
      card.onclick = () => window.open(r.sourceUrl, "_blank");

      const badges = [];
      if (r.vegan) badges.push(`<span class="badge vegan">Vegan</span>`);
      else if (r.vegetarian)
        badges.push(`<span class="badge veg">Vegetarian</span>`);
      if (r.glutenFree)
        badges.push(`<span class="badge gluten">Gluten-Free</span>`);
      if (r.dairyFree)
        badges.push(`<span class="badge dairy">Dairy-Free</span>`);

      const nutrition = Object.entries(r.nutrition || {})
        .map(([k, v]) => `${k}: ${v}`)
        .join(" · ");

      card.innerHTML = `
        <img src="${r.image}" alt="${r.title}" onerror="this.style.display='none'">
        <div class="card-body">
          <h3>${r.title}</h3>
          <div class="meta">⏱ ${r.readyInMinutes} min · 🍽 ${r.servings} servings</div>
          ${badges.length ? `<div class="badges">${badges.join("")}</div>` : ""}
          ${nutrition ? `<div class="nutrition">${nutrition}</div>` : ""}
        </div>
      `;
      grid.appendChild(card);
    });
    bubble.appendChild(grid);
  }

  wrap.appendChild(avatar);
  wrap.appendChild(bubble);
  chatBox.appendChild(wrap);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function addTyping() {
  const wrap = document.createElement("div");
  wrap.className = "message bot";
  wrap.id = "typing";
  wrap.innerHTML = `<div class="avatar">🍳</div><div class="bubble typing">Finding recipes...</div>`;
  chatBox.appendChild(wrap);
  chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendMessage() {
  const msg = userInput.value.trim();
  if (!msg) return;

  addMessage("user", msg);
  userInput.value = "";
  addTyping();

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: msg }),
    });
    const data = await res.json();
    document.getElementById("typing")?.remove();
    addMessage("bot", data.reply, data.recipes);
  } catch (err) {
    document.getElementById("typing")?.remove();
    addMessage("bot", "Something went wrong. Make sure Flask is running!");
  }
}

sendBtn.addEventListener("click", sendMessage);
userInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendMessage();
});
