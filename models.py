import os

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from settings import CONFIG


Base = automap_base()


# engine = create_engine(f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
#                        f"@"
#                        f"127.0.0.1:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}")

# print(f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
#                        f"@"
#                        f"{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}")

engine = create_engine(f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
                       f"@"
                       f"{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}")


# engine = create_engine(f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
#                        f"@"
#                        f"{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}")
#

Base.prepare(engine, reflect=True)
print("prepared")


UserSiteBalance = Base.classes.profile_usersitebalance

ETHContract = Base.classes.contracts_ethcontract
Contract = Base.classes.contracts_contract
Network = Base.classes.deploy_network
print("classes are setted")

details_names = ['contractdetailsxinfintoken', 'contractdetailstoken', 'contractdetailsmatictoken',
                 'contractdetailshecochaintoken', 'contractdetailsbinancetoken']
tokens_details = [getattr(Base.classes, 'contracts_' + details) for details in details_names]

session = Session(engine)
print("session created")

