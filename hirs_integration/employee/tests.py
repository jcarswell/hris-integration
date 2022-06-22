# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from django.test import TestCase, SimpleTestCase
from django.core.exceptions import ValidationError
from .validators import UsernameValidator, UPNValidator


# Create your tests here.
class Validators(SimpleTestCase):
    def test_username_validator(self):
        v = UsernameValidator()
        self.assertRaises(AttributeError, v)
        v("Valid")
        v.first = "a"
        v.parse()
        self.assertEqual(v.username, "a")
        v.first = "a"
        v.last = "b"
        v.parse()
        self.assertEqual(v.username, "ab")
        v.first = "Issac"
        v.last = "Asimov"
        v.parse()
        self.assertEqual(v.username, "IAsimov")
        v.last = "D`Arby"
        v.clean()
        self.assertEqual(v.username, "IDArby")
        self.assertRaises(ValidationError, v, "$")
        self.assertRaises(ValidationError, v, "oiansdnasd0n1oqn9s8dnashouasbd")
        v = UsernameValidator("Username")
        self.assertEqual(v.is_valid(), True)
        self.assertEqual(v.username, "Username")
        v = UsernameValidator("Issac", "Asimov")
        self.assertEqual(v.is_valid(), True)
        self.assertEqual(v.username, "IAsimov")
        v = UsernameValidator("Issac", "Asimov", "0")
        self.assertEqual(v.is_valid(), True)
        self.assertEqual(v.username, "IAsimov0")

    def test_upn_validator(self):
        v = UPNValidator()
        self.assertRaises(AttributeError, v)
        v("Valid")
        v.first = "a"
        v.parse()
        self.assertEqual(v.username, "a")
        v.first = "a"
        v.last = "b"
        v.parse()
        self.assertEqual(v.username, "a.b")
        v.first = "Issac"
        v.last = "Asimov"
        v.parse()
        self.assertEqual(v.username, "Issac.Asimov")
        v.last = "D`Arby"
        v.clean()
        self.assertEqual(v.username, "Issac.DArby")
        self.assertRaises(ValidationError, v, "$")
        self.assertRaises(
            ValidationError,
            v,
            "oiansdnasd0n1oqn9s8dnashouasbdoiansdnawndoainsdoanwoidsoasdoubasodub",
        )
        v = UPNValidator("Username")
        self.assertEqual(v.is_valid(), True)
        self.assertEqual(v.username, "Username")
        v = UPNValidator("Issac", "Asimov")
        self.assertEqual(v.is_valid(), True)
        self.assertEqual(v.username, "Issac.Asimov")
        v = UPNValidator("Issac", "Asimov", "0")
        self.assertEqual(v.is_valid(), True)
        self.assertEqual(v.username, "Issac.Asimov0")
