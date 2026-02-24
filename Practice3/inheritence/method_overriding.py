class Person:
  def __init__(self, fname, lname):
    self.firstname = fname
    self.lastname = lname
class Student(Person):
  def __init__(self, fname, lname):
    Person.__init__(self, fname, lname)