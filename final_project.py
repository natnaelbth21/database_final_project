import mysql.connector
from mysql.connector.errors import DatabaseError, Error
import random


DB_NAME = "school_database"

def connect_db(host:str, username:str, password:str):
    try:
        session = mysql.connector.connect(
        host=host,
        user=username,
        password=password
        )
        print("connect_db: OK")
        return session
    except DatabaseError as de:
        print("Failed to connect to database.\nerror: {}".format(de))
        exit(1)

# CREATE TABELES
def create_databases(session:'mysql.connector.connection_cext.CMySQLConnection', DB_NAME:str):
    try:
        cursor = session.cursor()
        print("Creating database {}".format(DB_NAME))
        cursor.execute("create database {}".format(DB_NAME))
        print("create_database: OK")
    except DatabaseError as de:
        if de.errno == 1007:
            print("create_database: database {} already exists.".format(DB_NAME))
            return
        else:
            print("Faild to create database, error:".format(de))
        exit(1)

def create_table_users(session:'mysql.connector.connection_cext.CMySQLConnection'):
    command = """CREATE TABLE users (
                user_id INT PRIMARY KEY AUTO_INCREMENT,
                username VARCHAR(50) UNIQUE,
                password VARCHAR(255),
                email VARCHAR(100),
                role ENUM('teacher', 'parent'),
                full_name VARCHAR(100),
                phone_number VARCHAR(15)
                );"""
    
    print("creating user table")
    cursor = session.cursor()
    cursor.execute("use {}".format(DB_NAME))
    try:
        cursor.execute(command)
        print("OK")
    except DatabaseError as de:
        if de.errno == 1050:
            print(de)
            return
        else:
            print(de)
            exit(1)

def create_table_students(session:'mysql.connector.connection_cext.CMySQLConnection'):
    command = """CREATE TABLE students (
                student_id INT PRIMARY KEY AUTO_INCREMENT,
                id_number VARCHAR(10) UNIQUE,
                first_name VARCHAR(50), 
                last_name VARCHAR(50), 
                date_of_birth DATE, 
                email VARCHAR(50), 
                phone_number VARCHAR(15), 
                address VARCHAR(255)
            );"""
    print("creating students table")
    cursor = session.cursor()
    cursor.execute("use {}".format(DB_NAME))
    try:
        cursor.execute(command)
        print("OK")
    except DatabaseError as de:
        if de.errno == 1050:
            print(de)
            return
        else:
            print(de)
            exit(1)

def create_table_subjects(session:'mysql.connector.connection_cext.CMySQLConnection'):
    command = """CREATE TABLE subjects (
                subject_id INT PRIMARY KEY AUTO_INCREMENT, 
                subject_name VARCHAR(50) UNIQUE, 
                teacher_id INT,
                start_date DATE,
                end_date DATE,
                total_points INT,
                
                FOREIGN KEY (teacher_id) REFERENCES users(user_id)                
            );"""

    print("creating subjects table")
    cursor = session.cursor()
    cursor.execute("use {}".format(DB_NAME))
    try:
        cursor.execute(command)
        print("OK")
    except DatabaseError as de:
        if de.errno == 1050:
            print(de)
            return
        else:
            print(de)
            exit(1)

def create_table_results(session:'mysql.connector.connection_cext.CMySQLConnection'):
    # the UNIQUE (student_id, subject_id) command will make sure
    # that the combination of student_id and subject_id is unique
    # this will make sure a student has only one entry on one subject
    command = """CREATE TABLE results (
                result_id INT PRIMARY KEY AUTO_INCREMENT, 
                student_id INT, 
                subject_id INT,
                points INT,
                percent FLOAT,
                
                UNIQUE (student_id, subject_id),
                
                FOREIGN KEY (student_id) REFERENCES students(student_id),
                FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
            );"""

    print("creating results table")
    cursor = session.cursor()
    cursor.execute("use {}".format(DB_NAME))
    try:
        cursor.execute(command)
        print("OK")
    except DatabaseError as de:
        if de.errno == 1050:
            print(de)
            return
        else:
            print(de)
            exit(1)

# CREATE TRIGGERS
def trigger_percent_results(session:'mysql.connector.connection_cext.CMySQLConnection'):
    """
    creates a trigger that calculates and inserts/updates a percent
    to the percent column in results table (points/total_points)*100
    """
    cursor = session.cursor()
    cursor.execute("use {}".format(DB_NAME))    
    # Drop triggers if they already exist
    cursor.execute("DROP TRIGGER IF EXISTS insert_percent;")
    cursor.execute("DROP TRIGGER IF EXISTS update_percent;")
    
    # trigger on inserting result
    on_insert_trigger = """
                CREATE TRIGGER insert_percent
                BEFORE INSERT ON results FOR EACH ROW
                BEGIN
                    DECLARE total INT;
                    SELECT total_points INTO total FROM subjects WHERE subject_id = NEW.subject_id;
                    SET NEW.percent = NEW.points / total;
                END
                """
    on_update_trigger = """
                CREATE TRIGGER update_percent
                BEFORE UPDATE ON results FOR EACH ROW
                BEGIN
                    DECLARE total INT;
                    SELECT total_points INTO total FROM subjects WHERE subject_id = NEW.subject_id;
                    SET NEW.percent = NEW.points / total;
                END
                """
    try:
        cursor.execute(on_insert_trigger)
        session.commit()
        print("insert_percent trigger added")
        
        cursor.execute(on_update_trigger)
        session.commit()
        print("update_percent trigger added")
        
        return
    except DatabaseError as de:
        print(de)
        session.rollback()
        return

# INSERT DATA
def insert_user(session:'mysql.connector.connection_cext.CMySQLConnection', username:str, password:str, email:str, role:str, full_name:str, phone_number:str):
    command = """
                INSERT INTO users (username, password, email, role, full_name, phone_number)
                VALUES ('{}', '{}', '{}', '{}', '{}', '{}')
                """.format(username, password, email, role, full_name, phone_number)
    
    cursor = session.cursor()
    try:
        cursor.execute("use {}".format(DB_NAME))
        cursor.execute(command)
        session.commit()
    except DatabaseError as de:
        if de.errno == 1062:
            print("user name {} already exists, please choose a different user name.".format(username))
            return
        else:
            print(de)
            return
        
def insert_student(session:'mysql.connector.connection_cext.CMySQLConnection',id_number:str, first_name:str, last_name:str, date_of_birth:str, email:str, phone_number:str, address:str):
    command = """
                INSERT INTO students (id_number, first_name, last_name, date_of_birth, email, phone_number, address)
                VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}')
                """.format(id_number, first_name, last_name, date_of_birth, email, phone_number, address)
    
    cursor = session.cursor()
    try:
        cursor.execute("use {}".format(DB_NAME))
        cursor.execute(command)
        session.commit()
    except DatabaseError as de:
        if de.errno == 1062:
            print("student already exists.")
            return
        else:
            print(de)
            return

def insert_subject(session:'mysql.connector.connection_cext.CMySQLConnection', subject_name:str, teacher_id:str, start_date:str, end_date:str, total_points:str):
    command = """
                INSERT INTO subjects (subject_name, teacher_id, start_date, end_date, total_points)
                VALUES ('{}', '{}', '{}', '{}', '{}')
                """.format(subject_name, teacher_id, start_date, end_date, total_points)
    
    cursor = session.cursor()
    try:
        cursor.execute("use {}".format(DB_NAME))
        cursor.execute(command)
        session.commit()
    except DatabaseError as de:
        if de.errno == 1062:
            print("subject already exists.")
            return
        else:
            print(de)
            return

def populate_results_table(session: 'mysql.connector.connection_cext.CMySQLConnection', num_entries: int):
    """
    Populates the results table with random data.
    
    Parameters:
    - session: MySQL connection object
    - num_entries: Number of random entries to insert
    """
    cursor = session.cursor()
    cursor.execute("USE {}".format(DB_NAME))
    
    # Fetch all student_ids
    cursor.execute("SELECT student_id FROM students;")
    student_ids = [row[0] for row in cursor.fetchall()]
    
    # Fetch all subject_ids
    cursor.execute("SELECT subject_id FROM subjects;")
    subject_ids = [row[0] for row in cursor.fetchall()]
    
    # Generate random data and insert into results table
    for _ in range(num_entries):
        student_id = random.choice(student_ids)
        subject_id = random.choice(subject_ids)
        if subject_id == '9' or '10':
            points = random.randint(0, 50)
        else:
            points = random.randint(0, 100)  # Assuming points are between 0 and 100
        
        # Insert data into results table
        command = """
            INSERT INTO results (student_id, subject_id, points)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE points=VALUES(points);
        """
        try:
            cursor.execute(command, (student_id, subject_id, points))
            session.commit()
        except Error as e:
            print(f"Error inserting data: {e}")
            session.rollback()
    
    print(f"Inserted {num_entries} entries into the results table.")
    cursor.close()

def populate_database(session:'mysql.connector.connection_cext.CMySQLConnection'):
    cursor = session.cursor()
    cursor.execute("use {}".format(DB_NAME))
    #--INSERT TEACHERS -------------------------------------------------------------------------------------------#
    teachers = [
        ('john_doe', 'password', 'john.doe@example.com', 'teacher', 'John Doe', '1234567890'),
        ('samuel_green', 'mypassword', 'samuel.green@school.com', 'teacher', 'Samuel Green', '0722334455'),
        ('jane_smith', 'securepass', 'jane.smith@school.com', 'teacher', 'Jane Smith', '0787654321'),
        ('linda_white', 'lindapass', 'linda.white@school.com', 'teacher', 'Linda White', '0733445566'),
        ('michael_brown', 'michael123', 'michael.brown@school.com', 'teacher', 'Michael Brown', '0744556677')
    ]
    print("inserting teachers")
    for teacher in teachers:
        insert_user(session, teacher[0], teacher[1], teacher[2], teacher[3], teacher[4], teacher[5])
    #--------------------------------------------------------------------------------------------------------#

    #--INSERT PARENTS -------------------------------------------------------------------------------------------#
    parents = [
        ('alice_jones', 'alicepass', 'alice.jones@example.com', 'parent', 'Alice Jones', '1234567891'),
        ('bob_smith', 'bobpass', 'bob.smith@example.com', 'parent', 'Bob Smith', '2234567892'),
        ('charlie_brown', 'charliepass', 'charlie.brown@example.com', 'parent', 'Charlie Brown', '3234567893'),
        ('david_clark', 'davidpass', 'david.clark@example.com', 'parent', 'David Clark', '4234567894'),
        ('eva_green', 'evapass', 'eva.green@example.com', 'parent', 'Eva Green', '5234567895'),
        ('frank_white', 'frankpass', 'frank.white@example.com', 'parent', 'Frank White', '6234567896'),
        ('grace_black', 'gracepass', 'grace.black@example.com', 'parent', 'Grace Black', '7234567897'),
        ('henry_adams', 'henrypass', 'henry.adams@example.com', 'parent', 'Henry Adams', '8234567898'),
        ('isabel_king', 'isabelpass', 'isabel.king@example.com', 'parent', 'Isabel King', '9234567899'),
        ('jack_lee', 'jackpass', 'jack.lee@example.com', 'parent', 'Jack Lee', '1023456789')
    ]
    print("inserting parents")
    for parent in parents:
        insert_user(session, parent[0], parent[1], parent[2], parent[3], parent[4], parent[5])
    #--------------------------------------------------------------------------------------------------------#

    #--INSERT STUDENTS -------------------------------------------------------------------------------------------#
    students = [
        ('AB12345678', 'Erik', 'Johansson', '2005-05-15', 'erik.johansson@student.school.com', '0701234567', 'Storgatan 1, 111 29 Stockholm'),
        ('CD23456789', 'Anna', 'Nilsson', '2006-03-22', 'anna.nilsson@student.school.com', '0702345678', 'Drottninggatan 2, 113 20 Stockholm'),
        ('EF34567890', 'Oskar', 'Lindberg', '2004-11-11', 'oskar.lindberg@student.school.com', '0703456789', 'Sveavägen 3, 114 35 Stockholm'),
        ('GH45678901', 'Sara', 'Larsson', '2005-07-07', 'sara.larsson@student.school.com', '0704567890', 'Kungsgatan 4, 111 43 Stockholm'),
        ('IJ56789012', 'Lukas', 'Andersson', '2006-02-19', 'lukas.andersson@student.school.com', '0705678901', 'Vasagatan 5, 111 20 Stockholm'),
        ('KL67890123', 'Emma', 'Karlsson', '2004-10-10', 'emma.karlsson@student.school.com', '0706789012', 'Birger Jarlsgatan 6, 114 34 Stockholm'),
        ('MN78901234', 'Viktor', 'Svensson', '2005-01-01', 'viktor.svensson@student.school.com', '0707890123', 'Hornsgatan 7, 118 46 Stockholm'),
        ('OP89012345', 'Matilda', 'Gustafsson', '2006-08-08', 'matilda.gustafsson@student.school.com', '0708901234', 'Götgatan 8, 118 26 Stockholm'),
        ('QR90123456', 'William', 'Pettersson', '2004-06-15', 'william.pettersson@student.school.com', '0709012345', 'Folkungagatan 9, 116 30 Stockholm'),
        ('ST01234567', 'Elin', 'Eriksson', '2005-09-09', 'elin.eriksson@student.school.com', '0700123456', 'Odengatan 10, 113 22 Stockholm')
    ]
    print("inserting students")
    for student in students:
        insert_student(session, student[0], student[1], student[2], student[3], student[4], student[5], student[6])
    #--------------------------------------------------------------------------------------------------------#

    #--INSERT SUBJECTS -------------------------------------------------------------------------------------------#
    subjects = [
        ('Mathematics', 'john_doe', '2024-09-01', '2024-12-15', 100),
        ('Physics', 'samuel_green', '2024-09-01', '2024-12-15', 100),
        ('Chemistry', 'jane_smith', '2024-09-01', '2024-12-15', 100),
        ('Biology', 'linda_white', '2024-09-01', '2024-12-15', 100),
        ('History', 'michael_brown', '2024-09-01', '2024-12-15', 100),
        ('Geography', 'john_doe', '2024-09-01', '2024-12-15', 100),
        ('English', 'samuel_green', '2024-09-01', '2024-12-15', 100),
        ('Swedish', 'jane_smith', '2024-09-01', '2024-12-15', 100),
        ('Art', 'linda_white', '2024-09-01', '2024-12-15', 50),
        ('Music', 'michael_brown', '2024-09-01', '2024-12-15', 50)
    ]
    cursor = session.cursor()
    print("inserting subjects")
    for subject in subjects:
        # select target teacher of the subject from users table by identifying him using username
        cursor.execute("SELECT user_id FROM users WHERE username='{}';".format(subject[1]))
        teacher = cursor.fetchone() # save result of the quiry (its a tuple), returns none if user not found
        if teacher:
            insert_subject(session, subject[0], teacher[0], subject[2], subject[3], subject[4])
        else:
            print("teacher {} not found".format(subject[1]))
    #--------------------------------------------------------------------------------------------------------#

# SELECT, INSERT, UPDATE, INNER JOIN
def fetch_result(session:'mysql.connector.connection_cext.CMySQLConnection', id_number:str, subject_name=""):
    """
    used to fetch resutls of a student on a given subject.\n
    if subject name is not given it will fetch results of all subjects to that student.\n
    returns a list of the results as tupels if any,\n
    else it will return empty list if result is empty
    """
    cursor = session.cursor()
    cursor.execute("use {}".format(DB_NAME))    
    
    command = """
                SELECT subjects.subject_name, results.points, subjects.total_points, results.percent
                FROM results INNER JOIN subjects
                ON results.subject_id = subjects.subject_id
                WHERE results.student_id = (SELECT student_id FROM students WHERE id_number='{}')
                """.format(id_number)
    # specify subject if given as a parameter
    if subject_name:
        specify_subject = "AND subjects.subject_name='{}'".format(subject_name)
        command += specify_subject
    cursor.execute(command)
    result = cursor.fetchall()
    return result

# SELECT in SELECT
def insert_results(session:'mysql.connector.connection_cext.CMySQLConnection', id_number:str, subject_name:str, points:str):
    """
    function used by teachers to
    inserts given students points in a given subject
    into results table.\n
    note: id_number is students id number
    """
    cursor = session.cursor()
    cursor.execute("use {}".format(DB_NAME))
    # check if result already exist and only needs update
    result = fetch_result(session, id_number, subject_name)
    # UPDATE if result already exists in database
    if result:
        command = """
                    UPDATE results
                    SET points='{}'
                    WHERE student_id=(SELECT student_id FROM students WHERE id_number='{}')
                    AND subject_id=(SELECT subject_id FROM subjects WHERE subject_name='{}')
                    """.format(points, id_number, subject_name)
    # INSERT if result is being registered first time       
    else:
        command = """
                    INSERT INTO results (student_id, subject_id, points)
                    VALUES (
                        (SELECT student_id FROM students WHERE id_number='{}'),
                        (SELECT subject_id FROM subjects WHERE subject_name='{}'),
                        '{}')
                    """.format(id_number, subject_name, points)
    try:
        cursor.execute(command)
        session.commit()
        return
    except DatabaseError as de:
        print(de)
        return
    
# FUNCTION and AGGREGATION [ AVG(), SUM() COUNT()]
def create_function_total_avg(session:'mysql.connector.connection_cext.CMySQLConnection'):
    """
    creates a function in the database\n
    the function calculate the total average of a student
    from the percent column in the results table
    and returns a tupel (Decimal('total_ave'),).\n
    cast the returned value to float dvs (float(returned value))
    """
    cursor = session.cursor()
    cursor.execute("use {}".format(DB_NAME))
    command = """                
                CREATE FUNCTION total_average(student INT)
                RETURNS DECIMAL(5,2)
                DETERMINISTIC
                BEGIN
                    DECLARE total_avg DECIMAL(5,2);
                    SELECT AVG(percent) INTO total_avg
                    FROM results
                    WHERE student_id = student;
                    RETURN total_avg;
                END
                """
    print("creating function in database.")
    try:
        cursor.execute("DROP FUNCTION IF EXISTS total_average;")
        cursor.execute(command)
        session.commit()
        print("OK")
    except DatabaseError as de:
        print(de)
        session.rollback()
    finally:
        return
    
def total_ave(session:'mysql.connector.connection_cext.CMySQLConnection', id_number:str):
    """
    teachers can use it to sort students with rank.\n
    parents can use it to see what rank their child is\n
    uses the function total_average in the database
    to calculate the average of a student and
    returns a lst where
    lst[0] is the total average of the student and
    lst[1] is the number of subjects reported for that student using SUM()
    returns None if there is no data or if error occures.
    """
    
    cursor = session.cursor()
    cursor.execute("use {}".format(DB_NAME))
    
    # get the student_id of the student with help of id_number
    cursor.execute("SELECT student_id FROM students WHERE id_number='{}';".format(id_number))
    student_id = cursor.fetchone()
    if not student_id:
        # print("student with id number {} not found.".format(id_number))
        cursor.close()
        return
    student_id = student_id[0]
    
    # get number of subjects reported (inserted results) for that student
    cursor.execute("SELECT COUNT(*) FROM results WHERE student_id='{}';".format(student_id))
    subject_count = cursor.fetchone()[0]
    if subject_count == 0:
        # print("the student has not subject reported to results")
        cursor.close()
        return
    
    # get total number of subjects in the subjects table
    cursor.execute("SELECT COUNT(*) FROM subjects;")
    total_subjects = cursor.fetchone()[0]
    
    # get total average using total_average function in database
    try:
        cursor.execute("SELECT total_average('{}') FROM results where student_id='{}';".format(student_id, student_id))        
        total_average = cursor.fetchall()[0][0]
        cursor.close()
        return (float(total_average), subject_count)
    except DatabaseError as de:
        cursor.close()
        print(de)
        return

def rank_students(session:'mysql.connector.connection_cext.CMySQLConnection'):
    """
    for teachers\n
    uses the function total_ave() to get total average of every student then
    rank students from highest to lowest according total average.\n
    """
    cursor = session.cursor()
    cursor.execute("use {}".format(DB_NAME))
    
    # get id numbers of all students from database
    command = """
                SELECT id_number FROM students;
                """
    cursor.execute(command)
    students = cursor.fetchall()    
    # if students table is empty
    if not students:
        print("no students in database.")
        return
    # id_numbers = ["CD23456789", "GH45678901"]
    id_numbers = []
    for i in range(0,len(students)):
        id_numbers.append(students[i][0])
    
    # average of all students in a list
    ave_lst = []
    for i in range(0,len(id_numbers)):
        ave_lst.append(total_ave(session, id_numbers[i]))
    
    print("Student id\t\t\tTotal average\t\tNumber of subjects")
    for i in range(0, len(ave_lst)):
        if ave_lst[i] == None:
            print("{}\t\t\tNone\t\t\tNone".format(id_numbers[i]))
        else:
            print("{}\t\t\t{}\t\t\t{}".format(id_numbers[i], ave_lst[i][0], ave_lst[i][1]))

def show_student_result(session:'mysql.connector.connection_cext.CMySQLConnection', id_number:str, subject_name:str=""):
    """
    for parents, to check their childs points in one or all subjects\n
    uses the function fetch_result() to do this.
    """
    result = fetch_result(session, id_number, subject_name)
    if result == None or len(result) == 0:
        result = [("NONE")]
    print("Subject\t\tPoints\t\tMaximum possible points\t\tPercent")
    for i in range(0,len(result)):
        print("{}\t\t{}\t\t{}\t\t\t\t{}".format(result[i][0], result[i][1], result[i][2], result[i][3]))

def register_result(session:'mysql.connector.connection_cext.CMySQLConnection', id_number:str, subject_name:str, points:str):
    """
    for teachers to register result of a student in a subject\n
    uses the function insert_results() to do this
    """
    try:
        insert_results(session, id_number, subject_name, points)
        print("result registered successfully.")
        return
    except:
        print("Error: result not registered.")
        return

def login(session:'mysql.connector.connection_cext.CMySQLConnection', username:str, password:str):
    command = """
                SELECT username, password, role FROM users
                WHERE username='{}' AND password='{}'
                """.format(username, password)
    
    cursor = session.cursor()
    cursor.execute("use {}".format(DB_NAME))
    cursor.execute(command)
    username_password = cursor.fetchone()
    # print(username_password)
    if username_password:
        return username_password[2]
    else:
        return False

# RUN ############################################
def main():
    session = connect_db("localhost", "root", "longpassword")
    cursor = session.cursor()
    print("\nWellcome to School data base")
    while(True):
        username = input("User name: ")
        password = input("password: ")
        loggedin = login(session, username, password)
        if loggedin != False:
            print("role: {}".format(loggedin))
            while(True):
                print("\nChoose options below:")
                if loggedin == "teacher":
                    print("1: show students rank.\n2: show student points\n3: register points.\n4: Exit")
                    choice = input("option: ")
                    if choice == '1':
                        rank_students(session)
                        continue
                    elif choice == '2':
                        id_number = input("student id number: ")
                        subject_name = input("subject name. (Optional): ")
                        show_student_result(session, id_number, subject_name)
                        continue
                    elif choice == '3':
                        id_number = input("student id number: ")
                        subject_name = input("subject name: ")
                        points = input("points: ")
                        register_result(session, id_number, subject_name, points)
                        continue
                    elif choice == '4':
                        break
                elif loggedin == "parent":
                    print("1: show student points.\n2: Exit.")
                    choice = input("option: ")
                    if choice == '1':
                        id_number = input("student id number: ")
                        subject_name = input("subject name. (Optional): ")
                        show_student_result(session, id_number, subject_name)
                        continue
                    elif choice == '2':
                        break
                    else:
                        print("unrecognized choice")
                        continue
                
        else:
            print("login unsuccessful")
            continue

#-----------------------------------------------------------------------#
# CREATE AND POPULATE DATABASE                                          #
# session = connect_db("localhost", "root", "longpassword")             #
# create_databases(session, DB_NAME)                                    #
# create_table_users(session)                                           #
# create_table_students(session)                                        #
# create_table_subjects(session)                                        #
# create_table_results(session)                                         #
# trigger_percent_results(session)                                      #
# populate_database(session)                                            #
# create_function_total_avg(session)                                    #
# populate_results_table(session, 200)                                  #
#-----------------------------------------------------------------------#

# RUN TERMINAL PROGRAM
main()
