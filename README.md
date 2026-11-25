:: FreshTrack :- Food Pantry Inventory & Expiration Manager ::

####
My FreshTrack is a Python desktop application built for "CIS 153 (Data Structures)" to help community food pantries track incoming donations in arrival order, look up items quickly, update stock levels, prioritize food expiring soonest.

::: About Project Files :::
`food_item.py`:- Defines the `FoodItem` class (`item_id`, `name`, `category`, `quantity`,          `expiration_date`).

`inventory_manager.py`:- Manages pantry records using a `dict` (O(1) ID lookup), `collections.deque` (FIFO intake queue), input validation, and a custom "Insertion Sort" by expiration date.

`freshtrack_app.py`:- Tkinter graphical user interface (GUI) for volunteers.

`test_freshtrack.py`:- 14 automated `unittest` test cases covering backend logic, sorting, validation, and GUI interactions.

::: How to Run :::
	1. Make sure "Python 3.10+" is installed (no third-party libraries required).
	2. Launch the GUI from the `FreshTrack` folder:
  	 ```bash
   	python freshtrack_app.py
   	```
	3. Run the unit tests:
   	```bash
   	python -m unittest test_freshtrack.py -v
   	```

::: Quick User Guide :::
	1. Record New Donation: Enter a unique Item ID, Food Name, Category, positive whole-number      Quantity, and Expiration Date (`YYYY-MM-DD`), then click Add Donation.
	2. Process Intake Queue: Click "Process Next Intake Item" to shelve the oldest incoming donation in FIFO order (`popleft()`).
	3. Search & Update Stock: Enter an Item ID and click "Search ID" to view and pre-fill its quantity, and then enter a new count, click "Update Qty" (`0` removes depleted items).
	4. Sort by Expiration: Click "Sort by Expiration (Soonest First)" to run custom Insertion Sort and display items expiring soonest at top.
