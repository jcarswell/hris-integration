.. ref_user_application:

User Application
=================

This module enables the tracking of software application to users. There are two parts to
this module:

1. The Applications:
    This table contains a list of application that can be associated with a user. Each 
    instance can be licensed or unlicensed, have a maximum number of users, and be tied
    to a specific AD group.

    In the instance that an application is licenses or has a the max users defined, the 
    account will be added into the employees list. This allows for limits to be placed on
    the number of users that can be associated with an application, as well as allows 
    for easier review of current usages.

    The max users is not exclusive to licensed software.

2. The Account:
    This is the table that allows for the association of a user to an application and the
    additional details that are pertinent to the login or instance. Each instance has 
    a generic notes field that can be used to store any information regrading this Account
    such as a user name, as well as a expiration date.

    The expiration date currently is just metadata. This data could be queried via the API
    to determine which accounts need to be cleaned up.

    The account entry is handled via the employee page, but all accounts can be viewed
    on the User Application Instance page.

Model: :ref:`model_user_application`