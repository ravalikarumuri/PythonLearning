import psycopg2
con = psycopg2.connect(dbname= 'poc_db', host='localhost', user='postgres',password='ravali123')
cursor = con.cursor()

user_table = "create table if not exists users (user_id serial PRIMARY KEY,first_name text,last_name text,email text,password text,is_admin boolean,user_type text)"
cursor.execute(user_table)

department_table = "create table if not exists departments(department_id serial PRIMARY KEY,name text,description text)"
cursor.execute(department_table)

role_table = "create table if not exists roles(role_id serial PRIMARY KEY,description text)"
cursor.execute(role_table)

student_table = "create table if not exists students(student_id serial PRIMARY KEY,first_name text,last_name text,email text,phone text,department_id int,profile_photo bytea)"
cursor.execute(student_table)

employee_table = "create table if not exists employees (employee_id serial PRIMARY KEY,first_name text,last_name text,email text,phone text,role_id int,department_id int)"
cursor.execute(employee_table)

student_department_fk="ALTER TABLE students ADD CONSTRAINT department_id FOREIGN KEY (department_id) REFERENCES departments (department_id)"
cursor.execute(student_department_fk)

employee_roleid_fk = "ALTER TABLE employees ADD CONSTRAINT role_id FOREIGN KEY (role_id) REFERENCES roles(role_id);"
cursor.execute(employee_roleid_fk)

employee_departmentid_fk = "ALTER TABLE employees ADD CONSTRAINT department_id FOREIGN KEY (department_id) REFERENCES departments(department_id)"
cursor.execute(employee_departmentid_fk)

con.commit()
con.close()
