import sqlite3
import matplotlib.pyplot as plt

# DATABASE SETUP ------------------------------------------------------------------------------------------------------------------------

conn = sqlite3.connect("student_group_manager.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    roll_no INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    sgpa REAL NOT NULL,
    status TEXT DEFAULT 'active',
    group_id INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS groups_table (
    group_id INTEGER PRIMARY KEY AUTOINCREMENT,
    avg_sgpa REAL,
    status TEXT DEFAULT 'active'
)
""")

conn.commit()

#  LOAD DUMMY DATA ------------------------------------------------------------------------------------------------

def load_dummy_data():
    cursor.execute("SELECT COUNT(*) FROM students")
    if cursor.fetchone()[0] > 0:
        print("Data already exists.\n")
        return

    sample_students = [
        ("Aarav","Sharma",8.5),("Vivaan","Patel",7.8),("Aditya","Verma",9.1),
        ("Vihaan","Rao",8.2),("Arjun","Gupta",7.4),("Sai","Kulkarni",8.9),
        ("Reyansh","Mehta",6.9),("Krishna","Joshi",9.3),("Ishaan","Deshmukh",8.0),
        ("Shaurya","Naik",7.6),("Ayaan","Reddy",8.4),("Atharva","Nair",7.7),
        ("Kabir","Iyer",9.0),("Rudra","Chavan",8.1),("Yash","Pillai",7.5),
        ("Dhruv","Mishra",8.8),("Aryan","Khan",6.8),("Kunal","Bose",8.6),
        ("Manav","Singh",7.9),("Harsh","Thakur",8.3),("Neel","Dubey",9.2),
        ("Om","Sawant",7.2),("Rohan","Jadhav",8.7),("Tanish","Kapoor",8.0),
        ("Dev","Malhotra",7.3),("Parth","Chaudhary",8.9),("Siddharth","Goyal",9.4),
        ("Aniket","Bansal",7.1),("Pranav","Saxena",8.2),("Laksh","Agarwal",7.8),
        ("Varun","Trivedi",8.5),("Nikhil","Bhatt",9.0),("Shivam","Yadav",6.7),
        ("Akash","Pandey",8.6),("Rahul","Tiwari",7.4),("Kartik","Solanki",8.8),
        ("Ansh","Tomar",9.1),("Mohit","Rawat",7.9),("Uday","Shetty",8.3),
        ("Tejas","Borkar",8.7)
    ]

    cursor.executemany(
        "INSERT INTO students (first_name,last_name,sgpa) VALUES (?,?,?)",
        sample_students
    )
    conn.commit()
    print("40 Sample Students Loaded.\n")

# DISPLAY FUNCTIONS -----------------------------------------------------------------------------------------------

def print_student_table(rows, title):
    if not rows:
        print("\nNo data found.\n")
        return

    print(f"\n{title}")
    print("{:<8} {:<15} {:<15} {:<6} {:<12}".format(
        "RollNo","First Name","Last Name","SGPA","Status"
    ))
    print("-"*70)

    for row in rows:
        print("{:<8} {:<15} {:<15} {:<6} {:<12}".format(*row))
    print()

# STUDENT FUNCTIONS -----------------------------------------------------------------------------------------------

def add_student():
    fn = input("First Name: ")
    ln = input("Last Name: ")

    try:
        sgpa = float(input("SGPA: "))
        if sgpa < 0 or sgpa > 10:
            print("SGPA must be between 0 and 10.\n")
            return
    except ValueError:
        print("Invalid SGPA! Please enter a number.\n")
        return

    cursor.execute(
        "INSERT INTO students (first_name,last_name,sgpa) VALUES (?,?,?)",
        (fn, ln, sgpa)
    )
    conn.commit()
    print("Student Added Successfully.\n")

def blacklist_student():
    try:
        roll = int(input("Roll No: "))
    except ValueError:
        print("Invalid Roll Number.\n")
        return
    cursor.execute("UPDATE students SET status='blacklisted' WHERE roll_no=?", (roll,))
    conn.commit()
    print("Student Blacklisted.\n")

def activate_student():
    try:
        roll = int(input("Roll No: "))
    except ValueError:
        print("Invalid Roll Number.\n")
        return
    cursor.execute("UPDATE students SET status='active' WHERE roll_no=?", (roll,))
    conn.commit()
    print("Student Activated.\n")

def show_all_students():
    cursor.execute("SELECT roll_no,first_name,last_name,sgpa,status FROM students")
    print_student_table(cursor.fetchall(), "All Students")

def show_active_students():
    cursor.execute("SELECT roll_no,first_name,last_name,sgpa,status FROM students WHERE status='active'")
    print_student_table(cursor.fetchall(), "Active Students")

def show_blacklisted_students():
    cursor.execute("SELECT roll_no,first_name,last_name,sgpa,status FROM students WHERE status='blacklisted'")
    print_student_table(cursor.fetchall(), "Blacklisted Students")

def show_rankwise_students():
    cursor.execute("""
        SELECT roll_no,first_name,last_name,sgpa,status
        FROM students
        WHERE status='active'
        ORDER BY sgpa DESC
    """)
    print_student_table(cursor.fetchall(), "Rankwise Students")

# GROUP FORMATION -------------------------------------------------------------------------------------------------

def form_groups():
    cursor.execute("DELETE FROM groups_table")
    cursor.execute("UPDATE students SET group_id=NULL")

    cursor.execute("""
        SELECT roll_no, sgpa
        FROM students
        WHERE status='active'
        ORDER BY sgpa DESC
    """)
    students = cursor.fetchall()
    total = len(students)

    if total < 3:
        print("Not enough students.\n")
        return

    remainder = total % 4

    if remainder == 0:
        size_pattern = [4]*(total//4)
    elif remainder == 1:
        size_pattern = [4]*((total//4)-1) + [3,3]
    elif remainder == 2:
        size_pattern = [4]*((total//4)-1) + [3,3]
    else:
        size_pattern = [4]*(total//4) + [3]

    index = 0

    for size in size_pattern:
        group = students[index:index+size]
        index += size

        avg = sum([s[1] for s in group]) / len(group)
        cursor.execute("INSERT INTO groups_table (avg_sgpa) VALUES (?)",(avg,))
        gid = cursor.lastrowid

        for s in group:
            cursor.execute("UPDATE students SET group_id=? WHERE roll_no=?",(gid,s[0]))

    conn.commit()
    print("Groups Formed Successfully.\n")

# GROUP STATUS ----------------------------------------------------------------------------------------------------

def show_group_details():
    cursor.execute("""
        SELECT group_id, avg_sgpa
        FROM groups_table
        ORDER BY avg_sgpa DESC
    """)
    groups = cursor.fetchall()

    for g in groups:
        print(f"\nGroup {g[0]} | Avg SGPA: {round(g[1],2)}")
        print("-" * 45)

        cursor.execute("""
            SELECT roll_no, first_name, last_name, sgpa
            FROM students
            WHERE group_id=? AND status='active'
        """, (g[0],))

        members = cursor.fetchall()

        for m in members:
            print("{:<6} {:<15} {:<15} {:<6}".format(
                m[0], m[1], m[2], m[3]
            ))

    print()


def show_active_groups():
    cursor.execute("""
        SELECT group_id, avg_sgpa
        FROM groups_table
        WHERE status='active'
        ORDER BY avg_sgpa DESC
    """)
    groups = cursor.fetchall()

    if not groups:
        print("\nNo active groups found.\n")
        return

    for g in groups:
        print(f"\nGroup {g[0]} | Avg SGPA: {round(g[1],2)}")
        print("-" * 45)

        cursor.execute("""
            SELECT roll_no, first_name, last_name, sgpa
            FROM students
            WHERE group_id=? AND status='active'
        """, (g[0],))

        members = cursor.fetchall()

        for m in members:
            print("{:<6} {:<15} {:<15} {:<6}".format(
                m[0], m[1], m[2], m[3]
            ))

    print()

def show_blacklisted_groups():
    cursor.execute("SELECT group_id,avg_sgpa FROM groups_table WHERE status='blacklisted'")
    rows = cursor.fetchall()

    print("\nBlacklisted Groups")
    print("{:<10} {:<10}".format("GroupID","Avg SGPA"))
    print("-"*25)

    for r in rows:
        print("{:<10} {:<10}".format(r[0], round(r[1],2)))
    print()

def blacklist_group():
    gid = int(input("Group ID: "))
    cursor.execute("UPDATE groups_table SET status='blacklisted' WHERE group_id=?", (gid,))
    conn.commit()
    print("Group Blacklisted.\n")

def activate_group():
    gid = int(input("Group ID: "))
    cursor.execute("UPDATE groups_table SET status='active' WHERE group_id=?", (gid,))
    conn.commit()
    print("Group Activated.\n")

def show_rankwise_groups():
    cursor.execute("""
        SELECT group_id, avg_sgpa
        FROM groups_table
        WHERE status='active'
        ORDER BY avg_sgpa DESC
    """)
    groups = cursor.fetchall()

    print("\nRankwise Groups")
    print("{:<6} {:<10} {:<10}".format("Rank","GroupID","Avg SGPA"))
    print("-"*35)

    rank = 1
    for g in groups:
        print("{:<6} {:<10} {:<10}".format(rank, g[0], round(g[1],2)))
        rank += 1
    print()

# GRAPH -----------------------------------------------------------------------------------------------------------

def show_graph():
    cursor.execute("SELECT group_id,avg_sgpa FROM groups_table WHERE status='active'")
    data = cursor.fetchall()

    if not data:
        print("No active groups.\n")
        return

    ids = [d[0] for d in data]
    avgs = [d[1] for d in data]

    plt.figure()
    plt.plot(ids,avgs,marker='o')
    plt.xlabel("Group ID")
    plt.ylabel("Average SGPA")
    plt.title("Group SGPA Graph")
    plt.show()

# MENU ------------------------------------------------------------------------------------------------------------

while True:
    print("===== STUDENT & GROUP MANAGER =====")
    print("1.Load Dummy Data")
    print("2.Add Student")
    print("3.Blacklist Student")
    print("4.Activate Student")
    print("5.Show All Students")
    print("6.Show Active Students")
    print("7.Show Blacklisted Students")
    print("8.Show Rankwise Students")
    print("9.Form Groups")
    print("10.Show Group Details")
    print("11.Show Active Groups")
    print("12.Show Blacklisted Groups")
    print("13.Blacklist Group")
    print("14.Activate Group")
    print("15.Show Rankwise Groups")
    print("16.Show Graph")
    print("17.Exit")

    choice = input("Enter Choice: ")

    if choice == "1": load_dummy_data()
    elif choice == "2": add_student()
    elif choice == "3": blacklist_student()
    elif choice == "4": activate_student()
    elif choice == "5": show_all_students()
    elif choice == "6": show_active_students()
    elif choice == "7": show_blacklisted_students()
    elif choice == "8": show_rankwise_students()
    elif choice == "9": form_groups()
    elif choice == "10": show_group_details()
    elif choice == "11": show_active_groups()
    elif choice == "12": show_blacklisted_groups()
    elif choice == "13": blacklist_group()
    elif choice == "14": activate_group()
    elif choice == "15": show_rankwise_groups()
    elif choice == "16": show_graph()
    elif choice == "17":
        conn.close()
        print("Exiting...")
        break
    else:
        print("Invalid Choice\n")
