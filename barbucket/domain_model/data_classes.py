from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class Contract(Base):
    __tablename__ = 'contracts'
    __table_args__ = (UniqueConstraint('contract_type', 'exchange',
                                       'broker_symbol', 'currency'), )

    id = Column(Integer, primary_key=True)
    contract_type = Column(String(30))
    exchange = Column(String(30))
    broker_symbol = Column(String(30))
    currency = Column(String(30))
    exchange_symbol = Column(String(30))
    name = Column(String(100))

    universe_memberships = relationship(
        "UniverseMembership",
        back_populates="contract",
        cascade="all, delete",
        passive_deletes=True)
    contract_details_ib = relationship(
        "ContractDetailsIb",
        back_populates="contract",
        cascade="all, delete",
        passive_deletes=True)
    contract_details_tv = relationship(
        "ContractDetailsTv",
        back_populates="contract",
        cascade="all, delete",
        passive_deletes=True)
    # quotes_status = relationship(
    #     "QuotesStatus",
    #     back_populates="contract",
    #     cascade="all, delete",
    #     passive_deletes=True)
    quote = relationship(
        "Quote",
        back_populates="contract",
        cascade="all, delete",
        passive_deletes=True)

    def __eq__(self, other):
        return (
            (self.contract_type == other.contract_type) and
            (self.exchange == other.exchange) and
            (self.broker_symbol == other.broker_symbol) and
            (self.currency == other.currency))

    def __hash__(self):
        return hash((self.contract_type, self.exchange, self.broker_symbol, self.currency))

    def __repr__(self):
        return f"""Contract(
            id={self.id},
            contract_type={self.contract_type},
            exchange={self.exchange}),
            exchange_symbol={self.exchange_symbol},
            broker_symbol={self.broker_symbol},
            name={self.name},
            currency={self.currency}"""


class UniverseMembership(Base):
    __tablename__ = 'universe_memberships'
    __table_args__ = (UniqueConstraint('contract_id', 'universe'),)

    id = Column(Integer, primary_key=True)
    contract_id = Column(
        Integer,
        ForeignKey('contracts.id', ondelete="CASCADE"))
    universe = Column(String(100))

    contract = relationship(
        "Contract", back_populates="universe_memberships")

    def __repr__(self):
        return f"""UniverseMembership(
            id={self.id},
            contract_id={self.contract_id},
            universe={self.universe},
            contract={self.contract})"""


class ContractDetailsIb(Base):
    __tablename__ = 'contract_details_ib'

    contract_id = Column(
        Integer,
        ForeignKey('contracts.id', ondelete="CASCADE"),
        primary_key=True)
    stock_type = Column(String(30))
    primary_exchange = Column(String(30))
    industry = Column(String(30))
    category = Column(String(30))
    subcategory = Column(String(30))

    contract = relationship(
        "Contract", back_populates="contract_details_ib")

    def __repr__(self):
        return f"""ContractDetailsIb(
            contract_id={self.contract_id},
            stock_type={self.stock_type},
            primary_exchange={self.primary_exchange},
            industry={self.industry},
            category={self.category},
            subcategory={self.subcategory},
            contract={self.contract})"""


class ContractDetailsTv(Base):
    __tablename__ = 'contract_details_tv'

    contract_id = Column(
        Integer,
        ForeignKey('contracts.id', ondelete="CASCADE"),
        primary_key=True)
    market_cap = Column(Integer)
    avg_vol_30_in_curr = Column(Integer)
    country = Column(String(30))
    employees = Column(Integer)
    profit = Column(Integer)
    revenue = Column(Integer)

    contract = relationship(
        "Contract", back_populates="contract_details_tv")

    def __repr__(self):
        return f"""ContractDetailsTv(
            contract_id={self.contract_id},
            market_cap={self.market_cap},
            avg_vol_30_in_curr={self.avg_vol_30_in_curr},
            country={self.country},
            employees={self.employees},
            profit={self.profit},
            revenue={self.revenue},
            contract={self.contract})"""


# class QuotesStatus(Base):
#     __tablename__ = 'quotes_status'

#     contract_id = Column(
#         Integer,
#         ForeignKey('contracts.id', ondelete="CASCADE"),
#         primary_key=True)
#     status_code = Column(Integer)
#     status_text = Column(String(255))
#     earliest_quote_requested = Column(Date)
#     latest_quote_requested = Column(Date)

#     contract = relationship(
#         "Contract", back_populates="quotes_status")

#     def __repr__(self):
#         return f"""QuotesStatus(
#             contract_id={self.contract_id},
#             status_code={self.status_code},
#             status_text={self.status_text},
#             latest_quote_requested={self.latest_quote_requested},
#             earliest_quote_requested={self.earliest_quote_requested},
#             contract={self.contract})"""


class Quote(Base):
    __tablename__ = 'quotes'
    __table_args__ = (UniqueConstraint('contract_id', 'date'),)

    id = Column(Integer, primary_key=True)
    contract_id = Column(
        Integer,
        ForeignKey('contracts.id', ondelete="CASCADE"))
    date = Column(Date)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)

    contract = relationship(
        "Contract", back_populates="quote")

    def __eq__(self, other):
        return (
            (self.contract == other.contract) and
            (self.date == other.date))

    def __repr__(self):
        return f"""QuotesStatus(
            contract_id={self.contract_id},
            date={self.date},
            open={self.open},
            high={self.high},
            low={self.low},
            close={self.close},
            volume={self.volume},
            contract={self.contract})"""
