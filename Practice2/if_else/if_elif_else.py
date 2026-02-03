budget = 5000
expense = 3200

if expense > budget:
    print("Alert: Project is over budget")
elif budget == expense:
    print("Notice: Project is exactly at budget limit")
else:
    print("Success: Project is under budget")


tickets_available = 5
requested_tickets = 8

if requested_tickets > tickets_available:
    print("Booking failed: Not enough seats available")
else:
    print("Booking successful: Enjoy your trip!")


current_year = 2026

if current_year % 4 == 0:
    print("This is a leap year cycle")
else:
    print("This is a standard year cycle")


wind_speed = 45

if wind_speed > 74:
    print("Condition: Hurricane force winds")
elif wind_speed > 39:
    print("Condition: Tropical storm winds")
elif wind_speed > 15:
    print("Condition: Breezy")
else:
    print("Condition: Calm")


product_id = "B001"

if len(product_id) == 4:
    print(f"Validated: {product_id} is a correct ID format")
else:
    print("Error: Invalid ID length")