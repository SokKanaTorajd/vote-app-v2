from backend.config import db
from sqlalchemy import ForeignKey
from datetime import *
from sqlalchemy.dialects.mysql import MEDIUMBLOB

class Organisasi(db.Model):
        id = db.Column(db.BigInteger, primary_key = True, autoincrement=True)
        nm_organisasi = db.Column(db.String(200), unique=True, nullable=False)
        password = db.Column(db.String(100), nullable=False)
        fakultas = db.Column(db.String(100), nullable=False)
        foreign_access = db.relationship('Kandidat', backref='organisasi', cascade='all, delete', lazy='select')

class Kandidat(db.Model):
        id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
        id_organisasi = db.Column(db.BigInteger, db.ForeignKey('organisasi.id', ondelete='CASCADE'))
        nm_pemilihan = db.Column(db.String(100), nullable=False)
        jumlah_kandidat = db.Column(db.Integer, nullable=False)
        jadwal = db.Column(db.Date, default=datetime.today())
        foreign_access = db.relationship('Kandidat_identity', backref='kandidat_identity', cascade='all, delete', lazy='select')


class Kandidat_identity(db.Model): 
        id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
        id_kandidat = db.Column(db.BigInteger, db.ForeignKey('kandidat.id', ondelete='CASCADE'))
        foto = db.Column(MEDIUMBLOB, nullable=False)
        nama = db.Column(db.String(100), nullable=False)
        visi_misi = db.Column(db.String(255), nullable=False)
        fakultas = db.Column(db.String(255), nullable=False)
        no_kandidat = db.Column(db.Integer, nullable=False)
        foreign_access = db.relationship('Voting', backref='your_choice', cascade='all, delete', lazy='select')

class Voting(db.Model):
        id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
        id_choice = db.Column(db.BigInteger, db.ForeignKey('kandidat_identity.id', ondelete='CASCADE'))
        access_token = db.Column(db.String(255), nullable=False)

