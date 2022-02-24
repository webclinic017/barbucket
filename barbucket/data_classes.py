from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class Contract(Base):
    __tablename__ = 'contracts'

    id = Column(Integer, primary_key=True)
    contract_type_from_listing = Column(String(30))
    exchange_symbol = Column(String(30))
    broker_sybmol = Column(String(30))
    name = Column(String(100))
    currency = Column(String(30))
    exchange = Column(String(30))

    UniqueConstraint('broker_sybmol', 'currency', 'exchange')

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
    quotes_status = relationship(
        "QuotesStatus",
        back_populates="contract",
        cascade="all, delete",
        passive_deletes=True)
    quote = relationship(
        "Quote",
        back_populates="contract",
        cascade="all, delete",
        passive_deletes=True)

    def __repr__(self):
        return f"""Contract(
            id={self.id},
            contract_type_from_listing={self.contract_type_from_listing},
            exchange_symbol={self.exchange_symbol},
            broker_sybmol={self.broker_sybmol},
            name={self.name},
            currency={self.currency},
            exchange={self.exchange})"""


class UniverseMembership(Base):
    __tablename__ = 'universe_memberships'

    id = Column(Integer, primary_key=True)
    contract_id = Column(
        Integer,
        ForeignKey('contracts.id', ondelete="CASCADE"))
    universe = Column(String(100))

    UniqueConstraint('contract_id', 'universe')

    contract = relationship(
        "Contract", back_populates="universe_memberships")

    def __repr__(self):
        return f"""UniverseMembership(
            id={self.id},
            contract_id={self.contract_id},
            universe={self.universe})"""


class ContractDetailsIb(Base):
    __tablename__ = 'contract_details_ib'

    contract_id = Column(
        Integer,
        ForeignKey('contracts.id', ondelete="CASCADE"),
        primary_key=True)
    contract_type_from_details = Column(String(30))
    primary_exchange = Column(String(30))
    industry = Column(String(30))
    category = Column(String(30))
    subcategory = Column(String(30))

    contract = relationship(
        "Contract", back_populates="contract_details_ib")

    def __repr__(self):
        return f"""ContractDetailsIb(
            contract_id={self.contract_id},
            contract_type_from_details={self.contract_type_from_details},
            primary_exchange={self.primary_exchange},
            industry={self.industry},
            category={self.category},
            subcategory={self.subcategory})"""


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
            revenue={self.revenue})"""


class QuotesStatus(Base):
    __tablename__ = 'quotes_status'

    contract_id = Column(
        Integer,
        ForeignKey('contracts.id', ondelete="CASCADE"),
        primary_key=True)
    status_code = Column(Integer)
    status_text = Column(String(255))
    latest_quote_requested = Column(Date)
    earliest_quote_requested = Column(Date)

    contract = relationship(
        "Contract", back_populates="quotes_status")

    def __repr__(self):
        return f"""QuotesStatus(
            contract_id={self.contract_id},
            status_code={self.status_code},
            status_text={self.status_text},
            latest_quote_requested={self.latest_quote_requested},
            earliest_quote_requested={self.earliest_quote_requested})"""


class Quote(Base):
    __tablename__ = 'quotes'

    contract_id = Column(
        Integer,
        ForeignKey('contracts.id', ondelete="CASCADE"))
    date = Column(Date)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)

    UniqueConstraint('contract_id', 'date')

    contract = relationship(
        "Contract", back_populates="quote")

    def __repr__(self):
        return f"""QuotesStatus(
            contract_id={self.contract_id},
            date={self.date},
            open={self.open},
            high={self.high},
            low={self.low},
            close={self.close},
            volume={self.volume})"""
