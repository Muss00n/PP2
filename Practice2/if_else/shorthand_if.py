p = 100
q = 50
if p > q: print("p exceeds q")


speed = 120
limit = 100
print("Over speed") if speed > limit else print("Safe speed")


team_a_goals = 3
team_b_goals = 1
lead_score = team_a_goals if team_a_goals > team_b_goals else team_b_goals
print("Top score:", lead_score)



width = 50
height = 50
print("Landscape") if width > height else print("Square") if width == height else print("Portrait")



inventory_a = 40
inventory_b = 85
highest_stock = inventory_a if inventory_a > inventory_b else inventory_b
print("Stock level:", highest_stock)


user_input = ""
status = user_input if user_input else "Offline"
print("User is:", status)