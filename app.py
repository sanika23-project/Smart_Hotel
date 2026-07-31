from flask import send_file
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from flask import Flask, render_template, request, redirect, session, flash
from werkzeug.utils import secure_filename
from database import *
from flask import *
from config import Config
import os
from chatbot import chatbot_reply
from flask import jsonify


app = Flask(__name__)
app.config.from_object("config.Config")
@app.route("/chatbot", methods=["POST"])
def chatbot():

    data = request.get_json()

    msg = data["message"].lower()

    if "hotel" in msg:

        reply = "🏨 Click View Hotels to see all available hotels."

    elif "book" in msg:

        reply = "📅 Select any hotel and click Book Now."

    elif "price" in msg:

        reply = "💰 Prices start from ₹1000 per night."

    elif "contact" in msg:

        reply = "📞 Call us at +91-9876543210."

    elif "hello" in msg or "hi" in msg:

        reply = "👋 Hello! Welcome to Smart Hotel."

    else:

        reply = "😊 Sorry, I didn't understand. Please ask about hotels, booking, prices or contact."

    return jsonify({

        "reply": reply

    })

# ======================================
# GLOBAL NOTIFICATIONS
# ======================================

@app.context_processor
def notification_data():

    if session.get("role") == "admin":

        notifications = get_notifications()

        unread_count = sum(
            1 for n in notifications
            if n["status"] == "Unread"
        )

        return dict(
            notifications=notifications,
            unread_count=unread_count
        )

    return dict(
        notifications=[],
        unread_count=0
    )

app.secret_key = "hotel_secret_key"
app.config["UPLOAD_FOLDER"] = Config.UPLOAD_FOLDER
create_tables()
create_default_admin()
@app.context_processor
def notification_context():

    if session.get("role") == "admin":

        return {

            "unread_count": unread_notification_count()

        }

    return {

        "unread_count": 0

    }


# ---------------- HOME ---------------- #

@app.route("/")
def home():
    return render_template("index.html")


# ---------------- REGISTER ---------------- #

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        fullname = request.form["fullname"]

        username = request.form["username"]

        email = request.form["email"]

        password = request.form["password"]

        confirm_password = request.form["confirm_password"]

        # Check password
        if password != confirm_password:

            flash("Passwords do not match!", "danger")

            return redirect("/register")

        status = register_user(

            fullname,

            username,

            email,

            password

        )

        if status:

            flash("Registration Successful!", "success")

            return redirect("/login")

        else:

            flash("Username already exists!", "danger")

    return render_template("register.html")
# ---------------- LOGIN ---------------- #

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = login_user(username, password)

        if user:

            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]

            if user["role"] == "admin":
                return redirect("/admin")

            else:
                return redirect("/user")

        else:
            flash("Invalid Username or Password", "danger")

    return render_template("login.html")

# ---------------- ADMIN DASHBOARD ---------------- #

@app.route("/admin")
def admin():

    if "role" not in session:
        return redirect("/login")

    if session["role"] != "admin":
        flash("Access Denied!", "danger")
        return redirect("/user")

    # ================= Dashboard Statistics =================

    data = get_dashboard_data()

    total_hotels = data["total_hotels"]
    total_users = data["total_users"]
    total_bookings = data["total_bookings"]
    total_available_rooms = data["available_rooms"]
    total_revenue = data["total_revenue"]

    # ================= Occupancy =================

    if data["total_rooms"] == 0:
        occupancy = 0
    else:
        occupancy = round(
            ((data["total_rooms"] - data["available_rooms"])
             / data["total_rooms"]) * 100,
            2
        )

    # ================= Charts =================

    booking_chart, hotel_chart = dashboard_chart_data()

    booking_labels = []
    booking_values = []

    for row in booking_chart:

        booking_labels.append(row["hotel_name"])
        booking_values.append(row["total"])

    hotel_labels = []
    hotel_values = []

    for row in hotel_chart:

        hotel_labels.append(row["name"])

        used = row["total_rooms"] - row["available_rooms"]

        hotel_values.append(used)

    # ================= Recent Bookings =================

    bookings = get_all_bookings()

    # ================= Recent Reviews =================

    reviews = get_all_reviews()

    # ================= Notifications =================

    notifications = get_notifications()

    unread_count = 0

    for note in notifications:

        if note["status"] == "Unread":

            unread_count += 1

    # ================= Render =================

    return render_template(

        "admin_dashboard.html",

        total_hotels=total_hotels,
        total_users=total_users,
        total_bookings=total_bookings,
        available_rooms=total_available_rooms,
        total_revenue=total_revenue,
        occupancy=occupancy,
        

        booking_labels=booking_labels,
        booking_values=booking_values,

        hotel_labels=hotel_labels,
        hotel_values=hotel_values,

        bookings=bookings,
        reviews=reviews,

        notifications=notifications,
        unread_count=unread_count

    )

# ======================================
# MARK AS READ
# ======================================

@app.route("/notification/read/<int:id>")
def notification_read(id):

    if "role" not in session:
        return redirect("/login")

    mark_notification_read(id)

    flash("Notification marked as read.", "success")

    return redirect(request.referrer or "/admin")


# ======================================
# DELETE NOTIFICATION
# ======================================

@app.route("/notification/delete/<int:id>")
def notification_delete(id):

    if "role" not in session:
        return redirect("/login")

    delete_notification(id)

    flash("Notification deleted.", "warning")

    return redirect("/notifications")
@app.route("/add_hotel", methods=["GET", "POST"])
def addHotel():

    if "username" not in session:
        return redirect("/")

    # Only admin can add hotels
    if session.get("role") != "admin":
        flash("Access Denied!", "danger")
        return redirect("/view_hotels")

    if request.method == "POST":

        image = request.files["image"]

        filename = ""

        if image.filename != "":
            filename = secure_filename(image.filename)

            image.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    filename
                )
            )

        hotel = {

            "name": request.form["name"],
            "description": request.form["description"],
            "location": request.form["location"],
            "phone": request.form["phone"],
            "email": request.form["email"],
            "google_map": request.form["google_map"],
            "price": request.form["price"],
            "rating": request.form["rating"],
            "total_rooms": request.form["total_rooms"],
            "wifi": request.form.get("wifi", "No"),
            "pool": request.form.get("pool", "No"),
            "parking": request.form.get("parking", "No"),
            "gym": request.form.get("gym", "No"),
            "spa": request.form.get("spa", "No"),
            "restaurant": request.form.get("restaurant", "No"),
            "breakfast": request.form.get("breakfast", "No"),
            "lunch": request.form.get("lunch", "No"),
            "dinner": request.form.get("dinner", "No"),
            "image": filename

        }

        add_hotel(hotel)

        flash("Hotel Added Successfully", "success")

        return redirect("/view_hotels")
    return render_template("add_hotel.html")
@app.route("/view_hotels")
def view_hotels():

    if "username" not in session:
        return redirect("/")

    hotels = get_hotels()

    return render_template(
        "view_hotels.html",
        hotels=hotels
    )
# ======================================
# HOTEL DETAILS
# ======================================
@app.route("/hotel/<int:id>")
def hotel_details(id):

    if "username" not in session:
        return redirect("/login")

    hotel = get_hotel(id)

    return render_template(
        "hotel_details.html",
       hotel=hotel
    )



@app.route("/hotel_gallery/<int:id>")
def hotel_gallery(id):

    if "username" not in session:
        return redirect("/login")

    hotel = get_hotel(id)

    images = get_gallery(id)

    return render_template(
        "hotel_gallery.html",
        hotel=hotel,
        images=images
    )

# ==============================
# SEARCH HOTEL
# ==============================

@app.route("/search_hotel", methods=["GET", "POST"])
def search_hotel():

    if "username" not in session:
        return redirect("/")

    hotels = []

    if request.method == "POST":

        keyword = request.form["keyword"]

        hotels = search_hotels(keyword)

    return render_template(
        "view_hotels.html",
        hotels=hotels
    )


# ==============================
# DELETE HOTEL
# ==============================

@app.route("/delete_hotel/<int:id>")
def remove_hotel(id):

    if "username" not in session:
        return redirect("/")

    if session.get("role") != "admin":
        flash("Access Denied!", "danger")
        return redirect("/view_hotels")

    delete_hotel(id)

    flash("Hotel Deleted Successfully", "success")

    return redirect("/view_hotels")


# ==============================
# EDIT HOTEL
# ==============================

@app.route("/edit_hotel/<int:id>", methods=["GET", "POST"])
def edit_hotel(id):

    if "username" not in session:
        return redirect("/")

    if session.get("role") != "admin":
        flash("Access Denied!", "danger")
        return redirect("/view_hotels")

    hotel = get_hotel(id)

    if request.method == "POST":

        hotel_data = {

            "id": id,
            "name": request.form["name"],
            "description": request.form["description"],
            "location": request.form["location"],
            "phone": request.form["phone"],
            "email": request.form["email"],
            "google_map": request.form["google_map"],
            "price": request.form["price"],
            "rating": request.form["rating"],
            "total_rooms": request.form["total_rooms"],
            "available_rooms": request.form["available_rooms"],
            "wifi": request.form.get("wifi", "No"),
            "pool": request.form.get("pool", "No"),
            "parking": request.form.get("parking", "No"),
            "gym": request.form.get("gym", "No"),
            "spa": request.form.get("spa", "No"),
            "restaurant": request.form.get("restaurant", "No"),
            "breakfast": request.form.get("breakfast", "No"),
            "lunch": request.form.get("lunch", "No"),
            "dinner": request.form.get("dinner", "No"),
            "image": hotel["image"]

        }

        update_complete_hotel(hotel_data)

        flash("Hotel Updated Successfully", "success")

        return redirect("/view_hotels")

    return render_template(
        "edit_hotel.html",
        hotel=hotel
    )
@app.route("/book/<int:id>", methods=["GET", "POST"])
def book_room(id):

    if "username" not in session:
        return redirect("/login")

    hotel = get_hotel(id)

    if request.method == "POST":

        rooms = int(request.form["rooms"])

        if rooms > hotel["available_rooms"]:

            flash("Rooms Not Available", "danger")

            return redirect(f"/book/{id}")

        total = rooms * hotel["price"]

        booking = {


            "customer": request.form["customer"],

            "hotel_id": hotel["id"],

            "hotel_name": hotel["name"],

            "rooms": rooms,

            "checkin": request.form["checkin"],

            "checkout": request.form["checkout"],

            "total": total,


        }

        # Save booking temporarily in session
        session["booking"] = booking

        # Go to payment page
        return redirect("/payment")

    return render_template(
        "book_room.html",
        hotel=hotel
    )

# ======================================
# PAYMENT
# ======================================

@app.route("/payment", methods=["GET", "POST"])
def payment():

    if "user_id" not in session:
        return redirect("/login")

    if "booking" not in session:
        flash("No booking found.", "danger")
        return redirect("/view_hotels")

    booking = session["booking"]

    if request.method == "POST":

        payment_method = request.form["payment"]

        # Save payment method
        booking["payment"] = payment_method

        # Save booking into database
        book_hotel(booking)

        # -----------------------------
        # Create Admin Notification
        # -----------------------------
        message = f"New booking by {booking['customer']} for {booking['hotel_name']}"
         
        add_notification(message)

        # -----------------------------
        # Remove temporary booking
        # -----------------------------
        session.pop("booking", None)

        flash("Payment Successful!", "success")
        
        return render_template(
            "booking_confirmation.html",
            booking=booking
        )

    return render_template(
        "payment.html",
        booking=booking
    )

# ==============================
# BOOKING HISTORY
# ==============================

@app.route("/booking_history")
def booking_history():

    if "username" not in session:
        return redirect("/login")

    # Admin can see all bookings
    if session["role"] == "admin":
        bookings = get_bookings()

    # User can see only their bookings
    else:
        bookings = get_user_bookings(session["username"])

    return render_template(
        "booking_history.html",
        bookings=bookings
    )
# =====================================
# BOOKING CALENDAR
# =====================================

@app.route("/booking_calendar")
def booking_calendar():

    if "role" not in session:
        return redirect("/login")

    bookings = calendar_bookings()

    return render_template(
        "booking_calendar.html",
        bookings=bookings
    )

@app.route("/receipt/<int:id>")
def receipt(id):

    booking = get_booking(id)

    return render_template(
        "payment_receipt.html",
        booking=booking
    )

@app.route("/download_receipt/<int:id>")
def download_receipt(id):

    booking = get_booking(id)

    pdf_name = f"Receipt_{id}.pdf"

    doc = SimpleDocTemplate(pdf_name)

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph("<>SMART HOTEL MANAGEMENT</b>",styles["Title"])
    )

    elements.append(
        Paragraph("<br/>",styles["BodyText"])
    )

    data=[

        ["Booking ID",booking["id"]],

        ["Hotel",booking["hotel_name"]],

        ["Customer",booking["customer"]],

        ["Rooms",booking["rooms"]],

        ["Check In",booking["checkin"]],

        ["Check Out",booking["checkout"]],

        ["Payment",booking["payment"]],

        ["Status",booking["status"]],

        ["Total","₹ "+str(booking["total"])]

    ]

    table=Table(data)

    table.setStyle(TableStyle([

        ('GRID',(0,0),(-1,-1),1,colors.black),

        ('BACKGROUND',(0,0),(-1,0),colors.lightblue),

        ('BACKGROUND',(0,0),(0,-1),colors.lightgrey),

        ('FONTNAME',(0,0),(-1,-1),'Helvetica'),

        ('BOTTOMPADDING',(0,0),(-1,-1),10)

    ]))

    elements.append(table)

    doc.build(elements)

    return send_file(pdf_name,as_attachment=True)
# ======================================
# ADMIN VIEW BOOKINGS
# ======================================

@app.route("/admin_bookings")
def admin_bookings():

    if "username" not in session:
        return redirect("/login")

    if session["role"] != "admin":
        return redirect("/user")

    bookings = get_all_bookings()

    return render_template(
        "admin_bookings.html",
        bookings=bookings
    )


# ======================================
# APPROVE BOOKING
# ======================================

@app.route("/approve_booking/<int:id>")
def approve_booking(id):

    if "role" not in session or session["role"] != "admin":
        return redirect("/login")

    update_booking_status(id, "Confirmed")

    flash("Booking Approved Successfully", "success")

    return redirect("/admin_bookings")


# ======================================
# CANCEL BOOKING
# ======================================

@app.route("/cancel_booking/<int:id>")
def cancel_booking_route(id):

    if "role" not in session or session["role"] != "admin":
        return redirect("/login")

    cancel_booking(id)

    flash("Booking Cancelled Successfully", "danger")

    return redirect("/admin_bookings")


# ======================================
# ADD TO WISHLIST
# ======================================

@app.route("/wishlist/<int:id>")
def wishlist(id):

    if "username" not in session:
        return redirect("/login")

    add_to_wishlist(
        session["user_id"],
        id
    )

    flash("Added to Wishlist!", "success")

    return redirect("/view_hotels")


# ======================================
# VIEW WISHLIST
# ======================================

@app.route("/wishlist")
def my_wishlist():

    if "user_id" not in session:
        return redirect("/login")

    hotels = get_wishlist(session["user_id"])

    return render_template(
        "wishlist.html",
        hotels=hotels
    )


# ======================================
# REMOVE WISHLIST
# ======================================

@app.route("/wishlist/remove/<int:id>")
def remove_from_wishlist(id):

    if "user_id" not in session:
        return redirect("/login")

    remove_wishlist(session["user_id"], id)

    flash("Removed From Wishlist", "warning")

    return redirect("/wishlist")
# ======================================
# USER DASHBOARD
# ======================================

@app.route("/user")
def user():

    if "user_id" not in session:
        return redirect("/login")

    hotels = get_hotels()

    return render_template(
        "user_dashboard.html",
        hotels=hotels
    )
# ---------------- LOGOUT ---------------- #

@app.route("/logout")
def logout():

    session.clear()

    flash("Logged Out Successfully", "success")

    return redirect("/")
# ======================================
# NOTIFICATIONS PAGE
# ======================================

@app.route("/notifications")
def notifications():

    if "role" not in session:
        return redirect("/login")

    if session["role"] != "admin":
        return redirect("/user")

    notifications = get_notifications()

    return render_template(
        "notifications.html",
        notifications=notifications
    )
# ==============================
# ADD REVIEW
# ==============================

@app.route("/review/<int:id>", methods=["GET", "POST"])
def review(id):

    if "username" not in session:
        return redirect("/login")

    hotel = get_hotel(id)

    if request.method == "POST":

        review = {
            "hotel_id": id,

            "username": session["username"],

            "rating": int(request.form["rating"]),

            "review": request.form["review"]

        }

        add_review(review)

        flash("Review Submitted Successfully!", "success")

        return redirect(f"/hotel/{id}")

    return render_template(
        "new_review.html",
        hotel=hotel
    )
# ======================================
# VIEW HOTEL REVIEWS
# ======================================

@app.route("/hotel_reviews/<int:id>")
def hotel_reviews(id):

    if "user_id" not in session:
        return redirect("/login")

    hotel = get_hotel(id)

    reviews = get_reviews(id)

    stats = get_review_statistics(id)

    return render_template(

        "view_reviews.html",

        hotel=hotel,

        reviews=reviews,

        avg=stats["average"],

        total_reviews=stats["total"],

        star5=stats["star5"],

        star4=stats["star4"],

        star3=stats["star3"],

        star2=stats["star2"],

        star1=stats["star1"]

    )
# ==============================
# ADMIN - ALL REVIEWS
# ==============================

@app.route("/admin_reviews")
def admin_reviews():

    if "role" not in session:
        return redirect("/login")

    if session["role"] != "admin":
        flash("Access Denied!", "danger")
        return redirect("/user")

    reviews = get_all_reviews()

    return render_template(
        "admin_reviews.html",
        reviews=reviews
    )

# ======================================
# HOTEL GALLERY
# ======================================

@app.route("/gallery/<int:id>", methods=["GET", "POST"])
def gallery(id):

    if "username" not in session:
        return redirect("/login")

    hotel = get_hotel(id)

    if hotel is None:
        flash("Hotel not found!", "danger")
        return redirect("/view_hotels")

    # Admin uploads images
    if request.method == "POST":

        if session.get("role") != "admin":
            flash("Only Admin can upload images.", "danger")
            return redirect(f"/gallery/{id}")

        image = request.files.get("image")

        if image and image.filename != "":

            filename = secure_filename(image.filename)

            image.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    filename
                )
            )

            add_gallery_image(id, filename)

            flash("Image Uploaded Successfully", "success")

        else:
            flash("Please select an image.", "warning")

        return redirect(f"/gallery/{id}")

    images = get_gallery(id)

    return render_template(
        "add_gallery.html",     # <-- Your template name
        hotel=hotel,
        images=images
    )


# ---------------- RUN ---------------- #

if __name__ == "__main__":
    app.run(debug=True)