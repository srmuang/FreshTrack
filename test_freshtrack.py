# test_freshtrack.py
# Unit tests for Sprint 1 of FreshTrack (backend/validation) and Sprint 2 (Tkinter GUI & intake)

import unittest
import tkinter as tk
from food_item import FoodItem
from inventory_manager import InventoryManager
from freshtrack_app import FreshTrackApp


class TestFreshTrackSprint1(unittest.TestCase):
    def setUp(self):
        # Create a fresh InventoryManager before each test runs
        
        self.manager = InventoryManager()

    def test_add_valid_donation(self):

        # To verify a valid item is added to both the dict and the intake deque
        item = self.manager.add_donation("F101", "Canned Beans", "Canned Goods", 15, "2027-05-10")
        self.assertEqual(len(self.manager.inventory), 1)
        self.assertEqual(len(self.manager.intake_queue), 1)
        self.assertEqual(item.name, "Canned Beans")

    def test_search_by_id_found_and_not_found(self):

        # To verify searching returns the right FoodItem or None if missing
        self.manager.add_donation("F102", "Whole Milk", "Dairy", 6, "2026-11-25")
        found = self.manager.search_by_id("F102")
        missing = self.manager.search_by_id("F999")

        self.assertIsNotNone(found)
        self.assertEqual(found.quantity, 6)
        self.assertIsNone(missing)

    def test_intake_queue_fifo_order(self):

        # To verify deque processes donations in the exact order they arrived
        self.manager.add_donation("F101", "Apples", "Produce", 20, "2026-11-20")
        self.manager.add_donation("F102", "Rice", "Grains", 10, "2027-08-01")

        first_out = self.manager.process_next_intake()
        second_out = self.manager.process_next_intake()

        self.assertEqual(first_out.item_id, "F101")
        self.assertEqual(second_out.item_id, "F102")
        self.assertIsNone(self.manager.process_next_intake())

    def test_reject_duplicate_id(self):

        # To verify adding an item with an existing ID raises ValueError
        self.manager.add_donation("F101", "Pasta", "Grains", 12, "2027-03-15")
        with self.assertRaises(ValueError):
            self.manager.add_donation("F101", "Tomato Sauce", "Canned Goods", 8, "2027-04-01")

    def test_reject_invalid_quantity(self):
        # To verify zero, negative, or non-integer quantities raise ValueError

        with self.assertRaises(ValueError):
            self.manager.add_donation("F103", "Bread", "Bakery", 0, "2026-11-18")
        with self.assertRaises(ValueError):
            self.manager.add_donation("F104", "Bread", "Bakery", -5, "2026-11-18")
        with self.assertRaises(ValueError):
            self.manager.add_donation("F105", "Bread", "Bakery", "ten", "2026-11-18")

    def test_reject_invalid_date_and_empty_fields(self):

        # To verify bad date formats and empty strings are caught
        with self.assertRaises(ValueError):
            self.manager.add_donation("F106", "Yogurt", "Dairy", 4, "11/25/2026")
        with self.assertRaises(ValueError):
            self.manager.add_donation("", "Yogurt", "Dairy", 4, "2026-11-25")
        with self.assertRaises(ValueError):
            self.manager.add_donation("F107", "   ", "Dairy", 4, "2026-11-25")


class TestFreshTrackSprint2GUI(unittest.TestCase):
    def setUp(self):

        # For setting up a hidden Tkinter root window and FreshTrackApp before each GUI test
        self.root = tk.Tk()
        self.root.withdraw()
        self.app = FreshTrackApp(self.root)

    def tearDown(self):

        # This, to destroy the Tkinter window after each test so tests stay isolated
        self.root.destroy()

    def test_gui_add_valid_donation(self):

        # This part will simulate filling out GUI form and submitting a valid donation
        self.app.id_entry.insert(0, "F201")
        self.app.name_entry.insert(0, "Oatmeal")
        self.app.category_var.set("Grains")
        self.app.qty_entry.insert(0, "14")
        self.app.exp_entry.insert(0, "2027-02-15")

        result = self.app.handle_add_donation(show_dialogs=False)

        self.assertTrue(result)
        self.assertEqual(self.app.intake_listbox.size(), 1)
        self.assertEqual(self.app.inventory_listbox.size(), 1)

        # This will verify form fields cleared after adding
        self.assertEqual(self.app.id_entry.get(), "")

    def test_gui_reject_invalid_donation(self):

        # To simulate submitting an invalid quantity through the GUI without crashing
        self.app.id_entry.insert(0, "F202")
        self.app.name_entry.insert(0, "Carrots")
        self.app.category_var.set("Produce")
        self.app.qty_entry.insert(0, "-3")
        self.app.exp_entry.insert(0, "2026-12-01")

        result = self.app.handle_add_donation(show_dialogs=False)

        self.assertFalse(result)
        self.assertEqual(len(self.app.manager.inventory), 0)
        self.assertEqual(self.app.intake_listbox.size(), 0)

    def test_gui_process_intake_queue(self):

        # To verify processing items removes them from the intake listbox in FIFO order
        self.app.manager.add_donation("F203", "Peaches", "Canned Goods", 10, "2027-06-01")
        self.app.manager.add_donation("F204", "Milk", "Dairy", 5, "2026-11-28")
        self.app.refresh_displays()

        self.assertEqual(self.app.intake_listbox.size(), 2)

        first = self.app.handle_process_intake(show_dialogs=False)
        self.assertEqual(first.item_id, "F203")
        self.assertEqual(self.app.intake_listbox.size(), 1)

        # This will verify that the main inventory still holds both items until distributed
        self.assertEqual(self.app.inventory_listbox.size(), 2)

if __name__ == "__main__":
    unittest.main(verbosity=2)
