from django.http import HttpResponse
from django.views.defaults import permission_denied
from django.template import loader


def handler404(request, exception: str = None):
    if exception == None:
        exception = ""
    return Error(request, 404, exception)


def handler403(request, exception: str = None):
    if exception == None:
        exception = ""
    return Error(request, 403, exception)


def handler400(request, exception: str = None):
    if exception == None:
        exception = ""
    return Error(request, 400, exception)


def handler500(request, exception: str = None):
    if exception == None:
        exception = ""
    return Error(request, 500, exception)


def Error(request, code: int, detail: str, template: str = None):
    base_template = "error.html"
    if code == "303":
        return permission_denied(request, detail)
    if template:
        t = loader.get_template(template)
    else:
        t = loader.get_template(base_template)

    return HttpResponse(
        t.render(
            {"title": f"{code}! Error", "err_code": code, "err_detail": detail}, request
        ),
        status=code,
        reason=detail,
    )
