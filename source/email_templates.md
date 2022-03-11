# Email Templates

Email Templates are avalible for a few specific function and can be configured 
in the Settings area. The current template enabled functions are:
- User Welcome Email
- Password Experation Notification
- New User Notification

## Adding Templates
Under settings select Email templates, by default there is an example templates which includes
an overview of template functions, this templates can be deleted if you so wish. To add a new
template simply select ![new button](_static/new_button.PNG) in the upper.


**Template Name** The internal referance of for the template

**Subject** The subject line of the rendered email. This feild supports variables

**Body** The body content of the rendered email. This field support Jinja2 Syntex and Variables


:::{note} Note
At this time, static media is not supported. All embeded media must be avalible externally
:::

## Syntex

For a full referance of supported syntex visit [Jinja Template Designer Documentation](https://jinja.palletsprojects.com/en/3.0.x/templates/)


**variable** are encapsulated in `{{ ... }}` for a list of variables see the [Variables](Variables) section

**If statments** can be used to optionally add sections to your email based on specific condition such as
if an employee is part of a specific department. If statment blocks start with `{% if <condition> %}` and
ends with `{% endif %}`

**For Loops** similar to if statements for loops can be added to support recursion of specific variables.
For loops block are written starting with `{% for v in varable group %}` and ending with `{% endfor %}`

The `include` derective does not work in email templates

:::{note} Note
If you email templates are not working double check that you have closed all of your block statements or check 
the log file to see if there are any errors.
:::



## Variables

The following varables are currently supported in each template

| Template Name | Variables Supported |
| --- | --- |
| User Welcome Email | `employee` |
| Password Experation Email | `employee` |
| New User Notification | `employees` which is a list of new employees derived from the employee model object |

### Variable: employee
:*employee*: The referanced [employee model](models/employee) object
:*overrides*: The referanced [employee overides model](models/employee_overrides) object
:*designations*: The employees designations
:*phone*: Primary phone number
:*firstname*: The perfered Firstname
:*lastname*: The perfered Lastname
:*username*: A users legacy log in user name
:*password*: The default first log in password
:*location*: The defined Home location
:*email_alias*: The users email_alias *see upn or email_address*
:*ou*: The Active Driectory Orginizational Unit
:*title*: The primary job role
:*status*: The status of the employee
:*id*: The Employee ID
:*bu*: The Business Unit based on the Primary Job Role
:*manager*: The reporting Manager [employee model](models/employee) object
:*upn*: The modern *email style* user log in name
:*pending*: Defines if the employee has been manually entered pending a import from the 
    upstream HIRS Database or if the employee is based off the upstream HIRS Database.
    
    When True variable such as ID or location may be unavalible
:password_expiry_date: The date that a users password will expire
:password_expiration_days: The number of days until a users password will expire
:email_aliases: A list of all email addresses for a user
:email_address: The Primary email address for the user

### Variable: employees
A list of [employee model](models/employee) objects. A for loop is required to iterate through this list


