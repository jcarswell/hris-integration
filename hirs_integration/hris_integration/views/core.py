# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging

from django.http import JsonResponse, HttpResponseBadRequest
from django.views.generic.base import TemplateResponseMixin
from .bases import LoggedInView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from common.functions import get_model_pk_name
from django.utils.safestring import mark_safe


logger = logging.getLogger("hris_integration.views.core")


class ListView(TemplateResponseMixin, LoggedInView):
    """A simple list view of all the objects in the model."""

    form = None
    template_name = "base/base_list.html"
    http_method_names = ["get", "head", "options", "trace"]

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        if self.form == None:
            raise ValueError("FormView has no ModelForm class specified")
        if hasattr(request.GET, "form"):
            request.GET.pop("form")

        self._model = self.form._meta.model
        self.fields = self.form.list_fields
        if self.fields == []:
            self.fields = list(self.form.base_fields.keys())

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.page_title = getattr(self.form, "name", None)
        self.page_description = getattr(self.form, "description", None)
        context = self.get_context(**kwargs)

        # theres no pk in the request so return the list view
        self.template_name = "base/base_list.html"

        labels = []
        for field in self.fields:
            labels.append(self.form.base_fields[field].label)

        context["form_fields"] = labels
        context["form_row"] = self.list_rows()

        logger.debug(f"context: {context}")
        return self.render_to_response(context)

    def list_rows(self):
        """Generate the rows for the list view."""

        logger.debug("requested list_rows")
        output = []
        pk = get_model_pk_name(self._model)
        if pk not in self.fields:
            pk = self.fields[0]
        logger.debug(f"using {pk} as primary key in view")
        for row in self._model.objects.all():
            output.append(f'<tr id="{row.pk}">')
            for field in self.fields:
                val = getattr(row, field)

                if field == pk:
                    val = f'<a href="{self.request.path}{row.pk}/"><strong>{val}</strong></a>'

                if (
                    getattr(self._model, field).__class__.__name__
                    == "ForwardManyToOneDescriptor"
                ):
                    # TODO: [#57] Lookup ForeignKey URL and update val with link to that view
                    pass

                output.append(f"<td>{val}</td>")
            output.append("</tr>")
        logger.debug(f"Output contains: {output}")
        return mark_safe("\n".join(output))


class FormView(TemplateResponseMixin, LoggedInView):
    """The edit view for a model object."""

    form = None
    template_name = "base/base_edit.html"
    enable_delete = True
    edit_postfix = "_edit"

    def setup(self, request: "django.http.HttpRequest", *args, **kwargs):
        super().setup(request, *args, **kwargs)

        if self.form == None:
            raise ValueError("FormView has no ModelForm class specified")
        if hasattr(request.POST, "form"):
            request.POST.pop("form")
        if hasattr(request.GET, "form"):
            request.GET.pop("form")

        try:
            pk = kwargs["id"]
        except KeyError:
            pk = 0

        self._model = self.form._meta.model
        self.fields = self.form.base_fields.keys()

        if pk > 0:
            model = self._model.objects.get(pk=pk)
        elif pk == 0:
            model = self._model()
            self.enable_delete = False

        if request.method in ("POST", "PUT"):
            self._form = self.form(request.POST, request.FILES, instance=model)
        elif isinstance(pk, int):
            self._form = self.form(instance=model)
        else:
            self._form = None

    @method_decorator(csrf_protect)
    def dispatch(self, request: "django.http.HttpRequest", *args, **kwargs):
        logger.debug(f"dispatching {request.method}")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request: "django.http.HttpRequest", *args, **kwargs):
        self.page_title = getattr(self.form, "name", None)
        self.page_description = getattr(self.form, "description", None)
        context = self.get_context(form_delete=self.enable_delete, **kwargs)

        context["form"] = self._form

        logger.debug(f"context: {context}")
        return self.render_to_response(context)

    def post(self, request: "django.http.HttpRequest", *args, **kwargs) -> JsonResponse:
        """
        Creates or updates a model instance based on the given form data.

        :param request: The request object
        :type request: django.http.HttpRequest
        :return: A JSON response containing status and errors or status and updated field
            values of the created/updated model
        :rtype: JsonResponse
        """

        logger.debug(f"post data is: {request.POST}")
        if kwargs["id"] != 0 and request.POST.get("id", 0) != kwargs.get("id", 0):
            return HttpResponseBadRequest("The ID may not be changed once set")
        if self._form.is_valid():
            logger.debug("Form is valid, saving()")
            save_data = self._form.save()
        else:
            logging.error(
                f"encountered Exception while saving form {self.form.name}\n"
                f"Errors are: {self._form._errors.keys()}"
            )
            ers = []
            for e in self._form._errors.values():
                ers.append("<br>".join(e))
            response = {
                "status": "error",
                "fields": list(self._form._errors.keys()),
                "errors": ers,
            }
            response.update(dict((k, v[0]) for k, v in self._form._errors.items()))
            logger.debug(f"response: {response}")
            return JsonResponse(response)

        res = {"status": "success", "id": save_data.pk}
        for field in self.fields:
            res[field] = getattr(save_data, field)
            if not isinstance(res[field], (str, int, bool)):
                if hasattr(res[field], "id"):
                    res[field] = res[field].id
                elif hasattr(res[field], "all"):
                    res[field] = [x.id for x in res[field].all()]
                else:
                    res[field] = str(res[field])

        response = JsonResponse(res)

        return response

    def delete(self, request, *args, **kwargs):
        try:
            pk = kwargs["id"]
        except KeyError:
            return HttpResponseBadRequest()

        o = self._model.objects.get(pk=pk)
        try:
            o.delete()
            return JsonResponse({"status": "success"})

        except Exception as e:
            logger.exception(f"lazy catch of {e}")
            return HttpResponseBadRequest(str(e))
