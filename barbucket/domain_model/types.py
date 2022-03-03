from enum import Enum, auto
import logging
from typing import Dict


_logger = logging.getLogger(__name__)


class Api(Enum):
    """Enumeration of available APIs"""
    IB = auto()
    TV = auto()


class Exchange(Enum):
    """Enumeration of available Exchanges"""
    AEB = auto()
    AMEX = auto()
    ARCA = auto()
    ATH = auto()
    BATS = auto()
    BM = auto()
    BVL = auto()
    BVME = auto()
    BVME_ETF = auto()
    EBS = auto()
    ENEXT_BE = auto()
    FWB = auto()
    GETTEX = auto()
    HEX = auto()
    ISED = auto()
    LSE = auto()
    LSE_ETF = auto()
    NASDAQ = auto()
    NYSE = auto()
    SBF = auto()
    SWB = auto()
    VSE = auto()
    XETRA = auto()
    XETRA_2 = auto()


class ContractType(Enum):
    """Enumeration of available contract types"""
    ADR = auto()
    BOND = auto()
    CLOSED_END_FUND = auto()
    COMMON_STOCK = auto()
    CONV_PREFERRED = auto()
    DUTCH_CERT = auto()
    ETC = auto()
    ETF = auto()
    ETN = auto()
    ETP = auto()
    FUND_OF_FUNDS = auto()
    GDR = auto()
    GERMAN_CERT = auto()
    LTD_PART = auto()
    MLP = auto()
    NY_REG_SHRS = auto()
    OPEN_END_FUND = auto()
    PREFERENCE = auto()
    PREFERRED = auto()
    REIT = auto()
    RIGHT = auto()
    ROYALTY_TRUST = auto()
    SAVINGS_SHARE = auto()
    TRACKING_STOCK = auto()
    UNIT = auto()
    US_DOMESTIC = auto()


class TickerSymbol():
    def __init__(self, name: str) -> None:
        """ """
        name = name.upper()
        name = name.replace(" ", "_")
        name = name.replace(".", "_")
        self.name = name


class ApiNotationTranslator():
    """Decode and encode internal type notation to specific API notations"""

    exchanges = {
        Exchange.AEB: {Api.IB: 'AEB'},
        Exchange.AMEX: {Api.IB: 'AMEX'},
        Exchange.ARCA: {Api.IB: 'ARCA', Api.TV: 'NYSE ARCA'},
        Exchange.ATH: {Api.IB: 'ATH'},
        Exchange.BATS: {Api.IB: 'BATS'},
        Exchange.BM: {Api.IB: 'BM'},
        Exchange.BVL: {Api.IB: 'BVL'},
        Exchange.BVME: {Api.IB: 'BVME'},
        Exchange.BVME_ETF: {Api.IB: 'BVME.ETF'},
        Exchange.EBS: {Api.IB: 'EBS'},
        Exchange.ENEXT_BE: {Api.IB: 'ENEXT.BE'},
        Exchange.FWB: {Api.IB: 'FWB', Api.TV: 'FWB'},
        Exchange.GETTEX: {Api.IB: 'GETTEX'},
        Exchange.HEX: {Api.IB: 'HEX'},
        Exchange.ISED: {Api.IB: 'ISED'},
        Exchange.LSE: {Api.IB: 'LSE'},
        Exchange.LSE_ETF: {Api.IB: 'LSEETF'},
        Exchange.NASDAQ: {Api.IB: 'ISLAND', Api.TV: 'NASDAQ'},
        Exchange.NYSE: {Api.IB: 'NYSE', Api.TV: 'NYSE'},
        Exchange.SBF: {Api.IB: 'SBF'},
        Exchange.SWB: {Api.IB: 'SWB'},
        Exchange.VSE: {Api.IB: 'VSE'},
        Exchange.XETRA: {Api.IB: 'IBIS', Api.TV: 'XETR'},
        Exchange.XETRA_2: {Api.IB: 'IBIS2'}}

    contract_types = {
        ContractType.ADR: {Api.IB: 'ADR'},
        ContractType.BOND: {Api.IB: 'BOND'},
        ContractType.CLOSED_END_FUND: {Api.IB: 'CLOSED-END FUND'},
        ContractType.COMMON_STOCK: {Api.IB: 'COMMON'},
        ContractType.CONV_PREFERRED: {Api.IB: 'CONVPREFERRED'},
        ContractType.DUTCH_CERT: {Api.IB: 'DUTCH CERT'},
        ContractType.ETC: {Api.IB: 'ETC'},
        ContractType.ETF: {Api.IB: 'ETF'},
        ContractType.ETN: {Api.IB: 'ETN'},
        ContractType.ETP: {Api.IB: 'ETP'},
        ContractType.FUND_OF_FUNDS: {Api.IB: 'FUND OF FUNDS'},
        ContractType.GDR: {Api.IB: 'GDR'},
        ContractType.GERMAN_CERT: {Api.IB: 'GERMAN CERT'},
        ContractType.LTD_PART: {Api.IB: 'LTD PART'},
        ContractType.MLP: {Api.IB: 'MLP'},
        ContractType.NY_REG_SHRS: {Api.IB: 'NY REG SHRS'},
        ContractType.OPEN_END_FUND: {Api.IB: 'OPEN-END FUND'},
        ContractType.PREFERENCE: {Api.IB: 'PREFERENCE'},
        ContractType.PREFERRED: {Api.IB: 'PREFERRED'},
        ContractType.REIT: {Api.IB: 'REIT'},
        ContractType.RIGHT: {Api.IB: 'RIGHT'},
        ContractType.ROYALTY_TRUST: {Api.IB: 'ROYALTY TRST'},
        ContractType.SAVINGS_SHARE: {Api.IB: 'SAVINGS SHARE'},
        ContractType.TRACKING_STOCK: {Api.IB: 'TRACKING STK'},
        ContractType.UNIT: {Api.IB: 'UNIT'},
        ContractType.US_DOMESTIC: {Api.IB: 'US DOMESTIC'}}

    @classmethod
    def get_api_notation_for_exchange(cls, exchange: Exchange, api: Api) -> str:
        """ """
        name = cls._get_api_notation_for_element(
            element=exchange, api=api, elements=cls.exchanges)  # type: ignore
        # IB inconsistently uses the names 'ISLAND' and 'NASDAQ'
        if (api == Api.IB) and (name == 'NASDAQ'):
            name = 'ISLAND'
        return name

    @classmethod
    def get_exchange_from_api_notation(cls, name: str, api: Api) -> Exchange:
        """ """
        # IB inconsistently uses the names 'ISLAND' and 'NASDAQ'
        if (api == Api.IB) and (name == "NASDAQ"):
            name = "ISLAND"

        return cls._get_element_from_api_notation(
            name=name, api=api, elements=cls.exchanges)  # type: ignore

    @classmethod
    def get_api_notation_for_contract_type(cls, contract_type: ContractType, api: Api) -> str:
        """ """
        return cls._get_api_notation_for_element(
            element=contract_type, api=api, elements=cls.contract_types)  # type: ignore

    @classmethod
    def get_contract_type_from_api_notation(cls, name: str, api: Api) -> ContractType:
        """ """
        return cls._get_element_from_api_notation(
            name=name, api=api, elements=cls.contract_types)  # type: ignore

    @classmethod
    def get_api_notation_for_ticker_symbol(cls, ticker_symbol: TickerSymbol, api: Api) -> str:
        """ """
        if api == Api.IB:
            return ticker_symbol.name.replace("_", " ")
        elif api == Api.TV:
            return ticker_symbol.name.replace("_", ".")
        raise NotImplementedError(
            "No logic to translate '{api}' implemented in 'TickerSymbol' yet.")
        # logging

    @classmethod
    def get_ticker_symbol_from_api_notation(cls, name: str, api: Api) -> TickerSymbol:
        """ """
        if api == Api.IB:
            return TickerSymbol(name=name.replace(" ", "_"))  # type: ignore
        elif api == Api.TV:
            return TickerSymbol(name=name.replace(".", "_"))  # type: ignore
        raise NotImplementedError(
            "No logic to translate '{api}' implemented in 'TickerSymbol' yet.")
        # logging

    # ~~~~~~~~~~~~~~~~~ private methods ~~~~~~~~~~~~~~~~~

    @classmethod
    def _get_api_notation_for_element(cls, element: Enum, api: Api, elements: Dict[Enum, Dict[Enum, str]]) -> str:
        if element in elements:
            if api in elements[element]:
                return elements[element][api]
            else:
                # Api not found
                raise NotImplementedError(
                    f"A value for '{api}' is not yet implemented in '{elements}':'{element}'.")
        else:
            # contract_type/exchange not found
            raise NotImplementedError(
                f"'{element}' is not yet implemented in '{elements}'.")

    @classmethod
    def _get_element_from_api_notation(cls, name: str, api: Api, elements: Dict[Enum, Dict[Enum, str]]) -> Enum:
        for elem_key, elem_value in elements.items():
            if api in elem_value:
                if elem_value[api] == name:
                    # logging
                    return elem_key
        raise NotImplementedError(
            f"Value '{name}' from '{api}' is not yet implemented in '{elements}'.")
