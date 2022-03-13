.. _ref_settings:

User Configurable Settings Module
=================================

Model: :ref:`model_settings`

.. _settings-field-definitions:

Field Definition
----------------

A field is made up of a number of configuable elements that tell the rendering engine how to
display a specfic field as well as the FieldManager what type of data should be expected.

:**Field Definition**: At minimum this needs to have field_properties and should define 
    the field type.

    | {
    |     'example_field': {
    |         "default_value": ...
    |         "hidden": ...
    |         "field_properties": {
    |             "type": ...
    |             "required": ...
    |             "disabled": ...
    |             "help_text": ...
    |             "validators": ...
    |             "label": ...
    |             "error_messages": ...
    |             "widget": ...
    |             "initial": ...
    |             "localize": ...
    |             "label_suffix": ...
    |         }
    |     }
    | }

    :*Type*: dictionary
:default_value: The inital value that will be set for the field
:hidden: Encrypt the value in the database and render the value as a
    password field
    
    :*Type*: boolean
:field_properties: In addition to the base field option there are some 
    extra properties avaliable depending on field type. All 
    properties and field type are based off of the built in 
    Django form fields.

    | *CharField*, *RegExField* - 'max_length', 'min_length', 
    |                             'strip', 'empty_value'
    | *ChoiceField*, *MultipleChoiceField* - 'choices'
    | *IntegerField*, *FloatField* - 'max_value', 'min_value'
    | *DecimalField* - 'max_value', 'min_value', 'max_digits', 'decimal_places'
    | *DateTimeField*, *DateField* - 'input_formats'
    | 

    :*Type*: string
:field_properties.type: One of: (Default: CharField)

    - CharField
    - ChoiceField
    - DateField
    - BooleanField
    - DecimalField
    - FloatField
    - DateTimeField
    - RegexField
    - IntegerField
    
    :*Type*: string
:field_properties.required: Defined if this a required input field (Default: False)

    :*Type*: boolean
:field_properties.disabled: Sets the field to disabled

    :*Type*: boolean
:field_properties.help_text: Field hint to help users know what they are setting

    :*Type*: string
:field_properties.validators: A list addiional validators that are used to validate a field.
    
    If you have specific validators they should be defined in your validators
    sub-module in the root of your module.

    `Django Validators <https://docs.djangoproject.com/en/4.0/ref/validators/>`

    :*Type*: list[objects]
:field_properties.label: Override the default field name.

    :*Type*: string
:field_properties.error_messages: An optional dictionary to override the default messages that 
    the field will raise.

    :*Type*: dictionary
:field_properties.widget:  The widget to use if the default widget isn't sufficiant

    :*Type*: callable
:field_properties.initial: The inline initial value that is rendered but not saved to 
    the database

    :*Type*: string
:field_properties.localize: Specify if the feild should be localized

    :*Type*: boolean
:field_properties.label_suffix: Overrides the suffix to be added to the lable

    :*Type*: string
:field_properties.min_length: *int* The minimum lenght if the field

    :*Type*: integer
:field_properties.max_length: *int* The max length of the feild (Default: 768)

    :*Type*: integer
:field_properties.strip: *bool* Stip the string (Default: True)

    :*Type*: boolean
:field_properties.empty_value: *str* The value to set if the a field is empty

    :*Type*: string
:field_properties.choices: The choices to render. 

    Refer to `Django choices <https://docs.djangoproject.com/en/4.0/ref/models/fields/#choices>`

    For more complex choice field definitions place them in your validtors 
    sub-module in the root of your module
:field_properties.min_value: The minimum acceptable value

    :*Type*: integer OR float
:field_properties.max_value: The maximum acceptable value

    :*Type*: integer OR float
:field_properties.max_digits: *int* The maximum number of digits

    :*Type*: integer
:field_properties.decimal_places: *int* The maximum number of decimal places

    :*Type*: integer
:field_properties.input_formats: *string* The date or date time format to use

    :*Type*: string