# # -*- coding: utf-8 -*-
# """ Autotrader

#  Copyright 2017-2018 Christoph Dieck

#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
# """
# import logging

# from freezegun import freeze_time

# from autotrader.datasource.database.stock_schema import Signal, Tag, Type
# from autotrader.tool.filter.build_filters import BuildFilters
# from autotrader.tool.strategy.back_testing import BackTestingStrategy


# class RecreateFilters:
#     """
#     This tool recreates given filters
#     """

#     def __init__(self, arguments: dict, logger: logging.Logger):
#         self.db_tool = arguments["db_tool"]
#         self.arguments = arguments
#         self.logger = logger

#     def delete_old_filter(self):
#         """
#         delete old filters
#         :return:
#         """
#         # delete old filters
#         for my_filter in self.arguments["filters"]:
#             self.logger.info("Delete filter {} from db.".format(my_filter))
#             self.db_tool.session.query(Signal).join(Tag).join(Type).\
#                 filter(Tag.tag == my_filter and Type.name == 'filter').delete()
#         self.db_tool.commit()

#     def build(self):
#         """
#         Starts the rebuild process for given filters
#         :return: nothing
#         """
#         exit_code = 0
#         to_date = self.arguments.get("to_date")
#         from_date = self.arguments.get("from_date")
#         if from_date is None or to_date is None:
#             to_date = self.db_tool.session.query(Signal.date).join(Tag).join(Type).\
#                 filter(Type.name == 'filter').order_by(Signal.date.desc()).first()
#             from_date = self.db_tool.session.query(Signal.date).join(Tag).join(Type).\
#                 filter(Type.name == 'filter').order_by(Signal.date.asc()).first()
#             if from_date is not None and to_date is not None:
#                 from_date = from_date[0]
#                 to_date = to_date[0]
#         if from_date is None or to_date is None:
#             self.logger.warning("Could not find start date and end date for recreate process.")
#             return -1

#         dates_to_build = BackTestingStrategy.date_range(from_date, to_date)
#         my_fridays = [my_friday for my_friday in dates_to_build if my_friday.weekday() == 4]
#         arguments = {
#             'db_tool': self.db_tool
#         }
#         my_builder = BuildFilters(arguments, self.logger)
#         # start to refresh signal
#         filters = [my_filter for my_filter in my_builder.filters
#                    if my_filter.name in self.arguments["filters"]]
#         if len(filters) == 0:
#             self.logger.warning("Not supported filters {}".format(self.arguments["filters"]))
#             return -1
#         my_builder.set_filters(filters)
#         self.db_tool.commit()
#         for my_friday in my_fridays:
#             exit_code = 0
#             with freeze_time(my_friday):
#                 self.logger.debug("Date is set to %s" % my_friday)
#                 exit_code += my_builder.build()
#         return exit_code
