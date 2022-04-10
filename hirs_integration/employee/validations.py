# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from hris_integration.validators import ValidationError

from .exceptions import ProcessError

class UsernameValidatorBase:
    """
    Class to validate usernames and aliases.
    """
    invalid_chars = ['!','@','#','$','%','^','&','*','(',')','_','+','=',';',':','\'','"',
                     ',','<','>',',',' ','`','~','{','}','|']
    substitute = ''

    
    def __init__(self, first:str, last:str =None, suffix:str =None, allowed_char:list =None):
        """Base initializer for username validator.

        :param first: Firstname or username/alias to be validate
        :type first: str
        :param last: lastname of the user, defaults to None
        :type last: str, optional
        :param suffix: suffix for the username to ensure uniqueness, defaults to None
        :type suffix: str, optional
        :param allowed_char: override the default list of invalid characters, defaults to None
        :type allowed_char: list, optional
        """

        self.first = first
        self.last = last or ''
        self.suffix = suffix or ''
        if isinstance(allowed_char, list):
            for char in allowed_char:
                if char in self.invalid_chars:
                    self.invalid_chars.remove(char)
        elif isinstance(allowed_char,str):
            if allowed_char in self.invalid_chars:
                self.invalid_chars.remove(allowed_char)

        self.parse()


    def parse(self):
        raise NotImplementedError("Must be implemented by subclass")

    def clean(self):
        """Ensure that the username is valid.

        :raises ProcessError: If clean is called before parse
        """

        if not hasattr(self,'username'):
            raise ProcessError("Username must be parsed before cleaning")
        for char in self.useranme:
            if char in self.invalid_chars:
                self.useranme = self.useranme.replace(char,self.substitute)

    def __call__(self):
        raise NotImplementedError("Must be implemented by subclass")

    def __str__(self) -> str:
        """Returns a valid username base on the initailized values.

        :return: Valid Username
        :rtype: str
        """

        self.clean()
        return self.useranme


class UsernameValidator(UsernameValidatorBase):
    """
    Username creation and validation helper. Ensures that usernames are built using standard
    username rules and do not contain invalid characters.
    """

    def parse(self):
        """
        Parse the passed values into a username.
        """

        if self.last is None and self.suffix is None:
            self.useranme = self.first

        else:
            self.useranme = self.first[1] + self.last
            if self.suffix:
                self.useranme = self.useranme[:20-len(self.suffix)] + self.suffix
            self.username = self.useranme[:20]

    def __call__(self):
        """ Validate the username.

        :raises ValidationError: If the username contains invalid characters or is too long.
        """

        self.parse()
        for char in self.useranme:
            if char in self.invalid_chars:
                raise ValidationError(f"Username contains invalid character: {char}")

        if len(self.username) > 20:
            raise ValidationError(f"Username is too long: {self.username}")


class UPNValidator(UsernameValidatorBase):
    def __call__(self):
        self.parse()

        for char in self.useranme:
            if char in self.invalid_chars:
                raise ValidationError(f"Username contains invalid character: {char}")

    def parse(self):
        """
        Parse the passed values into a username.
        """

        if self.last is '' and self.suffix is '':
            self.useranme = self.first
        else:
            self.useranme = f"{self.first}.{self.last}{self.suffix}"
