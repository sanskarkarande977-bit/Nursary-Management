// =====================================================================
// GO GREEN - Frontend JavaScript
// Connects HTML interface to app.py and displays saved stock, sales & care info
// =====================================================================

let plantsData = {};
let cartData = [];
let salesData = [];

// Load saved plants, cart, and sales history when the page opens
window.onload = function () {
  loadData();
};

// Switch visible section when clicking one of the 8 menu buttons
function showSection(sectionName) {
  const sections = ["add", "view", "search", "update", "sell", "bill", "care", "exit"];
  for (let i = 0; i < sections.length; i++) {
    document.getElementById("section-" + sections[i]).classList.add("hidden");
  }

  document.getElementById("section-" + sectionName).classList.remove("hidden");

  // Highlight active menu button
  const buttons = document.querySelectorAll(".menu-btn");
  for (let i = 0; i < buttons.length; i++) {
    buttons[i].classList.remove("active");
    if (sections[i] === sectionName) {
      buttons[i].classList.add("active");
    }
  }

  hideMessage();

  if (sectionName === "bill") {
    document.getElementById("pending-bill-box").classList.remove("hidden");
    document.getElementById("final-receipt").classList.add("hidden");
  }

  loadData();
}

// Jump directly to a specific plant's Care Info card from the View All table
function openCareForPlant(plantName) {
  showSection("care");
  setTimeout(function () {
    const filter = document.getElementById("care-filter");
    filter.value = plantName;
    renderCareCards();
  }, 50);
}

// Show a green success or red error message at the top
function showMessage(text, isSuccess) {
  const box = document.getElementById("message-box");
  box.textContent = text;
  box.classList.remove("hidden", "success", "error");
  box.classList.add(isSuccess ? "success" : "error");
}

function hideMessage() {
  document.getElementById("message-box").classList.add("hidden");
}

// Fetch latest saved plants, cart, and sales history from Python backend
async function loadData() {
  try {
    const response = await fetch("/api/data");
    const data = await response.json();
    plantsData = data.plants;
    cartData = data.cart;
    salesData = data.sales || [];

    renderPlantsTable();
    renderDropdowns();
    renderCart();
    renderSalesHistory();
    renderCareCards();
  } catch (error) {
    showMessage("Cannot connect to Python server. Please run: python3.12 app.py", false);
  }
}

// Helper to create a table cell safely with text
function createCell(text, className) {
  const td = document.createElement("td");
  td.textContent = text;
  if (className) {
    td.className = className;
  }
  return td;
}

// Helper to add a billing row safely to a table body
function appendBillRow(tbody, item) {
  const row = document.createElement("tr");
  row.appendChild(createCell(item.name));
  row.appendChild(createCell(item.quantity));
  row.appendChild(createCell("₹" + item.price));
  row.appendChild(createCell("₹" + item.price * item.quantity));
  tbody.appendChild(row);
}

// Display all plants in Option 2 table
function renderPlantsTable() {
  const tbody = document.getElementById("plants-table-body");
  tbody.innerHTML = "";

  const plantNames = Object.keys(plantsData);
  document.getElementById("total-count").textContent = plantNames.length + " Plants";

  for (let i = 0; i < plantNames.length; i++) {
    const name = plantNames[i];
    const details = plantsData[name];
    const statusText = details.quantity > 0 ? "In Stock" : "Out of Stock";
    const statusClass = details.quantity > 0 ? "status-in" : "status-out";

    const row = document.createElement("tr");
    row.appendChild(createCell(i + 1));

    const nameCell = document.createElement("td");
    const strongName = document.createElement("strong");
    strongName.textContent = name;
    nameCell.appendChild(strongName);
    row.appendChild(nameCell);

    row.appendChild(createCell("₹" + details.price));
    row.appendChild(createCell(details.quantity + " pieces"));
    row.appendChild(createCell(statusText, statusClass));

    const actionCell = document.createElement("td");
    const careBtn = document.createElement("button");
    careBtn.className = "small-btn";
    careBtn.textContent = "View Care";
    careBtn.onclick = function () {
      openCareForPlant(name);
    };
    actionCell.appendChild(careBtn);
    row.appendChild(actionCell);

    tbody.appendChild(row);
  }
}

// Fill dropdowns in Option 4 (Update), Option 5 (Sell), and Option 7 (Care Filter)
function renderDropdowns() {
  const updateSelect = document.getElementById("update-select");
  const sellSelect = document.getElementById("sell-select");
  const careFilter = document.getElementById("care-filter");

  const previousUpdate = updateSelect.value;
  const previousSell = sellSelect.value;
  const previousCare = careFilter.value || "ALL";

  updateSelect.innerHTML = "";
  sellSelect.innerHTML = "";
  careFilter.innerHTML = "";

  const allOption = document.createElement("option");
  allOption.value = "ALL";
  allOption.textContent = "Show All Plants";
  careFilter.appendChild(allOption);

  const plantNames = Object.keys(plantsData);
  for (let i = 0; i < plantNames.length; i++) {
    const name = plantNames[i];
    const details = plantsData[name];

    const option1 = document.createElement("option");
    option1.value = name;
    option1.textContent = name + " (Stock: " + details.quantity + ")";
    updateSelect.appendChild(option1);

    const option2 = document.createElement("option");
    option2.value = name;
    option2.textContent = name + " - ₹" + details.price + " (Stock: " + details.quantity + ")";
    sellSelect.appendChild(option2);

    const option3 = document.createElement("option");
    option3.value = name;
    option3.textContent = name;
    careFilter.appendChild(option3);
  }

  if (previousUpdate && plantsData[previousUpdate]) {
    updateSelect.value = previousUpdate;
  }
  if (previousSell && plantsData[previousSell]) {
    sellSelect.value = previousSell;
  }
  if (previousCare === "ALL" || plantsData[previousCare]) {
    careFilter.value = previousCare;
  }
}

// Build a care info line (Water, Fertilizer, or Sunlight)
function createCareLine(label, value) {
  const line = document.createElement("p");
  line.className = "care-item";
  const strong = document.createElement("strong");
  strong.textContent = label + ": ";
  line.appendChild(strong);
  line.appendChild(document.createTextNode(value || "Not specified"));
  return line;
}

// Display Plant Care Information cards (Option 7)
function renderCareCards() {
  const container = document.getElementById("care-cards-container");
  const selected = document.getElementById("care-filter").value || "ALL";
  container.innerHTML = "";

  const plantNames = Object.keys(plantsData);
  for (let i = 0; i < plantNames.length; i++) {
    const name = plantNames[i];
    if (selected !== "ALL" && name !== selected) {
      continue;
    }

    const details = plantsData[name];
    const card = document.createElement("div");
    card.className = "care-card";

    const header = document.createElement("div");
    header.className = "care-card-header";

    const title = document.createElement("h3");
    title.textContent = name;
    const tag = document.createElement("span");
    tag.className = "care-price-tag";
    tag.textContent = "₹" + details.price + " | " + details.quantity + " pcs";

    header.appendChild(title);
    header.appendChild(tag);
    card.appendChild(header);

    card.appendChild(createCareLine("💧 Water Required", details.water));
    card.appendChild(createCareLine("🌱 Fertilizer Used", details.fertilizer));
    card.appendChild(createCareLine("☀️ Sunlight Required", details.sunlight));

    container.appendChild(card);
  }
}

// Display current customer cart in Sell & Generate Bill tabs
function renderCart() {
  const miniBox = document.getElementById("mini-cart-box");
  const miniList = document.getElementById("mini-cart-list");
  const cartBody = document.getElementById("cart-table-body");
  const statusText = document.getElementById("cart-status-text");

  miniList.innerHTML = "";
  cartBody.innerHTML = "";

  if (cartData.length === 0) {
    miniBox.classList.add("hidden");
    statusText.textContent = "No plants in current bill. Use '5. Sell Plant' first.";
    return;
  }

  miniBox.classList.remove("hidden");
  statusText.textContent = "Items ready for customer bill:";

  for (let i = 0; i < cartData.length; i++) {
    const item = cartData[i];
    const total = item.price * item.quantity;

    const li = document.createElement("li");
    li.textContent = item.name + " × " + item.quantity + " = ₹" + total;
    miniList.appendChild(li);

    appendBillRow(cartBody, item);
  }
}

// Display saved sales history loaded from JSON file
function renderSalesHistory() {
  const salesBody = document.getElementById("sales-table-body");
  const emptyText = document.getElementById("sales-empty-text");
  const salesTable = document.getElementById("sales-table");
  const badge = document.getElementById("sales-total-badge");

  salesBody.innerHTML = "";

  if (salesData.length === 0) {
    emptyText.classList.remove("hidden");
    salesTable.classList.add("hidden");
    badge.textContent = "Total Sold: ₹0";
    return;
  }

  emptyText.classList.add("hidden");
  salesTable.classList.remove("hidden");

  let revenue = 0;
  for (let i = salesData.length - 1; i >= 0; i--) {
    const sale = salesData[i];
    revenue = revenue + sale.total;

    const row = document.createElement("tr");
    row.appendChild(createCell(sale.name));
    row.appendChild(createCell(sale.quantity));
    row.appendChild(createCell("₹" + sale.price));
    row.appendChild(createCell("₹" + sale.total));
    row.appendChild(createCell(sale.date || ""));
    salesBody.appendChild(row);
  }

  badge.textContent = "Total Sold: ₹" + revenue;
}

// Option 1: Add New Plant
async function addPlant() {
  const name = document.getElementById("add-name").value;
  const price = document.getElementById("add-price").value;
  const quantity = document.getElementById("add-qty").value;
  const water = document.getElementById("add-water").value;
  const fertilizer = document.getElementById("add-fertilizer").value;
  const sunlight = document.getElementById("add-sunlight").value;

  const response = await fetch("/api/add", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      name: name,
      price: price,
      quantity: quantity,
      water: water,
      fertilizer: fertilizer,
      sunlight: sunlight
    })
  });

  const result = await response.json();
  showMessage(result.message, result.ok);

  if (result.ok) {
    document.getElementById("add-name").value = "";
    document.getElementById("add-price").value = "";
    document.getElementById("add-qty").value = "";
    document.getElementById("add-water").value = "";
    document.getElementById("add-fertilizer").value = "";
    document.getElementById("add-sunlight").value = "";
    loadData();
  }
}

// Option 3: Search Plant (shows Price, Stock, Water, Fertilizer & Sunlight)
async function searchPlant() {
  const query = document.getElementById("search-input").value;
  const resultsBox = document.getElementById("search-results");
  resultsBox.innerHTML = "";

  const response = await fetch("/api/search", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query: query })
  });

  const result = await response.json();
  if (!result.ok) {
    showMessage(result.message, false);
    return;
  }

  hideMessage();

  if (result.matches.length === 0) {
    const msg = document.createElement("p");
    msg.className = "muted-text";
    msg.textContent = "No plant found matching '" + query + "'.";
    resultsBox.appendChild(msg);
    return;
  }

  for (let i = 0; i < result.matches.length; i++) {
    const plant = result.matches[i];
    const card = document.createElement("div");
    card.className = "search-card";

    const title = document.createElement("strong");
    title.textContent = plant.name + " — ₹" + plant.price + " (" + plant.quantity + " pieces)";
    card.appendChild(title);

    card.appendChild(createCareLine("💧 Water Required", plant.water));
    card.appendChild(createCareLine("🌱 Fertilizer Used", plant.fertilizer));
    card.appendChild(createCareLine("☀️ Sunlight Required", plant.sunlight));

    resultsBox.appendChild(card);
  }
}

// Option 4: Update Plant Stock
async function updateStock() {
  const name = document.getElementById("update-select").value;
  const quantity = document.getElementById("update-qty").value;

  const response = await fetch("/api/update", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name: name, quantity: quantity })
  });

  const result = await response.json();
  showMessage(result.message, result.ok);

  if (result.ok) {
    document.getElementById("update-qty").value = "";
    loadData();
  }
}

// Option 5: Sell Plant
async function sellPlant() {
  const name = document.getElementById("sell-select").value;
  const quantity = document.getElementById("sell-qty").value;

  const response = await fetch("/api/sell", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name: name, quantity: quantity })
  });

  const result = await response.json();
  showMessage(result.message, result.ok);

  if (result.ok) {
    document.getElementById("sell-qty").value = "";
    loadData();
  }
}

// Option 6: Generate Bill
async function generateBill() {
  const response = await fetch("/api/bill", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({})
  });

  const result = await response.json();
  if (!result.ok) {
    showMessage(result.message, false);
    return;
  }

  hideMessage();
  document.getElementById("pending-bill-box").classList.add("hidden");
  document.getElementById("final-receipt").classList.remove("hidden");

  const receiptBody = document.getElementById("receipt-table-body");
  const receiptCareList = document.getElementById("receipt-care-list");
  receiptBody.innerHTML = "";
  receiptCareList.innerHTML = "";

  for (let i = 0; i < result.items.length; i++) {
    const item = result.items[i];
    appendBillRow(receiptBody, item);

    const careCard = document.createElement("div");
    careCard.className = "receipt-care-item";

    const careTitle = document.createElement("strong");
    careTitle.textContent = item.name + " (" + item.quantity + " pcs)";
    careCard.appendChild(careTitle);

    careCard.appendChild(createCareLine("💧 Water Required", item.water));
    careCard.appendChild(createCareLine("🌱 Fertilizer Used", item.fertilizer));
    careCard.appendChild(createCareLine("☀️ Sunlight Required", item.sunlight));
    receiptCareList.appendChild(careCard);
  }

  document.getElementById("receipt-grand-total").textContent = "₹" + result.total;
  loadData();
}

// Reset sample records from Exit screen
async function resetNursery() {
  const response = await fetch("/api/reset", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({})
  });

  const result = await response.json();
  showSection("view");
  showMessage(result.message, result.ok);
}
