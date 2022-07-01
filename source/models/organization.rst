.. _model_organization:

Organization Models
=====================

Business Units
--------------

The business unit model represents the each organization unit and contains the parent 
relationship and the employee that represents the manager of the unit.

.. autoclass:: organization.models.BusinessUnit
    :members:
    :show-inheritance:


Job Roles
---------

These represent the different roles that can be assigned to an employee and the relationship
to an business unit

.. autoclass:: organization.models.JobRole
    :members:
    :show-inheritance:


Locations
---------

These represent the logical location that are used to defined an employee home base which
could be a physical location, room, or any other representation that is useful to the
business.

.. autoclass:: organization.models.Location
    :members:
    :show-inheritance:
