Active Directory Export
=======================

Process Flow
^^^^^^^^^^^^

.. image:: /_static/ad_export.svg

This diagram covers the BaseExport class but in practice this
class is only used if you don't use the Exchange mailbox functions.
The default form is ADUserExport, which builds on the base class,
but defines new_user_post and run_post. The class also add's a
__del__ handler to ensure that any pending mailboxes are dealt with.

The function new_user_post passes the Employee object to add_mailbox
and appends the output to self.mailboxes.

The add_mailbox function is responsible for building the mailbox command
that is passed to powershell to create the users mailbox based on 
the user configuration set.

the run_post checks if there are any mailboxes to be created, renders
the PowerShell script and lastly calls the PowerShell script.

