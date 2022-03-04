import requests

from barbucket.domain_model.types import Api, Exchange, ApiNotationTranslator


class ExchangeistingDownloader():

    @classmethod
    def get_weblisting_singlepage(cls, exchange: Exchange) -> str:
        ex = ApiNotationTranslator.get_api_notation_for_exchange(
            exchange=exchange, api=Api.IB)
        url = (f"https://www.interactivebrokers.com/en/index.php?f=567&exch="
               f"{ex}")
        return requests.get(url).text

    @classmethod
    def get_weblisting_multipage(cls, exchange: Exchange, page: int) -> str:
        ex = ApiNotationTranslator.get_api_notation_for_exchange(
            exchange=exchange, api=Api.IB)
        url = (f"https://www.interactivebrokers.com/en/index.php?f=2222"
               f"&exch={ex}&showcategories=STK&p=&cc=&limit="
               f"100&page={page}")
        return requests.get(url).text
