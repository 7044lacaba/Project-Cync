Cync is a scheduling software that allows for companies to plan and manage schedules based on employees set availability. Companies can set up job titles further specifying how many they need and what days they need them. Linked though a company code, employees are able to see what titles are made and can add it to their availability. Companies can then begin to form their schedules. 


Company Registration:
Any blank fields, usernames consisting of numbers, usernames consisting of weekdays (specifically in the ‘day’ list), taken usernames, taken company codes, taken company names, and miss matched passwords would all return an error.
Instead of an apology function I stored the error message into a variable and passed that into a html that would render an error page.
Once everything is checked all the information gets passed into a table called ‘users’, it's a pre-made table and starts empty. ‘users’ stores multiple things; an automatically incrementing id key, ‘company’ which stores the name of the company, ‘code’ which stores the company code, ‘username’ which stores the username, ‘hash’ which stores a hash of the users password, ‘status’ which stores the account type, either company or employee (since this is the company registration page it is set to company), and ‘name’ which stores the users name.
(SIDENOTE) The other tables are not premade. They are created using the username of the user as the name of the table. I was planning to create a table using the company code and one using the company name to store information about schedules but I found a work around. I decided to keep that option open, this is why a username must be unique to not only other usernames but unique also to company codes and company names. 


Employee Registration: 
Employee registration is practically identical to company registration with few key differences.
Regemp ‘GET’ will pass in a list of all companies. This will be displayed in a drop down list on the front end where the employee will be able to select what company they want to sign up for. 
Regemp ‘POST’ will cross match the selected company from the drop down and the company code. If successful then everything will be logged into the database. 




Info (Manager):
Info is a page that simply displays the company name and company code


Title (Manager):
Title ‘GET’ renders title.html which displays all created titles organized by day of the week. If empty the table will still appear showing only the days of the week. 
On the top of the page there are 3 inputs you can submit to create a job title. If any fields are blank it will return an error.
Title ‘POST’ will take the ‘day’, ‘job title’, and ‘amount’ input and store it into a table named using the username of the current company account. The table will also store an additional value called ‘listed’, this value is an indicator of how many employees have been scheduled to work that job title (naturally when first created should be set to 0).
Skipping ahead a little, you must understand that when the employee table is created it stores a copy of the titles. Therefore when adding a new title you must update all existing employee tables. Looping through a list of employees the function tries to add the title into each existing table and skips the rest.


Delete (Manager):
For each created title there is a delete button (accessed through title.html). This function receives an ‘id’ through ‘POST’ and deletes it from the company database.
Since the title is being deleted from the manager table it should also be deleted from the employee tables (given they exist). The function goes through the list of employees (linked by company code) and uses ‘try’ to delete it from each employee table. 


Availability (Employee):
Availability ‘GET’ will try to pull information from the current employees table. This will in turn display each title and whether or not they are available to work. On the off chance that the table has yet to be created this function will take care of that then render the page. There is also the possibility that the management side has yet to create any titles, this will then result in an apology. 
When a table is created it uses the username of the current user as the name for the table. It then pulls all the title ids from the manager list and stores it under ‘title_id’. The table contains 2 other columns; ‘status’ and ‘working’. ‘status’ lets us know if they are able to work that shift and ‘working’ lets us know if they are actually scheduled. Both are naturally set to ‘no’. 
Availability ‘POST’ will take the submitted title id and change the ‘status’ to either ‘yes’ or ‘no’ depending on the desired outcome


Schedule Company (Manager):
Schecomp ‘GET’ displays each title from the manager list (sorted by day) and underneath displays each of the employees that are available to work that title. Through the utilization of a nested dictionary all existing employee tables are passed into schecomp.html as well as another variable that holds the company table. The frontend also includes an add/remove button which would add/remove that employee to the final schedule.
A lot of the heavy lifting was actually done on the html side. Through loops and if statements jinja code loops through the company table and cross matches it with employees from the nested dictionary. If the company title id matched the employee title id AND the ‘status’ was set to ‘yes’ that would mean the employee was able to work that day and in turn display it on the frontend. Using hidden values the program is able to pass in critical information that would allow the change of the ‘scheduled’ table to either yes or no.
Schecomp ‘POST’ takes the hidden values ‘username’, ‘title_id’, and ‘value’ from the html and processes it. If ‘value’ is ‘yes’ then it would add it to the company schedule setting ‘listed’ adding one more to its previous value. If the max amount of employees are already scheduled then it would return an apology. If ‘value’ is ‘no’ then it would subtract one from the previous value. 


Schedule Employee (employee):
Scheemp ‘GET’ passes in the current users table into scheemp.html. This would then display all of the shifts scheduled to work that week. 
I left the possibility of ‘POST’ up just in case there is something I want to implement in the future. 


layout.html:
Once logged it will render 2 different types of pages, one for employees and one for companies. When you take a look at the end of each function in app.py you can see it always passes in a variable called status (if @login_required); status will let layout.html know what type of page to load. This is how I decided to organize access to links. Knowing employees cannot access company functions because that navbar simply wouldn't show up saved me a lot of headaches. This was all at the cost of knowing that url manipulation would straight up destroy my project as employees would be able to access company features. 
