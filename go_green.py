# =====================================================================
# GO GREEN - Plant Nursery Management System
# Beginner-friendly menu-driven Python project with file saving
# =====================================================================

from datetime import datetime
import json
import os

# File where all plants, updated stock, and sold plant history are saved
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nursery_data.json")

# Initial sample plant records (used the first time the program runs)
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

# Active data loaded from file
plants = {}
sales_history = []
cart = []


def load_data():
    """Load saved plants and sales history from JSON file, or create sample data."""
    global plants, sales_history

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            saved = json.load(file)
            plants = saved.get("plants", {})
            sales_history = saved.get("sales", [])
    else:
        plants = {}
        for name, details in INITIAL_PLANTS.items():
            plants[name] = details.copy()
        sales_history = []
        save_data()


def save_data():
    """Save current plants stock and sold plant records permanently to JSON file."""
    data = {
        "plants": plants,
        "sales": sales_history,
    }
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def show_menu():
    """Display the project title and main menu options."""
    print("\n" + "=" * 46)
    print("                GO GREEN 🌱")
    print("       PLANT NURSERY MANAGEMENT SYSTEM")
    print("=" * 46)
    print("1. Add New Plant")
    print("2. View All Plants")
    print("3. Search Plant")
    print("4. Update Plant Stock")
    print("5. Sell Plant")
    print("6. Generate Bill")
    print("7. Plant Care Info")
    print("8. Exit")
    print("=" * 46)


def find_plant(plant_name):
    """Find a plant by name (ignoring uppercase/lowercase) and return its exact key."""
    clean_name = plant_name.strip().lower()
    for name in plants:
        if name.lower() == clean_name:
            return name
    return None


def get_positive_number(prompt):
    """Ask the user for a positive whole number and avoid crashes on wrong input."""
    while True:
        try:
            value = int(input(prompt))
            if value > 0:
                return value
            else:
                print("Please enter a number greater than 0.")
        except ValueError:
            print("Invalid input! Please enter numbers only.")


def get_non_empty_text(prompt):
    """Ask the user for text and make sure it is not blank."""
    while True:
        text = input(prompt).strip()
        if text != "":
            return text
        print("This field cannot be empty!")


def print_care_details(name, details):
    """Print water, fertilizer, and sunlight details for one plant."""
    print(f"Plant Name : {name}")
    print(f"Price      : ₹{details['price']} | Stock: {details['quantity']} pieces")
    print(f"Water      : {details.get('water', 'Not specified')}")
    print(f"Fertilizer : {details.get('fertilizer', 'Not specified')}")
    print(f"Sunlight   : {details.get('sunlight', 'Not specified')}")


def add_plant():
    """Add a new plant with price, stock, and care info, then save to file."""
    print("\n--- Add New Plant ---")
    name = input("Enter plant name: ").strip()

    if name == "":
        print("Plant name cannot be empty!")
        return

    if find_plant(name) is not None:
        print("This plant already exists! Use Option 4 to update its stock.")
        return

    price = get_positive_number("Enter plant price (in ₹): ")
    quantity = get_positive_number("Enter available quantity: ")
    water = get_non_empty_text("Enter water required (e.g., Moderate, 2-3 times a week): ")
    fertilizer = get_non_empty_text("Enter fertilizer to use (e.g., Vermicompost monthly): ")
    sunlight = get_non_empty_text("Enter sunlight required (e.g., Full sunlight 5-6 hours): ")

    formatted_name = name.title()
    plants[formatted_name] = {
        "price": price,
        "quantity": quantity,
        "water": water,
        "fertilizer": fertilizer,
        "sunlight": sunlight,
    }
    save_data()

    print(f"\n'{formatted_name}' added and saved successfully!")


def view_plants():
    """Display all plants with their price and available stock."""
    print("\n" + "-" * 50)
    print("             ALL AVAILABLE PLANTS")
    print("-" * 50)

    if len(plants) == 0:
        print("No plants available in the nursery.")
        print("-" * 50)
        return

    print(f"{'No.':<4} {'Plant Name':<20} {'Price':<10} {'Stock'}")
    print("-" * 50)

    count = 1
    for name, details in plants.items():
        price_text = f"₹{details['price']}"
        stock_text = f"{details['quantity']} pieces"
        print(f"{count:<4} {name:<20} {price_text:<10} {stock_text}")
        count = count + 1

    print("-" * 50)


def search_plant():
    """Search for a plant by name and display its price, stock, and care info."""
    print("\n--- Search Plant ---")
    search_name = input("Enter plant name to search: ").strip()

    if search_name == "":
        print("Please enter a plant name to search.")
        return

    found = False
    for name, details in plants.items():
        if search_name.lower() in name.lower():
            print("\nPlant Found!")
            print_care_details(name, details)
            found = True

    if not found:
        print(f"\nSorry, '{search_name}' was not found in the nursery.")


def update_stock():
    """Select an existing plant, increase its stock, and save to file."""
    print("\n--- Update Plant Stock ---")
    view_plants()

    name = input("Enter the name of the plant to update: ").strip()
    matched_name = find_plant(name)

    if matched_name is None:
        print(f"Plant '{name}' not found!")
        return

    add_qty = get_positive_number(f"Enter quantity to add to {matched_name}: ")

    plants[matched_name]["quantity"] = plants[matched_name]["quantity"] + add_qty
    save_data()

    print(
        f"\nStock updated and saved! '{matched_name}' now has "
        f"{plants[matched_name]['quantity']} pieces."
    )


def sell_plant():
    """Sell a plant if sufficient stock exists, then save updated stock and sale."""
    print("\n--- Sell Plant ---")
    view_plants()

    name = input("Enter plant name to buy: ").strip()
    matched_name = find_plant(name)

    if matched_name is None:
        print(f"Plant '{name}' not found!")
        return

    available = plants[matched_name]["quantity"]
    if available == 0:
        print(f"Sorry, '{matched_name}' is currently out of stock!")
        return

    buy_qty = get_positive_number("Enter quantity the customer wants to buy: ")

    if buy_qty > available:
        print(
            f"Insufficient stock! Only {available} pieces of "
            f"'{matched_name}' are available."
        )
        return

    # Reduce stock and record sale permanently
    plants[matched_name]["quantity"] = available - buy_qty
    price = plants[matched_name]["price"]
    total = price * buy_qty

    sales_history.append({
        "name": matched_name,
        "quantity": buy_qty,
        "price": price,
        "total": total,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
    })
    save_data()

    # Add to current customer's bill cart
    already_in_cart = False
    for item in cart:
        if item["name"] == matched_name:
            item["quantity"] = item["quantity"] + buy_qty
            already_in_cart = True
            break

    if not already_in_cart:
        cart.append({"name": matched_name, "price": price, "quantity": buy_qty})

    print(f"\nPurchase successful and saved! Sold {buy_qty} piece(s) of '{matched_name}' for ₹{total}.")
    print(f"Remaining stock of '{matched_name}': {plants[matched_name]['quantity']} pieces.")
    print("Select Option 6 (Generate Bill) when ready to print the bill.")


def generate_bill():
    """Display the customer bill and show saved sales history if cart is empty."""
    print("\n" + "=" * 54)
    print("              GO GREEN 🌱 - CUSTOMER BILL")
    print("=" * 54)

    if len(cart) == 0:
        print("No new items in current cart. Please sell a plant first (Option 5).")
        if len(sales_history) > 0:
            print("\n--- Saved Sales History ---")
            for sale in sales_history:
                print(
                    f"- {sale['name']} x {sale['quantity']} "
                    f"(₹{sale['price']} each) = ₹{sale['total']} [{sale['date']}]"
                )
        print("=" * 54)
        return

    print(f"{'Plant Name':<20} {'Qty':<6} {'Price':<10} {'Total'}")
    print("-" * 54)

    grand_total = 0
    for item in cart:
        item_total = item["price"] * item["quantity"]
        grand_total = grand_total + item_total
        price_text = f"₹{item['price']}"
        print(f"{item['name']:<20} {item['quantity']:<6} {price_text:<10} ₹{item_total}")

    print("-" * 54)
    print(f"{'Total Amount:':<38} ₹{grand_total}")
    print("=" * 54)
    print("      PLANT CARE GUIDE FOR YOUR PURCHASED PLANTS")
    print("-" * 54)
    for item in cart:
        info = plants.get(item["name"], {})
        print(f"* {item['name']}:")
        print(f"  Water      : {info.get('water', 'Not specified')}")
        print(f"  Fertilizer : {info.get('fertilizer', 'Not specified')}")
        print(f"  Sunlight   : {info.get('sunlight', 'Not specified')}")
    print("=" * 54)
    print("     Thank you for shopping with GO GREEN 🌱!")
    print("          Save Plants, Save Earth!")
    print("=" * 54)

    cart.clear()


def view_plant_care():
    """Display water, fertilizer, and sunlight requirements for plants."""
    print("\n--- Plant Care Information ---")
    plant_name = input("Enter plant name (or press Enter to view all): ").strip()

    if plant_name == "":
        print("\n" + "-" * 54)
        for name, details in plants.items():
            print_care_details(name, details)
            print("-" * 54)
        return

    matched_name = find_plant(plant_name)
    if matched_name is None:
        print(f"Plant '{plant_name}' not found!")
        return

    print("-" * 54)
    print_care_details(matched_name, plants[matched_name])
    print("-" * 54)


def main():
    """Load saved data and run the main menu loop until Exit."""
    load_data()

    while True:
        show_menu()
        choice = input("Enter your choice (1-8): ").strip()

        if choice == "1":
            add_plant()
        elif choice == "2":
            view_plants()
        elif choice == "3":
            search_plant()
        elif choice == "4":
            update_stock()
        elif choice == "5":
            sell_plant()
        elif choice == "6":
            generate_bill()
        elif choice == "7":
            view_plant_care()
        elif choice == "8":
            save_data()
            print("\nAll plant stock and sales are saved!")
            print("Thank you for using GO GREEN 🌱 Plant Nursery Management System!")
            print("Goodbye! Keep growing green!")
            break
        else:
            print("\nInvalid choice! Please enter a number between 1 and 8.")


if __name__ == "__main__":
    main()
