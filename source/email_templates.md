# Email Templates

Email Templates are available for a few specific function and can be configured 
in the Settings area. The current template enabled functions are:
- User Welcome Email
- Password Expiration Notification
- New User Notification

## Adding Templates
Under settings select Email templates, by default there is an example templates which includes
an overview of template functions, this templates can be deleted if you so wish. To add a new
template simply select ![new button](_static/new_button.PNG) in the upper.


**Template Name** The internal reference of for the template

**Subject** The subject line of the rendered email. This field supports variables

**Body** The body content of the rendered email. This field support Jinja2 Syntax and Variables


:::{note} Note
At this time, static media is not supported. All embedded media must be available externally
:::

## Syntax

For a full reference of supported syntax visit [Jinja Template Designer Documentation](https://jinja.palletsprojects.com/en/3.0.x/templates/)


**variable** are encapsulated in `{{ ... }}` for a list of variables see the [Variables](Variables) section

**If statements** can be used to optionally add sections to your email based on specific condition such as
if an employee is part of a specific department. If statement blocks start with `{% if <condition> %}` and
ends with `{% endif %}`

**For Loops** similar to if statements for loops can be added to support recursion of specific variables.
For loops block are written starting with `{% for v in variable group %}` and ending with `{% endfor %}`

The `include` directive does not work in email templates

:::{note} Note
If you email templates are not working double check that you have closed all of your block statements or check 
the log file to see if there are any errors.
:::



## Variables

The following variables are currently supported in each template

| Template Name | Variables Supported |
| --- | --- |
| User Welcome Email | `employee` |
| Password Expiration Email | `employee` |
| New User Notification | `employees` which is a list of new employees derived from the employee model object |

### Variable: employee
:*first_name*: The preferred First name
:*last_name*: The preferred Last name
:*password*: The default first log in password
:*title*: The primary job role
:*designations*: The employees designations
:*location*: The defined Home location
:*bu*: The Business Unit based on the Primary Job Role
:*manager*: The reporting Manager [employee model](models/employee) object
:password_expiry_date: The date that a users password will expire
:password_expiration_days: The number of days until a users password will expire
:email_address: The Primary email address for the user

For a full list of available variables refer to the [Employee Manager](models/employee_manager)
documentation.

### Variable: employees
A list of [employee model](models/employee) objects. A for loop is required to iterate through this list


