# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from pyad.adquery import ADQuery

from .exceptions import noExecutedQuery


class Query(ADQuery):
    """
    Extension of the ADQuery class adding return values as tuple
    which is needed for the Django models.

    Added functions:
      - get_all_results_tuple: Gets all results from the executed query and returns a list of tuples
      - get_single_result_tuple: Fetches the next result in the result set
    """

    __row_counter = 0

    def __init__(self, options={}):
        super().__init__(options)

    def get_all_results_tuple(self) -> list:
        """
        Get all results and returns them in a list of tuples

        Raises:
            noExecutedQuery: if called before calling execute_query()

        Returns:
            list: list of tuples with the queried values
        """

        if not self._ADQuery__queried:
            raise noExecutedQuery
        if not self._ADQuery__rs.EOF:
            self._ADQuery__rs.MoveFirst()

        rows = []
        while not self._ADQuery__rs.EOF:
            vals = []
            for f in self._ADQuery__rs.Fields:
                vals.append(f.Value)
            rows.append(tuple(vals))
            self._ADQuery__rs.MoveNext()

        return rows

    def get_single_result_tuple(self) -> tuple:
        """
        Gets the next result in the result set.

        Raises:
            noExecutedQuery: if called before calling execute_query()

        Returns:
            tuple: list of values for the query result
        """

        if not self._ADQuery__queried:
            raise noExecutedQuery
        if not self._ADQuery__rs.EOF and self.__row_counter == 0:
            self._ADQuery__rs.MoveFirst()

        d = []
        for f in self._ADQuery__rs.Fields:
            d.append(f.Value)

        self.__row_counter += 1
        self._ADQuery__rs.MoveNext()

        return tuple(d)
