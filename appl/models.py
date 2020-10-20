from datetime import datetime

import numpy as np
from sqlalchemy import Column, Integer, String, Float, DateTime
from tabula import read_pdf
import pandas as pd

from .views import db


class Parcel(db.Model):
    __tablename__ = "parcel"

    id = Column(Integer, primary_key=True)
    parcel_id = Column(String(30), nullable=False, unique=True)
    address = Column(String(400), nullable=False)
    latitude = Column(Float(precision=64), nullable=False)
    longitude = Column(Float(precision=64), nullable=False)
    date_created = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "<Parcel(id='%s', parcel_id='%s', address='%s', latitude='%s', latitude='%s')>" % (
            self.id, self.parcel_id, self.address, self.latitude, self.longitude)


class PropertyRecord:
    def __init__(self, type, attorney, plantiff, sheriffId, defendant, address, parcel, status, principal):
        self.type = type
        self.attorney = attorney
        self.plantiff = plantiff
        self.sheriffId = sheriffId
        self.defendant = defendant
        self.address = address
        self.parcel = parcel
        self.status = status
        self.principal = principal

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}> (type:{self.type}, attorney:{self.attorney}, attorney:{self.attorney}, ' \
               f'plantiff:{self.plantiff}, sheriffId:{self.sheriffId}, defendant:{self.defendant}, ' \
               f'address:{self.address}, parcel:{self.parcel}, status:{self.status}, principal:{self.principal}) '


def timestamp():
    epoch = datetime.utcfromtimestamp(0)
    now = datetime.now()
    delta = now - epoch
    return delta.total_seconds()


def date():
    return datetime.now().strftime('%Y-%m-%d')


def process_data(pdf_path):
    dfs = read_pdf(pdf_path, pages="all", pandas_options={'header': None})
    foreclosures = []
    columns = ['type', 'attorney', 'plantiff', 'sheriffId', 'defendant', 'address', 'parcel', 'status', 'principal']
    replacements = {
        'type': {r'(TYPE|TYPE\r)': ''},
        'attorney': {r'(ATTORNEY|ATTORNEY\r)': ''},
        'plantiff': {r'(PLAINTIFF)': ''},
        'sheriffId': {r'(SHERIFF #|SHERIFF #\r)': ''},
        'defendant': {r'(DEFENDANT)': ''},
        'address': {r'(ADDRESS|ADDRESS\r)': ''},
        'parcel': {r'(PARCEL)': ''},
        'status': {r'(STATUS|STATUS\r)': ''},
        'principal': {r'(PRINCIPAL)': ''},
    }
    for df in dfs:
        if len(df) > 1:
            df.columns = columns
            df.replace(replacements, regex=True, inplace=True)
            df = df.replace('\r', ' ', regex=True)
            df.replace('', np.nan, inplace=True)
            df = df.apply(lambda x: x.str.strip())
            df = df.dropna()
            df['principal'] = df['principal'].str.replace('[\$,]', '', regex=True)
            df['principal'] = pd.to_numeric(df['principal'], errors='coerce')
        foreclosures.extend([PropertyRecord(**args) for args in df.to_dict(orient='records')])

    return foreclosures
