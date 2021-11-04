from enum import Enum


class Api(Enum):
    """Enumeration of available APIs"""
    IB = 1
    TV = 2


class EncodingBase(Enum):
    """Base class for encodings"""

    @classmethod
    def encode(cls, name: str, to_api: Api) -> str:
        """Encode from Barbucket notation to specific API notation

        :param name: Name to encode
        :type name: str
        :param to_api: Api to encode to
        :type to_api: Api
        :raises AttributeError: Name was not found in encoding table
        :return: Encoded name
        :rtype: str
        """

        for element in cls:
            if element.name == name:
                return element.value[to_api]
        raise AttributeError(f"Attribute '{name}' not found.")

    @classmethod
    def decode(cls, name: str, from_api: Api) -> str:
        """Decode from specific API notation to Barbucket notation

        :param name: Name to decode
        :type name: str
        :param from_api: Api to decode from
        :type from_api: Api
        :raises AttributeError: Name was not found in encoding table
        :return: Decoded name
        :rtype: str
        """

        for element in cls:
            if element.value[from_api] == name:
                return element.name
        raise AttributeError(f"Attribute '{name}' not found.")


class Exchange(EncodingBase):
    """Decode and encode exchange names to specific API notations"""

    AEB = {Api.IB: 'AEB', Api.TV: ''}
    AMEX = {Api.IB: 'AMEX', Api.TV: ''}
    ARCA = {Api.IB: 'ARCA', Api.TV: 'NYSE ARCA'}
    ATH = {Api.IB: 'ATH', Api.TV: ''}
    BATS = {Api.IB: 'BATS', Api.TV: ''}
    BM = {Api.IB: 'BM', Api.TV: ''}
    BVL = {Api.IB: 'BVL', Api.TV: ''}
    BVME = {Api.IB: 'BVME', Api.TV: ''}
    BVME_ETF = {Api.IB: 'BVME.ETF', Api.TV: ''}
    EBS = {Api.IB: 'EBS', Api.TV: ''}
    ENEXT_BE = {Api.IB: 'ENEXT.BE', Api.TV: ''}
    FWB = {Api.IB: 'FWB', Api.TV: 'FWB'}
    GETTEX = {Api.IB: 'GETTEX', Api.TV: ''}
    HEX = {Api.IB: 'HEX', Api.TV: ''}
    ISED = {Api.IB: 'ISED', Api.TV: ''}
    LSE = {Api.IB: 'LSE', Api.TV: ''}
    LSE_ETF = {Api.IB: 'LSEETF', Api.TV: ''}
    NASDAQ = {Api.IB: 'ISLAND', Api.TV: 'NASDAQ'}
    NYSE = {Api.IB: 'NYSE', Api.TV: 'NYSE'}
    SBF = {Api.IB: 'SBF', Api.TV: ''}
    SWB = {Api.IB: 'SWB', Api.TV: ''}
    VSE = {Api.IB: 'VSE', Api.TV: ''}
    XETRA = {Api.IB: 'IBIS', Api.TV: 'XETR'}
    XETRA_2 = {Api.IB: 'IBIS2', Api.TV: ''}

    @classmethod
    def decode(cls, name: str, from_api: Api) -> str:
        """Decode from specific api notation to Barbucket notation"""

        # IB inconsistently uses the names 'ISLAND' and 'NASDAQ'
        if (from_api == Api.IB) and (name == 'NASDAQ'):
            name = 'ISLAND'
        return super().decode(name=name, from_api=from_api)


class ContractType(EncodingBase):
    """Decode and encode contract type names to specific API notations"""

    ADR = {Api.IB: 'ADR', Api.TV: ''}
    BOND = {Api.IB: 'BOND', Api.TV: ''}
    CLOSED_END_FUND = {Api.IB: 'CLOSED-END FUND', Api.TV: ''}
    COMMON_STOCK = {Api.IB: 'COMMON', Api.TV: ''}
    CONV_PREFERRED = {Api.IB: 'CONVPREFERRED', Api.TV: ''}
    DUTCH_CERT = {Api.IB: 'DUTCH CERT', Api.TV: ''}
    ETC = {Api.IB: 'ETC', Api.TV: ''}
    ETF = {Api.IB: 'ETF', Api.TV: ''}
    ETN = {Api.IB: 'ETN', Api.TV: ''}
    ETP = {Api.IB: 'ETP', Api.TV: ''}
    FUND_OF_FUNDS = {Api.IB: 'FUND OF FUNDS', Api.TV: ''}
    GDR = {Api.IB: 'GDR', Api.TV: ''}
    GERMAN_CERT = {Api.IB: 'GERMAN CERT', Api.TV: ''}
    LTD_PART = {Api.IB: 'LTD PART', Api.TV: ''}
    MLP = {Api.IB: 'MLP', Api.TV: ''}
    NY_REG_SHRS = {Api.IB: 'NY REG SHRS', Api.TV: ''}
    OPEN_END_FUND = {Api.IB: 'OPEN-END FUND', Api.TV: ''}
    PREFERENCE = {Api.IB: 'PREFERENCE', Api.TV: ''}
    PREFERRED = {Api.IB: 'PREFERRED', Api.TV: ''}
    REIT = {Api.IB: 'REIT', Api.TV: ''}
    RIGHT = {Api.IB: 'RIGHT', Api.TV: ''}
    ROYALTY_TRUST = {Api.IB: 'ROYALTY TRST', Api.TV: ''}
    SAVINGS_SHARE = {Api.IB: 'SAVINGS SHARE', Api.TV: ''}
    TRACKING_STOCK = {Api.IB: 'TRACKING STK', Api.TV: ''}
    UNIT = {Api.IB: 'UNIT', Api.TV: ''}
    US_DOMESTIC = {Api.IB: 'US DOMESTIC', Api.TV: ''}


class Symbol():
    """Decode and encode symbol names to specific API notations"""

    @classmethod
    def encode(cls, name: str, to_api: Api) -> str:
        """Encode from Barbucket notation to specific API notation"""

        if to_api == Api.IB:
            name = name.replace("_", " ")
        elif to_api == Api.TV:
            name = name.replace("_", ".")
        return name

    @classmethod
    def decode(cls, name: str, from_api: Api) -> str:
        """Decode from specific API notation to Barbucket notation"""

        if from_api == Api.IB:
            name = name.replace(" ", "_")
        elif from_api == Api.TV:
            name = name.replace(".", "_")
        return name
