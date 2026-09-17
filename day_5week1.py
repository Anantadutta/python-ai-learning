import json
students = {}
DATA_FILE="students.json"


def add_student(name,marks):
    students[name] = marks

def calculate_average(marks):
    return sum(marks.values()) / len(marks)  

def assign_grade(average):
    if average >=85:
     return "A"
    elif average >=75:
     return "B"
    else:
     return "C"
    
def find_topper():
    best_name =None
    best_avg=-1
    for name, marks in students.items():
        avg = calculate_average(marks) #calculate avg function upar line 5
        if avg > best_avg:
            best_avg = avg #these lines run iff the condn is true 
            best_name = name
    return best_name, best_avg

def students_above(threshold):
    return [name for name, marks in students.items() if calculate_average(marks) > threshold] #list comprehension
def view_all():
    for name, marks in students.items(): #loop 
        avg = calculate_average(marks)#avg compute 
        grade = assign_grade(avg)#grade compute
        print(f"{name}: {marks} | Average: {avg:.2f} | Grade: {grade}")#focring exactly 2 deci places 
def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(students, f, indent=4)

def load_data():
    global students
    try:
        with open(DATA_FILE, "r") as f:
            students = json.load(f)
    except FileNotFoundError:
        students = {}
load_data()

while True:
    print("\n1. Add Student\n2. View All\n3. Show Topper\n4. Above Average\n5. Exit")
    choice = input("Enter choice: ")
    if choice == "5":
        break
    elif choice == "1":
        name = input("Enter student name: ")
        num_subjects = int(input("How many subjects? "))
        marks = {}
        for i in range(num_subjects):
            subject = input("Subject name: ")
            score = float(input(f"Marks in {subject}: "))
            marks[subject] = score
        add_student(name, marks)
        save_data()
        print(f"{name} added successfully!")
    elif choice == "2":
        if students:
            view_all()
        else:
            print("No students yet.")
    elif choice == "3":
        if students:
            name, avg = find_topper()
            print(f"Topper: {name} with average {avg:.2f}")
        else:
            print("No students yet.")
    elif choice == "4":
        threshold = float(input("Enter threshold average: "))
        result = students_above(threshold)
        if result:
            print("Students above threshold:", result)
        else:
            print("No students above that threshold.")
    # handle other choice
