
import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
import re

from database import (
    create_table,
    save_record,
    get_records,
    get_bmi_history,
    delete_record
)


# ==================================================
# COLOUR THEME
# ==================================================

BG = "#F1F5FF"
WHITE = "#FFFFFF"
PRIMARY = "#2563EB"
DARK = "#1E3A8A"
TEXT = "#334155"
MUTED = "#64748B"
GREEN = "#059669"
RED = "#DC2626"
RED_DARK = "#B91C1C"
TEAL = "#0D9488"
PURPLE = "#7C3AED"
LIGHT_BLUE = "#DBEAFE"
LIGHT_ROW = "#F8FAFC"


# ==================================================
# WINDOW POSITION
# ==================================================

def center_window(window, width, height):

    window.update_idletasks()

    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    window.geometry(f"{width}x{height}+{x}+{y}")


# ==================================================
# CREATE DATABASE
# ==================================================

create_table()


# ==================================================
# BMI CALCULATION
# ==================================================

def calculate_bmi():

    name = name_entry.get().strip()

    # Validate name
    if not name:
        messagebox.showerror(
            "Input Error",
            "Please enter your name.",
            parent=root
        )
        name_entry.focus()
        return

    # Only letters and spaces allowed
    if not re.fullmatch(r"[A-Za-z ]+", name):
        messagebox.showerror(
            "Invalid Name",
            "Name must contain letters only.\n"
            "Numbers and special characters are not allowed.",
            parent=root
        )
        name_entry.focus()
        return

    # Validate weight and height
    try:

        weight = float(weight_entry.get())
        height = float(height_entry.get())

        if weight <= 0 or height <= 0:
            messagebox.showerror(
                "Input Error",
                "Weight and height must be greater than zero.",
                parent=root
            )
            return

        # Calculate BMI
        bmi = weight / (height ** 2)

        # Determine category
        if bmi < 18.5:
            category = "Underweight"
            result_color = PRIMARY

        elif bmi < 25:
            category = "Normal"
            result_color = GREEN

        elif bmi < 30:
            category = "Overweight"
            result_color = "#D97706"

        else:
            category = "Obese"
            result_color = RED

        # Save record
        save_record(
            name,
            weight,
            height,
            bmi,
            category
        )

        # Display result without success popup
        result_label.config(
            text=f"Your BMI: {bmi:.2f}\nCategory: {category}",
            fg=result_color
        )

        # Clear weight and height fields
        weight_entry.delete(0, tk.END)
        height_entry.delete(0, tk.END)

        weight_entry.focus()

    except ValueError:

        messagebox.showerror(
            "Input Error",
            "Please enter valid numbers for weight and height.",
            parent=root
        )

    except Exception as error:

        messagebox.showerror(
            "Database Error",
            str(error),
            parent=root
        )


# ==================================================
# BMI HISTORY WINDOW
# ==================================================

def view_history():

    history_window = tk.Toplevel(root)
    history_window.title("BMI History Records")
    history_window.configure(bg=BG)
    history_window.resizable(True, True)

    center_window(history_window, 1250, 700)

    # Heading
    tk.Label(
        history_window,
        text="BMI HISTORY RECORDS",
        font=("Arial", 24, "bold"),
        bg=BG,
        fg=DARK
    ).pack(pady=(20, 5))

    tk.Label(
        history_window,
        text="View and manage your saved BMI records",
        font=("Arial", 11),
        bg=BG,
        fg=MUTED
    ).pack(pady=(0, 18))

    # Main table container
    outer_frame = tk.Frame(
        history_window,
        bg=WHITE,
        bd=1,
        relief="solid"
    )

    outer_frame.pack(
        fill="both",
        expand=True,
        padx=25,
        pady=10
    )

    # Scrollable canvas
    canvas = tk.Canvas(
        outer_frame,
        bg=WHITE,
        highlightthickness=0
    )

    scrollbar = tk.Scrollbar(
        outer_frame,
        orient="vertical",
        command=canvas.yview
    )

    canvas.configure(
        yscrollcommand=scrollbar.set
    )

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    # Frame inside canvas
    table_frame = tk.Frame(
        canvas,
        bg=WHITE
    )

    canvas_window = canvas.create_window(
        (0, 0),
        window=table_frame,
        anchor="nw"
    )

    # Update scroll area
    def update_scroll_region(event=None):

        canvas.configure(
            scrollregion=canvas.bbox("all")
        )

    table_frame.bind(
        "<Configure>",
        update_scroll_region
    )

    # Keep table width equal to canvas width
    def resize_table(event):

        canvas.itemconfigure(
            canvas_window,
            width=event.width
        )

    canvas.bind(
        "<Configure>",
        resize_table
    )

    # Table columns
    column_names = [
        "No.",
        "Name",
        "Weight",
        "Height",
        "BMI",
        "Category",
        "Date",
        "Action"
    ]

    column_weights = [1, 2, 1, 1, 1, 2, 3, 1]

    for index, weight in enumerate(column_weights):

        table_frame.grid_columnconfigure(
            index,
            weight=weight,
            uniform="table"
        )

    # Header
    header_frame = tk.Frame(
        table_frame,
        bg=PRIMARY
    )

    header_frame.grid(
        row=0,
        column=0,
        columnspan=8,
        sticky="ew"
    )

    for index, title in enumerate(column_names):

        tk.Label(
            header_frame,
            text=title,
            font=("Arial", 10, "bold"),
            bg=PRIMARY,
            fg=WHITE,
            padx=5,
            pady=15
        ).grid(
            row=0,
            column=index,
            sticky="nsew"
        )

        header_frame.grid_columnconfigure(
            index,
            weight=column_weights[index],
            uniform="header"
        )

    # Footer
    footer = tk.Label(
        history_window,
        text="",
        font=("Arial", 11, "bold"),
        bg=BG,
        fg=DARK
    )

    footer.pack(pady=12)

    # Refresh history table
    def refresh_history():

        for widget in table_frame.winfo_children():

            if widget != header_frame:
                widget.destroy()

        records = get_records()

        # Records come from database in A-Z order
        for index, record in enumerate(records, start=1):

            (
                record_id,
                name,
                weight,
                height,
                bmi,
                category,
                date
            ) = record

            row_color = (
                LIGHT_BLUE if index % 2 == 0
                else LIGHT_ROW
            )

            row_frame = tk.Frame(
                table_frame,
                bg=row_color
            )

            row_frame.grid(
                row=index,
                column=0,
                columnspan=8,
                sticky="ew"
            )

            values = [
                index,
                name or "Unknown",
                f"{weight:.1f} kg",
                f"{height:.2f} m",
                f"{bmi:.2f}",
                category,
                date
            ]

            # Display row information
            for col_index, value in enumerate(values):

                tk.Label(
                    row_frame,
                    text=str(value),
                    font=("Arial", 10),
                    bg=row_color,
                    fg=TEXT,
                    padx=5,
                    pady=13,
                    anchor="center"
                ).grid(
                    row=0,
                    column=col_index,
                    sticky="nsew"
                )

                row_frame.grid_columnconfigure(
                    col_index,
                    weight=column_weights[col_index],
                    uniform="row"
                )

            # Actual red DELETE button
            delete_button = tk.Button(
                row_frame,
                text="DELETE",
                font=("Arial", 9, "bold"),
                bg=RED,
                fg=WHITE,
                activebackground=RED_DARK,
                activeforeground=WHITE,
                relief="flat",
                cursor="hand2",
                bd=0,
                padx=10,
                pady=6,
                command=lambda rid=record_id: delete_selected_record(rid)
            )

            delete_button.grid(
                row=0,
                column=7,
                padx=5,
                pady=5,
                sticky="nsew"
            )

        footer.config(
            text=f"Total BMI Records: {len(records)}"
        )

        update_scroll_region()

    # Delete immediately without confirmation
    def delete_selected_record(record_id):

        try:

            delete_record(record_id)

            # Refresh and renumber records
            refresh_history()

        except Exception as error:

            messagebox.showerror(
                "Delete Error",
                str(error),
                parent=history_window
            )

    # Display initial records
    refresh_history()


# ==================================================
# BMI TREND GRAPH
# ==================================================

def show_bmi_graph():

    records = get_bmi_history()

    if not records:

        messagebox.showinfo(
            "BMI History",
            "No BMI records available to display.",
            parent=root
        )
        return

    bmi_values = [record[0] for record in records]
    dates = [record[1] for record in records]

    plt.figure(
        figsize=(10, 5),
        facecolor=BG
    )

    plt.plot(
        range(1, len(bmi_values) + 1),
        bmi_values,
        marker="o",
        markersize=8,
        linewidth=2,
        color=PRIMARY,
        label="BMI"
    )

    plt.title(
        "BMI Progress Trend",
        fontsize=16,
        fontweight="bold",
        color=DARK
    )

    plt.xlabel("Record Number")
    plt.ylabel("BMI Value")

    plt.xticks(
        range(1, len(dates) + 1),
        dates,
        rotation=45,
        ha="right"
    )

    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()


# ==================================================
# MAIN APPLICATION WINDOW
# ==================================================

root = tk.Tk()

root.title("BMI Calculator")
root.configure(bg=BG)
root.resizable(False, False)

center_window(root, 500, 650)


# ==================================================
# MAIN HEADING
# ==================================================

tk.Label(
    root,
    text="BMI CALCULATOR",
    font=("Arial", 26, "bold"),
    bg=BG,
    fg=DARK
).pack(pady=(25, 5))

tk.Label(
    root,
    text="Calculate and monitor your Body Mass Index",
    font=("Arial", 10),
    bg=BG,
    fg=MUTED
).pack(pady=(0, 20))


# ==================================================
# INPUT FRAME
# ==================================================

input_frame = tk.Frame(
    root,
    bg=WHITE,
    padx=30,
    pady=15
)

input_frame.pack(
    padx=35,
    fill="x"
)


def create_input(label_text):

    tk.Label(
        input_frame,
        text=label_text,
        font=("Arial", 11, "bold"),
        bg=WHITE,
        fg=TEXT
    ).pack(pady=(8, 4))

    entry = tk.Entry(
        input_frame,
        font=("Arial", 12),
        justify="center",
        relief="solid",
        bd=1
    )

    entry.pack(
        fill="x",
        ipady=6,
        pady=(0, 5)
    )

    return entry


name_entry = create_input("User Name")
weight_entry = create_input("Weight (kg)")
height_entry = create_input("Height (metres)")


# ==================================================
# BUTTON CREATION
# ==================================================

def create_button(parent, text, color, hover_color, command):

    return tk.Button(
        parent,
        text=text,
        font=("Arial", 11, "bold"),
        bg=color,
        fg=WHITE,
        activebackground=hover_color,
        activeforeground=WHITE,
        relief="flat",
        cursor="hand2",
        bd=0,
        command=command
    )


# Calculate button
create_button(
    root,
    "CALCULATE BMI",
    PRIMARY,
    DARK,
    calculate_bmi
).pack(
    fill="x",
    padx=65,
    pady=(20, 8),
    ipady=9
)


# History button
create_button(
    root,
    "VIEW BMI HISTORY",
    TEAL,
    "#0F766E",
    view_history
).pack(
    fill="x",
    padx=65,
    pady=7,
    ipady=8
)


# Graph button
create_button(
    root,
    "SHOW BMI GRAPH",
    PURPLE,
    "#6D28D9",
    show_bmi_graph
).pack(
    fill="x",
    padx=65,
    pady=7,
    ipady=8
)


# ==================================================
# RESULT DISPLAY
# ==================================================

result_label = tk.Label(
    root,
    text="Enter your details to calculate BMI",
    font=("Arial", 14, "bold"),
    bg=BG,
    fg=GREEN,
    justify="center"
)

result_label.pack(pady=20)


# ==================================================
# START APPLICATION
# ==================================================

root.mainloop()