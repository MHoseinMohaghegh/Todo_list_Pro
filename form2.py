import tkinter as tk
from tkcalendar import Calendar

chosen_date = None


def create_new_page():
    global window2
    window2 = tk.Toplevel()  # Create a Toplevel window instead of Tk()
    window2.title("Choose Date")
    window2.geometry('300x220')
    frame = tk.Frame(window2)
    frame.pack()

    cal = Calendar(frame, selectmode="day", date_pattern="yyyy-mm-dd")
    cal.grid(row=0, column=0)

    choose_button = tk.Button(frame, text='Choose',
                              command=lambda: save_chosen_date(cal, window2))
    choose_button.grid(row=1, column=0)


def save_chosen_date(cal, window):
    global chosen_date
    chosen_date = cal.get_date()
    window.destroy()  # Close the window
