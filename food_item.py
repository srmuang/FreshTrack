# food_item.py
# the file represents a single donated food item in the FreshTrack pantry system.

class FoodItem:
    def __init__(self, item_id, name, category, quantity, expiration_date):
        # Store core attributes for each donated item
        self.item_id = item_id
        self.name = name
        self.category = category
        self.quantity = quantity
        self.expiration_date = expiration_date  # Stored in YYYY-MM-DD format

    def update_quantity(self, new_quantity):
        # Update the item count after validation in the manager
        self.quantity = new_quantity

    def __str__(self):
        # Return a readable string for displaying in reports or lists
        return (
            f"[{self.item_id}] {self.name} ({self.category}) - "
            f"Qty: {self.quantity} | Expires: {self.expiration_date}"
        )
