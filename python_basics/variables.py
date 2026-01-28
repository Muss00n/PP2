x = 85
y = "arsen"
print(x)
print(y)


a = str(3)    
b = int(3)    
c = float(3) 
print(a,b,c)

i, j, k = "Lebron", "Wemby", "Harden"
print(i + j + k)


x = "awful"
def W():
  x = "horrendous"
  print("This game is " + x)
W()
print("This game is " + x)



def rig():
  global x
  x = "four"
rig()
print("My kid is " + x)

