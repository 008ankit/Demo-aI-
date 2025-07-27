function showChat() {
  document.getElementById("landing-section").style.display = "none";
  document.getElementById("chatbox-section").style.display = "block";
}

let lastAmbiguousQuery = null;

async function sendMessage() {
  const input = document.getElementById("user-input");
  const msg = input.value.trim();
  if (!msg) return;

  const chatBox = document.getElementById("chat-messages");

  // Show user message
  const userMsg = document.createElement("div");
  userMsg.className = "user-message";
  userMsg.innerHTML = `<div class="message-content">${msg}</div>`;
  chatBox.appendChild(userMsg);
  input.value = "";
  chatBox.scrollTop = chatBox.scrollHeight;

  // Check if last AI message asked for recommendations
  const lastAiMsg = chatBox.querySelector(
    ".ai-message:last-child .message-content"
  );
  if (
    lastAiMsg &&
    lastAiMsg.textContent &&
    lastAiMsg.textContent.includes(
      "Would you like to see some product recommendations"
    )
  ) {
    // Find the last user message before the AI's question
    const userMessages = Array.from(
      chatBox.querySelectorAll(".user-message .message-content")
    );
    if (userMessages.length >= 2) {
      // The second last user message is the ambiguous query
      lastAmbiguousQuery = userMessages[userMessages.length - 2].textContent;
    } else if (userMessages.length === 1) {
      lastAmbiguousQuery = userMessages[0].textContent;
    }
  }

  // If user says yes and lastAmbiguousQuery exists, send explicit recommend query
  const yesWords = [
    "yes",
    "yes please",
    "sure",
    "ok",
    "okay",
    "please do",
    "show me",
    "show",
    "go ahead",
  ];
  if (lastAmbiguousQuery && yesWords.includes(msg.toLowerCase())) {
    await sendMessageWithQuery(lastAmbiguousQuery);
    lastAmbiguousQuery = null;
    return;
  }

  // Show loading message
  const loadingMsg = document.createElement("div");
  loadingMsg.className = "ai-message";
  loadingMsg.innerHTML = `<div class="message-content">🤖 Thinking...</div>`;
  chatBox.appendChild(loadingMsg);
  chatBox.scrollTop = chatBox.scrollHeight;

  // Simple keyword-based detection for product queries
  const productKeywords = [
    "buy",
    "price",
    "recommend",
    "suggest",
    "show me products",
    "list products",
    "best products",
    "top products",
    "find products",
    "give me products",
    "offer products",
    "buy products",
    "laptop",
    "phone",
    "mobile",
    "tv",
    "camera",
    "product",
    "headphone",
    "tablet",
    "earbud",
    "smartwatch",
    "shoes",
    "clothes",
    "jeans",
    "tshirt",
    "shirt",
    "dress",
    "fridge",
    "washing machine",
    "ac",
    "air conditioner",
    "refrigerator",
    "microwave",
    "oven",
    "mixer",
    "blender",
    "sofa",
    "bed",
    "furniture",
    "fan",
    "cooler",
    "monitor",
    "mouse",
    "keyboard",
    "speaker",
    "soundbar",
    "router",
    "printer",
    "projector",
    "gaming",
    "console",
    "ps5",
    "xbox",
    "nintendo",
    "tablet",
    "ipad",
    "macbook",
    "surface",
    "chromebook",
  ];
  const isProductQuery = productKeywords.some((kw) =>
    msg.toLowerCase().includes(kw)
  );

  try {
    let data;
    if (isProductQuery) {
      // Product search
      const response = await fetch(
        `http://127.0.0.1:8000/search?query=${encodeURIComponent(msg)}`
      );
      data = await response.json();
      loadingMsg.remove();
      if (data.ai_response) {
        displayAIResponse(data.ai_response, chatBox);
      } else if (data.products) {
        displayAIResponse(data, chatBox);
      } else {
        const errMsg = document.createElement("div");
        errMsg.className = "ai-message";
        errMsg.innerHTML = `<div class="message-content">🤖 No suggestions found.</div>`;
        chatBox.appendChild(errMsg);
      }
    } else {
      // General chat
      const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: msg }),
      });
      data = await response.json();
      loadingMsg.remove();
      if (data.products) {
        displayAIResponse(data, chatBox);
      } else {
        const aiMsg = document.createElement("div");
        aiMsg.className = "ai-message";
        aiMsg.innerHTML = `<div class="message-content">${
          data.response || data.error || "No response from AI."
        }</div>`;
        chatBox.appendChild(aiMsg);
      }
    }
  } catch (err) {
    loadingMsg.remove();
    const errMsg = document.createElement("div");
    errMsg.className = "ai-message";
    errMsg.innerHTML = `<div class="message-content" style="color: #ef4444;">❌ Error: Could not connect to backend.</div>`;
    chatBox.appendChild(errMsg);
  }

  chatBox.scrollTop = chatBox.scrollHeight;
}

// Helper to send a message with a specific query (used for confirmation flow)
async function sendMessageWithQuery(query) {
  const input = document.getElementById("user-input");
  const chatBox = document.getElementById("chat-messages");

  // Show user message
  const userMsg = document.createElement("div");
  userMsg.className = "user-message";
  userMsg.innerHTML = `<div class="message-content">${query}</div>`;
  chatBox.appendChild(userMsg);
  chatBox.scrollTop = chatBox.scrollHeight;

  // Show loading message
  const loadingMsg = document.createElement("div");
  loadingMsg.className = "ai-message";
  loadingMsg.innerHTML = `<div class="message-content">🤖 Thinking...</div>`;
  chatBox.appendChild(loadingMsg);
  chatBox.scrollTop = chatBox.scrollHeight;

  try {
    const response = await fetch(
      `http://127.0.0.1:8000/search?query=${encodeURIComponent(query)}`
    );
    const data = await response.json();
    loadingMsg.remove();
    if (data.ai_response) {
      displayAIResponse(data.ai_response, chatBox);
    } else if (data.products) {
      displayAIResponse(data, chatBox);
    } else {
      const errMsg = document.createElement("div");
      errMsg.className = "ai-message";
      errMsg.innerHTML = `<div class="message-content">🤖 No suggestions found.</div>`;
      chatBox.appendChild(errMsg);
    }
  } catch (err) {
    loadingMsg.remove();
    const errMsg = document.createElement("div");
    errMsg.className = "ai-message";
    errMsg.innerHTML = `<div class="message-content" style="color: #ef4444;">❌ Error: Could not connect to backend.</div>`;
    chatBox.appendChild(errMsg);
  }
  chatBox.scrollTop = chatBox.scrollHeight;
}

function displayAIResponse(data, container) {
  const aiMsg = document.createElement("div");
  aiMsg.className = "ai-message";

  const messageContent = document.createElement("div");
  messageContent.className = "message-content";

  // Check if we have structured product data
  if (data.products && Array.isArray(data.products)) {
    let content = "";
    if (data.intro) {
      content += `<strong>🤖 ${data.intro}</strong><br/><br/>`;
    } else {
      content += `<strong>🤖 Product Recommendations:</strong><br/><br/>`;
    }
    // Create product cards
    data.products.forEach((product, idx) => {
      const imageUrl =
        product.image ||
        `https://picsum.photos/300x200?random=${
          Math.abs(
            product.title.split("").reduce((a, b) => a + b.charCodeAt(0), 0)
          ) % 1000
        }`;

      content += `
        <div class="product-card-chat" style="margin-bottom: 16px; background: rgba(255,255,255,0.05); border-radius: 12px; overflow: hidden; border: 1px solid rgba(255,255,255,0.1);">
          <div style="display: flex; align-items: stretch;">
            <div style="width: 120px; height: 120px; flex-shrink: 0;">
                            <img src="${imageUrl}" alt="${
        product.title
      }" style="width: 100%; height: 100%; object-fit: cover; border-radius: 8px 0 0 8px;" onerror="this.src='https://picsum.photos/120x120?random=${
        Math.abs(
          product.title.split("").reduce((a, b) => a + b.charCodeAt(0), 0)
        ) % 1000
      }'">
            </div>
            <div style="flex: 1; padding: 16px;">
              <h4 style="margin: 0 0 8px 0; color: #f8fafc; font-size: 16px;">${
                product.title
              }</h4>
              <p style="margin: 0 0 4px 0; color: #3b82f6; font-weight: 600; font-size: 14px;">${
                product.price
              }</p>
              <p style="margin: 0 0 4px 0; color: #fbbf24; font-size: 14px;">⭐ ${
                product.rating
              }</p>
              <p style="margin: 0; color: #94a3b8; font-size: 12px; line-height: 1.4;">${
                product.review
              }</p>
              <button class='fav-btn' onclick='addToWishlistFromCard(${JSON.stringify(
                product
              )})'>Add to Fav</button>
            </div>
          </div>
        </div>
      `;
    });

    messageContent.innerHTML = content;
  } else if (data.fallback_text) {
    // Fallback for text-only responses
    messageContent.innerHTML = `<strong>🤖 AI Response:</strong><br/><br/>${data.fallback_text}`;
  } else if (data.response) {
    // General info text answer
    messageContent.innerHTML = `<span>🤖 ${data.response}</span>`;
  } else {
    // Handle error cases
    messageContent.textContent = data.error || "No suggestions available.";
  }

  aiMsg.appendChild(messageContent);
  container.appendChild(aiMsg);

  // Save search history if we have products (non-intrusive addition)
  if (
    data.products &&
    Array.isArray(data.products) &&
    data.products.length > 0
  ) {
    const firstProduct = data.products[0];
    const searchQuery =
      container.querySelector(".user-message:last-child .message-content")
        ?.textContent || "Product Search";
    saveSearchHistory({
      query: searchQuery,
      price: firstProduct.price || "",
      rating: firstProduct.rating || "",
      source: data.source || firstProduct.dataset || "Dataset",
      time: Date.now(),
    });
  }
}

function updateProductSession(productName) {
  const list = document.getElementById("session-list");
  const newItem = document.createElement("li");
  newItem.textContent = productName;
  if (
    list.children[0] &&
    list.children[0].textContent === "No recent products"
  ) {
    list.innerHTML = ""; // clear placeholder
  }
  list.prepend(newItem);
}

function updatePriceInsight(low, avg, high) {
  document.getElementById("lowest-price").textContent = `$${low}`;
  document.getElementById("avg-price").textContent = `$${avg}`;
  document.getElementById("highest-price").textContent = `$${high}`;
}

function updateComparison(prodA, prodB) {
  document.getElementById("prod-a-price").textContent = `$${prodA.price}`;
  document.getElementById("prod-b-price").textContent = `$${prodB.price}`;
  document.getElementById("prod-a-rating").textContent = prodA.rating;
  document.getElementById("prod-b-rating").textContent = prodB.rating;
  document.getElementById("prod-a-stock").textContent = prodA.stock;
  document.getElementById("prod-b-stock").textContent = prodB.stock;
}

let isLogin = true;

function toggleAuth(show) {
  if (show) {
    isLoginMode = true;
    document.getElementById("modal-title").textContent = "Login";
    document.getElementById("toggle-text").textContent =
      "Don't have an account?";
    document.querySelector("#auth-modal a").textContent = "Sign up";
    document.getElementById("auth-username").value = "";
    document.getElementById("auth-password").value = "";
    document.getElementById("auth-fullname").style.display = "none";
    document.getElementById("auth-email").style.display = "none";
  }
  document.getElementById("auth-modal").style.display = show ? "flex" : "none";
  document.getElementById("auth-message").textContent = "";
}

function switchAuthMode() {
  isLoginMode = !isLoginMode;
  document.getElementById("modal-title").textContent = isLoginMode
    ? "Login"
    : "Sign Up";
  document.getElementById("toggle-text").textContent = isLoginMode
    ? "Don't have an account?"
    : "Already have an account?";
  document.querySelector("#auth-modal a").textContent = isLoginMode
    ? "Sign up"
    : "Login";
  document.getElementById("auth-message").textContent = "";
  document.getElementById("auth-username").value = "";
  document.getElementById("auth-password").value = "";
  document.getElementById("auth-fullname").value = "";
  document.getElementById("auth-email").value = "";
  document.getElementById("auth-fullname").style.display = isLoginMode
    ? "none"
    : "block";
  document.getElementById("auth-email").style.display = isLoginMode
    ? "none"
    : "block";
}

function openSignupModal() {
  isLoginMode = false;
  document.getElementById("auth-modal").style.display = "flex";
  document.getElementById("modal-title").textContent = "Sign Up";
  document.getElementById("toggle-text").textContent =
    "Already have an account?";
  document.querySelector("#auth-modal a").textContent = "Login";
  document.getElementById("auth-message").textContent = "";
  document.getElementById("auth-username").value = "";
  document.getElementById("auth-password").value = "";
  document.getElementById("auth-fullname").value = "";
  document.getElementById("auth-email").value = "";
  document.getElementById("auth-fullname").style.display = "block";
  document.getElementById("auth-email").style.display = "block";
}

const authSubmitBtn = document.getElementById("auth-submit-btn");
if (authSubmitBtn) {
  authSubmitBtn.onclick = async function () {
    const username = document.getElementById("auth-username").value.trim();
    const password = document.getElementById("auth-password").value.trim();
    const fullname = document.getElementById("auth-fullname").value.trim();
    const email = document.getElementById("auth-email").value.trim();
    const msg = document.getElementById("auth-message");
    if (isLoginMode) {
      if (!username || !password) {
        msg.textContent = "Please enter both fields.";
        msg.style.color = "red";
        return;
      }
    } else {
      if (!fullname || !email || !username || !password) {
        msg.textContent = "Please fill all fields.";
        msg.style.color = "red";
        return;
      }
    }
    msg.textContent = "";
    msg.style.color = "#fff";
    // Send to backend
    try {
      const endpoint = isLoginMode
        ? "http://localhost:8000/login"
        : "http://localhost:8000/signup";
      const payload = isLoginMode
        ? { username, password }
        : { fullname, email, username, password };
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      msg.textContent = data.message;
      msg.style.color = data.success ? "green" : "red";
      if (data.success) {
        setTimeout(() => {
          toggleAuth(false);
        }, 1200);
      }
    } catch (err) {
      msg.textContent = "Server error. Please try again.";
      msg.style.color = "red";
    }
  };
}

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function reloadToMain() {
  // Show the landing section and hide the chatbox
  document.getElementById("landing-section").style.display = "block";
  document.getElementById("chatbox-section").style.display = "none";

  // Scroll to top
  window.scrollTo({ top: 0, behavior: "smooth" });
}

async function searchProduct(query) {
  const res = await fetch(
    `http://127.0.0.1:8000/search?query=${encodeURIComponent(query)}`
  );
  const data = await res.json();
  const chatbox = document.getElementById("chatbox");
  chatbox.innerHTML = ""; // clear old

  if (data.source === "scraper") {
    const allProducts = [
      ...(data.results.flipkart || []),
      ...(data.results.amazon || []),
    ];
    allProducts.forEach(renderProductCard);
  } else if (data.source === "ai" && data.ai_response.products) {
    data.ai_response.products.forEach(renderProductCard);
  } else {
    const div = document.createElement("div");
    div.className = "ai-fallback";
    div.textContent = data.ai_response?.error || "No results found.";
    chatbox.appendChild(div);
  }
}

function renderProductCard(product) {
  const card = document.createElement("div");
  card.className = "product-card";

  card.innerHTML = `
    <img src="${product.image}" alt="Product Image" class="product-img" />
    <div class="product-details">
      <h3 class="product-title">${product.title}</h3>
      <p class="product-price">${product.price}</p>
      <p class="product-rating">⭐ ${product.rating}</p>
      <p class="product-review">${product.review}</p>
      <button class="fav-btn" onclick='addToWishlistFromCard(${JSON.stringify(
        product
      )})'>Add to Fav</button>
    </div>
  `;

  document.getElementById("chatbox").appendChild(card);
}

// Enable sending message with Enter key in chat input
const chatInput = document.getElementById("user-input");
if (chatInput) {
  chatInput.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
      event.preventDefault();
      sendMessage();
    }
  });
}

// Featured Products Data and Rendering
const featuredProducts = [
  {
    category: "Electronics",
    image:
      "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=400&q=80",
    title: "Samsung Galaxy M34 5G",
    price: "₹18,999",
    rating: "4.3",
    review: "Great camera quality, long battery life",
    link: "#",
  },
  {
    category: "Audio",
    image:
      "https://images.unsplash.com/photo-1519125323398-675f0ddb6308?auto=format&fit=crop&w=400&q=80",
    title: "Apple AirPods Pro",
    price: "₹19,999",
    rating: "4.5",
    review: "Excellent sound quality, noise cancellation",
    link: "#",
  },
  {
    category: "E-Readers",
    image:
      "https://images.unsplash.com/photo-1509395176047-4a66953fd231?auto=format&fit=crop&w=400&q=80",
    title: "Kindle Paperwhite",
    price: "₹10,999",
    rating: "4.8",
    review: "High-resolution display, long battery life",
    link: "#",
  },
  {
    category: "Audio",
    image:
      "https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=crop&w=400&q=80",
    title: "Sony WH-1000XM4",
    price: "₹24,990",
    rating: "4.7",
    review: "Industry-leading noise cancellation",
    link: "#",
  },
  // Additional cards for scrolling
  {
    category: "Wearables",
    image:
      "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=400&q=80",
    title: "Fitbit Versa 3",
    price: "₹15,999",
    rating: "4.2",
    review: "Accurate fitness tracking, long battery life",
    link: "#",
  },
  {
    category: "Laptops",
    image:
      "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=400&q=80",
    title: "Dell XPS 13",
    price: "₹99,999",
    rating: "4.6",
    review: "Sleek design, powerful performance",
    link: "#",
  },
  {
    category: "Smart Home",
    image:
      "https://images.unsplash.com/photo-1519125323398-675f0ddb6308?auto=format&fit=crop&w=400&q=80",
    title: "Amazon Echo Dot (4th Gen)",
    price: "₹3,999",
    rating: "4.4",
    review: "Great sound, smart assistant integration",
    link: "#",
  },
  {
    category: "Photography",
    image:
      "https://images.unsplash.com/photo-1509395176047-4a66953fd231?auto=format&fit=crop&w=400&q=80",
    title: "Canon EOS 1500D",
    price: "₹32,999",
    rating: "4.5",
    review: "Excellent entry-level DSLR",
    link: "#",
  },
];

function renderFeaturedProducts() {
  const container = document.getElementById("featured-products-cards");
  if (!container) return;
  container.innerHTML = featuredProducts
    .map(
      (product) => `
    <div class="product-card-featured">
      <span class="product-category-badge">${product.category}</span>
      <img src="${product.image}" alt="${
        product.title
      }" class="product-img-featured" />
      <div class="product-details-featured">
        <h3 class="product-title-featured">${product.title}</h3>
        <p class="product-price-featured">${product.price}</p>
        <p class="product-rating-featured">⭐ ${product.rating}</p>
        <p class="product-review-featured">${product.review}</p>
        <button class='fav-btn' onclick='addToWishlistFromCard(${JSON.stringify(
          product
        )})'>Add to Fav</button>
      </div>
    </div>
  `
    )
    .join("");
}

// Call on page load
renderFeaturedProducts();

// --- Scroll-to-end for featured products: show 'More' button ---
(function () {
  const container = document.getElementById("featured-products-cards");
  const moreBtn = document.getElementById("more-products-btn");
  if (!container || !moreBtn) return;
  container.addEventListener("scroll", function () {
    const threshold = 10;
    if (
      container.scrollLeft + container.clientWidth >=
      container.scrollWidth - threshold
    ) {
      moreBtn.style.display = "block";
    } else {
      moreBtn.style.display = "none";
    }
  });
})();

// Wishlist & Price Alerts stubs
function addToWishlist(product) {
  let wishlist = JSON.parse(localStorage.getItem("wishlist") || "[]");
  if (!wishlist.some((item) => item.title === product.title)) {
    wishlist.push(product);
    localStorage.setItem("wishlist", JSON.stringify(wishlist));
    alert("Added to wishlist: " + product.title);
  } else {
    alert("Product already in wishlist: " + product.title);
  }
}

function addToWishlistFromCard(product) {
  addToWishlist(product);
}

function removeFromWishlist(productId) {
  // TODO: Implement removing product from wishlist
  alert("Removed from wishlist: " + productId);
}

function checkPriceAlerts() {
  // TODO: Implement price drop alert logic
  alert("Checking price alerts...");
}

// --- Search History Helper (for use in other pages) ---
function saveSearchHistory(entry) {
  if (!entry || !entry.query) return;
  let history = [];
  try {
    history = JSON.parse(localStorage.getItem("searchHistory") || "[]");
  } catch (e) {
    history = [];
  }
  // Remove duplicates (same query, price, rating, source)
  history = history.filter(
    (item) =>
      !(
        item.query === entry.query &&
        item.price === entry.price &&
        item.rating === entry.rating &&
        item.source === entry.source
      )
  );
  history.push({
    query: entry.query,
    price: entry.price || "",
    rating: entry.rating || "",
    source: entry.source || "",
    time: entry.time || Date.now(),
  });
  // Limit to last 30 entries
  if (history.length > 30) history = history.slice(history.length - 30);
  localStorage.setItem("searchHistory", JSON.stringify(history));
}

document.addEventListener("DOMContentLoaded", function () {
  renderFeaturedProducts();

  // Dashboard charts (mock data)
  if (window.Chart) {
    // Line chart: Price trend
    const ctxLine = document.getElementById("dashboardLineChart");
    if (ctxLine) {
      new Chart(ctxLine, {
        type: "line",
        data: {
          labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
          datasets: [
            {
              label: "Price Trend",
              data: [18999, 18500, 19200, 18800, 19100, 18700, 19000],
              borderColor: "#60a5fa",
              backgroundColor: "rgba(96,165,250,0.15)",
              tension: 0.4,
              fill: true,
              pointRadius: 3,
              pointBackgroundColor: "#2563eb",
            },
          ],
        },
        options: {
          plugins: { legend: { display: false } },
          scales: {
            x: { display: true, grid: { display: false } },
            y: {
              display: true,
              grid: { color: "#23234a" },
              beginAtZero: false,
            },
          },
        },
      });
    }
    // Bar chart: Category distribution
    const ctxBar = document.getElementById("dashboardBarChart");
    if (ctxBar) {
      new Chart(ctxBar, {
        type: "bar",
        data: {
          labels: ["Phones", "Audio", "Laptops", "Wearables", "Smart Home"],
          datasets: [
            {
              label: "Products",
              data: [12, 8, 6, 5, 4],
              backgroundColor: [
                "#60a5fa",
                "#818cf8",
                "#fbbf24",
                "#34d399",
                "#f472b6",
              ],
              borderRadius: 6,
            },
          ],
        },
        options: {
          plugins: { legend: { display: false } },
          scales: {
            x: { display: true, grid: { display: false } },
            y: { display: true, grid: { color: "#23234a" }, beginAtZero: true },
          },
        },
      });
    }
  }
});
