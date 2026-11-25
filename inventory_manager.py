"""
This file manages the food pantry inventory using a dictionary for quick ID lookup,
a deque for tracking newly arrived donations in order, and a custom.
Insertion Sort algorithm to prioritize items that expire soonest.
"""

from collections import deque
from datetime import datetime
from food_item import FoodItem

class InventoryManager:
    def __init__(self):
        # Dictionary to map item_id (str) -> FoodItem object for O(1) lookup
        self.inventory = {}
        # Deque to store incoming donations in arrival order (FIFO)
        self.intake_queue = deque()

    def validate_item_data(self, item_id, name, category, quantity, expiration_date):
        # To check that required text fields are not left blank
        if not item_id or not str(item_id).strip():
            raise ValueError("Item ID cannot be empty.")
        if not name or not str(name).strip():
            raise ValueError("Food name cannot be empty.")
        if not category or not str(category).strip():
            raise ValueError("Category cannot be empty.")

        # To make sure the ID does not already exist in the main inventory
        if item_id.strip() in self.inventory:
            raise ValueError(f"Item ID '{item_id}' already exists.")

        # To verify that quantity is a whole number greater than zero
        if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity <= 0:
            raise ValueError("Quantity must be a positive whole number.")

        # To validate that the expiration date follows YYYY-MM-DD format
        try:
            datetime.strptime(expiration_date.strip(), "%Y-%m-%d")
        except (ValueError, AttributeError):
            raise ValueError("Expiration date must follow YYYY-MM-DD format.")

    def add_donation(self, item_id, name, category, quantity, expiration_date):
        # This part will validate the inputs before creating and storing the FoodItem
        self.validate_item_data(item_id, name, category, quantity, expiration_date)

        clean_id = item_id.strip()
        new_item = FoodItem(
            clean_id,
            name.strip(),
            category.strip(),
            quantity,
            expiration_date.strip()
        )

        # Add to the dictionary for fast ID lookup and to the deque for intake order
        self.inventory[clean_id] = new_item
        self.intake_queue.append(new_item)
        return new_item

    def search_by_id(self, item_id):
        # To return the matching FoodItem from the dictionary, or None if missing
        if not item_id or not str(item_id).strip():
            return None
        return self.inventory.get(item_id.strip())

    def update_item_quantity(self, item_id, new_quantity):
        # This part will update an item's stock count or remove it if quantity hits 0
        if not item_id or not str(item_id).strip():
            raise ValueError("Please enter an Item ID to update.")

        clean_id = item_id.strip()
        if clean_id not in self.inventory:
            raise ValueError(f"Item ID '{clean_id}' was not found in inventory.")

        if not isinstance(new_quantity, int) or isinstance(new_quantity, bool) or new_quantity < 0:
            raise ValueError("New quantity must be zero or a positive whole number.")

        if new_quantity == 0:
            # Remove the depleted item from active inventory once all units are given out
            removed_item = self.inventory.pop(clean_id)
            removed_item.update_quantity(0)
            return removed_item

        item = self.inventory[clean_id]
        item.update_quantity(new_quantity)
        return item

    def process_next_intake(self):
        # To remove and return the oldest donation waiting in the intake queue
        if not self.intake_queue:
            return None
        return self.intake_queue.popleft()

    def get_all_items(self):
        # To return a list of all FoodItem objects currently stored in inventory
        return list(self.inventory.values())

    def insertion_sort_by_expiration(self):
        # Custom Insertion Sort (written from scratch without .sort() or sorted())
        # This will arrange FoodItem objects from soonest expiration date to latest
        items = self.get_all_items()

        for i in range(1, len(items)):
            key_item = items[i]
            key_date = datetime.strptime(key_item.expiration_date, "%Y-%m-%d")
            j = i - 1

            # Shift items that expire later than key_item one spot to the right
            while j >= 0 and datetime.strptime(items[j].expiration_date, "%Y-%m-%d") > key_date:
                items[j + 1] = items[j]
                j -= 1

            items[j + 1] = key_item

        return items
