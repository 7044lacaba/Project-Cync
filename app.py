import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
# app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///cync.db")

# Make sure API key is set
#  if not os.environ.get("API_KEY"):
#    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():

    id = session['user_id']
    status = db.execute("SELECT status FROM users WHERE id = ?", id)[0]['status']

    # Pass in name
    name = db.execute("SELECT name FROM users WHERE id = ?", id)[0]['name']

    if status == 'company':
        return render_template("comphome.html", status = status, name = name)
    else:
        return render_template("emphome.html", status = status, name = name)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            input = "Must Provide Username"
            return render_template("problem.html", input = input)

        # Ensure password was submitted
        elif not request.form.get("password"):
            input = "Must Provide Password"
            return render_template("problem.html", input = input)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            input = "Invalid Username and/or Password"
            return render_template("problem.html", input = input)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/regcom", methods=["GET", "POST"])
def regcom():
    """Register user"""

    if request.method == "POST":

        # Check if any field is blank
        if not request.form.get("company") or not request.form.get("code") or not request.form.get("username") or not request.form.get("password") or not request.form.get("confirm") or not request.form.get("name"):
            input = "Each Field is Required"
            return render_template("problem.html", input = input)

        # Check if username is not pure numbers
        buff = request.form.get("username")
        try:
            int(buff)
            input = "Username Cannot Be All Numbers"
            return render_template("problem.html", input = input)
        except:
            x = 0

        # Check if name is not pure numbers
        buff = request.form.get("name")
        try:
            int(buff)
            input = "Name Cannot Be All Numbers"
            return render_template("problem.html", input = input)
        except:
            x = 0

        # Check if username is not day
        day = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
        ]
        if buff in day:
            input = "Try Another Username"
            return render_template("problem.html", input = input)

        # Check if all fields are unique from one another
        if (request.form.get("company") == request.form.get("code")) or (request.form.get("code") == request.form.get("username")) or (request.form.get("username") == request.form.get("company")):
            input = "Company Title, Code, and Username Must Be Unique"
            return render_template("problem.html", input = input)

        # Check if passwords match
        if request.form.get("password") != request.form.get("confirm"):
            input = "Passwords Do Not Match"
            return render_template("problem.html", input = input)

        # Check if username is taken
        usernames = db.execute("SELECT username FROM users")
        username_list = []
        for user in usernames:
            buff = user["username"]
            username_list.append(buff)
        if request.form.get("username") in username_list:
            input = "Username Already Taken"
            return render_template("problem.html", input = input)

        # Check if company code is taken
        codes = db.execute("SELECT code FROM users")
        code_list = []
        for code in codes:
            buff = code["code"]
            code_list.append(buff)
        if request.form.get("code") in code_list:
            input = "Company Code Already Taken"
            return render_template("problem.html", input = input)

        # Check if company name is taken
        companies = db.execute("SELECT company FROM users")
        comp_list = []
        for com in companies:
            buff = com["company"]
            comp_list.append(buff)
        if request.form.get("company") in comp_list:
            input = "Company Name Already Taken"
            return render_template("problem.html", input = input)

        # Check if username exist in 'code' or 'company'
        if (request.form.get("username") in code_list) or (request.form.get("username") in comp_list):
            input = "Please Select a Different Username"
            return render_template("problem.html", input = input)

        # Check if code exist in 'company' or 'username'
        if (request.form.get("code") in comp_list) or (request.form.get("code") in username_list):
            input = "Please Select A Different Company Code"
            return render_template("problem.html", input = input)

        # Check if company exist in 'username' or 'code'
        if (request.form.get("company") in username_list) or (request.form.get("company") in code_list):
            input = "Please Select A Different Company Name"
            return render_template("problem.html", input = input)

        # Store into database as company
        name = request.form.get("name")
        company = request.form.get("company")
        code = request.form.get("code")
        username = request.form.get("username")
        password = generate_password_hash(request.form.get("password"))
        db.execute("INSERT INTO users (company, code, username, hash, status, name) VALUES (?, ?, ?, ?, ?, ?)", company, code, username, password, "company", name)

        # Log user in
        id_buff = db.execute("SELECT id FROM users WHERE username = (?)", username)
        session["user_id"] = id_buff[0]['id']
        return redirect("/")

    else:
        return render_template("regcom.html")

@app.route("/regemp", methods=["GET", "POST"])
def regemp():
    if request.method == "POST":

        # Check if any feild is blank
        if not request.form.get("company"):
            input = "Company Must Be Selected"
            return render_template("problem.html", input = input)
        if not request.form.get("code") or not request.form.get("username") or not request.form.get("password") or not request.form.get("confirm") or not request.form.get("name"):
            input = "Each Feild is Required"
            return render_template("problem.html", input = input)

        # Check if username is not pure numbers
        buff = request.form.get("username")
        try:
            int(buff)
            input = "Username Cannot Be All Numbers"
            return render_template("problem.html", input = input)
        except:
            x = 0

        # Check if name is not pure numbers
        buff = request.form.get("name")
        try:
            int(buff)
            input = "Name Cannot Be All Numbers"
            return render_template("problem.html", input = input)
        except:
            x = 0

        # Check if username is not day
        day = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
        ]
        if buff in day:
            input = "Try Another Username"
            return render_template("problem.html", input = input)

        # Check if username is taken
        usernames = db.execute("SELECT username FROM users")
        username_list = []
        for user in usernames:
            buff = user["username"]
            username_list.append(buff)
        if request.form.get("username") in username_list:
            input = "Username Already Taken"
            return render_template("problem.html", input = input)

        # Check if passwords match
        if request.form.get("password") != request.form.get("confirm"):
            input = "Passwords Do Not Match"
            return render_template("problem.html", input = input)

        # Check if company code matches company
        code = request.form.get("code")
        company = request.form.get("company")
        codecheck = db.execute("SELECT code FROM users WHERE company = ?", company)[0]['code']
        if code != codecheck:
            input = "Code Does Not Match With Company"
            return render_template("problem.html", input = input)

        # Check if username exist in 'code' or 'company'
        codes = db.execute("SELECT code FROM users")
        code_list = []
        for code in codes:
            buff = code["code"]
            code_list.append(buff)
        companies = db.execute("SELECT company FROM users")
        comp_list = []
        for com in companies:
            buff = com["company"]
            comp_list.append(buff)
        if (request.form.get("username") in code_list) or (request.form.get("username") in comp_list):
            input = "Please Select a Different Username"
            return render_template("problem.html", input = input)

        # Store into database as employee
        name = request.form.get("name")
        company = request.form.get("company")
        code = request.form.get("code")
        username = request.form.get("username")
        password = generate_password_hash(request.form.get("password"))
        db.execute("INSERT INTO users (company, code, username, hash, status, name) VALUES (?, ?, ?, ?, ?, ?)", company, code, username, password, "employee", name)

        # Log user in
        buffer = db.execute("SELECT id FROM users WHERE username = (?)", username)
        session["user_id"] = buffer[0]['id']

        return redirect("/")

    else:

        # Pass through list of companies
        buffer = db.execute("SELECT company FROM users WHERE status = 'company'")
        return render_template("regemp.html", buffer = buffer)


@app.route("/info", methods=["GET", "POST"])
@login_required
def info():

    # Pass through current company code
    id = session["user_id"]
    status = db.execute("SELECT status FROM users WHERE id = ?", id)[0]['status']
    code = (db.execute("SELECT code FROM users WHERE id = ?", id))[0]["code"]
    company = (db.execute("SELECT company FROM users WHERE id = ?", id))[0]["company"]
    return render_template("info.html", code=code, company=company, status=status)


@app.route("/title", methods=["GET", "POST"])
@login_required
def title():

    # Pass in status of user
    id = session['user_id']
    status = db.execute("SELECT status FROM users WHERE id = ?", id)[0]['status']

    if request.method == "POST":

        # Create table linked to managment username if none
        username = db.execute("SELECT username FROM users WHERE id = ?", id)[0]['username']
        db.execute("CREATE TABLE IF NOT EXISTS ? (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, title TEXT, amount INT, listed INT, day TEXT)", username)

        # Check if valid input
        if not request.form.get("day"):
            input = "Day Must Be Selected"
            return render_template("problem.html", input = input)
        if not request.form.get("jobtitle") or not request.form.get("amount"):
            input = "Connot Be Blank"
            return render_template("problem.html", input = input)

        # Store info in variables
        title = request.form.get("jobtitle")
        amount = request.form.get("amount")
        day = request.form.get("day")

        # Save into table
        db.execute("INSERT INTO ? (title, amount, listed, day) VALUES (?, ?, ?, ?)", username, title, amount, 0, day)

        # Add into existing employee tables
        com_code = db.execute("SELECT code FROM users WHERE id = ?", id)[0]['code']
        emp_list = db.execute("SELECT username FROM users WHERE code = ? AND status = ?", com_code, 'employee')

        # List of employees under the same code
        list_emp = []
        for emp in emp_list:
            list_emp.append(emp['username'])

        # find id of title just added
        id_list_buffer = db.execute("SELECT id FROM ?", username)
        id_list = []
        title_id = 0
        for id in id_list_buffer:
            id_list.append(id['id'])
        for id in id_list:
            if id > title_id:
                title_id = id

        # Loop through list of employees and try to insert into each of them
        for emp in list_emp:
            try:
                db.execute("INSERT INTO ? (title_index, status, working) VALUES (?, ?, ?)", emp, title_id, 'no', 'no')
            except:
                x = 0
        return redirect("/title")

    else:

        # Display all job titles in company
        username = db.execute("SELECT username FROM users WHERE id = ?", id)[0]["username"]
        day = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        nada = []
        try:
            buffer = db.execute("SELECT * FROM ?", username)
            return render_template("title.html", buffer = buffer, day = day, status = status)
        except:
            return render_template("title.html", buffer = nada, day = day, status = status)


@app.route("/delete", methods=["POST"])
@login_required
def delete():

    # Delete from management database
    id = session["user_id"]
    delete_id = request.form['id_delete']
    username = db.execute("SELECT username FROM users WHERE id = ?", id)[0]["username"]
    db.execute('DELETE FROM ? WHERE id = ?', username, delete_id)

    # Get list of employees under the same code
    com_code = db.execute("SELECT code FROM users WHERE id = ?", id)[0]['code']
    emp_list = db.execute("SELECT username FROM users WHERE code = ? AND status = ?", com_code, 'employee')
    list_emp = []
    for emp in emp_list:
        list_emp.append(emp['username'])

    # Go through every employee linked to the company code and TRY to delete
    for emp in list_emp:
        try:
            db.execute("DELETE FROM ? WHERE title_index = ?", emp, delete_id)
        except:
            x = 0

    return redirect("/title")


@app.route("/availability", methods=["GET", "POST"])
@login_required
def availability():

    id = session["user_id"]
    status = db.execute("SELECT status FROM users WHERE id = ?", id)[0]['status']

    # Get company username with employee id
    curr_code = db.execute("SELECT code FROM users WHERE id = ?", id)[0]['code']
    comp_user = db.execute("SELECT username FROM users WHERE code = ? AND status = ?", curr_code, 'company')[0]['username']
    curr_user = db.execute("SELECT username FROM users WHERE id = ?", id)[0]['username']

    # List of days
    day = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
    ]

    if request.method == "POST":

        #Get a list of ids in employee database
        comp_id_list = db.execute("SELECT id FROM ?", comp_user)
        clean_id_list = []
        for id in comp_id_list:
            clean_id_list.append(id['id'])

        # Get a list of submitted ids
        submitted_ids = []
        for id in clean_id_list:
            buff = request.form.get(str(id))
            submitted_ids.append(buff)

        # If they match change status
        for id in clean_id_list:
            if str(id) in submitted_ids:
                db.execute("UPDATE ? SET status = ? WHERE title_index = ?", curr_user, 'yes', id)
            else:
                db.execute("UPDATE ? SET status = ? WHERE title_index = ?", curr_user, 'no', id)

                # If working set working to yes then change to no
                if db.execute("SELECT working FROM ? WHERE title_index = ?", curr_user, id)[0]['working'] == 'yes':
                    db.execute("UPDATE ? SET working = ? WHERE title_index = ?", curr_user, 'no', id)

                    # Find value of listed and subtract by one then update
                    listed = db.execute("SELECT listed FROM ? WHERE id = ?", comp_user, id)[0]['listed']
                    db.execute("UPDATE ? SET listed = ? WHERE id = ?", comp_user, (listed - 1) ,id)

        #return render_template("check.html", a = submitted_ids, b = buffyes, c = buffno, status = status)

        return redirect("/availability")

    else:
        try:

            # Load all information into the html page (assume its all up to date)
            curr_user_table = db.execute("SELECT * FROM ?", curr_user)
            comp_user_table = db.execute("SELECT * FROM ?", comp_user)
            num = len(comp_user_table)

            return render_template("availability.html", table = comp_user_table, sting = curr_user_table, num = num, day = day, status = status)

        except:
            try:
                # Try to extract a list of titles from manager account (if it exist)
                comp_user_table = db.execute("SELECT * FROM ?", comp_user)

                try:

                    # Try to extract a list of availability from current user account
                    curr_user_table = db.execute("SELECT * FROM ?", curr_user)
                    num = len(comp_user_table)
                    return render_template("availability.html", table = comp_user_table, sting = curr_user_table, num = num, day = day, status = status)

                except:
                    # If it fails then create a employee list
                    db.execute("CREATE TABLE IF NOT EXISTS ? (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, title_index INT, status TEXT, working TEXT)", curr_user)
                    for title in comp_user_table:
                        db.execute("INSERT INTO ? (title_index, status, working) VALUES (?, ?, ?)", curr_user, title['id'], 'no', 'no')
                    num = len(comp_user_table)
                    curr_user_table = db.execute("SELECT * FROM ?", curr_user)
                    return render_template("availability.html", table = comp_user_table, sting = curr_user_table, num = num, day = day, status = status)

            # If it fails return an apology
            except:
                input = "Management Must Create Job Positions"
                return render_template("problem.html", input = input)


@app.route("/schecomp", methods=["GET", "POST"])
@login_required
def schecomp():

    id = session["user_id"]
    status = db.execute("SELECT status FROM users WHERE id = ?", id)[0]['status']
    curr_comp = db.execute("SELECT username FROM users WHERE id = ?", id)[0]['username']
    comp_code = db.execute("SELECT code FROM users WHERE id = ?", id)[0]['code']


    # Get list of employees linked to company code
    emp_list = db.execute("SELECT username FROM users WHERE code = ? AND status = ?", comp_code, 'employee')
    clean_emp_list = []
    for emp in emp_list:
        clean_emp_list.append(emp['username'])

    if request.method == "POST":

        # Get submitted data
        username = request.form.get('username')
        title_id = request.form.get('title_id')
        value = request.form.get('value')

        amount = db.execute("SELECT amount FROM ? WHERE id = ?", curr_comp, int(title_id))[0]['amount']
        listed = db.execute("SELECT listed FROM ? WHERE id = ?", curr_comp, int(title_id))[0]['listed']

        if value == 'yes':

            # Check if listed can go any higher (return apology) add to listed if there is room
            if amount == listed:
                input = "Cannot Schedule Any More Employees"
                return render_template("problem.html", input = input)
            else:
                db.execute("UPDATE ? SET listed = ? WHERE id = ?", curr_comp, (listed + 1), title_id)

            # Update working status to yes
            db.execute("UPDATE ? SET working = ? WHERE title_index = ?", username, value, title_id)
            return redirect("/schecomp")

        else:

            db.execute("UPDATE ? SET listed = ? WHERE id = ?", curr_comp, (listed - 1), title_id)
            db.execute("UPDATE ? SET working = ? WHERE title_index = ?", username, value, title_id)
            return redirect("/schecomp")

    else:

        day = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
        ]

        comp_list = db.execute("SELECT * FROM ?", curr_comp)

        # Filter through employees and kick out the ones that havent made a table
        updated_emp_list = clean_emp_list.copy()
        for emp in clean_emp_list:
            try:
                db.execute("SELECT * FROM ?", emp)
            except:
                updated_emp_list.remove(emp)

        # Pass in table containing title details
        company_info = db.execute("SELECT * FROM ?", curr_comp)

        # Create nested dictionary
        mega = {}
        for emp in clean_emp_list:
            try:
                emp_dictionary = db.execute("SELECT * FROM ?", emp)
                mega[emp] = emp_dictionary
            except:
                x = 0

        # Length of company list
        length = len(comp_list)

        # Pass in names with usernames
        names_and_users = db.execute("SELECT username, name FROM users")

        return render_template("schecomp.html", days = day, list_emp = updated_emp_list, manager_list = company_info, mega_list = mega, title_range = length, names = names_and_users, status = status)


@app.route("/scheemp", methods=["GET", "POST"])
@login_required
def scheemp():

    id = session["user_id"]
    status = db.execute("SELECT status FROM users WHERE id = ?", id)[0]['status']
    curr_user = db.execute("SELECT username FROM users WHERE id = ?", id)[0]['username']
    curr_code = db.execute("SELECT code FROM users WHERE id = ?", id)[0]['code']
    comp_user = db.execute("SELECT username FROM users WHERE code = ? AND status = ?", curr_code, 'company')[0]['username']

    if request.method == "POST":
        return render_template("scheemp.html", status = status)

    else:

        # Get working status from current user
        emp = db.execute("SELECT * FROM ?", curr_user)

        # Get title details from company table
        comp = db.execute("SELECT * FROM ?", comp_user)

        # Get length of list
        length = len(comp)

        #return render_template("check.html", a = length, b = 0, c = 0, status = status)

        return render_template("scheemp.html", comp = comp, emp = emp, length = length, status = status)


#return render_template("check.html", a = buffer, b = 0, c = 0, status = status)
#CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, company TEXT NOT NULL, code TEXT NOT NULL, username TEXT NOT NULL, hash TEXT NOT NULL, status TEXT NOT NULL);
#CREATE TABLE sqlite_sequence(name,seq);
#CREATE UNIQUE INDEX username ON users (username);