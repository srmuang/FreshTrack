# inventory_manager.py
# Manages pantry inventory using a dictionary for fast ID lookup
# and a deque for tracking newly arrived donations in order.

from collections import deque
from datetime import datetime
from food_item import FoodItem


class InventoryManager:
    def __init__(self):
        # Dictionary maps item_id (str) -> FoodItem object for O(1) lookup
        self.inventory = {}
        # Deque stores incoming donations in arrival order (FIFO)
        self.intake_queue = deque()

    def validate_item_data(self, item_id, name, category, quantity, expiration_date):
        # Check that required text fields are not empty
        if not item_id or not str(item_id).strip():
            raise ValueError("Item ID cannot be empty.")
        if not name or not str(name).strip():
            raise ValueError("Food name cannot be empty.")
        if not category or not str(category).strip():
            raise ValueError("Category cannot be empty.")

        # Ensure ID is unique in the main inventory
        if item_id.strip() in self.inventory:
            raise ValueError(f"Item ID '{item_id}' already exists.")

        # Validate that quantity is an integer greater than zero
        if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity <= 0:
            raise ValueError("Quantity must be a positive whole number.")

        # Validate expiration date format (YYYY-MM-DD)
        try:
            datetime.strptime(expiration_date.strip(), "%Y-%m-%d")
        except (ValueError, AttributeError):
            raise ValueError("Expiration date must follow YYYY-MM-DD format.")

    def add_donation(self, item_id, name, category, quantity, expiration_date):
        # Validate inputs before creating or storing the FoodItem
        self.validate_item_data(item_id, name, category, quantity, expiration_date)

        clean_id = item_id.strip()
        new_item = FoodItem(
            clean_id,
            name.strip(),
            category.strip(),
            quantity,
            expiration_date.strip()
        )

        # Add to main dictionary for quick searching and to intake deque for processing
        self.inventory[clean_id] = new_item
        self.intake_queue.append(new_item)
        return new_item

    def search_by_id(self, item_id):
        # Return the FoodItem if found in the dictionary, otherwise None
        if not item_id or not str(item_id).strip():
            return None
        return self.inventory.get(item_id.strip())

    def process_next_intake(self):
        # Remove and return the oldest donation waiting in the intake queue
        if not self.intake_queue:
            return None
        return self.intake_queue.popleft()

    def get_all_items(self):
        # Return a list of all FoodItem objects currently in inventory
        return list(self.inventory.values())
