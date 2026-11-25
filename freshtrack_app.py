""" 
Tkinter GUI for FreshTrack: connects donation entry, FIFO intake queue,
O(1) ID search, quantity updates, and custom Insertion Sort expiration ordering.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from inventory_manager import InventoryManager


class FreshTrackApp(tk.Frame):
    def __init__(self, master, manager=None):
        self.master = master
        super().__init__(self.master)
        self.manager = manager if manager is not None else InventoryManager()
        self.sort_by_expiration_active = False

        self.configure_gui()
        self.create_widgets()
        self.refresh_displays()

    def configure_gui(self):
        # For setting up the main window title, dimensions, and outer padding
        self.master.title("FreshTrack - Food Pantry Inventory & Expiration Manager")
        self.master.geometry("820x610")
        self.master.resizable(False, False)
        self.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

    def create_widgets(self):
        # To organize the GUI layout into three separate sections
        self.create_entry_form()
        self.create_search_update_bar()
        self.create_lists_panel()

    def create_entry_form(self):
        # Frame for recording new food donations
        form_frame = tk.LabelFrame(self, text="Record New Donation", padx=10, pady=8)
        form_frame.pack(fill=tk.X, pady=(0, 10))

        # Row 0: Item ID and Food Name inputs
        tk.Label(form_frame, text="Item ID:").grid(row=0, column=0, sticky=tk.W, pady=4)
        self.id_entry = tk.Entry(form_frame, width=18)
        self.id_entry.grid(row=0, column=1, padx=(5, 20), pady=4)

        tk.Label(form_frame, text="Food Name:").grid(row=0, column=2, sticky=tk.W, pady=4)
        self.name_entry = tk.Entry(form_frame, width=25)
        self.name_entry.grid(row=0, column=3, padx=(5, 10), pady=4)

        # Row 1: Category dropdown and Quantity input
        tk.Label(form_frame, text="Category:").grid(row=1, column=0, sticky=tk.W, pady=4)
        self.category_var = tk.StringVar(value="Canned Goods")
        self.category_combo = ttk.Combobox(
            form_frame,
            textvariable=self.category_var,
            values=["Canned Goods", "Produce", "Dairy", "Grains", "Bakery", "Protein", "Other"],
            state="readonly",
            width=15
        )
        self.category_combo.grid(row=1, column=1, padx=(5, 20), pady=4)

        tk.Label(form_frame, text="Quantity:").grid(row=1, column=2, sticky=tk.W, pady=4)
        self.qty_entry = tk.Entry(form_frame, width=25)
        self.qty_entry.grid(row=1, column=3, padx=(5, 10), pady=4)

        # Row 2: Expiration Date input and Add button
        tk.Label(form_frame, text="Expiration (YYYY-MM-DD):").grid(row=2, column=0, sticky=tk.W, pady=4)
        self.exp_entry = tk.Entry(form_frame, width=18)
        self.exp_entry.grid(row=2, column=1, padx=(5, 20), pady=4)

        self.add_btn = tk.Button(
            form_frame,
            text="Add Donation",
            width=20,
            bg="#2e7d32",
            fg="white",
            command=self.handle_add_donation
        )
        self.add_btn.grid(row=2, column=3, sticky=tk.E, padx=(5, 10), pady=4)

    def create_search_update_bar(self):
        # Frame for looking up an item by ID and updating its stock quantity
        manage_frame = tk.LabelFrame(self, text="Search & Update Inventory", padx=10, pady=8)
        manage_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(manage_frame, text="Item ID:").grid(row=0, column=0, sticky=tk.W, pady=4)
        self.search_id_entry = tk.Entry(manage_frame, width=15)
        self.search_id_entry.grid(row=0, column=1, padx=(5, 10), pady=4)

        self.search_btn = tk.Button(
            manage_frame,
            text="Search ID",
            width=12,
            command=self.handle_search_item
        )
        self.search_btn.grid(row=0, column=2, padx=(0, 20), pady=4)

        tk.Label(manage_frame, text="New Quantity:").grid(row=0, column=3, sticky=tk.W, pady=4)
        self.update_qty_entry = tk.Entry(manage_frame, width=12)
        self.update_qty_entry.grid(row=0, column=4, padx=(5, 10), pady=4)

        self.update_btn = tk.Button(
            manage_frame,
            text="Update Qty",
            width=12,
            command=self.handle_update_quantity
        )
        self.update_btn.grid(row=0, column=5, pady=4)

    def create_lists_panel(self):
        # Container frame holding Intake Queue (left) and Main Inventory (right)
        lists_frame = tk.Frame(self)
        lists_frame.pack(fill=tk.BOTH, expand=True)

        # Left side: Intake Queue (deque in FIFO arrival order)
        intake_frame = tk.LabelFrame(lists_frame, text="Intake Queue (Arrival Order)", padx=8, pady=8)
        intake_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        self.intake_listbox = tk.Listbox(intake_frame, height=14, width=40)
        self.intake_listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        self.process_btn = tk.Button(
            intake_frame,
            text="Process Next Intake Item",
            command=self.handle_process_intake
        )
        self.process_btn.pack(fill=tk.X)

        # Right side: Main Inventory with custom Insertion Sort button
        inv_frame = tk.LabelFrame(lists_frame, text="Inventory & Expiration Report", padx=8, pady=8)
        inv_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(8, 0))

        self.inventory_listbox = tk.Listbox(inv_frame, height=14, width=44)
        self.inventory_listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        self.sort_btn = tk.Button(
            inv_frame,
            text="Sort by Expiration (Soonest First)",
            bg="#1565c0",
            fg="white",
            command=self.handle_sort_expiration
        )
        self.sort_btn.pack(fill=tk.X)

    def handle_add_donation(self, show_dialogs=True):
        # This part will read the entry boxes and validate the quantity before adding
        item_id = self.id_entry.get()
        name = self.name_entry.get()
        category = self.category_var.get()
        raw_qty = self.qty_entry.get().strip()
        exp_date = self.exp_entry.get()

        try:
            if not raw_qty or not raw_qty.lstrip("-").isdigit():
                raise ValueError("Quantity must be a positive whole number.")
            quantity = int(raw_qty)

            new_item = self.manager.add_donation(item_id, name, category, quantity, exp_date)
            self.clear_form()
            self.refresh_displays()
            if show_dialogs:
                messagebox.showinfo("Donation Added", f"Recorded: {new_item.name} (ID: {new_item.item_id})")
            return True
        except ValueError as err:
            if show_dialogs:
                messagebox.showerror("Input Error", str(err))
            return False

    def handle_search_item(self, show_dialogs=True):
        # To look up an item by ID and pre-fill its current quantity for quick updates
        search_id = self.search_id_entry.get().strip()
        found = self.manager.search_by_id(search_id)

        if found is None:
            if show_dialogs:
                messagebox.showwarning("Not Found", f"No item found with ID '{search_id}'.")
            return None

        self.update_qty_entry.delete(0, tk.END)
        self.update_qty_entry.insert(0, str(found.quantity))
        if show_dialogs:
            messagebox.showinfo("Item Found", str(found))
        return found

    def handle_update_quantity(self, show_dialogs=True):
        # This will update an item's quantity or remove it from inventory if set to 0
        item_id = self.search_id_entry.get().strip()
        raw_qty = self.update_qty_entry.get().strip()

        try:
            if not raw_qty or not raw_qty.lstrip("-").isdigit():
                raise ValueError("New quantity must be zero or a positive whole number.")
            new_qty = int(raw_qty)

            updated = self.manager.update_item_quantity(item_id, new_qty)
            self.refresh_displays()
            if show_dialogs:
                if new_qty == 0:
                    messagebox.showinfo("Item Depleted", f"[{updated.item_id}] {updated.name} reached 0 and was removed.")
                else:
                    messagebox.showinfo("Quantity Updated", f"Updated: {updated}")
            return True
        except ValueError as err:
            if show_dialogs:
                messagebox.showerror("Update Error", str(err))
            return False

    def handle_sort_expiration(self):
        # To turn on custom Insertion Sort ordering for the inventory listbox
        self.sort_by_expiration_active = True
        self.refresh_displays()

    def handle_process_intake(self, show_dialogs=True):
        # To pop the oldest donation from the deque so a volunteer can shelve it
        processed = self.manager.process_next_intake()
        self.refresh_displays()
        if processed is None:
            if show_dialogs:
                messagebox.showinfo("Intake Empty", "No donations waiting in the intake queue.")
            return None
        if show_dialogs:
            messagebox.showinfo(
                "Intake Processed",
                f"Shelved: [{processed.item_id}] {processed.name} (Qty: {processed.quantity})"
            )
        return processed

    def clear_form(self):
        # To reset the form entry widgets after a donation is added
        self.id_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.qty_entry.delete(0, tk.END)
        self.exp_entry.delete(0, tk.END)
        self.category_var.set("Canned Goods")

    def refresh_displays(self):
        # Sync the Intake Queue listbox with the deque
        self.intake_listbox.delete(0, tk.END)
        for item in self.manager.intake_queue:
            self.intake_listbox.insert(tk.END, str(item))

        self.inventory_listbox.delete(0, tk.END)
        items = (
            self.manager.insertion_sort_by_expiration()
            if self.sort_by_expiration_active
            else self.manager.get_all_items()
        )
        for item in items:
            self.inventory_listbox.insert(tk.END, str(item))


if __name__ == "__main__":
    root = tk.Tk()
    app = FreshTrackApp(root)
    root.mainloop()