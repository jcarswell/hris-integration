Extending the FTP Import Form
=============================

The FTP import form is responsible for taking a parsed row of data from the the CSV parser and coverting
the raw data in to a valid employee object. Your custom form will need to at minimum define the save_main method.

It is recommended that you review the BaseImport

Your form will extend the base class which provides most of the basic interfaces and data.
You will need to define the `save` method which is what will be called after class initalization.

The class initailization will take the required data to be saved, do any general parsing required and
make it availble in self to be utilized

Base Froms:
- ftp_import: ftp_import.forms.BaseImport

An example module would look something like:

.. code-block:: python

    from ftp_import.forms import BaseImport
    Class MyImportClass(BaseImport):
        def save(self):
            for key,value in self.kwargs:
                if hasattr(self.employee):
                    setattr(self.employee,key,value)

    form = MyImportClass


Once you have you module loaded update the configuration to be the import path for your form.