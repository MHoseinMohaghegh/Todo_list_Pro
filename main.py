# Import necessary libraries
import tkinter as tk  # Import the tkinter library and alias it as tk
import tkinter  # Import the tkinter module
from tkinter import ttk  # Import the ttk module from tkinter
from tkinter import *  # Import all classes from tkinter
from tkcalendar import Calendar  # Import the Calendar class from tkcalendar module
import sqlite3  # Import the sqlite3 module for SQLite database operations
import form2  # Import form2 module assuming it contains necessary functions
# Import messagebox module from tkinter for displaying messages
from tkinter import messagebox
import datetime  # Import datetime module for date and time operations
import babel.numbers  # Import numbers module from babel for number formatting


# Connect to the SQLite database
conn = sqlite3.connect("data_base.db")

# Create a cursor object to execute SQL commands
cur = conn.cursor()

# Create tasks table if it doesn't exist
cur.execute('''CREATE TABLE IF NOT EXISTS tasks (
                task_id INTEGER PRIMARY KEY,
                task_date DATE NOT NULL,
                task_description TEXT NOT NULL,
                task_status TEXT DEFAULT 'Not Done'
            )''')


def show():
    """
    Function to show tasks for the selected date.
    """
    # Check if the user has chosen date or not
    if not form2.chosen_date:
        messagebox.showwarning(
            "Warning", "Please choose a valid date.")
        return

    # Creating tasks dict for task ids
    global tasks_dict
    tasks_dict = {}
    # Query tasks for the chosen date from the database
    cur.execute(
        "SELECT task_description FROM tasks WHERE task_date = ?", (form2.chosen_date,))
    tasks = cur.fetchall()  # Fetch all tasks for the chosen date

    if tasks:
        # Add task numbers to descriptions
        global task_descriptions
        task_descriptions = [
            f"{task[0]}" for i, task in enumerate(tasks)]
        tasks_combo['values'] = [
            f"Task {i+1}" for i in range(len(task_descriptions))]
        cur.execute(
            "SELECT task_id FROM tasks WHERE task_date = ?", (form2.chosen_date,))
        tasks_ids = cur.fetchall()  # Fetch all tasks for the chosen date
        for i, task_id in enumerate(tasks_ids):
            tasks_dict[f"Task {i+1}"] = (task_id)

        # Set the combobox selection to the first task
        tasks_combo.current(0)

        # Display the description of the first task
        show_selected_task(None)
        new_button.config(state='normal')
        edit_button.config(state='normal')
        delete_button.config(state='normal')
    else:
        tasks_combo['values'] = [""]
        tasks_combo.current(0)
        done_button.config(background='white')
        not_done_button.config(background='white')
        clear_data()
        new_button.config(state='normal')
        edit_button.config(state='disabled')
        delete_button.config(state='disabled')
        # Display a message if there are no tasks for the selected date
        messagebox.showwarning(
            "Warning", "There are no tasks for the selected date.")


def show_selected_task(event):
    """
    Function to display the selected task description.
    """
    selected_task = tasks_combo.get()  # Get the selected task from the combobox
    if selected_task:
        # Extract the task number and convert it to an index
        task_index = int(selected_task.split()[1]) - 1
        if 0 <= task_index < len(task_descriptions):
            # Get the corresponding task description from the task_descriptions list
            selected_task_description = task_descriptions[task_index]
            # Clear the data text widget
            data.delete('1.0', tk.END)
            # Display the selected task description in the data text widget
            data.insert(tk.END, selected_task_description)
            cur.execute(
                "SELECT task_status FROM tasks WHERE task_id = ?", (tasks_dict[selected_task][0],))
            status = cur.fetchone()  # Use fetchone() since we expect only one result
            if status and status[0] == 'Done':  # Access the value inside the tuple
                done_button.config(background='green')
                not_done_button.config(background='red')
            else:
                not_done_button.config(background='green')
                done_button.config(background='red')


def clear_data():
    """
    Function to clear the data text widget.
    """
    data.delete('1.0', tk.END)  # Clear the text widget


def toggle_new_button():
    """
    Function to toggle between adding a new task and saving the task.
    """
    current_date = form2.chosen_date

    # Check if the chosen date is not in the past
    if current_date < datetime.date.today().isoformat():
        messagebox.showwarning(
            "Warning", "You cannot add tasks to past dates.")
        return
    elif current_date == datetime.date.today().isoformat():
        messagebox.showwarning(
            "Warning", "You cannot add tasks on today.")
        return

    if new_button.cget('text') == 'New' and form2.chosen_date:  # If button text is "New"
        clear_data()  # Clear the text widget
        tasks_combo['values'] = ['New Task']
        tasks_combo.current(0)
        new_button.config(text='Save')  # Change button text to "Save"
        edit_button.config(state='disabled')
        history_button.config(state='disabled')
        delete_button.config(state='disabled')
    elif form2.chosen_date:  # If button text is "Save"
        save_task()  # Save the task
        clear_data()  # Clear the text widget
        tasks_combo['values'] = ['']
        tasks_combo.current(0)
        show()
        tasks_combo.current(len(tasks_combo['values']) - 1)
        show_selected_task(None)
        new_button.config(text='New')  # Change button text back to "New"
        edit_button.config(state='normal')
        history_button.config(state='normal')
        delete_button.config(state='normal')
    else:
        messagebox.showwarning(
            'Warning', 'Please enter a valid Date.')


def save_task():
    """
    Function to save a new task to the database.
    """
    # Get task description from text widget
    task_description = data.get("1.0", tk.END).strip()

    if task_description and form2.chosen_date:  # If task description is not empty

        # Get the current date
        current_date = form2.chosen_date
        # Insert the new task into the database
        cur.execute("INSERT INTO tasks (task_date, task_description) VALUES (?, ?)",
                    (current_date, task_description))
        conn.commit()  # Commit the transaction
        clear_data()  # Clear the text widget after saving
        show()  # Calling show function
    elif form2.chosen_date:
        messagebox.showwarning(
            "Warning", "Please enter a task description.")
    elif task_description:
        messagebox.showwarning(
            "Warning", "Please enter a valid task date.")
    else:
        messagebox.showwarning(
            "Warning", "Please enter a task description and a valid task date.")


def edit():
    """
    Function to edit a task description.
    """
    if not tasks_combo.get():
        messagebox.showwarning(
            "Warning", "Please choose a task.")
        return
    if edit_button.cget("text") == "Edit" and tasks_combo.get():  # If button text is "Edit"
        # Change button text to "Save"
        new_button.config(state='disabled')
        history_button.config(state='disabled')
        edit_button.config(text="Save")

    elif tasks_combo.get():  # If button text is "Save"
        # Get the modified task description from the data text widget
        edit_button.config(text="Edit")
        new_button.config(state='normal')
        history_button.config(state='normal')
        if not data.get("1.0", "end-1c"):
            show_selected_task(None)
            messagebox.showwarning(
                "Warning", "Please enter a task description.")
            return
        modified_task_description = data.get('1.0', tk.END).strip()
        # Retrieve the corresponding task description from the task_dict dictionary
        selected_task = tasks_combo.get()  # Get the selected task label from the combobox
        task_id = tasks_dict[selected_task][0]
        # Update the task description in the database
        cur.execute("UPDATE tasks SET task_description = ? WHERE task_id = ?",
                    (modified_task_description, task_id))
        conn.commit()  # Commit the transaction

        # Change button text back to "Edit"

        show()


def open_and_show():
    """
    Function to open a new window and show tasks.
    """
    form2.create_new_page()
    # Wait for the Toplevel window to be destroyed
    window.wait_window(form2.window2)
    date_label.config(text=form2.chosen_date)
    show()


def mark_task_as_done():
    """
    Function to mark a task as done.
    """
    selected_task = tasks_combo.get()  # Get the selected task label from the combobox
    # Check if a task is selected
    if not selected_task:
        messagebox.showwarning("Warning", "Please select a task.")
        return
    task_id = tasks_dict[selected_task][0]
    # Update the task status to 'Done' in the database
    cur.execute(
        "UPDATE tasks SET task_status = 'Done' WHERE task_id = ?", (task_id,))
    conn.commit()  # Commit the transaction
    show_selected_task(None)
    # Display a message indicating that the task has been marked as done
    messagebox.showinfo("Success", "Task marked as Done.")


def mark_task_as_not_done():
    """
    Function to mark a task as not done.
    """
    selected_task = tasks_combo.get()  # Get the selected task label from the combobox
    # Check if a task is selected
    if not selected_task:
        messagebox.showwarning("Warning", "Please select a task.")
        return
    task_id = tasks_dict[selected_task][0]
    # Update the task status to 'Done' in the database
    cur.execute(
        "UPDATE tasks SET task_status = 'Not Done' WHERE task_id = ?", (task_id,))
    conn.commit()  # Commit the transaction
    show_selected_task(None)
    # Display a message indicating that the task has been marked as done
    messagebox.showinfo("Success", "Task marked as Not Done.")


def show_history():
    """
    Function to display task history.
    """
    new_button.config(state='disabled')
    edit_button.config(state='disabled')
    delete_button.config(state='disabled')

    form2.chosen_date = ''
    date_label.config(text='Data')
    tasks_combo['values'] = ['History']
    tasks_combo.current(0)
    done_button.config(background='white')
    not_done_button.config(background='white')
    # Get today's date
    today = datetime.date.today().isoformat()

    # Query tasks until today from the database
    cur.execute("SELECT task_status FROM tasks WHERE task_date <= ?", (today,))
    tasks_until_today = cur.fetchall()

    # Count the number of tasks done and tasks not done
    tasks_done = sum(1 for task in tasks_until_today if task[0] == 'Done')
    tasks_not_done = sum(
        1 for task in tasks_until_today if task[0] == 'Not Done')

    # Calculate the percentage of success
    total_tasks = len(tasks_until_today)
    if total_tasks == 0:
        success_percentage = 0
    else:
        success_percentage = (tasks_done / total_tasks) * 100

    # Display the results
    data.delete('1.0', tk.END)
    # Display the selected task description in the data text widget
    data.insert(tk.END, f'''Task History

    Total tasks until today: {total_tasks}\n
    Tasks done: {tasks_done}\n
    Tasks not done: {tasks_not_done}\n

Success percentage: {success_percentage:.2f}%''')


def delete_task():
    """
    Function to delete a task.
    """
    current_date = form2.chosen_date

    # Check if the chosen date is not in the past
    if current_date < datetime.date.today().isoformat():
        messagebox.showwarning(
            "Warning", "You cannot delete tasks of past dates.")
        return
    elif current_date == datetime.date.today().isoformat():
        messagebox.showwarning(
            "Warning", "You cannot delete tasks of today.")
        return
    selected_task = tasks_combo.get()  # Get the selected task label from the combobox
    edit_button.config(text='Edit')
    history_button.config(state='normal')
    # Check if a task is selected
    if not selected_task:
        messagebox.showwarning("Warning", "Please select a task.")
        return
    task_id = tasks_dict[selected_task][0]

    cur.execute(
        "DELETE FROM tasks WHERE task_id = ?", (task_id,))
    conn.commit()  # Commit the transaction
    # Display a message indicating that the task has been marked as done
    messagebox.showinfo("Success", "The task has successfullly deleted.")
    show()


# Creating tkinter window and frames
window = tk.Tk()
window.title("Todo Pro")
window.geometry('440x310')
frame = tkinter.Frame(window)
frame.pack()

left_frame = tk.Frame(frame)
left_frame.grid(row=0, column=0)

right_frame = tk.Frame(frame)
right_frame.grid(row=0, column=1)

# Creating left_frame objects

choose_date_label = tk.Label(left_frame, text='Choose Day:')
choose_date_label.pack(pady=5)


date_button = tk.Button(left_frame, text='Select', command=open_and_show)
date_button.pack(pady=5)

date_label = tk.Label(left_frame, text='Date')
date_label.pack(pady=5)

tasks_label = tk.Label(left_frame, text='Tasks:')
tasks_label.pack(pady=5)

tasks_combo = ttk.Combobox(left_frame)
tasks_combo.pack(pady=5)

edit_button = tk.Button(left_frame, text='Edit', command=edit)
edit_button.pack(pady=5)

new_button = tk.Button(left_frame, text='New', command=toggle_new_button)
new_button.pack(pady=5)

delete_button = tk.Button(left_frame, text='Delete', command=delete_task)
delete_button.pack(pady=5)

history_button = tk.Button(left_frame, text='History', command=show_history)
history_button.pack(pady=5)

# Creating right frame objects
data = tkinter.Text(right_frame, height=10,
                    width=28, font=("Helvetica", 12))
data.pack(pady=5, padx=5)

# Create a vertical scrollbar
scrollbar = tk.Scrollbar(right_frame, command=data.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Attach the scrollbar to the Text widget
data.config(yscrollcommand=scrollbar.set)


done_button = tk.Button(right_frame, text='Done', command=mark_task_as_done)
done_button.pack(pady=10)

not_done_button = tk.Button(
    right_frame, text='Not Done', command=mark_task_as_not_done)
not_done_button.pack(pady=10)

tasks_combo.bind("<<ComboboxSelected>>", show_selected_task)


window.mainloop()
