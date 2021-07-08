from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from settings import CONFIG

Base = automap_base()
engine = create_engine(CONFIG['db']['url'])
Base.prepare(engine, reflect=True)

UserSiteBalance = Base.classes.profile_usersitebalance

ETHContract = Base.classes.contracts_ethcontract
Contract = Base.classes.contracts_contract
Network = Base.classes.deploy_network

tokens = {'xin': 'contractdetailsxinfintoken', 'eth': 'contractdetailstoken', 'polygon': 'contractdetailsmatictoken',
          'heco': 'contractdetailshecochaintoken', 'binance': 'contractdetailsbinancetoken'}
tokens_details = {token: getattr(Base.classes, 'contracts_' + details) for token, details in tokens}

session = Session(engine)
