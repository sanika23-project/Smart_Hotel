import sqlite3

from config import Config

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)


# =====================================================
# DATABASE CONNECTION
# =====================================================

def get_connection():

    conn = sqlite3.connect(Config.DATABASE)

    conn.row_factory = sqlite3.Row

    return conn


# Copy old customer data if exists

    cursor.execute("""
        UPDATE reviews
        SET username = customer
        WHERE username IS NULL
        """)


    conn.commit()

    conn.close()

print("Database Updated")
# =====================================================
# DATABASE CONNECTION
# =====================================================

def get_connection():

    conn = sqlite3.connect(Config.DATABASE)

    conn.row_factory = sqlite3.Row

    return conn



# =====================================================
# CREATE DATABASE TABLES
# =====================================================

def create_tables():

    conn = get_connection()

    cursor = conn.cursor()


    # ---------------- USERS ----------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        fullname TEXT NOT NULL,

        username TEXT UNIQUE NOT NULL,

        email TEXT,

        password TEXT NOT NULL,

        role TEXT NOT NULL

    )
    """)



    # ---------------- HOTELS ----------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hotels(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        name TEXT,

        description TEXT,

        location TEXT,

        phone TEXT,

        email TEXT,

        google_map TEXT,

        price REAL,

        rating REAL,

        total_rooms INTEGER,

        available_rooms INTEGER,

        wifi TEXT,

        pool TEXT,

        parking TEXT,

        gym TEXT,

        spa TEXT,

        restaurant TEXT,

        breakfast TEXT,

        lunch TEXT,

        dinner TEXT,

        status TEXT,

        image TEXT

    )
    """)



    # ---------------- BOOKINGS ----------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookings(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        customer TEXT,

        hotel_id INTEGER,

        hotel_name TEXT,

        rooms INTEGER,

        checkin TEXT,

        checkout TEXT,

        total REAL,

        payment TEXT,

        status TEXT

    )
    """)



    # ---------------- REVIEWS ----------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reviews(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        hotel_id INTEGER,

        username TEXT,

        rating INTEGER,

        review TEXT,

        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )
    """)
    # =====================================================
    # GET HOTEL REVIEWS
    # =====================================================

    def get_reviews(hotel_id):
        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM reviews
            WHERE hotel_id=?
            ORDER BY id DESC
        """,
        (
            hotel_id,
        ))

        reviews = cursor.fetchall()

        conn.close()

        return reviews

    

    # ---------------- GALLERY ----------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS gallery(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        hotel_id INTEGER,

        image TEXT

    )
    """)



    # ---------------- WISHLIST ----------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS wishlist(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER,

        hotel_id INTEGER,

        UNIQUE(user_id,hotel_id)

    )
    """)



    # ---------------- NOTIFICATIONS ----------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notifications(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        message TEXT,

        status TEXT DEFAULT 'Unread',

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )
    """)



    conn.commit()

    conn.close()


# ======================================
# GET NOTIFICATIONS
# ======================================

def get_notifications():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM notifications
        ORDER BY id DESC
    """)

    notifications = cursor.fetchall()

    conn.close()

    return notifications
# ======================================
# DASHBOARD DATA
# ======================================

def get_dashboard_data():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM hotels")
    total_hotels = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users WHERE role='user'")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bookings")
    total_bookings = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(total) FROM bookings")
    revenue = cursor.fetchone()[0]

    if revenue is None:
        revenue = 0

    cursor.execute("""
        SELECT
            SUM(total_rooms),
            SUM(available_rooms)
        FROM hotels
    """)

    rooms = cursor.fetchone()

    total_rooms = rooms[0] if rooms[0] else 0
    available_rooms = rooms[1] if rooms[1] else 0

    conn.close()

    return {
        "total_hotels": total_hotels,
        "total_users": total_users,
        "total_bookings": total_bookings,
        "total_revenue": revenue,
        "total_rooms": total_rooms,
        "available_rooms": available_rooms
    }

# ======================================
# DASHBOARD CHART DATA
# ======================================

def dashboard_chart_data():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            hotel_name,
            COUNT(*) AS total
        FROM bookings
        GROUP BY hotel_name
    """)

    booking_chart = cursor.fetchall()

    cursor.execute("""
        SELECT
            name,
            total_rooms,
            available_rooms
        FROM hotels
    """)

    hotel_chart = cursor.fetchall()

    conn.close()

    return booking_chart, hotel_chart
# ======================================
# MARK NOTIFICATION AS READ
# ======================================

def mark_notification_read(id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE notifications
        SET status='Read'
        WHERE id=?
    """, (id,))

    conn.commit()
    conn.close()

# =====================================================
# CREATE DEFAULT ADMIN ACCOUNT
# =====================================================

def create_default_admin():

    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute(
        "SELECT * FROM users WHERE username=?",
        ("admin",)
    )


    admin = cursor.fetchone()



    if admin is None:


        password = generate_password_hash(
            "admin123"
        )


        cursor.execute("""
        INSERT INTO users(

            fullname,

            username,

            email,

            password,

            role

        )

        VALUES(?,?,?,?,?)

        """,
        (

            "Administrator",

            "admin",

            "admin@gmail.com",

            password,

            "admin"

        ))



        conn.commit()



    conn.close()





# =====================================================
# USER REGISTRATION
# =====================================================

def register_user(
        fullname,
        username,
        email,
        password
):

    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute(
        "SELECT * FROM users WHERE username=?",
        (username,)
    )



    if cursor.fetchone():

        conn.close()

        return False



    password = generate_password_hash(password)



    cursor.execute("""
    INSERT INTO users(

        fullname,

        username,

        email,

        password,

        role

    )

    VALUES(?,?,?,?,?)

    """,
    (

        fullname,

        username,

        email,

        password,

        "user"

    ))



    conn.commit()

    conn.close()


    return True





# =====================================================
# USER LOGIN
# =====================================================

def login_user(
        username,
        password
):

    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute(
        "SELECT * FROM users WHERE username=?",
        (username,)
    )


    user = cursor.fetchone()


    conn.close()



    if user:

        if check_password_hash(
            user["password"],
            password
        ):

            return user



    return None





# =====================================================
# GET USER BY ID
# =====================================================

def get_user(id):

    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute(
        "SELECT * FROM users WHERE id=?",
        (id,)
    )


    user = cursor.fetchone()


    conn.close()


    return user





# =====================================================
# ADD HOTEL
# =====================================================

def add_hotel(data):

    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute("""
    INSERT INTO hotels(

        name,

        description,

        location,

        phone,

        email,

        google_map,

        price,

        rating,

        total_rooms,

        available_rooms,

        wifi,

        pool,

        parking,

        gym,

        spa,

        restaurant,

        breakfast,

        lunch,

        dinner,

        status,

        image

    )

    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)

    """,
    (

        data["name"],

        data["description"],

        data["location"],

        data["phone"],

        data["email"],

        data["google_map"],

        data["price"],

        data["rating"],

        data["total_rooms"],

        data["total_rooms"],

        data["wifi"],

        data["pool"],

        data["parking"],

        data["gym"],

        data["spa"],

        data["restaurant"],

        data["breakfast"],

        data["lunch"],

        data["dinner"],

        "Available",

        data["image"]

    ))



    conn.commit()

    conn.close()





# =====================================================
# GET ALL HOTELS
# =====================================================

def get_hotels():

    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute("""
        SELECT *
        FROM hotels
        ORDER BY id DESC
    """)



    hotels = cursor.fetchall()


    conn.close()


    return hotels





# =====================================================
# GET SINGLE HOTEL
# =====================================================

def get_hotel(id):

    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute(
        "SELECT * FROM hotels WHERE id=?",
        (id,)
    )


    hotel = cursor.fetchone()


    conn.close()


    return hotel

# =====================================================
# DELETE HOTEL
# =====================================================

def delete_hotel(id):

    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute(
        "DELETE FROM hotels WHERE id=?",
        (id,)
    )


    conn.commit()

    conn.close()





# =====================================================
# UPDATE COMPLETE HOTEL
# =====================================================

def update_complete_hotel(data):

    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute("""
    UPDATE hotels SET

        name=?,

        description=?,

        location=?,

        phone=?,

        email=?,

        google_map=?,

        price=?,

        rating=?,

        total_rooms=?,

        available_rooms=?,

        wifi=?,

        pool=?,

        parking=?,

        gym=?,

        spa=?,

        restaurant=?,

        breakfast=?,

        lunch=?,

        dinner=?,

        image=?


    WHERE id=?

    """,
    (

        data["name"],

        data["description"],

        data["location"],

        data["phone"],

        data["email"],

        data["google_map"],

        data["price"],

        data["rating"],

        data["total_rooms"],

        data["available_rooms"],

        data["wifi"],

        data["pool"],

        data["parking"],

        data["gym"],

        data["spa"],

        data["restaurant"],

        data["breakfast"],

        data["lunch"],

        data["dinner"],

        data["image"],

        data["id"]

    ))


    conn.commit()

    conn.close()





# =====================================================
# SEARCH HOTELS
# =====================================================

def search_hotels(keyword):

    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute("""
    
    SELECT *

    FROM hotels

    WHERE

    name LIKE ?

    OR

    location LIKE ?

    ORDER BY id DESC

    """,
    (

        "%" + keyword + "%",

        "%" + keyword + "%"

    ))


    hotels = cursor.fetchall()


    conn.close()


    return hotels





# =====================================================
# BOOK HOTEL
# =====================================================

def book_hotel(data):

    conn = get_connection()

    cursor = conn.cursor()



    # Check available rooms

    cursor.execute("""
        SELECT available_rooms
        FROM hotels
        WHERE id=?
    """,
    (
        data["hotel_id"],
    ))



    hotel = cursor.fetchone()



    if hotel is None:

        conn.close()

        return False



    if hotel["available_rooms"] < data["rooms"]:

        conn.close()

        return False





    # Insert Booking

    cursor.execute("""
    INSERT INTO bookings(

        customer,

        hotel_id,

        hotel_name,

        rooms,

        checkin,

        checkout,

        total,

        payment,

        status

    )

    VALUES(?,?,?,?,?,?,?,?,?)

    """,
    (

        data["customer"],

        data["hotel_id"],

        data["hotel_name"],

        data["rooms"],

        data["checkin"],

        data["checkout"],

        data["total"],

        data["payment"],

        "Confirmed"

    ))





    # Reduce Available Rooms

    cursor.execute("""
    UPDATE hotels

    SET available_rooms = available_rooms - ?

    WHERE id=?

    """,
    (

        data["rooms"],

        data["hotel_id"]

    ))



    conn.commit()

    conn.close()


    return True





# =====================================================
# GET ALL BOOKINGS ADMIN
# =====================================================

def get_all_bookings():

    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute("""
        SELECT *

        FROM bookings

        ORDER BY id DESC
    """)


    bookings = cursor.fetchall()


    conn.close()


    return bookings





# =====================================================
# USER BOOKINGS
# =====================================================

def get_user_bookings(username):

    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute("""
    
    SELECT *

    FROM bookings

    WHERE customer=?

    ORDER BY id DESC

    """,
    (
        username,
    ))



    bookings = cursor.fetchall()


    conn.close()


    return bookings





# =====================================================
# SINGLE BOOKING
# =====================================================

def get_booking(id):

    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute(
        "SELECT * FROM bookings WHERE id=?",
        (id,)
    )


    booking = cursor.fetchone()


    conn.close()


    return booking





# =====================================================
# UPDATE BOOKING STATUS
# =====================================================

def update_booking_status(id,status):

    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute("""
        UPDATE bookings

        SET status=?

        WHERE id=?

    """,
    (

        status,

        id

    ))


    conn.commit()

    conn.close()





# =====================================================
# CANCEL BOOKING
# =====================================================

def cancel_booking(id):

    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute(
        "SELECT * FROM bookings WHERE id=?",
        (id,)
    )


    booking = cursor.fetchone()



    if booking:


        # Restore rooms

        cursor.execute("""
        UPDATE hotels

        SET available_rooms = available_rooms + ?

        WHERE id=?

        """,
        (

            booking["rooms"],

            booking["hotel_id"]

        ))



        cursor.execute(
            "DELETE FROM bookings WHERE id=?",
            (id,)
        )



    conn.commit()

    conn.close()





# =====================================================
# BOOKING CALENDAR DATA
# =====================================================

def calendar_bookings():

    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute("""
    
    SELECT

        hotel_name,

        customer,

        checkin,

        checkout


    FROM bookings

    ORDER BY checkin

    """)



    bookings = cursor.fetchall()


    conn.close()


    return bookings





# =====================================================
# DASHBOARD DATA
# =====================================================

def get_dashboard_data():

    conn = get_connection()

    cursor = conn.cursor()



    # Total Hotels

    cursor.execute(
        "SELECT COUNT(*) FROM hotels"
    )

    total_hotels = cursor.fetchone()[0]



    # Total Users

    cursor.execute("""
        SELECT COUNT(*)

        FROM users

        WHERE role='user'
    """)


    total_users = cursor.fetchone()[0]



    # Total Bookings

    cursor.execute(
        "SELECT COUNT(*) FROM bookings"
    )


    total_bookings = cursor.fetchone()[0]



    # Revenue

    cursor.execute(
        "SELECT SUM(total) FROM bookings"
    )


    revenue = cursor.fetchone()[0]


    if revenue is None:

        revenue = 0





    # Rooms

    cursor.execute("""
        SELECT

        SUM(total_rooms),

        SUM(available_rooms)

        FROM hotels
    """)



    rooms = cursor.fetchone()



    total_rooms = rooms[0] if rooms[0] else 0

    available_rooms = rooms[1] if rooms[1] else 0




    conn.close()



    return {


        "total_hotels": total_hotels,


        "total_users": total_users,


        "total_bookings": total_bookings,


        "total_revenue": revenue,


        "total_rooms": total_rooms,


        "available_rooms": available_rooms

    }





# =====================================================
# DASHBOARD CHART DATA
# =====================================================

def dashboard_chart_data():

    conn = get_connection()

    cursor = conn.cursor()



    # Booking Chart

    cursor.execute("""
        SELECT

        hotel_name,

        COUNT(*) AS total


        FROM bookings


        GROUP BY hotel_name

    """)



    booking_chart = cursor.fetchall()



    # Room Occupancy Chart

    cursor.execute("""
        SELECT

        name,

        total_rooms,

        available_rooms


        FROM hotels

    """)



    hotel_chart = cursor.fetchall()



    conn.close()



    return booking_chart, hotel_chart
# =====================================================
# TOTAL REVENUE
# =====================================================

def get_total_revenue():

    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute("""
        SELECT SUM(total)

        FROM bookings
    """)


    revenue = cursor.fetchone()[0]


    conn.close()


    return revenue if revenue else 0





# =====================================================
# TOTAL USERS
# =====================================================

def total_users():

    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute("""
        SELECT COUNT(*)

        FROM users

        WHERE role='user'
    """)


    count = cursor.fetchone()[0]


    conn.close()


    return count





# =====================================================
# TOTAL BOOKINGS
# =====================================================

def total_bookings():

    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute("""
        SELECT COUNT(*)

        FROM bookings
    """)


    count = cursor.fetchone()[0]


    conn.close()


    return count





# =====================================================
# TOTAL HOTELS
# =====================================================

def total_hotels():

    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute("""
        SELECT COUNT(*)

        FROM hotels
    """)


    count = cursor.fetchone()[0]


    conn.close()


    return count





# =====================================================
# AVAILABLE ROOMS
# =====================================================

def total_available_rooms():

    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute("""
        SELECT SUM(available_rooms)

        FROM hotels
    """)


    rooms = cursor.fetchone()[0]


    conn.close()


    return rooms if rooms else 0





# =====================================================
# ADD REVIEW
# =====================================================

def add_review(review):

    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute("""
    
    INSERT INTO reviews(

        hotel_id,

        username,

        rating,

        review

    )

    VALUES(?,?,?,?)

    """,
    (

        review["hotel_id"],

        review["username"],

        review["rating"],

        review["review"]

    ))



    conn.commit()

    conn.close()


# =====================================================
# GET REVIEWS OF SINGLE HOTEL
# =====================================================

def get_reviews(hotel_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
    
        SELECT *

        FROM reviews

        WHERE hotel_id=?

        ORDER BY id DESC

    """,
    (
        hotel_id,
    ))

    reviews = cursor.fetchall()

    conn.close()

    return reviews


# =====================================================
# GET ALL REVIEWS ADMIN
# =====================================================

def get_all_reviews():

    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute("""
    
    SELECT

        reviews.*,

        hotels.name AS hotel_name


    FROM reviews


    INNER JOIN hotels


    ON reviews.hotel_id = hotels.id


    ORDER BY reviews.id DESC

    """)



    reviews = cursor.fetchall()



    conn.close()



    return reviews





# =====================================================
# AVERAGE HOTEL RATING
# =====================================================

def get_average_rating(hotel_id):

    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute("""
    
    SELECT AVG(rating)

    FROM reviews

    WHERE hotel_id=?

    """,
    (
        hotel_id,
    ))



    avg = cursor.fetchone()[0]


    conn.close()



    if avg:

        return round(avg,1)


    return 0





# =====================================================
# REVIEW STATISTICS
# =====================================================

def get_review_statistics(hotel_id):

    conn = get_connection()

    cursor = conn.cursor()



    stats = {}



    # Average rating

    cursor.execute("""
        SELECT ROUND(AVG(rating),1)

        FROM reviews

        WHERE hotel_id=?
    """,
    (
        hotel_id,
    ))



    average = cursor.fetchone()[0]


    stats["average"] = average if average else 0




    # Total reviews

    cursor.execute("""
        SELECT COUNT(*)

        FROM reviews

        WHERE hotel_id=?
    """,
    (
        hotel_id,
    ))



    stats["total"] = cursor.fetchone()[0]




    # Star wise count

    for star in range(5,0,-1):


        cursor.execute("""
            SELECT COUNT(*)

            FROM reviews

            WHERE hotel_id=?

            AND rating=?

        """,
        (

            hotel_id,

            star

        ))



        stats[f"star{star}"] = cursor.fetchone()[0]



    conn.close()


    return stats





# =====================================================
# ADD TO WISHLIST
# =====================================================

def add_to_wishlist(user_id, hotel_id):

    conn = get_connection()

    cursor = conn.cursor()



    try:

        cursor.execute("""
            INSERT INTO wishlist(

                user_id,

                hotel_id

            )

            VALUES(?,?)

        """,
        (

            user_id,

            hotel_id

        ))


        conn.commit()


    except sqlite3.IntegrityError:

        pass



    conn.close()





# =====================================================
# GET USER WISHLIST
# =====================================================

def get_wishlist(user_id):

    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute("""
    
    SELECT hotels.*

    FROM hotels


    INNER JOIN wishlist


    ON hotels.id = wishlist.hotel_id


    WHERE wishlist.user_id=?


    ORDER BY wishlist.id DESC


    """,
    (
        user_id,
    ))



    hotels = cursor.fetchall()



    conn.close()



    return hotels





# =====================================================
# REMOVE FROM WISHLIST
# =====================================================

def remove_wishlist(user_id,hotel_id):

    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute("""
        DELETE FROM wishlist

        WHERE user_id=?

        AND hotel_id=?

    """,
    (

        user_id,

        hotel_id

    ))



    conn.commit()

    conn.close()





# =====================================================
# ADD GALLERY IMAGE
# =====================================================

def add_gallery_image(hotel_id,filename):

    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute("""
    
    INSERT INTO gallery(

        hotel_id,

        image

    )

    VALUES(?,?)

    """,
    (

        hotel_id,

        filename

    ))



    conn.commit()

    conn.close()





# =====================================================
# GET GALLERY IMAGES
# =====================================================

def get_gallery(hotel_id):

    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute("""
    
    SELECT *

    FROM gallery


    WHERE hotel_id=?


    ORDER BY id DESC


    """,
    (
        hotel_id,
    ))



    images = cursor.fetchall()



    conn.close()



    return images





# =====================================================
# DELETE GALLERY IMAGE
# =====================================================

def delete_gallery_image(image_id):

    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute("""
        DELETE FROM gallery

        WHERE id=?

    """,
    (
        image_id,
    ))



    conn.commit()

    conn.close()





# =====================================================
# GET SINGLE GALLERY IMAGE
# =====================================================

def get_gallery_image(image_id):

    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute("""
        SELECT *

        FROM gallery

        WHERE id=?

    """,
    (
        image_id,
    ))



    image = cursor.fetchone()



    conn.close()



    return image





# =====================================================
# ADD NOTIFICATION
# =====================================================

def add_notification(message):

    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute("""
        INSERT INTO notifications(

            message

        )

        VALUES(?)

    """,
    (
        message,
    ))



    conn.commit()

    conn.close()





# =====================================================
# GET ALL NOTIFICATIONS
# =====================================================

def get_notifications():

    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute("""
    
    SELECT *

    FROM notifications

    ORDER BY created_at DESC


    """)



    notifications = cursor.fetchall()



    conn.close()



    return notifications





# =====================================================
# MARK NOTIFICATION AS READ
# =====================================================

def mark_notification_read(notification_id):

    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute("""
        UPDATE notifications

        SET status='Read'

        WHERE id=?

    """,
    (
        notification_id,
    ))



    conn.commit()

    conn.close()





# =====================================================
# DELETE NOTIFICATION
# =====================================================

def delete_notification(notification_id):

    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute("""
        DELETE FROM notifications

        WHERE id=?

    """,
    (
        notification_id,
    ))



    conn.commit()

    conn.close()





# =====================================================
# UNREAD NOTIFICATION COUNT
# =====================================================

def unread_notification_count():

    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute("""
    
    SELECT COUNT(*)

    FROM notifications

    WHERE status='Unread'


    """)



    count = cursor.fetchone()[0]



    conn.close()



    return count
# ======================================
# MONTHLY REVENUE
# ======================================

def monthly_revenue():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

    SELECT

    substr(checkin,6,2) AS month,

    SUM(total)

    FROM bookings

    GROUP BY month

    ORDER BY month

    """)

    data = cursor.fetchall()

    conn.close()

    return data