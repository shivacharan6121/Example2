import customtkinter as ctk
import pymysql
from tkinter import ttk, filedialog

import csv

# Configure theme
ctk.set_appearance_mode("Dark")  # Modes: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("green")  # Themes: "blue", "green", "dark-blue"

# Styled MessageBox
class CustomMessageBox(ctk.CTkToplevel):
    def __init__(self, title, message, color, action=None):
        super().__init__()
        self.title(title)
        self.geometry("450x225")
        #app_width=450
        #app_height=225
        #Ensure MessageBox stays on top and modal
        self.transient(app)
        self.grab_set()
        self.lift()
        self.configure(bg=color)
        self.action = action
        
        #centering MessageBox
        self.update_idletasks()
        width=self.winfo_screenwidth()
        height=self.winfo_screenheight()
        app_width=450
        app_height=225
        x = (width - app_width) // 2
        y = (height - app_height) // 2
        self.geometry(f"+{int(x)}+{int(y)}")
        self.configure(bg=color)
        self.action=action
        

        #self.grab_set()
        
        
        # Label for displaying message
        label = ctk.CTkLabel(self, text=message, font=("Arial", 16), text_color="white")
        label.pack(padx=20,pady=30)

        # Frame to hold buttons
        button_frame = ctk.CTkFrame(self, bg_color=color)
        button_frame.pack(pady=10)

        # OK button
        ok_button = ctk.CTkButton(button_frame, text="OK", command=self.on_ok, fg_color="black", hover_color="gray")
        ok_button.grid(row=0, column=0, padx=10)

        # Cancel button
        cancel_button = ctk.CTkButton(button_frame, text="Cancel", command=self.on_cancel, fg_color="red", hover_color="dark red")
        cancel_button.grid(row=0, column=1, padx=10)
        self.focus_force()
    '''def center_window(self):
        
        parent_x=app.winfo_x()
        parent_y=app.winfo_y()
        parent_width=app.winfo_width()
        parent_height=app.winfo_height()

        x=parent_x + (parent_width//2)-(450//2)
        y=parent_y + (parent_width//2)-(225//2)

        self.geometry(f"450x225+{x}+{y}")'''
                    
            

    def on_ok(self):
        if self.action:
            self.action()
        self.destroy()

    def on_cancel(self):
        self.destroy()

# Database Connection Functions
def execute_query(query, params):
    try:
        conn = pymysql.connect(
            host="localhost", user="root", password="", database="connectors.db"
        )
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        display_data()  # refresh the database items
    except pymysql.Error as err:
        CustomMessageBox("Error", "Database Error could not connect to the server", "#8B0000")

# Function to insert data into the database
def insert_data(part_no, connectors_required):
    if part_no and connectors_required:
        try:
            conn = pymysql.connect(
                host="localhost", user="root", password="", database="connectors.db"
            )
            cursor = conn.cursor()
            cursor.execute("SELECT quantity FROM parts WHERE part_no = %s", (part_no,))
            result = cursor.fetchone()
            conn.close()

            if result:
                existing_quantity = result[0]
                added_quantity = int(connectors_required)
                new_quantity = existing_quantity + added_quantity
                action = lambda: execute_query("UPDATE parts SET quantity = %s WHERE part_no = %s", (new_quantity, part_no))
                CustomMessageBox("Update Confirmation", f"Part No: {part_no}\nNo of Available Connectors: {existing_quantity}\nNo of Added Connectors: {added_quantity}\nTotal No of Connectors: {new_quantity}", "#228B22", action)
            else:
                '''action = lambda: execute_query("INSERT INTO parts (part_no, quantity) VALUES (%s, %s)", (part_no, connectors_required))
                CustomMessageBox("New Entry Confirmation", f"New Part No added: {part_no}\nAdded Connectors: {connectors_required}", "#006400", action)'''
                CustomMessageBox("New Part No Warning", f"New Part No Detected: {part_no}\n The New Part No {part_no} cannot be added here.", "#8B0000")
        except pymysql.Error as err:
            CustomMessageBox("Error", "Database Error could not connect to the server", "#8B0000")
    else:
        CustomMessageBox("Warning", "Please enter valid data!", "#FFD700")
# Function to add a new part (separate function)
def add_part_data(part_no, connectors_required):
    if part_no and connectors_required:
        try:
            conn = pymysql.connect(
                host="localhost", user="root", password="", database="connectors.db"
            )
            cursor = conn.cursor()
            cursor.execute("SELECT part_no FROM parts WHERE part_no = %s", (part_no,))
            result = cursor.fetchone()
            
            if result:
                # Part already exists
                CustomMessageBox("Warning", f"Part No {part_no} already exists!", "#FFD700")
            else:
                # Add new part
                action = lambda: execute_query("INSERT INTO parts (part_no, quantity) VALUES (%s, %s)", (part_no, connectors_required))
                CustomMessageBox("Success", f"New Part No added: {part_no}\nNo of Connectors added: {connectors_required}", "#006400", action)
            
            conn.close()
        except pymysql.Error as err:
            CustomMessageBox("Error", "Database Error could not connect to the server", "#8B0000")
    else:
        CustomMessageBox("Warning", "Please enter valid data!", "#FFD700")

# Function to remove data from the database
def remove_data(part_no, quantity_to_remove):
    if part_no and quantity_to_remove:
        try:
            conn = pymysql.connect(
                host="localhost", user="root", password="", database="connectors.db"
            )
            cursor = conn.cursor()
            cursor.execute("SELECT quantity FROM parts WHERE part_no = %s", (part_no,))
            result = cursor.fetchone()
            conn.close()

            if result:
                current_quantity = result[0]
                removed_quantity = int(quantity_to_remove)
                if current_quantity >= removed_quantity:
                    new_quantity = current_quantity - removed_quantity
                    action = lambda: execute_query("UPDATE parts SET quantity = %s WHERE part_no = %s", (new_quantity, part_no))
                    CustomMessageBox("Removal Confirmation", f"Part No: {part_no}\nNo of Required Connectors: {removed_quantity}\nNo of Remaining Connectors: {new_quantity}", "#FF4500", action)
                else:
                    CustomMessageBox("Warning", f"Insufficient Connectors\nNo of Available Connectors: {current_quantity}\nNo of Required Connectors: {removed_quantity}", "#FFD700")
            else:
                CustomMessageBox("Error", f"Invalid Part No: {part_no}", "#8B0000")
        except pymysql.Error as err:
            CustomMessageBox("Error", "Database Error could not connect to the server", "#8B0000")
    else:
        CustomMessageBox("Warning", "Please enter valid data!", "#FFD700")

# Function to display data in the table
def display_data(search_query=None):
    for i in table.get_children():
        table.delete(i)
    try:
        conn = pymysql.connect(
            host="localhost", user="root", password="", database="connectors.db"
        )
        cursor = conn.cursor()
        if search_query:
            # Filter records based on the search query
            cursor.execute("SELECT * FROM parts WHERE part_no LIKE %s", (f"%{search_query}%",))
        else:
            # Show all records
            cursor.execute("SELECT * FROM parts")
        rows = cursor.fetchall()
        for idx, row in enumerate(rows, start=1):
            table.insert("", "end", values=(idx, row[0], row[1]), tags=("even" if idx % 2 == 0 else "odd"))
        conn.close()
    except pymysql.Error as err:
        CustomMessageBox("Error", "Database Error could not connect to the server", "#8B0000")

# Function to handle search button click
def on_search():
    search_query = search_entry.get()
    if search_query:
        try:
            conn = pymysql.connect(host="localhost", user="root", password="", database="connectors.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM parts WHERE part_no = %s", (search_query, ))
            result=cursor.fetchone()
            conn.close()
            if not result:
                CustomMessageBox("Warning", f"Part No '{search_query}' does not exist!", "#FFD700")
            else:
                display_data(search_query)
        except pymysql.Error as err:
            CustomMessageBox("Error", "Database Error could not connect to the server", "#8B0000")

    else:
        display_data()
            
    display_data(search_query)
# Function to download data to a CSV file
def download_data():
    try:
        conn = pymysql.connect(
            host="localhost", user="root", password="", database="connectors.db"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM parts")
        rows = cursor.fetchall()
        conn.close()

        file_path=filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            with open(file_path, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Part No", "Quantity"])
                writer.writerows(rows)
            CustomMessageBox("Success", f"Data downloaded successfully at:\n{file_path}", "#228B22")
    except pymysql.Error as err:
        CustomMessageBox("Error", "Database Error could not connect to the server", "#8B0000")

# GUI Setup
app = ctk.CTk()
app.title("Connector Management System")
width = app.winfo_screenwidth()
height = app.winfo_screenheight()
app.geometry(f'{width}x{height}+0+0')
#app.geometry("500x600")
#app.attributes('-zoomed',True)
#app.after(10,lambda:app._set_window_state("zoomed"))
# Title
title_label = ctk.CTkLabel(app, text="CONNECTOR MANAGEMENT SYSTEM", font=("'Poppins',sans-serif", 35, "bold"))
title_label.pack(pady=10)

# Menu Bar
menu_bar = ctk.CTkFrame(app, fg_color=None)
menu_bar.pack(fill="x", padx=20, pady=10)

add_part_button = ctk.CTkButton(menu_bar, text="Add Part", command=lambda: show_container("add_part"), font=("'Poppins',sans-serif", 15))
add_part_button.grid(row=0, column=0, padx=5)

add_connectors_button = ctk.CTkButton(menu_bar, text="Add Connectors", command=lambda: show_container("add_connectors"), font=("'Poppins',sans-serif", 15))
add_connectors_button.grid(row=0, column=1, padx=5)

remove_connectors_button = ctk.CTkButton(menu_bar, text="Required Connectors", command=lambda: show_container("remove_connectors"), font=("'Poppins',sans-serif", 15))
remove_connectors_button.grid(row=0, column=2, padx=5)

view_button = ctk.CTkButton(menu_bar, text="View", command=lambda: show_container("view"), font=("'Poppins',sans-serif", 15))
view_button.grid(row=0, column=3, padx=5)

download_button = ctk.CTkButton(menu_bar, text="Downloads", command=download_data, font=("'Poppins',sans-serif", 15))
download_button.grid(row=0, column=4, padx=5)

# Exit Button
exit_button = ctk.CTkButton(menu_bar, text="Exit", command=app.destroy, font=("'Poppins',sans-serif", 15))
exit_button.grid(row=0, column=5, padx=5)

# Container Frame
container_frame = ctk.CTkFrame(app)
container_frame.pack(fill="both", expand=True, padx=200, pady=100)

# Add Part Container
add_part_container = ctk.CTkFrame(container_frame)
add_part_label = ctk.CTkLabel(add_part_container, text="Add Parts", font=("'Poppins',sans-serif", 30, "bold"))
add_part_label.pack(padx=20,pady=20)

part_no_label = ctk.CTkLabel(add_part_container, text="Enter New Part No:", font=("'Poppins',sans-serif", 15, "bold"))
part_no_label.pack(pady=5)
part_entry_add_part = ctk.CTkEntry(add_part_container, width=250, font=("'Poppins',sans-serif", 15), placeholder_text="Enter new part no")
part_entry_add_part.pack(pady=5)

connectors_label = ctk.CTkLabel(add_part_container, text="Add No. of Connectors:", font=("'Poppins',sans-serif", 15, "bold"))
connectors_label.pack(pady=5)
connectors_entry_add_part = ctk.CTkEntry(add_part_container, width=250, font=("'Poppins',sans-serif", 15), placeholder_text="Enter no of connectors")
connectors_entry_add_part.pack(pady=5)

add_part_button = ctk.CTkButton(add_part_container, text="ADD NEW PART", command=lambda: add_part_data(part_entry_add_part.get(), connectors_entry_add_part.get()), fg_color="green", hover_color="dark green", font=("Arial", 12, "bold"))
add_part_button.pack(pady=10)

# Add Connectors Container
add_connectors_container = ctk.CTkFrame(container_frame)
add_connectors_label = ctk.CTkLabel(add_connectors_container, text="Add Connectors", font=("'Poppins',sans-serif", 30, "bold"))
add_connectors_label.pack(padx=20,pady=20)

part_no_label = ctk.CTkLabel(add_connectors_container, text="Enter Part No:", font=("'Poppins',sans-serif", 15, "bold"))
part_no_label.pack(pady=5)
part_entry_add_connectors = ctk.CTkEntry(add_connectors_container, width=250, font=("'Poppins',sans-serif", 15), placeholder_text="Enter part no")
part_entry_add_connectors.pack(pady=5)

connectors_label = ctk.CTkLabel(add_connectors_container, text="Add No. of Connectors:", font=("'Poppins',sans-serif", 15, "bold"))
connectors_label.pack(pady=5)
connectors_entry_add_connectors = ctk.CTkEntry(add_connectors_container, width=250, font=("'Poppins',sans-serif", 15), placeholder_text="Enter no of connectors")
connectors_entry_add_connectors.pack(pady=5)

add_connectors_button = ctk.CTkButton(add_connectors_container, text="ADD CONNECTORS", command=lambda: insert_data(part_entry_add_connectors.get(), connectors_entry_add_connectors.get()), fg_color="green", hover_color="dark green", font=("Arial", 12, "bold"))
add_connectors_button.pack(pady=10)

# Remove Connectors Container
remove_connectors_container = ctk.CTkFrame(container_frame)
remove_connectors_label = ctk.CTkLabel(remove_connectors_container, text="Required Connectors", font=("'Poppins',sans-serif", 30, "bold"))
remove_connectors_label.pack(padx=20,pady=20)

part_no_label = ctk.CTkLabel(remove_connectors_container, text="Enter Part No:", font=("'Poppins',sans-serif", 15, "bold"))
part_no_label.pack(pady=5)
part_entry_remove_connectors = ctk.CTkEntry(remove_connectors_container, width=250, font=("'Poppins',sans-serif", 15), placeholder_text="Enter part no")
part_entry_remove_connectors.pack(pady=5)

connectors_label = ctk.CTkLabel(remove_connectors_container, text="No. of Connectors Required:", font=("'Poppins',sans-serif", 15, "bold"))
connectors_label.pack(pady=5)
connectors_entry_remove_connectors = ctk.CTkEntry(remove_connectors_container, width=250, font=("'Poppins',sans-serif", 15),placeholder_text="Enter no of connectors ")
connectors_entry_remove_connectors.pack(pady=5)

remove_connectors_button = ctk.CTkButton(remove_connectors_container, text="REQUIRED CONNECTORS", command=lambda: remove_data(part_entry_remove_connectors.get(), connectors_entry_remove_connectors.get()), fg_color="red", hover_color="dark red", font=("Arial", 12, "bold"))
remove_connectors_button.pack(pady=10)

'''# View Container
view_container = ctk.CTkFrame(container_frame)
table_frame = ctk.CTkFrame(view_container)
table_frame.pack(fill="both", expand=True, padx=20, pady=10)

columns = ("Serial No", "Part No", "Quantity")
table = ttk.Treeview(table_frame, columns=columns, show="headings")
for col in columns:
    table.heading(col, text=col)
    table.column(col, anchor="center", width=150)

table.pack(fill="both", expand=True)'''
# View Container
view_container = ctk.CTkFrame(container_frame)

# Search Bar and Button
search_frame = ctk.CTkFrame(view_container)
search_frame.pack(fill="x", padx=20, pady=10)

search_entry = ctk.CTkEntry(search_frame, width=300, placeholder_text="Search by Part No")
search_entry.grid(row=0, column=0, padx=5, pady=5)

search_button = ctk.CTkButton(search_frame, text="Search", command=on_search, fg_color="blue", hover_color="dark blue")
search_button.grid(row=0, column=1, padx=5, pady=5)

# Table Frame
table_frame = ctk.CTkFrame(view_container)
table_frame.pack(fill="both", expand=True, padx=20, pady=10)

columns = ("Serial No", "Part No", "Quantity")
table = ttk.Treeview(table_frame, columns=columns, show="headings")
for col in columns:
    table.heading(col, text=col)
    table.column(col, anchor="center", width=150)

table.pack(fill="both", expand=True)


# Function to show the selected container
def show_container(container_name):
    for widget in container_frame.winfo_children():
        widget.pack_forget()

    if container_name == "add_part":
        add_part_container.pack(fill="both", expand=True)
    elif container_name == "add_connectors":
        add_connectors_container.pack(fill="both", expand=True)
    elif container_name == "remove_connectors":
        remove_connectors_container.pack(fill="both", expand=True)
    elif container_name == "view":
        view_container.pack(fill="both", expand=True)
        display_data()

# Initially show the add part container
show_container("add_part")

app.mainloop()
