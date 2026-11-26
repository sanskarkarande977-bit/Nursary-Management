# =====================================================================
# GO GREEN - Plant Nursery Management System (Web Version)
# Python backend with persistent JSON file storage + HTML/CSS/JS frontend
# =====================================================================

from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import sys
import webbrowser

# Folder where app.py, HTML/CSS/JS files, and saved JSON data live
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "nursery_data.json")

# Initial sample plant records (used when no saved data file exists yet)
INITIAL_PLANTS = {
    "Money Plant": {
        "price": 50,
        "quantity": 20,
        "water": "Moderate (2-3 times a week, when topsoil feels dry)",
        "fertilizer": "Liquid houseplant fertilizer or vermicompost once a month",
        "sunlight": "Indirect bright light (avoid harsh afternoon sun)",
    },
    "Rose Plant": {
        "price": 80,
        "quantity": 15,
        "water": "Regular (daily in summer, every 2 days in winter)",
        "fertilizer": "Compost, cow dung manure, or NPK rose fertilizer every 15-20 days",
        "sunlight": "Full direct sunlight (5-6 hours daily)",
    },
    "Aloe Vera": {
        "price": 60,
        "quantity": 12,
        "water": "Low (once every 1-2 weeks; let soil dry completely)",
        "fertilizer": "Succulent fertilizer or mild compost twice a year",
        "sunlight": "Bright sunlight (4-6 hours daily)",
    },
    "Tulsi Plant": {
        "price": 40,
        "quantity": 25,
        "water": "Moderate (daily light watering in well-drained soil)",
        "fertilizer": "Organic compost, vermicompost, or neem cake every 3-4 weeks",
        "sunlight": "Full to partial sunlight (4-6 hours daily)",
    },
    "Sunflower": {
        "price": 70,
        "quantity": 10,
        "water": "Regular (keep soil moist, especially during flowering)",
        "fertilizer": "Balanced NPK or organic compost every 2-3 weeks",
        "sunlight": "Full direct sunlight (6-8 hours daily)",
    },
}

# Active nursery data in memory + saved to DATA_FILE
plants = {}
sales_history = []
cart = []


def save_data():
    """Save plants stock and sold plant records to nursery_data.json."""
    data = {
        "plants": plants,
        "sales": sales_history,
    }
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def load_data():
    """Load saved plants and sales from nursery_data.json, or create initial records."""
    global plants, sales_history

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            saved = json.load(file)
            plants = saved.get("plants", {})
            sales_history = saved.get("sales", [])
    else:
        reset_data()


def reset_data():
    """Reset plant stock to sample records, clear sales & cart, and save to file."""
    plants.clear()
    for name, details in INITIAL_PLANTS.items():
        plants[name] = details.copy()
    sales_history.clear()
    cart.clear()
    save_data()


def find_plant(plant_name):
    """Find a plant by name (ignoring uppercase/lowercase) and return its exact key."""
    clean_name = plant_name.strip().lower()
    for name in plants:
        if name.lower() == clean_name:
            return name
    return None


def parse_positive_int(raw_value, field_name):
    """Convert an input value to a positive integer, or return (None, error_message)."""
    try:
        value = int(raw_value)
    except (ValueError, TypeError):
        return None, f"{field_name} must be a whole number."

    if value <= 0:
        return None, f"{field_name} must be greater than 0."
    return value, None


# Load saved data as soon as app.py starts
load_data()


class NurseryHandler(BaseHTTPRequestHandler):
    """Handle web page requests and nursery actions from the frontend."""

    def send_json(self, status_code, data):
        """Send a JSON response back to JavaScript."""
        body = json.dumps(data).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def send_file(self, filename, content_type):
        """Read an HTML, CSS, or JS file and send it to the browser."""
        file_path = os.path.join(BASE_DIR, filename)
        if not os.path.exists(file_path):
            self.send_error(404, "File not found")
            return

        with open(file_path, "rb") as file:
            content = file.read()

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(content)

    def read_json_body(self):
        """Read JSON data sent by JavaScript in a POST request."""
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw_data = self.rfile.read(length).decode("utf-8")
        return json.loads(raw_data)

    def do_GET(self):
        """Handle GET requests for web files and nursery data."""
        if self.path == "/" or self.path == "/index.html":
            self.send_file("index.html", "text/html; charset=utf-8")
        elif self.path == "/style.css":
            self.send_file("style.css", "text/css; charset=utf-8")
        elif self.path == "/script.js":
            self.send_file("script.js", "application/javascript; charset=utf-8")
        elif self.path == "/api/data":
            self.send_json(200, {"plants": plants, "cart": cart, "sales": sales_history})
        else:
            self.send_error(404, "Page not found")

    def do_POST(self):
        """Handle POST requests for Add, Search, Update, Sell, Bill, and Reset."""
        data = self.read_json_body()

        # 1. Add New Plant (with water, fertilizer, sunlight info) & Save
        if self.path == "/api/add":
            name = str(data.get("name", "")).strip()
            water = str(data.get("water", "")).strip()
            fertilizer = str(data.get("fertilizer", "")).strip()
            sunlight = str(data.get("sunlight", "")).strip()

            if name == "":
                self.send_json(400, {"ok": False, "message": "Plant name cannot be empty."})
                return

            if find_plant(name) is not None:
                self.send_json(
                    400,
                    {"ok": False, "message": "This plant already exists! Use Update Stock instead."},
                )
                return

            price, price_err = parse_positive_int(data.get("price"), "Price")
            if price_err:
                self.send_json(400, {"ok": False, "message": price_err})
                return

            quantity, qty_err = parse_positive_int(data.get("quantity"), "Quantity")
            if qty_err:
                self.send_json(400, {"ok": False, "message": qty_err})
                return

            if water == "" or fertilizer == "" or sunlight == "":
                self.send_json(
                    400,
                    {"ok": False, "message": "Please fill in Water, Fertilizer, and Sunlight details."},
                )
                return

            formatted_name = name.title()
            plants[formatted_name] = {
                "price": price,
                "quantity": quantity,
                "water": water,
                "fertilizer": fertilizer,
                "sunlight": sunlight,
            }
            save_data()
            self.send_json(200, {"ok": True, "message": f"'{formatted_name}' added and saved!"})

        # 2. Search Plant
        elif self.path == "/api/search":
            query = str(data.get("query", "")).strip().lower()
            if query == "":
                self.send_json(400, {"ok": False, "message": "Please enter a plant name to search."})
                return

            matches = []
            for name, details in plants.items():
                if query in name.lower():
                    matches.append(
                        {
                            "name": name,
                            "price": details["price"],
                            "quantity": details["quantity"],
                            "water": details.get("water", "Not specified"),
                            "fertilizer": details.get("fertilizer", "Not specified"),
                            "sunlight": details.get("sunlight", "Not specified"),
                        }
                    )

            self.send_json(200, {"ok": True, "matches": matches})

        # 3. Update Plant Stock & Save
        elif self.path == "/api/update":
            name = str(data.get("name", "")).strip()
            matched_name = find_plant(name)
            if matched_name is None:
                self.send_json(404, {"ok": False, "message": f"Plant '{name}' not found."})
                return

            add_qty, qty_err = parse_positive_int(data.get("quantity"), "Quantity to add")
            if qty_err:
                self.send_json(400, {"ok": False, "message": qty_err})
                return

            plants[matched_name]["quantity"] = plants[matched_name]["quantity"] + add_qty
            save_data()
            new_stock = plants[matched_name]["quantity"]
            self.send_json(
                200,
                {
                    "ok": True,
                    "message": f"Stock updated and saved! '{matched_name}' now has {new_stock} pieces.",
                },
            )

        # 4. Sell Plant & Save updated stock + sold record
        elif self.path == "/api/sell":
            name = str(data.get("name", "")).strip()
            matched_name = find_plant(name)
            if matched_name is None:
                self.send_json(404, {"ok": False, "message": f"Plant '{name}' not found."})
                return

            available = plants[matched_name]["quantity"]
            if available == 0:
                self.send_json(400, {"ok": False, "message": f"Sorry, '{matched_name}' is out of stock!"})
                return

            buy_qty, qty_err = parse_positive_int(data.get("quantity"), "Quantity")
            if qty_err:
                self.send_json(400, {"ok": False, "message": qty_err})
                return

            if buy_qty > available:
                self.send_json(
                    400,
                    {
                        "ok": False,
                        "message": f"Insufficient stock! Only {available} pieces of '{matched_name}' available.",
                    },
                )
                return

            # Reduce stock and save permanent sale record
            plants[matched_name]["quantity"] = available - buy_qty
            price = plants[matched_name]["price"]
            total = price * buy_qty

            sales_history.append(
                {
                    "name": matched_name,
                    "quantity": buy_qty,
                    "price": price,
                    "total": total,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                }
            )
            save_data()

            # Add to active customer cart for bill generation
            already_in_cart = False
            for item in cart:
                if item["name"] == matched_name:
                    item["quantity"] = item["quantity"] + buy_qty
                    already_in_cart = True
                    break

            if not already_in_cart:
                cart.append({"name": matched_name, "price": price, "quantity": buy_qty})

            self.send_json(
                200,
                {
                    "ok": True,
                    "message": f"Sold {buy_qty} piece(s) of '{matched_name}' for ₹{total}. Stock & sale saved!",
                },
            )

        # 5. Generate Bill
        elif self.path == "/api/bill":
            if len(cart) == 0:
                self.send_json(
                    400,
                    {"ok": False, "message": "No plants in current cart. Please sell a plant first."},
                )
                return

            bill_items = []
            grand_total = 0
            for item in cart:
                item_total = item["price"] * item["quantity"]
                grand_total = grand_total + item_total
                plant_info = plants.get(item["name"], {})
                bill_items.append(
                    {
                        "name": item["name"],
                        "quantity": item["quantity"],
                        "price": item["price"],
                        "total": item_total,
                        "water": plant_info.get("water", "Not specified"),
                        "fertilizer": plant_info.get("fertilizer", "Not specified"),
                        "sunlight": plant_info.get("sunlight", "Not specified"),
                    }
                )

            cart.clear()
            self.send_json(200, {"ok": True, "items": bill_items, "total": grand_total})

        # 6. Reset Data
        elif self.path == "/api/reset":
            reset_data()
            self.send_json(
                200,
                {"ok": True, "message": "Nursery records reset to initial sample plants."},
            )

        else:
            self.send_error(404, "Endpoint not found")


def start_server():
    """Start the local Python web server on port 8000 (or next free port)."""
    server = None
    port = 8000
    for try_port in range(8000, 8010):
        try:
            server = HTTPServer(("127.0.0.1", try_port), NurseryHandler)
            port = try_port
            break
        except OSError:
            continue

    if server is None:
        print("Could not start server: ports 8000-8009 are unavailable.")
        return

    url = f"http://127.0.0.1:{port}"
    print("=" * 50)
    print("  GO GREEN 🌱 - Web Server Running!")
    print(f"  Saved data file: {DATA_FILE}")
    print(f"  Open in browser: {url}")
    print("  Press Ctrl + C to stop the server.")
    print("=" * 50)

    if "--no-browser" not in sys.argv:
        webbrowser.open(url)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        save_data()
        print("\nData saved. Server stopped. Goodbye!")
        server.server_close()


if __name__ == "__main__":
    start_server()
