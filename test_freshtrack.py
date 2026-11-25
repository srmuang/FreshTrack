"""
Unit tests for FreshTrack: Sprint 1 (backend/validation), Sprint 2 (Tkinter GUI & intake),
and Sprint 3 (custom Insertion Sort, quantity updates, and GUI search/sort controls)
"""

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
        self.assertEqual(found.item_id, "F102")
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


class TestFreshTrackSprint3SortingAndUpdates(unittest.TestCase):
    def setUp(self):
        # For setting up a hidden Tkinter window and FreshTrackApp before each Sprint 3 test
        self.root = tk.Tk()
        self.root.withdraw()
        self.app = FreshTrackApp(self.root)

    def tearDown(self):
        # To destroy the Tkinter window after each test finishes
        self.root.destroy()

    def test_insertion_sort_by_expiration_order(self):
        # To verify Insertion Sort arranges items from soonest expiration date to latest
        self.app.manager.add_donation("F301", "Canned Corn", "Canned Goods", 10, "2027-09-01")
        self.app.manager.add_donation("F302", "Fresh Milk", "Dairy", 5, "2026-11-28")
        self.app.manager.add_donation("F303", "Bread", "Bakery", 8, "2026-11-20")
        self.app.manager.add_donation("F304", "Cheese", "Dairy", 4, "2026-11-28")

        sorted_items = self.app.manager.insertion_sort_by_expiration()
        sorted_ids = [item.item_id for item in sorted_items]

        # This will verify F303 (Nov 20) comes first, then F302 and F304 (Nov 28), then F301 (Sep 2027)
        self.assertEqual(sorted_ids, ["F303", "F302", "F304", "F301"])

    def test_insertion_sort_already_and_reverse_sorted(self):
        # To verify Insertion Sort works properly on reverse-ordered and already-ordered dates
        self.app.manager.add_donation("F310", "Beans", "Canned Goods", 9, "2027-12-01")
        self.app.manager.add_donation("F311", "Salsa", "Canned Goods", 7, "2027-06-15")
        self.app.manager.add_donation("F312", "Eggs", "Dairy", 12, "2026-11-26")

        sorted_items = self.app.manager.insertion_sort_by_expiration()
        self.assertEqual([item.item_id for item in sorted_items], ["F312", "F311", "F310"])

    def test_update_quantity_and_zero_removal(self):
        # To verify updating quantity changes the count, and setting it to 0 removes the item
        self.app.manager.add_donation("F305", "Rice", "Grains", 12, "2027-04-10")
        self.app.manager.update_item_quantity("F305", 7)
        self.assertEqual(self.app.manager.search_by_id("F305").quantity, 7)

        # This part will set quantity to 0 and check that the depleted item is removed
        self.app.manager.update_item_quantity("F305", 0)
        self.assertIsNone(self.app.manager.search_by_id("F305"))

    def test_update_quantity_invalid_cases(self):
        # To verify missing IDs or negative quantities raise ValueError
        with self.assertRaises(ValueError):
            self.app.manager.update_item_quantity("UNKNOWN", 5)

        self.app.manager.add_donation("F306", "Soup", "Canned Goods", 6, "2027-01-15")
        with self.assertRaises(ValueError):
            self.app.manager.update_item_quantity("F306", -2)

    def test_gui_search_update_and_sort_display(self):
        # To simulate searching, updating quantity, and sorting the listbox through the GUI
        self.app.manager.add_donation("F307", "Pasta", "Grains", 15, "2027-05-01")
        self.app.manager.add_donation("F308", "Yogurt", "Dairy", 6, "2026-11-19")

        self.app.search_id_entry.insert(0, "F308")
        found = self.app.handle_search_item(show_dialogs=False)
        self.assertEqual(found.name, "Yogurt")
        self.assertEqual(self.app.update_qty_entry.get(), "6")

        self.app.update_qty_entry.delete(0, tk.END)
        self.app.update_qty_entry.insert(0, "3")
        self.assertTrue(self.app.handle_update_quantity(show_dialogs=False))

        self.app.handle_sort_expiration()
        first_displayed = self.app.inventory_listbox.get(0)
        self.assertIn("F308", first_displayed)
        self.assertIn("Qty: 3", first_displayed)


if __name__ == "__main__":
    unittest.main(verbosity=2)