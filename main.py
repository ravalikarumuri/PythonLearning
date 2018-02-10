import psycopg2
from flask import Flask,request,render_template,url_for,redirect,flash,session
from flask_bootstrap import Bootstrap
from werkzeug import secure_filename
import functools
#from flask_restful import Resource, Api
#from flask_jwt import JWT,jwt_required
from flask_bcrypt import Bcrypt
app = Flask(__name__)
app.secret_key = 'ravali'
bcrypt = Bcrypt(app)
bootstrap = Bootstrap(app)
#api = Api(app)
connection = psycopg2.connect(dbname= 'poc_db', host='localhost', user='postgres',password='ravali123')
cursor = connection.cursor()

def current_user(user_email):
    cursor.execute('select user_id from users where email = %s;',(user_email,))
    user = cursor.fetchone()
    return user

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/main')
def main():
    return render_template('main.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signin',methods =['POST','GET'])
def signin():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cursor.execute("SELECT * FROM users WHERE email = %s ;", (email,))
        result=cursor.fetchone()
        if result:
            original_password = result[4]
            if bcrypt.check_password_hash(original_password, password):
                session['user'] = current_user(email)
                return redirect(url_for('main'))
            else:
                return redirect(url_for('login'))
                error = 'Invalid username or password. Please try again!'
        else:
            error = 'No Such User, Please sign up.'
            return redirect(url_for('main'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/signup',methods = ['POST','GET'])
def signup():
    error = None
    insert_query = "insert into users(first_name, last_name, email, password,is_admin,user_type) values(%s,%s,%s,%s,%s,%s)"
    if request.method == 'POST':
        fname = request.form['first_name']
        lname = request.form['last_name']
        email_id = request.form['email']
        pwd =  bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        is_admin = False
        user_type = 'Employee'
        if request.form['password'] == request.form['confirm_password']:
            cursor.execute(insert_query,(fname,lname,email_id,pwd,is_admin,user_type))
            connection.commit()
        return redirect(url_for('main'))

#Employees views
@app.route('/employee_register')
def employee_register():
    error = None
    if session:
        select_departments = "select department_id,name from departments"
        cursor.execute(select_departments)
        departments_list = cursor.fetchall()
        select_roles = "select role_id,description from roles"
        cursor.execute(select_roles)
        roles_list = cursor.fetchall()
        return render_template('employee_signup.html',departments_list = departments_list,roles_list = roles_list)
    else:
        error = 'Please sign in.'
        return render_template('index.html')

@app.route('/employee_signup',methods = ['POST','GET'])
def employee_signup():
    error = None
    if session:
        insert_employee_query = "insert into employees(first_name, last_name, email,department_id,role_id,phone) values(%s,%s,%s,%s,%s,%s)"
        insert_user_query = "insert into users(first_name, last_name, email, password,is_admin,user_type) values(%s,%s,%s,%s,%s,%s)"
        if request.method == 'POST':
            fname = request.form['first_name']
            lname = request.form['last_name']
            email_id = request.form['email']
            count_query = "select count(*) from employees"
            cursor.execute(count_query)
            data = cursor.fetchone()
            count = data[0] + 1
            passwd =  "employee"+ str(data[0] + 1)
            pwd = bcrypt.generate_password_hash(passwd).decode('utf-8')
            department_id = request.form['department_option']
            role_id = request.form['role_option']
            phone = request.form['phnumber']
            is_admin = False
            user_type = "Employee"
            cursor.execute(insert_employee_query,(fname,lname,email_id,department_id,role_id,phone))
            cursor.execute(insert_user_query,(fname,lname,email_id,pwd,is_admin,user_type))
            connection.commit()
        return redirect(url_for('main'))
    else:
        error = 'Please sign in.'
        return render_template('index.html')

@app.route('/employees_index')
def employees_index():
    error = None
    if session:
        employees_list_query= "select * from employees"
        cursor.execute(employees_list_query)
        employees_list = cursor.fetchall()
        print(employees_list)
        return render_template('employees_index.html',employees_list = employees_list)
    else:
        error = 'Please sign in.'
        return render_template('index.html')

@app.route('/employee_edit/<int:id>',methods=['POST','GET'])
def employee_edit(id):
    error = None
    if session:
        if request.method =='POST':
            employee_update = "update employees set first_name = %s,last_name = %s,email = %s, role_id = %s,department_id = %s,phone = %s where employee_id = %s"
            fname           = request.form['first_name']
            lname           = request.form['last_name']
            email_id        = request.form['email']
            department_id   = request.form['department_option']
            role_id         = request.form['role_option']
            phone           = request.form['phnumber']
            employee_id     = id
            cursor.execute(employee_update,(fname,lname,email_id,role_id,department_id,phone,employee_id))
            connection.commit()
            return render_template('main.html')
        else:
            select_departments = "select department_id,name from departments"
            cursor.execute(select_departments)
            departments_list = cursor.fetchall()
            select_roles = "select role_id,description from roles"
            cursor.execute(select_roles)
            roles_list = cursor.fetchall()
            edit_employee = employee_by_id(id)
            return render_template('employee_edit.html',edit_employee = edit_employee,departments_list = departments_list,roles_list = roles_list)
    else:
        error ='Please sign in'
        return render_template('index.html')

@app.route('/delete_employee/<int:id>',methods = ['POST','GET'])
def delete_employee(id):
    error = None
    if session:
        if request.method == 'POST':
            delete_employee = "delete from employees where employee_id= %s"
            cursor.execute(delete_employee,(id,))
            connection.commit()
            return render_template('main.html')
        else:
            error ="Cannot delete"
            return render_template('employees_index.html')
    else:
        error ='Please sign in'
        return render_template('index.html')

def employee_by_id(id):
    employee = "select * from employees where employee_id = %s"
    cursor.execute(employee,(id,))
    return cursor.fetchone()

#Student Views
@app.route('/student_register')
def student_register():
    error = None
    if session:
        select_departments = "select department_id,name from departments"
        cursor.execute(select_departments)
        departments_list = cursor.fetchall()
        return render_template('student_signup.html',departments_list = departments_list)
    else:
        error ='Please sign in'
        return render_template('index.html')

@app.route('/student_signup',methods = ['POST','GET'])
def student_signup():
    error = None
    if session:
        insert_student_query = "insert into students(first_name, last_name, email,phone,department_id,profile_photo) values(%s,%s,%s,%s,%s,%s)"
        insert_user_query = "insert into users(first_name, last_name, email, password,is_admin,user_type) values(%s,%s,%s,%s,%s,%s)"
        if request.method == 'POST':
            print(' i am in idddddddddddddddddddddddddfffffffffffffff')
            fname = request.form['first_name']
            lname = request.form['last_name']
            email_id = request.form['email']
            phone_number = request.form['phnumber']
            photo = request.files['photo']
            mypic=open('/home/ravalikarumuri/Desktop/Ravalis_Document/My own/Diwali Pics/IMG_0857.JPG','rb').read()
            print(mypic)
            #print(photo)
            count_query = "select count(*) from students"
            cursor.execute(count_query)
            data = cursor.fetchone()
            count = data[0] + 1
            passwd =  "student"+ str(data[0] + 1)
            pwd = bcrypt.generate_password_hash(passwd).decode('utf-8')
            department_id = request.form['department_option']
            is_admin = False
            user_type = "Student"
            #cursor.execute(insert_user_query,(fname,lname,email_id,pwd,is_admin,user_type))
            cursor.execute(insert_student_query,(fname,lname,email_id,phone_number,department_id,mypic))
            connection.commit()
        return redirect(url_for('main'))
    else:
        error = "Please sign in"
        return render_template('index.html')

@app.route('/students_index')
def students_index():
    students_list_query= "select * from students"
    cursor.execute(students_list_query)
    students_list = cursor.fetchall()
    return render_template('students_index.html',students_list = students_list)

@app.route('/edit_student/<int:id>',methods=['POST','GET'])
def edit_student(id):
    error = None
    if session:
        if request.method =='POST':
            employee_update = "update students set first_name = %s,last_name = %s,email = %s,phone = %s ,department_id = %s where student_id = %s"
            fname           = request.form['first_name']
            lname           = request.form['last_name']
            email_id        = request.form['email']
            department_id   = request.form['department_option']
            phone           = request.form['phnumber']
            student_id     = id
            cursor.execute(employee_update,(fname,lname,email_id,phone,department_id,student_id))
            connection.commit()
            return render_template('main.html')
        else:
            select_departments = "select department_id,name from departments"
            cursor.execute(select_departments)
            departments_list = cursor.fetchall()
            edit_student = students_by_id(id)
            return render_template('edit_student.html',edit_student = edit_student,departments_list = departments_list)
    else:
        error = "Please sign in"
        return render_template('index.html')


@app.route('/delete_student/<int:id>',methods = ['POST','GET'])
def delete_student(id):
    error = None
    if session:
        delete_student = "delete from students where student_id= %s"
        cursor.execute(delete_student,(id,))
        connection.commit()
        return render_template('main.html')
    else:
        error = "Please sign in"
        return render_template('index.html')


def students_by_id(id):
    student = "select * from students where student_id = %s"
    cursor.execute(student,(id,))
    return cursor.fetchone()

#Role views
@app.route('/new_role')
def new_role():
    error = None
    if session:
        return render_template('create_role.html')
    else:
        error = "Please sign in"
        return render_template('index.html')

@app.route('/create_role',methods=['POST','GET'])
def create_role():
    error = None
    if session:
        if request.method == 'POST':
            description = request.form['role_name']
            if description!= "":
                insert_query = "insert into roles(description) values(%s);"
                cursor.execute(insert_query,(description,))
                connection.commit()
                return redirect(url_for('main'))
        else:
            error = 'Please fill the role name'
            return redirect(url_for('new_role'))
    else:
        error = "Please sign in"
        return render_template('index.html')

@app.route('/roles_index')
def roles_index():
    error = None
    if session:
        roles_list_query= "select * from roles"
        cursor.execute(roles_list_query)
        roles_list = cursor.fetchall()
        print(roles_list)
        return render_template('roles_index.html',roles_list = roles_list)
    else:
        error = "Please sign in"
        return render_template('index.html')

@app.route('/role_edit/<int:id>',methods=['POST','GET'])
def role_edit(id):
    error = None
    if session:
        if request.method =='POST':
            role_update = "update roles set description = %s where role_id = %s"
            description  = request.form['role_name']
            role_id = id
            cursor.execute(role_update,(description,role_id))
            connection.commit()
            return render_template('main.html')
        else:
            edit_role_query = "select * from roles where role_id = %s"
            cursor.execute(edit_role_query,(id,))
            edit_role = cursor.fetchone()
            return render_template('role_edit.html',edit_role = edit_role)
    else:
            error = "Please sign in"
            return render_template('index.html')

@app.route('/delete_role/<int:id>',methods = ['POST','GET'])
def delete_role(id):
    error = None
    if session:
        delete_role = "delete from roles where role_id= %s"
        cursor.execute(delete_role,(id,))
        connection.commit()
        return render_template('main.html')
    else:
        error = "Please sign in"
        return render_template('index.html')

#Department views
@app.route('/new_department')
def new_department():
    error = None
    if session:
        return render_template('create_department.html')
    else:
        error = "Please sign in"
        return render_template('index.html')

@app.route('/create_department',methods=['POST','GET'])
def create_department():
    error = None
    if session:
        if request.method == 'POST':
            name = request.form['department_name']
            description = request.form['department_description']
            insert_query = "insert into departments(name,description) values(%s,%s);"
            cursor.execute(insert_query,(name,description))
            connection.commit()
            return redirect(url_for('main'))
        else:
            error = 'Please fill valid fields'
            return redirect(url_for('new_department'))
    else:
        error = "Please sign in"
        return render_template('index.html')

@app.route('/departments_index')
def departments_index():
    error = None
    if session:
        departments_list_query= "select * from departments"
        cursor.execute(departments_list_query)
        departments_list = cursor.fetchall()
        return render_template('departments_index.html',departments_list = departments_list)
    else:
        error = "Please sign in"
        return render_template('index.html')

@app.route('/edit_department/<int:id>',methods=['POST','GET'])
def edit_department(id):
    error = None
    if session:
        if request.method =='POST':
            role_update = "update departments set name= %s, description = %s where department_id = %s"
            name  = request.form['department_name']
            description = request.form['department_description']
            department_id = id
            cursor.execute(role_update,(name,description,department_id))
            connection.commit()
            return render_template('main.html')
        else:
            edit_department_query = "select * from departments where department_id = %s"
            cursor.execute(edit_department_query,(id,))
            edit_department = cursor.fetchone()
            return render_template('edit_department.html',edit_department = edit_department)
    else:
        error = "Please sign in"
        return render_template('index.html')

@app.route('/delete_department/<int:id>',methods = ['POST','GET'])
def delete_department(id):
    error = None
    if session:
        delete_department = "delete from departments where department_id= %s"
        cursor.execute(delete_department,(id,))
        connection.commit()
        return render_template('main.html')
    else:
        error = "Please sign in"
        return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
