from hris_integration.exceptions import HrisIntegrationBaseError

class EmloyeeBaseError(HrisIntegrationBaseError):
    pass


class ProcessError(EmloyeeBaseError):
    pass


class EmployeeNotFound(EmloyeeBaseError):
    pass