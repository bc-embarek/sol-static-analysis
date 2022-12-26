# -*- coding:utf-8 -*-
import os

from sqlalchemy import Column, Integer, String, Boolean, create_engine, Index, TIMESTAMP
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import declarative_base, Session

from common.config import GlobalConfig
from common.decorator import format_address
from common.enums import Networks

Base = declarative_base()


class Contract(Base):
    __tablename__ = "contract"
    id = Column(Integer, primary_key=True)
    network = Column(String)
    address = Column(String, index=True)

    is_proxy = Column(Boolean)
    proxy_address = Column(String)
    has_source_code = Column(Boolean)
    compile_success = Column(Boolean)
    last_check_time = Column(TIMESTAMP)

    def __str__(self):
        return f'{self.network}({self.address})'


Index('unique_idx_contract_network_address', Contract.network, Contract.address)


def init_database(global_config: GlobalConfig):
    # Sqlite
    engine = create_engine(f'sqlite:///{os.path.join(global_config.storage_path, "cache.db")}')
    Base.metadata.create_all(engine)
    return engine


@format_address
def get_or_add_contract(session: Session, network: Networks, contract_address: str):
    try:
        return session.query(Contract) \
            .filter(Contract.network == network.value, Contract.address == contract_address).one()
    except NoResultFound:
        contract = Contract(network=network.value, address=contract_address)
        session.add(contract)
        return contract


def get_all_new_contracts(session: Session, network: Networks):
    try:
        return session.query(Contract) \
            .filter(Contract.network == network.value, Contract.has_source_code == None,
                    Contract.is_proxy == None).order_by(Contract.id.desc()).all()
    except NoResultFound:
        return []


def get_all_compiled_contracts(session: Session, network: Networks):
    try:
        return session.query(Contract) \
            .filter(Contract.network == network.value, Contract.has_source_code == True,
                    Contract.compile_success == True).order_by(Contract.id.desc()).all()
    except NoResultFound:
        return []
