# freshtrack_app.py
# Tkinter GUI for FreshTrack to connect donation entry and FIFO intake workflow
# to the InventoryManager backend.

import tkinter as tk
from tkinter import ttk, messagebox
from inventory_manager import InventoryManager


class FreshTrackApp(tk.Frame):
    def __init__(self, master, manager=None):
        self.master = master
        super().__init__(self.master)
        # Allow passing an existing manager (helpful for unit testing)
        self.manager = manager if manager is not None else InventoryManager()

        self.configure_gui()
        self.create_widgets()
        self.refresh_displays()

    def configure_gui(self):
        # Set up main window title, size, and layout padding
        self.master.title("FreshTrack - Food Pantry Inventory & Expiration Manager")
        self.master.geometry("760x520")
        self.master.resizable(False, False)
        self.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

    def create_widgets(self):
        # Organize the interface into top entry form and bottom display panels
        self.create_entry_form()
        self.create_lists_panel()

    def create_entry_form(self):
        # Frame for recording new food donations
        form_frame = tk.LabelFrame(self, text="Record New Donation", padx=10, pady=10)
        form_frame.pack(fill=tk.X, pady=(0, 12))

        # Row 0: Item ID and Food Name
        tk.Label(form_frame, text="Item ID:").grid(row=0, column=0, sticky=tk.W, pady=4)
        self.id_entry = tk.Entry(form_frame, width=18)
        self.id_entry.grid(row=0, column=1, padx=(5, 20), pady=4)

        tk.Label(form_frame, text="Food Name:").grid(row=0, column=2, sticky=tk.W, pady=4)
        self.name_entry = tk.Entry(form_frame, width=25)
        self.name_entry.grid(row=0, column=3, padx=(5, 10), pady=4)

        # Row 1: Category Dropdown and Quantity
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

        # Row 2: Expiration Date and Add Button
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

    def create_lists_panel(self):
        # Container frame holding Intake Queue (left) and Inventory Overview (right)
        lists_frame = tk.Frame(self)
        lists_frame.pack(fill=tk.BOTH, expand=True)

        # Left side: Intake Queue (deque - FIFO arrival order)
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

        # Right side: Main Inventory (dict values)
        inv_frame = tk.LabelFrame(lists_frame, text="All Recorded Inventory", padx=8, pady=8)
        inv_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(8, 0))

        self.inventory_listbox = tk.Listbox(inv_frame, height=16, width=42)
        self.inventory_listbox.pack(fill=tk.BOTH, expand=True)

    def handle_add_donation(self, show_dialogs=True):
        # Read user input from entry boxes and validate quantity conversion
        item_id = self.id_entry.get()
        name = self.name_entry.get()
        category = self.category_var.get()
        raw_qty = self.qty_entry.get().strip()
        exp_date = self.exp_entry.get()

        try:
            # Ensure quantity converts cleanly to an integer before passing to manager
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

    def handle_process_intake(self, show_dialogs=True):
        # Pop the oldest donation from the deque so a volunteer can shelve it
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
        # Reset entry widgets after a successful donation submission
        self.id_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.qty_entry.delete(0, tk.END)
        self.exp_entry.delete(0, tk.END)
        self.category_var.set("Canned Goods")

    def refresh_displays(self):
        # Sync both Listboxes with the current state of the deque and dictionary
        self.intake_listbox.delete(0, tk.END)
        for item in self.manager.intake_queue:
            self.intake_listbox.insert(tk.END, str(item))

        self.inventory_listbox.delete(0, tk.END)
        for item in self.manager.get_all_items():
            self.inventory_listbox.insert(tk.END, str(item))


if __name__ == "__main__":
    root = tk.Tk()
    app = FreshTrackApp(root)
    root.mainloop()
