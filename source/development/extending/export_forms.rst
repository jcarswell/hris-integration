Overriding export forms
=======================

Where the configuration allows for it, an export form or module may be overridden
to accommodate custom configuration. To do this setup a custom module that will either be
in the root directory of the Django app or will be installed into your global path.

Your form will extend the base class which provides most of the basic interfaces and data.
You will need to define the `run` method which is what will be called after class initialization.

Once you have built your class you will need to define add a form variable that points to your
custom class.

If you have not worked with Django before, the app root is added to the path. When you are importing
other classes you would not use hirs_integration.module, instead you just call the module directly.

Base Forms:
- corepoint_export: corepoint_export.forms.BaseExport

An example module would look something like:

.. code-block:: python

    from corepoint_export.forms import BaseExport
    Class MyExportClass(BaseImport):
        def run(self):
            keys = []
            for key,value in self.map.items():
                if value:
                    keys.append(value)
            with open(self.export_file, 'w') as output:
                output.write(",".join(keys))
                for employee in self.employees:
                    line = []
                    for key in keys:
                        line.append(str(getattr(employee,key,'')))
                    output.write(",".join(line))
            
            subprocess.run(self.callable)
            self.set_last_run()

    form = MyExportClass

Once you have you module loaded update the configuration to be the import path for your form.
