pass
# import logging
# from datetime import date, timedelta

# import numpy as np

# from barbucket.domain_model.data_classes import QuotesStatus
# from barbucket.util.config_reader import ConfigReader


# _logger = logging.getLogger(__name__)


# class QuotesStatusHandler():
#     @classmethod
#     def has_error_status(cls, status: QuotesStatus) -> bool:
#         if status.status_code > 1:
#             return True
#         else:
#             return False

#     @classmethod
#     def is_quotes_recent(cls, status: QuotesStatus) -> bool:
#         if status.status_code == 0:
#             return False
#         elif status.status_code > 1:
#             return False
#         else:  # quotes existing
#             redownload_days = int(ConfigReader.get_config_value_single(
#                 section="quotes", option="redownload_days"))
#             age_days = np.busday_count(
#                 status.latest_quote_requested, date.today())
#             if age_days > redownload_days:
#                 return False
#             else:
#                 return True

#     @classmethod
#     def update_download_successful(cls, status: QuotesStatus) -> QuotesStatus:
#         status.status_code = 1
#         status.status_text = "Download successful"
#         status.
#         return status

#     @classmethod
#     def update_download_failed(cls, status: QuotesStatus) -> QuotesStatus:
#         status.
#         return status
