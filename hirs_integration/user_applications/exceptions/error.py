# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from hris_integration.exceptions import HrisIntegrationBaseError


class UserApplicationError(HrisIntegrationBaseError):
    """The base exception for which all hris_integration error are derived."""
