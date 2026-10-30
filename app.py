
import re
import sqlite3
from pathlib import Path
from io import BytesIO

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_file
)

# ==========================================
# 1. FLASK CONFIGURATION
# ==========================================

app = Flask(__name__)
app.secret_key = "bmi_calculator_secret_key"

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "bmi_records.db"


# ==========================================
# 2. DATABASE CONNECTION
# ==========================================

def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def create_table():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS web_bmi_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                weight REAL NOT NULL,
                height REAL NOT NULL,
                bmi REAL NOT NULL,
                category TEXT NOT NULL
            )
        """)


# ==========================================
# 3. BMI CATEGORY
# ==========================================

def get_category(bmi):

    if bmi < 18.5:
        return "Underweight", "underweight"

    elif bmi < 25:
        return "Normal", "normal"

    elif bmi < 30:
        return "Overweight", "overweight"

    return "Obese", "obese"


# ==========================================
# 4. GET BMI RECORDS
# ==========================================

def get_records():

    with get_connection() as connection:

        records = connection.execute("""
            SELECT id, name, weight, height, bmi, category
            FROM web_bmi_records
            ORDER BY name COLLATE NOCASE ASC, id ASC
        """).fetchall()

    return records


# ==========================================
# 5. HOME PAGE
# ==========================================

@app.route("/")
def index():

    records = get_records()

    return render_template(
        "index.html",
        records=records,
        bmi=None
    )


# ==========================================
# 6. CALCULATE BMI
# ==========================================

@app.route("/calculate", methods=["POST"])
def calculate():

    name = request.form.get("name", "").strip()
    weight_input = request.form.get("weight", "").strip()
    height_input = request.form.get("height", "").strip()

    # Name validation
    if not re.fullmatch(r"[A-Za-z ]+", name):

        flash(
            "Please enter a valid name using English letters only.",
            "error"
        )

        return redirect(url_for("index"))

    # Numeric validation
    try:
        weight = float(weight_input)
        height = float(height_input)

    except ValueError:

        flash(
            "Please enter valid numeric weight and height.",
            "error"
        )

        return redirect(url_for("index"))

    # Positive number validation
    if weight <= 0 or height <= 0:

        flash(
            "Weight and height must be greater than zero.",
            "error"
        )

        return redirect(url_for("index"))

    # Prevent invalid infinite values
    if not (weight < float("inf") and height < float("inf")):

        flash("Please enter valid finite numbers.", "error")

        return redirect(url_for("index"))

    # BMI calculation
    bmi = round(weight / (height * height), 2)

    category, category_class = get_category(bmi)

    # Save record
    with get_connection() as connection:

        connection.execute("""
            INSERT INTO web_bmi_records
            (name, weight, height, bmi, category)
            VALUES (?, ?, ?, ?, ?)
        """, (name, weight, height, bmi, category))

    records = get_records()

    return render_template(
        "index.html",
        records=records,
        bmi=bmi,
        category=category,
        category_class=category_class
    )


# ==========================================
# 7. BMI HISTORY PAGE
# ==========================================

@app.route("/history")
def history():

    records = get_records()

    return render_template(
        "history.html",
        records=records
    )


# ==========================================
# 8. DELETE BMI RECORD
# ==========================================

@app.route("/delete/<int:record_id>", methods=["POST"])
def delete_record(record_id):

    with get_connection() as connection:

        connection.execute("""
            DELETE FROM web_bmi_records
            WHERE id = ?
        """, (record_id,))

    flash("BMI record deleted successfully.", "success")

    return redirect(url_for("history"))


# ==========================================
# 9. BMI GRAPH PAGE
# ==========================================

@app.route("/graph")
def show_graph():

    records = get_records()

    return render_template(
        "graph.html",
        records=records
    )


# ==========================================
# 10. GENERATE BMI GRAPH IMAGE
# ==========================================

@app.route("/graph-image")
def graph_image():

    records = get_records()

    plt.figure(figsize=(10, 5))

    if records:

        names = [record["name"] for record in records]
        bmi_values = [record["bmi"] for record in records]

        plt.plot(
            names,
            bmi_values,
            marker="o",
            linewidth=2,
            label="BMI"
        )

        plt.axhline(
            y=18.5,
            linestyle="--",
            label="Underweight limit"
        )

        plt.axhline(
            y=25,
            linestyle="--",
            label="Normal limit"
        )

        plt.axhline(
            y=30,
            linestyle="--",
            label="Overweight limit"
        )

        plt.legend()

    else:

        plt.text(
            0.5, 0.5,
            "No BMI records available yet",
            horizontalalignment="center",
            verticalalignment="center",
            transform=plt.gca().transAxes,
            fontsize=14
        )

        plt.xticks([])
        plt.yticks([])

    plt.title("BMI History Graph")
    plt.xlabel("Name")
    plt.ylabel("BMI")

    plt.xticks(rotation=30)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    image = BytesIO()

    plt.savefig(
        image,
        format="png",
        dpi=120
    )

    image.seek(0)
    plt.close()

    return send_file(
        image,
        mimetype="image/png"
    )


# ==========================================
# 11. ABOUT PAGE
# ==========================================

@app.route("/about")
def about():

    return render_template("about.html")


# ==========================================
# 12. START APPLICATION
# ==========================================

if __name__ == "__main__":

    create_table()

    print("----------------------------------")
    print("BMI CALCULATOR FLASK APPLICATION")
    print("----------------------------------")
    print("Server: http://127.0.0.1:5000")
    print("----------------------------------")

    app.run(debug=True)
