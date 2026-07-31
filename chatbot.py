from database import get_hotels

def chatbot_reply(message):

    msg = message.lower()

    # Greetings
    if "hello" in msg or "hi" in msg:
        return "👋 Hello! Welcome to Smart Hotel. How can I help you?"

    if "how are you" in msg:
        return "😊 I'm doing great! How can I assist you today?"

    if "thank" in msg:
        return "You're welcome! Have a wonderful day."

    # Booking
    if "book" in msg:
        return "🏨 To book a hotel, click 'Book Now' on any hotel."

    if "payment" in msg:
        return "💳 We support Cash, Card and UPI demo payments."

    if "receipt" in msg:
        return "📄 After booking you can download your PDF receipt."

    if "wishlist" in msg:
        return "❤️ Click the heart icon to save hotels."

    if "review" in msg:
        return "⭐ You can submit reviews after visiting a hotel."

    if "gallery" in msg:
        return "🖼 Every hotel has its own image gallery."

    if "location" in msg:
        return "📍 Every hotel page contains Google Map."

    if "contact" in msg:
        return "☎ Every hotel page contains phone number and email."

    if "price" in msg:

        hotels = get_hotels()

        if len(hotels) == 0:
            return "No hotels available."

        text = "💰 Hotel Prices:\n\n"

        for hotel in hotels:

            text += f"{hotel['name']} : ₹{hotel['price']}/Night\n"

        return text

    if "hotel" in msg:

        hotels = get_hotels()

        if len(hotels) == 0:
            return "No hotels available."

        text = "🏨 Available Hotels:\n\n"

        for hotel in hotels:

            text += hotel["name"] + "\n"

        return text

    return "🤖 Sorry, I didn't understand. Ask me about hotels, booking, prices, payment, reviews or wishlist."