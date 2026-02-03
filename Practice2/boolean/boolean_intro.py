print(7 > 6)
print(7 == 6)
print(7 < 6)


x = "Merci"
y = 67

print(bool(x))
print(bool(y))



class myclass():
  def __len__(self):
    return 0

myobj = myclass()
print(bool(myobj))



def myFunction() :
  return True

print(myFunction())



x = 200
print(isinstance(x, int))
