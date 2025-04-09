import tkinter as tk
from tkinter import messagebox
import mysql.connector

# Establish database connection
def db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="psswd",  # Replace with your MySQL password
        database="BusReservation"
    )

# Handle user authentication (login)
def login_user():
    username = username_entry.get()
    password = password_entry.get()

    if username and password:
        db = db_connection()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM Users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        db.close()

        if user:
            messagebox.showinfo("Login Success", "Login Successful!")
            show_bus_selection_window(user[0])  # Pass user_id for further use
        else:
            messagebox.showerror("Login Error", "Invalid username or password!")
    else:
        messagebox.showwarning("Input Error", "Please enter both username and password!")

# Show sign-up window
def show_signup_window():
    signup_window = tk.Toplevel(root)
    signup_window.title("Sign Up")
    signup_window.geometry("400x350")  # Increased height for gender selection
    signup_window.transient(root)  # Set relationship with main window
    
    # Make this window modal (block interaction with parent)
    signup_window.grab_set()

    def signup_user():
        username = signup_username_entry.get()
        password = signup_password_entry.get()
        email = signup_email_entry.get()
        phone = signup_phone_entry.get()
        gender = gender_var.get()

        if username and password and email and phone and gender:
            db = db_connection()
            cursor = db.cursor()
            cursor.execute("INSERT INTO Users (username, password, email, phone, gender) VALUES (%s, %s, %s, %s, %s)", 
                          (username, password, email, phone, gender))
            db.commit()
            db.close()
            messagebox.showinfo("Sign Up Success", "User registered successfully!")
            signup_window.destroy()  # Close sign-up window after success
        else:
            messagebox.showwarning("Input Error", "Please fill in all fields!")

    signup_username_label = tk.Label(signup_window, text="Username:")
    signup_username_label.pack(pady=5)
    signup_username_entry = tk.Entry(signup_window)
    signup_username_entry.pack(pady=5)

    signup_password_label = tk.Label(signup_window, text="Password:")
    signup_password_label.pack(pady=5)
    signup_password_entry = tk.Entry(signup_window, show="*")
    signup_password_entry.pack(pady=5)

    signup_email_label = tk.Label(signup_window, text="Email:")
    signup_email_label.pack(pady=5)
    signup_email_entry = tk.Entry(signup_window)
    signup_email_entry.pack(pady=5)

    signup_phone_label = tk.Label(signup_window, text="Phone:")
    signup_phone_label.pack(pady=5)
    signup_phone_entry = tk.Entry(signup_window)
    signup_phone_entry.pack(pady=5)

    # Gender selection
    gender_label = tk.Label(signup_window, text="Gender:")
    gender_label.pack(pady=5)
    
    gender_var = tk.StringVar(value="other")
    gender_frame = tk.Frame(signup_window)
    gender_frame.pack(pady=5)
    
    male_radio = tk.Radiobutton(gender_frame, text="Male", variable=gender_var, value="male")
    male_radio.pack(side=tk.LEFT, padx=10)
    
    female_radio = tk.Radiobutton(gender_frame, text="Female", variable=gender_var, value="female")
    female_radio.pack(side=tk.LEFT, padx=10)
    
    other_radio = tk.Radiobutton(gender_frame, text="Other", variable=gender_var, value="other")
    other_radio.pack(side=tk.LEFT, padx=10)

    signup_button = tk.Button(signup_window, text="Sign Up", command=signup_user)
    signup_button.pack(pady=15)

# Show bus selection window after successful login
def show_bus_selection_window(user_id):
    # Close login form after successful login
    root.withdraw()  # Hide the main window instead of destroying it
    
    bus_selection_window = tk.Toplevel(root)
    bus_selection_window.title("Select Bus")
    bus_selection_window.geometry("600x500")  # Increased window size
    
    # When this window is closed, exit the application
    bus_selection_window.protocol("WM_DELETE_WINDOW", lambda: on_closing(bus_selection_window))

    db = db_connection()
    cursor = db.cursor()
    
    # Modified query to get bus details along with available seats count
    cursor.execute("""
        SELECT b.bus_id, b.bus_name, b.source, b.destination, b.departure_time, 
               COUNT(CASE WHEN s.status = 'available' THEN 1 ELSE NULL END) AS available_seats,
               b.total_seats
        FROM Buses b
        LEFT JOIN Seats s ON b.bus_id = s.bus_id
        GROUP BY b.bus_id
    """)
    buses = cursor.fetchall()
    db.close()

    # Add search functionality
    def search_buses():
        search_text = search_entry.get().lower()
        bus_listbox.delete(0, tk.END)  # Clear previous list
        for bus in buses:
            if (search_text in bus[1].lower() or search_text in bus[2].lower() or 
                search_text in bus[3].lower()):
                bus_listbox.insert(tk.END, f"{bus[1]} ({bus[2]} to {bus[3]}) - {bus[5]}/{bus[6]} seats available")

    search_label = tk.Label(bus_selection_window, text="Search Bus (name or route):")
    search_label.pack(pady=10)

    search_entry = tk.Entry(bus_selection_window, width=40)
    search_entry.pack(pady=5)

    search_button = tk.Button(bus_selection_window, text="Search", command=search_buses)
    search_button.pack(pady=5)

    # Bus list with heading
    bus_list_label = tk.Label(bus_selection_window, text="Available Buses", font=("Arial", 12, "bold"))
    bus_list_label.pack(pady=10)
    
    # Create frame for bus list
    list_frame = tk.Frame(bus_selection_window)
    list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    # Create scrollbar
    scrollbar = tk.Scrollbar(list_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Create listbox with scrollbar
    bus_listbox = tk.Listbox(list_frame, width=60, height=12, font=("Arial", 10))
    bus_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # Configure scrollbar
    scrollbar.config(command=bus_listbox.yview)
    bus_listbox.config(yscrollcommand=scrollbar.set)

    def select_bus(user_id, bus_id):
        # This function will handle seat selection for the selected bus
        show_seat_selection_window(user_id, bus_id, bus_selection_window)

    # Initially populate the listbox with all buses - without departure date
    for bus in buses:
        bus_listbox.insert(tk.END, f"{bus[1]} ({bus[2]} to {bus[3]}) - {bus[5]}/{bus[6]} seats available")

    def on_bus_select():
        selected_bus = bus_listbox.curselection()
        if selected_bus:
            bus_id = buses[selected_bus[0]][0]
            select_bus(user_id, bus_id)  # Pass user_id and bus_id
        else:
            messagebox.showwarning("Selection Error", "Please select a bus from the list.")

    # Control frame for buttons
    control_frame = tk.Frame(bus_selection_window)
    control_frame.pack(pady=10, fill=tk.X)
    
    select_button = tk.Button(control_frame, text="Select Bus", width=15, command=on_bus_select)
    select_button.pack(side=tk.LEFT, padx=20)
    
    refresh_button = tk.Button(control_frame, text="Refresh List", width=15, 
                              command=lambda: refresh_bus_list(bus_listbox, buses))
    refresh_button.pack(side=tk.RIGHT, padx=20)

def refresh_bus_list(bus_listbox, buses):
    # Refresh the bus list data
    db = db_connection()
    cursor = db.cursor()
    cursor.execute("""
        SELECT b.bus_id, b.bus_name, b.source, b.destination, b.departure_time, 
               COUNT(CASE WHEN s.status = 'available' THEN 1 ELSE NULL END) AS available_seats,
               b.total_seats
        FROM Buses b
        LEFT JOIN Seats s ON b.bus_id = s.bus_id
        GROUP BY b.bus_id
    """)
    updated_buses = cursor.fetchall()
    db.close()
    
    # Update the listbox - without departure date
    bus_listbox.delete(0, tk.END)
    for bus in updated_buses:
        bus_listbox.insert(tk.END, f"{bus[1]} ({bus[2]} to {bus[3]}) - {bus[5]}/{bus[6]} seats available")
    
    # Update the buses variable in the parent function's scope
    buses[:] = updated_buses  # Update the original list in-place

# Function to get adjacent seat numbers based on seat layout - CORRECTED VERSION
def get_adjacent_seats(seat_number, total_seats):
    seat_num = int(seat_number)
    adjacent_seats = []
    
    # Bus layout: 2 seats on each side of aisle
    # Left side: 1,2,5,6,...
    # Right side: 3,4,7,8,...
    
    # Calculate row and position
    row = (seat_num - 1) // 4  # Each row has 4 seats
    position = (seat_num - 1) % 4  # Position within the row (0,1,2,3)
    
    # Same row, adjacent seat (if any)
    if position == 0:  # Left window
        adjacent_seats.append(str(seat_num + 1))  # Left aisle
    elif position == 1:  # Left aisle
        adjacent_seats.append(str(seat_num - 1))  # Left window
        if seat_num + 1 <= total_seats and (seat_num + 1) % 4 == 3:
            adjacent_seats.append(str(seat_num + 1))  # Right aisle (across aisle)
    elif position == 2:  # Right aisle
        adjacent_seats.append(str(seat_num + 1))  # Right window
        if seat_num - 1 > 0 and (seat_num - 1) % 4 == 1:
            adjacent_seats.append(str(seat_num - 1))  # Left aisle (across aisle)
    elif position == 3:  # Right window
        adjacent_seats.append(str(seat_num - 1))  # Right aisle
    
    return adjacent_seats

# Show seat selection window
def show_seat_selection_window(user_id, bus_id, parent_window):
    seat_selection_window = tk.Toplevel(parent_window)
    seat_selection_window.title("Select Seats")
    seat_selection_window.geometry("600x550")  # Larger window for better view
    seat_selection_window.transient(parent_window)  # Set relationship
    
    # When this window is closed, return to parent window
    seat_selection_window.protocol("WM_DELETE_WINDOW", lambda: seat_selection_window.destroy())

    # Get the user's gender
    db = db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT gender FROM Users WHERE user_id = %s", (user_id,))
    user_gender_result = cursor.fetchone()
    user_gender = user_gender_result[0] if user_gender_result else "other"
    
    # Store user gender for later use
    current_user_gender = user_gender.lower()

    # Retrieve bus details and information about booked seats
    cursor.execute("SELECT bus_name FROM Buses WHERE bus_id = %s", (bus_id,))
    bus_name = cursor.fetchone()[0]
    
    cursor.execute("SELECT total_seats FROM Buses WHERE bus_id = %s", (bus_id,))
    total_seats = cursor.fetchone()[0]
    
    # Get seat information including gender of the user who booked it
    cursor.execute("""
        SELECT s.seat_id, s.seat_number, s.status, s.user_id, IFNULL(u.gender, 'other') as gender 
        FROM Seats s 
        LEFT JOIN Users u ON s.user_id = u.user_id 
        WHERE s.bus_id = %s
    """, (bus_id,))
    
    seats = cursor.fetchall()
    db.close()

    # Create a dictionary of seats for easy lookup
    seat_dict = {s[1]: s for s in seats}
    
    # Find all seats booked by female users
    female_booked_seats = [s[1] for s in seats if s[2] == "booked" and s[4].lower() == "female"]
    
    # Find all seats adjacent to female-booked seats
    restricted_seats = set()
    for female_seat in female_booked_seats:
        adjacent_seats = get_adjacent_seats(female_seat, total_seats)
        restricted_seats.update(adjacent_seats)
    
    # Title and bus info at the top
    title_frame = tk.Frame(seat_selection_window)
    title_frame.pack(fill=tk.X, pady=10)
    
    bus_title = tk.Label(title_frame, text=f"Bus: {bus_name}", font=("Arial", 12, "bold"))
    bus_title.pack()
    
    # Legend for seat colors
    legend_frame = tk.Frame(seat_selection_window)
    legend_frame.pack(fill=tk.X, pady=5)
    
    tk.Label(legend_frame, text="Legend:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=10)
    
    # Available seat legend
    av_frame = tk.Frame(legend_frame)
    av_frame.pack(side=tk.LEFT, padx=5)
    av_color = tk.Label(av_frame, bg="green", width=2, height=1)
    av_color.pack(side=tk.LEFT)
    tk.Label(av_frame, text="Available").pack(side=tk.LEFT, padx=2)
    
    # Selected seat legend
    sel_frame = tk.Frame(legend_frame)
    sel_frame.pack(side=tk.LEFT, padx=5)
    sel_color = tk.Label(sel_frame, bg="blue", width=2, height=1)
    sel_color.pack(side=tk.LEFT)
    tk.Label(sel_frame, text="Selected").pack(side=tk.LEFT, padx=2)
    
    # Booked by male legend
    male_frame = tk.Frame(legend_frame)
    male_frame.pack(side=tk.LEFT, padx=5)
    male_color = tk.Label(male_frame, bg="red", width=2, height=1)
    male_color.pack(side=tk.LEFT)
    tk.Label(male_frame, text="Booked (Male)").pack(side=tk.LEFT, padx=2)
    
    # Booked by female legend
    female_frame = tk.Frame(legend_frame)
    female_frame.pack(side=tk.LEFT, padx=5)
    female_color = tk.Label(female_frame, bg="pink", width=2, height=1)
    female_color.pack(side=tk.LEFT)
    tk.Label(female_frame, text="Booked (Female)").pack(side=tk.LEFT, padx=2)
    
    # Restricted seat legend (new)
    restricted_frame = tk.Frame(legend_frame)
    restricted_frame.pack(side=tk.LEFT, padx=5)
    restricted_color = tk.Label(restricted_frame, bg="orange", width=2, height=1)
    restricted_color.pack(side=tk.LEFT)
    tk.Label(restricted_frame, text="Female Only").pack(side=tk.LEFT, padx=2)

    # Create a main frame for the seat layout
    main_frame = tk.Frame(seat_selection_window)
    main_frame.pack(pady=10)

    seat_buttons = {}
    selected_seats = []  # Initialize here, inside the function

    # Generate seat layout (20 seats on each side of the aisle)
    rows = 10  # 10 rows of seats

    for row in range(rows):
        # Left side seats (2 columns)
        for col in range(2):
            seat_number = f"{row * 4 + col + 1}"
            seat = next((s for s in seats if s[1] == seat_number), None)

            if seat:
                if seat[2] == "available":
                    # Check if this is a restricted seat (next to female passenger)
                    if seat_number in restricted_seats:
                        if current_user_gender == "female":
                            # Female user can book this seat
                            seat_button = tk.Button(main_frame, text=seat_number, width=5, height=2, bg="green", 
                                                command=lambda s=seat_number: toggle_seat(s, seat_buttons, selected_seats))
                        else:
                            # Non-female users can't book this seat
                            seat_button = tk.Button(main_frame, text=seat_number, width=5, height=2, 
                                                 bg="orange", state="disabled")
                            seat_button.config(text=f"{seat_number}*")  # Add asterisk to indicate restriction
                    else:
                        # Regular available seat
                        seat_button = tk.Button(main_frame, text=seat_number, width=5, height=2, bg="green", 
                                              command=lambda s=seat_number: toggle_seat(s, seat_buttons, selected_seats))
                elif seat[2] == "booked":
                    # Seat is already booked
                    gender = seat[4]
                    
                    # Set color based on gender - case insensitive comparison
                    if gender and gender.lower() == "female":
                        bg_color = "pink"
                    else:
                        bg_color = "red"
                        
                    seat_button = tk.Button(main_frame, text=seat_number, width=5, height=2, 
                                          bg=bg_color, state="disabled")
                
                seat_buttons[seat_number] = seat_button
                seat_button.grid(row=row, column=col, padx=5, pady=5)

        # Aisle separator (middle column)
        aisle_label = tk.Label(main_frame, text="", width=2)
        aisle_label.grid(row=row, column=2, padx=5, pady=5)

        # Right side seats (2 columns)
        for col in range(2):
            seat_number = f"{row * 4 + col + 3}"  # Adjusted to start from 3 (after the aisle)
            seat = next((s for s in seats if s[1] == seat_number), None)

            if seat:
                if seat[2] == "available":
                    # Check if this is a restricted seat (next to female passenger)
                    if seat_number in restricted_seats:
                        if current_user_gender == "female":
                            # Female user can book this seat
                            seat_button = tk.Button(main_frame, text=seat_number, width=5, height=2, bg="green", 
                                                command=lambda s=seat_number: toggle_seat(s, seat_buttons, selected_seats))
                        else:
                            # Non-female users can't book this seat
                            seat_button = tk.Button(main_frame, text=seat_number, width=5, height=2, 
                                                 bg="orange", state="disabled")
                            seat_button.config(text=f"{seat_number}*")  # Add asterisk to indicate restriction
                    else:
                        # Regular available seat
                        seat_button = tk.Button(main_frame, text=seat_number, width=5, height=2, bg="green", 
                                              command=lambda s=seat_number: toggle_seat(s, seat_buttons, selected_seats))
                elif seat[2] == "booked":
                    # Seat is already booked
                    gender = seat[4]
                    
                    # Set color based on gender - case insensitive comparison
                    if gender and gender.lower() == "female":
                        bg_color = "pink"
                    else:
                        bg_color = "red"
                        
                    seat_button = tk.Button(main_frame, text=seat_number, width=5, height=2, 
                                          bg=bg_color, state="disabled")
                
                seat_buttons[seat_number] = seat_button
                seat_button.grid(row=row, column=col+3, padx=5, pady=5)  # col+3 because of the aisle

    # Add driver seat 
    driver_seat_button = tk.Button(main_frame, text="D", width=5, height=2, bg="yellow", state="disabled")
    driver_seat_button.grid(row=0, column=0, padx=5, pady=5)

    # Add restriction info label
    restriction_label = tk.Label(seat_selection_window, text="* Seats marked with asterisk can only be booked by female passengers", 
                             font=("Arial", 9, "italic"))
    restriction_label.pack(pady=5)

    # Status frame for showing selection count
    status_frame = tk.Frame(seat_selection_window)
    status_frame.pack(fill=tk.X, pady=5)
    
    selection_label = tk.Label(status_frame, text="Selected: 0 seats", font=("Arial", 10))
    selection_label.pack()

    def toggle_seat(seat_number, seat_buttons, selected_seats):
        seat_button = seat_buttons[seat_number]
        if seat_button.cget("bg") == "green":  # If the seat is available
            seat_button.config(bg="blue")  # Mark as selected
            selected_seats.append(seat_number)
        elif seat_button.cget("bg") == "blue":  # If the seat is selected
            seat_button.config(bg="green")  # Deselect it
            selected_seats.remove(seat_number)
        
        # Update selection count
        selection_label.config(text=f"Selected: {len(selected_seats)} seats")

    def book_seats():
        if selected_seats:
            db = db_connection()
            cursor = db.cursor()
            
            # Count the number of selected seats
            total_tickets = len(selected_seats)
            
            # Insert into Bookings table
            cursor.execute("INSERT INTO Bookings (user_id, bus_id, total_tickets) VALUES (%s, %s, %s)", 
                          (user_id, bus_id, total_tickets))
            db.commit()
            
            # Get the booking_id of the newly inserted booking
            cursor.execute("SELECT LAST_INSERT_ID()")
            booking_id = cursor.fetchone()[0]
            
            # Update the status of each seat to 'booked' and assign the user_id
            for seat_number in selected_seats:
                cursor.execute("UPDATE Seats SET status = %s, user_id = %s WHERE seat_number = %s AND bus_id = %s", 
                              ("booked", user_id, seat_number, bus_id))
            
            db.commit()  # Commit all changes
            db.close()
            
            messagebox.showinfo("Booking Success", f"{total_tickets} seats successfully booked!")
            seat_selection_window.destroy()  # Close window after booking
        else:
            messagebox.showwarning("Selection Error", "Please select at least one seat.")

    # Button frame
    button_frame = tk.Frame(seat_selection_window)
    button_frame.pack(fill=tk.X, pady=15)
    
    book_button = tk.Button(button_frame, text="Book Selected Seats", width=20, 
                           command=book_seats, font=("Arial", 10, "bold"))
    book_button.pack(side=tk.RIGHT, padx=20)
    
    cancel_button = tk.Button(button_frame, text="Cancel", width=15, 
                             command=lambda: seat_selection_window.destroy())
    cancel_button.pack(side=tk.LEFT, padx=20)

# Function to handle window closing events
def on_closing(window):
    window.destroy()
    root.destroy()  # Destroy the main application when a window is closed
    
# Main root window
root = tk.Tk()
root.title("Bus Reservation System")
root.geometry("450x350")

# Creating a welcome frame
welcome_frame = tk.Frame(root)
welcome_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

# Title
title_label = tk.Label(welcome_frame, text="Bus Reservation System", font=("Arial", 16, "bold"))
title_label.pack(pady=20)

# Login frame
login_frame = tk.Frame(welcome_frame, bd=2, relief=tk.GROOVE, padx=15, pady=15)
login_frame.pack(fill=tk.X)

login_title = tk.Label(login_frame, text="User Login", font=("Arial", 12, "bold"))
login_title.pack(pady=5)

username_label = tk.Label(login_frame, text="Username:")
username_label.pack(pady=5)
username_entry = tk.Entry(login_frame, width=30)
username_entry.pack(pady=5)

password_label = tk.Label(login_frame, text="Password:")
password_label.pack(pady=5)
password_entry = tk.Entry(login_frame, show="*", width=30)
password_entry.pack(pady=5)

button_frame = tk.Frame(login_frame)
button_frame.pack(pady=10)

login_button = tk.Button(button_frame, text="Login", width=10, command=login_user)
login_button.pack(side=tk.LEFT, padx=10)

signup_button = tk.Button(button_frame, text="Sign Up", width=10, command=show_signup_window)
signup_button.pack(side=tk.LEFT, padx=10)

# Set up closing protocol for main window
root.protocol("WM_DELETE_WINDOW", lambda: root.destroy())

# Start the application
root.mainloop()