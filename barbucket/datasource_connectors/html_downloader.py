import requests

from barbucket.domain_model.types import Api, Exchange, ApiNotationTranslator


class HtmlDownloader():
    def __init__(self, api_notation_translator: ApiNotationTranslator) -> None:
        self._api_notation_translator = api_notation_translator

    def get_weblisting_singlepage(self, exchange: Exchange) -> str:
        ex = self._api_notation_translator.get_api_notation_for_exchange(
            exchange=exchange, api=Api.IB)
        url = (f"https://www.interactivebrokers.com/en/index.php?f=567&exch="
               f"{ex}")
        return requests.get(url).text

    def get_weblisting_multipage(self, exchange: Exchange, page: int) -> str:
        ex = self._api_notation_translator.get_api_notation_for_exchange(
            exchange=exchange, api=Api.IB)
        url = (f"https://www.interactivebrokers.com/en/index.php?f=2222"
               f"&exch={ex}&showcategories=STK&p=&cc=&limit="
               f"100&page={page}")
        return requests.get(url).text
