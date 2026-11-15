# test_freshtrack.py
# Unit tests for FreshTrack Sprint 1: FoodItem, InventoryManager, and validation.

import unittest
from food_item import FoodItem
from inventory_manager import InventoryManager


class TestFreshTrackSprint1(unittest.TestCase):
    def setUp(self):
        # Create a fresh InventoryManager before each test runs
        self.manager = InventoryManager()

    def test_add_valid_donation(self):
        # Verify a valid item is added to both the dict and the intake deque
        item = self.manager.add_donation("F101", "Canned Beans", "Canned Goods", 15, "2027-05-10")
        self.assertEqual(len(self.manager.inventory), 1)
        self.assertEqual(len(self.manager.intake_queue), 1)
        self.assertEqual(item.name, "Canned Beans")

    def test_search_by_id_found_and_not_found(self):
        # Verify searching returns the right FoodItem or None if missing
        self.manager.add_donation("F102", "Whole Milk", "Dairy", 6, "2026-11-25")
        found = self.manager.search_by_id("F102")
        missing = self.manager.search_by_id("F999")

        self.assertIsNotNone(found)
        self.assertEqual(found.quantity, 6)
        self.assertIsNone(missing)

    def test_intake_queue_fifo_order(self):
        # Verify deque processes donations in the exact order they arrived
        self.manager.add_donation("F101", "Apples", "Produce", 20, "2026-11-20")
        self.manager.add_donation("F102", "Rice", "Grains", 10, "2027-08-01")

        first_out = self.manager.process_next_intake()
        second_out = self.manager.process_next_intake()

        self.assertEqual(first_out.item_id, "F101")
        self.assertEqual(second_out.item_id, "F102")
        self.assertIsNone(self.manager.process_next_intake())


    def test_reject_duplicate_id(self):
        # Verify adding an item with an existing ID raises ValueError
        self.manager.add_donation("F101", "Pasta", "Grains", 12, "2027-03-15")
        with self.assertRaises(ValueError):
            self.manager.add_donation("F101", "Tomato Sauce", "Canned Goods", 8, "2027-04-01")

    def test_reject_invalid_quantity(self):
        # Verify zero, negative, or non-integer quantities raise ValueError
        with self.assertRaises(ValueError):
            self.manager.add_donation("F103", "Bread", "Bakery", 0, "2026-11-18")
        with self.assertRaises(ValueError):
            self.manager.add_donation("F104", "Bread", "Bakery", -5, "2026-11-18")
        with self.assertRaises(ValueError):
            self.manager.add_donation("F105", "Bread", "Bakery", "ten", "2026-11-18")


    def test_reject_invalid_date_and_empty_fields(self):
        # Verify bad date formats and empty strings are caught
        with self.assertRaises(ValueError):
            self.manager.add_donation("F106", "Yogurt", "Dairy", 4, "11/25/2026")
        with self.assertRaises(ValueError):
            self.manager.add_donation("", "Yogurt", "Dairy", 4, "2026-11-25")
        with self.assertRaises(ValueError):
            self.manager.add_donation("F107", "   ", "Dairy", 4, "2026-11-25")

if __name__ == "__main__":
    unittest.main(verbosity=2)
