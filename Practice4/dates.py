#Subtract five days from current date
import datetime

current_date = datetime.datetime.now()
five_days_ago = current_date - datetime.timedelta(days=5)

print("Current date:", current_date)
print("Five days ago:", five_days_ago)

#Print yesterday, today, tomorrow
import datetime

today = datetime.datetime.now()
yesterday = today - datetime.timedelta(days=1)
tomorrow = today + datetime.timedelta(days=1)

print("Yesterday:", yesterday)
print("Today:", today)
print("Tomorrow:", tomorrow)

#Drop microseconds from datetime
import datetime

now = datetime.datetime.now()
without_microseconds = now.replace(microsecond=0)

print("Before:", now)
print("After:", without_microseconds)

#Calculate difference between two dates in seconds
import datetime

date1 = datetime.datetime(2025, 2, 20, 12, 0, 0)
date2 = datetime.datetime(2025, 2, 25, 15, 30, 0)

difference = date2 - date1
seconds = difference.total_seconds()


print("Difference in seconds:", seconds)

#