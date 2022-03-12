## Overriding import forms
Similar to export forms some import forms may be overridden there the configuration allows for it.
However a import form will be called once per object instead of expecting the form to to produce the
output data.

Your form will extend the base class which provides most of the basic interfaces and data.
You will need to define the `save` method which is what will be called after class initalization.

The class initailization will take the required data to be saved, do any general parsing required and
make it availble in self to be utilized

Base Froms:
- ftp_import: ftp_import.forms.BaseImport

An example module would look something like:
```
from ftp_import.forms import BaseImport
Class MyImportClass(BaseImport):
    def save(self):
        for key,value in self.kwargs:
            if hasattr(self.employee):
                setattr(self.employee,key,value)

form = MyImportClass
```

Once you have you module loaded update the configuration to be the import path for your form.