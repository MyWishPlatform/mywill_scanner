from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from settings import CONFIG

Base = automap_base()
engine = create_engine(CONFIG['db']['url'])
Base.prepare(engine, reflect=True)

DepositModel = Base.classes.deposits_deposit
# Transfers = Base.classes.transfers_ducatustransfer

session = Session(engine)
