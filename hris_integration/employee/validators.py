# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from hris_integration.validators import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _t

__all__ = ("UsernameValidator", "UPNValidator")


@deconstructible
class UsernameValidatorBase:
    """Class to validate usernames and aliases."""

    message = _t("Enter a valid username.")
    code = "invalid"

    #: list: The list of invalid characters for a username or email alias
    invalid_chars = [
        "!",
        "@",
        "#",
        "$",
        "%",
        "^",
        "&",
        "*",
        "(",
        ")",
        "_",
        "+",
        "=",
        ";",
        ":",
        "'",
        '"',
        ",",
        "<",
        ">",
        " ",
        "`",
        "~",
        "{",
        "}",
        "|",
    ]
    #: str: The default character to replace invalid characters with
    substitute = ""
    #: int: The default max length for a username
    max_length = None

    def __init__(
        self,
        first: str = None,
        last: str = None,
        suffix: str = None,
        allowed_char: list = None,
        max_length: int = None,
    ):
        """Base initializer for username validator.

        :param first: Firstname or username/alias to be validate
        :type first: str
        :param last: lastname of the user, defaults to None
        :type last: str, optional
        :param suffix: suffix for the username to ensure uniqueness, defaults to None
        :type suffix: str, optional
        :param allowed_char: override the default list of invalid characters, defaults to None
        :type allowed_char: list, optional
        :param max_length: override the default max length, defaults to None
        :type max_length: int, optional
        """

        self.first = first or ""
        self.last = last or ""
        self.suffix = suffix or ""
        self.max_length = max_length or self.max_length
        if isinstance(allowed_char, list):
            for char in allowed_char:
                if char in self.invalid_chars:
                    self.invalid_chars.remove(char)
        elif isinstance(allowed_char, str):
            if allowed_char in self.invalid_chars:
                self.invalid_chars.remove(allowed_char)

        if self.last is None and self.suffix is None:
            self.username = first
        else:
            self.parse()

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, self.__class__)
            and self.is_valid() == other.is_valid()
            and self.max_length == other.max_length
            and self.first == other.first
            and self.username
            or None == other.username
            or None
        )

    def parse(self):
        raise NotImplementedError("Must be implemented by subclass")

    def clean(self):
        """Ensure that the username is valid."""

        self.parse()
        for char in self.username:
            if char in self.invalid_chars:
                self.username = self.username.replace(char, self.substitute)

    def is_valid(self):
        """Check that the username is valid."""
        try:
            self.__call__()
            return True
        except ValidationError:
            return False

    def __call__(self, value: str = None) -> str:
        """Validate the username.

        :param value: Username to validate, for compatibility with Django
        :type value: str, optional
        :raises ValidationError: If the username contains invalid characters or is too long.
        """

        try:
            username = value or self.username
        except AttributeError:
            self.parse()  # If the username is not set, call the parser to generate it
            username = self.username
        for char in username:
            if char in self.invalid_chars:
                raise ValidationError(f"Username contains invalid character: {char}")

        if len(username) > self.max_length:
            raise ValidationError(f"Username is too long: {username}")

    def __str__(self) -> str:
        """Returns a valid username base on the initialized values.

        :return: Valid Username
        :rtype: str
        """

        self.clean()
        return self.username

    def __eq__(self, other: object) -> bool:
        if isinstance(other, UsernameValidatorBase):
            return (
                self.username == other.username
                and self.invalid_chars == other.invalid_chars
                and self.max_length == other.max_length
                and self.__class__.__name__ == other.__class__.__name__
            )
        return False


@deconstructible
class UsernameValidator(UsernameValidatorBase):
    """
    Username creation and validation helper. Ensures that usernames are built using standard
    username rules and do not contain invalid characters.
    """

    #: int: The default max length for a username
    max_length = 20

    def parse(self):
        """
        Parse the passed values into a username.
        """

        if self.first == "":
            raise AttributeError("First name/Username is required.")

        if self.last == "" and self.suffix == "":
            self.username = self.first

        else:
            self.username = self.first[0] + self.last
            if self.suffix:
                self.suffix = str(self.suffix)
                self.username = (
                    self.username[: self.max_length - len(self.suffix)] + self.suffix
                )

        self.username = self.username[: self.max_length]


@deconstructible
class UPNValidator(UsernameValidatorBase):
    """
    UserPrincipalName creation and validation helper. Ensures that UPNs are built using standard
    upn rules and do not contain invalid characters.
    """

    #: int: The default max length for a UserPrincipalName (As per ms-Exch-Mail-Nickname rangeUpper)
    max_length = 64

    def parse(self):
        """
        Parse the passed values into a username.
        """

        if self.first == "":
            raise AttributeError("First name/Username is required.")

        if self.last == "" and self.suffix == "":
            self.username = self.first

        else:
            self.username = f"{self.first}.{self.last}{self.suffix}"

        self.username = self.username[: self.max_length]
