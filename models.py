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

details_names = ['contractdetailsxinfintoken', 'contractdetailstoken', 'contractdetailsmatictoken',
                 'contractdetailshecochaintoken', 'contractdetailsbinancetoken']
tokens_details = [getattr(Base.classes, 'contracts_' + details) for details in details_names]

session = Session(engine)
