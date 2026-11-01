import re
import math
from io import BytesIO

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import Wedge

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_file,
    Response,
    jsonify
)

from database import (
    create_table,
    create_water_table,
    save_record,
    get_records,
    get_latest_record,
    get_weight_history,
    delete_record,
    get_today_water,
    save_today_water
)


# ==========================================
# FLASK APPLICATION CONFIGURATION
# ==========================================

app = Flask(__name__)

app.secret_key = "bmi_calculator_secret_key"


# ==========================================
# BMI CATEGORY FOR ADULTS
# ==========================================

def get_adult_category(bmi):

    if bmi < 18.5:
        return "Underweight", "underweight"

    elif bmi < 25:
        return "Normal", "normal"

    elif bmi < 30:
        return "Overweight", "overweight"

    else:
        return "Obese", "obese"


# ==========================================
# BMI CATEGORY FOR CHILD / TEEN
# ==========================================

def get_child_category(bmi):

    # Simplified educational categories.
    # Real child BMI assessment should use
    # age-and-sex-specific BMI percentiles.

    if bmi < 14:
        return "Underweight", "underweight"

    elif bmi < 22:
        return "Healthy Range", "normal"

    elif bmi < 25:
        return "Overweight", "overweight"

    else:
        return "Obese", "obese"


# ==========================================
# HOME PAGE
# ==========================================

@app.route("/")
def index():

    return render_template(
        "index.html",
        bmi=None
    )


# ==========================================
# CALCULATE BMI
# ==========================================

@app.route("/calculate", methods=["POST"])
def calculate():

    # --------------------------------------
    # GET FORM DATA
    # --------------------------------------

    name = request.form.get(
        "name",
        ""
    ).strip()

    age_input = request.form.get(
        "age",
        ""
    ).strip()

    gender = request.form.get(
        "gender",
        ""
    ).strip().lower()

    weight_input = request.form.get(
        "weight",
        ""
    ).strip()

    height_input = request.form.get(
        "height",
        ""
    ).strip()


    # --------------------------------------
    # VALIDATE NAME
    # --------------------------------------

    if not re.fullmatch(
        r"[A-Za-z ]{2,50}",
        name
    ):

        flash(
            "Please enter a valid name using English letters only.",
            "error"
        )

        return redirect(
            url_for("index")
        )


    # --------------------------------------
    # VALIDATE AGE
    # --------------------------------------

    try:

        age = int(age_input)

    except ValueError:

        flash(
            "Please enter a valid age.",
            "error"
        )

        return redirect(
            url_for("index")
        )


    if age < 2 or age > 120:

        flash(
            "Please enter an age between 2 and 120.",
            "error"
        )

        return redirect(
            url_for("index")
        )


    # --------------------------------------
    # VALIDATE GENDER
    # --------------------------------------

    if gender not in [
        "male",
        "female",
        "other"
    ]:

        flash(
            "Please select a valid gender.",
            "error"
        )

        return redirect(
            url_for("index")
        )


    # --------------------------------------
    # VALIDATE WEIGHT AND HEIGHT
    # --------------------------------------

    try:

        weight = float(weight_input)

        height = float(height_input)

    except ValueError:

        flash(
            "Please enter valid numeric weight and height.",
            "error"
        )

        return redirect(
            url_for("index")
        )


    if weight <= 0 or height <= 0:

        flash(
            "Weight and height must be greater than zero.",
            "error"
        )

        return redirect(
            url_for("index")
        )


    # --------------------------------------
    # CHECK FINITE VALUES
    # --------------------------------------

    if not (
        math.isfinite(weight)
        and math.isfinite(height)
    ):

        flash(
            "Please enter valid finite numbers.",
            "error"
        )

        return redirect(
            url_for("index")
        )


    # --------------------------------------
    # CALCULATE BMI
    # --------------------------------------

    bmi = round(
        weight / (height * height),
        2
    )


    # --------------------------------------
    # DETERMINE AGE GROUP
    # --------------------------------------

    if age < 18:

        age_group = "child"

        category, category_class = get_child_category(
            bmi
        )

    else:

        age_group = "adult"

        category, category_class = get_adult_category(
            bmi
        )


    # --------------------------------------
    # SAVE RECORD TO DATABASE
    # --------------------------------------

    save_record(
        name,
        age,
        gender,
        age_group,
        weight,
        height,
        bmi,
        category
    )


    # --------------------------------------
    # SHOW RESULT
    # --------------------------------------

    return render_template(
        "index.html",
        bmi=bmi,
        category=category,
        category_class=category_class,
        name=name,
        age=age,
        gender=gender,
        weight=weight,
        height=height,
        age_group=age_group
    )


# ==========================================
# DASHBOARD
# ==========================================

@app.route("/dashboard")
def dashboard():

    records = get_records()

    latest_record = None

    latest_category_class = None


    if records:

        latest_record = records[0]

        category = (
            latest_record["category"]
            .lower()
            .replace(" ", "-")
        )


        if category == "underweight":

            latest_category_class = "underweight"


        elif category in [
            "normal",
            "healthy-range"
        ]:

            latest_category_class = "normal"


        elif category == "overweight":

            latest_category_class = "overweight"


        else:

            latest_category_class = "obese"


    # --------------------------------------
    # GET TODAY'S WATER DATA
    # --------------------------------------

    water_count = get_today_water()


    return render_template(
        "dashboard.html",
        latest_record=latest_record,
        latest_category_class=latest_category_class,
        water_count=water_count
    )


# ==========================================
# UPDATE WATER TRACKER
# ==========================================

@app.route(
    "/update-water",
    methods=["POST"]
)
def update_water():

    data = request.get_json()

    if not data:

        return jsonify({
            "success": False,
            "message": "Invalid request."
        }), 400


    water_count = data.get(
        "water_count",
        0
    )


    try:

        water_count = int(
            water_count
        )

    except (
        ValueError,
        TypeError
    ):

        return jsonify({
            "success": False,
            "message": "Invalid water count."
        }), 400


    # Limit between 0 and 8 glasses

    water_count = max(
        0,
        min(water_count, 8)
    )


    save_today_water(
        water_count
    )


    return jsonify({

        "success": True,

        "water_count": water_count

    })


# ==========================================
# BMI HISTORY
# ==========================================

@app.route("/history")
def history():

    records = get_records()

    return render_template(
        "history.html",
        records=records
    )


# ==========================================
# DELETE BMI RECORD
# ==========================================

@app.route(
    "/delete/<int:record_id>",
    methods=["POST"]
)
def delete(record_id):

    deleted_rows = delete_record(
        record_id
    )


    if deleted_rows:

        flash(
            "BMI record deleted successfully.",
            "success"
        )

    else:

        flash(
            "BMI record was not found.",
            "error"
        )


    return redirect(
        url_for("history")
    )


# ==========================================
# BMI GAUGE PAGE
# ==========================================

@app.route("/graph")
def show_graph():

    records = get_records()

    latest_record = None


    if records:

        latest_record = records[0]


    return render_template(
        "graph.html",
        latest_record=latest_record
    )


# ==========================================
# GENERATE BMI GAUGE IMAGE
# ==========================================

@app.route("/graph-image")
def graph_image():

    records = get_records()


    # --------------------------------------
    # GET LATEST BMI
    # --------------------------------------

    if records:

        bmi_value = records[0]["bmi"]

    else:

        bmi_value = 0


    # --------------------------------------
    # CREATE FIGURE
    # --------------------------------------

    fig, ax = plt.subplots(
        figsize=(9, 5)
    )


    # --------------------------------------
    # BMI RANGE SETTINGS
    # --------------------------------------

    max_bmi = 40

    bmi_value = min(
        bmi_value,
        max_bmi
    )


    # --------------------------------------
    # GAUGE SEGMENTS
    # --------------------------------------

    segments = [

        (0, 18.5, "#6ec6ff"),

        (18.5, 25, "#66bb6a"),

        (25, 30, "#ffca28"),

        (30, 40, "#ef5350")

    ]


    # --------------------------------------
    # DRAW BMI GAUGE
    # --------------------------------------

    for start, end, color in segments:

        start_angle = (
            180 -
            (start / max_bmi * 180)
        )

        end_angle = (
            180 -
            (end / max_bmi * 180)
        )


        wedge = Wedge(

            (0, 0),

            1,

            end_angle,

            start_angle,

            width=0.30,

            facecolor=color,

            edgecolor="white"

        )


        ax.add_patch(
            wedge
        )


    # --------------------------------------
    # BMI POINTER
    # --------------------------------------

    pointer_angle = (
        180 -
        (bmi_value / max_bmi * 180)
    )


    pointer_radians = math.radians(
        pointer_angle
    )


    pointer_x = (
        0.78 *
        math.cos(pointer_radians)
    )


    pointer_y = (
        0.78 *
        math.sin(pointer_radians)
    )


    ax.plot(

        [0, pointer_x],

        [0, pointer_y],

        linewidth=3,

        color="#263238"

    )


    ax.scatter(

        0,

        0,

        s=100,

        color="#263238"

    )


    # --------------------------------------
    # BMI VALUE TEXT
    # --------------------------------------

    ax.text(

        0,

        -0.25,

        f"BMI: {bmi_value:.2f}",

        ha="center",

        va="center",

        fontsize=18,

        fontweight="bold"

    )


    # --------------------------------------
    # GAUGE LABELS
    # --------------------------------------

    ax.text(
        -1.15,
        -0.05,
        "Underweight\nBelow 18.5",
        ha="center",
        va="center"
    )


    ax.text(
        -0.35,
        1.20,
        "Normal\n18.5 - 24.9",
        ha="center",
        va="center"
    )


    ax.text(
        0.50,
        1.10,
        "Overweight\n25 - 29.9",
        ha="center",
        va="center"
    )


    ax.text(
        1.15,
        -0.05,
        "Obese\n30+",
        ha="center",
        va="center"
    )


    # --------------------------------------
    # GRAPH SETTINGS
    # --------------------------------------

    ax.set_xlim(
        -1.5,
        1.5
    )

    ax.set_ylim(
        -0.5,
        1.45
    )

    ax.set_aspect(
        "equal"
    )

    ax.axis(
        "off"
    )


    plt.tight_layout()


    # --------------------------------------
    # SAVE IMAGE TO MEMORY
    # --------------------------------------

    image = BytesIO()


    plt.savefig(

        image,

        format="png",

        dpi=150,

        bbox_inches="tight"

    )


    image.seek(
        0
    )


    plt.close()


    return send_file(

        image,

        mimetype="image/png"

    )


# ==========================================
# WEIGHT TRACKING PAGE
# ==========================================

@app.route("/weight-tracker")
def weight_tracker():

    records = get_weight_history()

    latest_weight = None

    previous_weight = None

    weight_difference = None


    if records:

        latest_weight = records[-1]["weight"]


        if len(records) >= 2:

            previous_weight = records[-2]["weight"]


            weight_difference = round(

                latest_weight -
                previous_weight,

                2

            )


    return render_template(

        "weight_tracker.html",

        records=records,

        latest_weight=latest_weight,

        previous_weight=previous_weight,

        weight_difference=weight_difference

    )


# ==========================================
# WEIGHT GRAPH IMAGE
# ==========================================

@app.route("/weight-graph-image")
def weight_graph_image():

    records = get_weight_history()

    fig, ax = plt.subplots(
        figsize=(10, 5)
    )


    if records:

        labels = []

        weights = []


        for index, record in enumerate(
            records,
            start=1
        ):

            labels.append(
                f"Record {index}"
            )

            weights.append(
                record["weight"]
            )


        ax.plot(

            labels,

            weights,

            marker="o",

            linewidth=2

        )


        for index, weight in enumerate(weights):

            ax.text(

                index,

                weight,

                f"{weight:.1f} kg",

                ha="center",

                va="bottom"

            )


        ax.set_title(
            "Weight Progress"
        )

        ax.set_xlabel(
            "BMI Records"
        )

        ax.set_ylabel(
            "Weight (kg)"
        )

        ax.grid(

            True,

            linestyle="--",

            alpha=0.5

        )


    else:

        ax.text(

            0.5,

            0.5,

            "No weight records available",

            ha="center",

            va="center",

            fontsize=16

        )

        ax.axis(
            "off"
        )


    plt.tight_layout()


    image = BytesIO()


    plt.savefig(

        image,

        format="png",

        dpi=150,

        bbox_inches="tight"

    )


    image.seek(
        0
    )


    plt.close()


    return send_file(

        image,

        mimetype="image/png"

    )


# ==========================================
# DOWNLOAD BMI REPORT
# ==========================================

@app.route("/download-report")
def download_report():

    latest_record = get_latest_record()


    if not latest_record:

        flash(
            "No BMI record available to download.",
            "error"
        )

        return redirect(
            url_for("dashboard")
        )


    report = f"""
BMI CALCULATOR - HEALTH REPORT
========================================

Name: {latest_record['name']}
Age: {latest_record['age']}
Gender: {latest_record['gender'].capitalize()}
Age Group: {latest_record['age_group'].capitalize()}

Weight: {latest_record['weight']} kg
Height: {latest_record['height']} m

BMI: {latest_record['bmi']}
BMI Category: {latest_record['category']}

Date: {latest_record['date']}

========================================
Generated by BMI Calculator
Oasis Infobyte Python Internship Project
"""


    return Response(

        report,

        mimetype="text/plain",

        headers={

            "Content-Disposition":
            "attachment; filename=BMI_Health_Report.txt"

        }

    )


# ==========================================
# ABOUT PAGE
# ==========================================

@app.route("/about")
def about():

    return render_template(
        "about.html"
    )


# ==========================================
# START APPLICATION
# ==========================================

if __name__ == "__main__":

    # Create BMI database table

    create_table()


    # Create water tracker table

    create_water_table()


    print(
        "\nBMI CALCULATOR FLASK APPLICATION"
    )


    print(
        "Open: http://127.0.0.1:5000"
    )


    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )