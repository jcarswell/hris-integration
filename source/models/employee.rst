.. _model_employee:

Employee Models
=================

These models represent the mutable employee data and the synced data from the source HRIS
system. The employee data represents the current source of truth that is being synced to 
Active Directory and any other exports or applications that bind to the system, and is the
instance to which all related data is bound, including the synced data.

Base Employee Model
-------------------

.. autoclass:: employee.models.base.EmployeeBase
   :members:

(Mutable) Employee Model
-------------------------

.. autoclass:: employee.models.Employee
    :members:
    :show-inheritance:


EmployeeImport Model
--------------------

.. autoclass:: employee.models.EmployeeImport
    :members:
    :show-inheritance:


Employee State Model
--------------------

.. autoclass:: employee.models.base.EmployeeState
    :members:
    :show-inheritance: