from backend.query import Ref_User
from flask_jwt_extended import (create_access_token, create_refresh_token)
from flask_restful import Resource, reqparse
from passlib.hash import sha256_crypt
import pandas as pd
import os, sys
import uuid, base64
import requests
import mysql.connector as sql
from datetime import *
from pandas import ExcelFile
from flask import jsonify
from backend.config import db, mail
from backend.models import Organisasi, Kandidat, Kandidat_identity, Voting
from sqlalchemy import create_engine
from backend.variableDB import user, host, database, password
from flask_mail import Message
from werkzeug.utils import secure_filename

var_dict = {}

class OrganisasiRegist(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('nm_organisasi', type=str, help="You must completed organization's name")
        self.parser.add_argument('password', type=str, help="You must completed password")
        self.parser.add_argument('fakultas', type=str, help="You must completed faculty")
        self.parser.add_argument('access_token', type=str, help="access token is essential for your generate code")
    
    def post(self):
        data = self.parser.parse_args()
        nm_organisasi = data['nm_organisasi']
        password = sha256_crypt.hash(data['password'])
        fakultas = data['fakultas']
        access_token = create_access_token(identity=nm_organisasi)
        cross_check = Organisasi.query.filter_by(nm_organisasi=nm_organisasi).first()
        try:
            if cross_check is not None:
                cross_check.nm_organisasi = nm_organisasi
                cross_check.password = password
                cross_check.fakultas = fakultas
                db.session.add(cross_check)
                db.session.commit()
                return jsonify({'error' : 'Your name available, but data updated'})
            new = Organisasi(nm_organisasi=nm_organisasi, password=password, fakultas=fakultas)
            db.session.add(new)
            db.session.commit()
            return jsonify({
                'access_token': access_token,
                'success' : "Registry successfully"
            })
        except:
            return jsonify({'error': "System can't reading your entry"})

class OrganisasiSigin(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('nm_organisasi', type=str, help="You must completed organization's name")
        self.parser.add_argument('password', type=str, help="You must completed password")
        self.parser.add_argument('access_token', type=str, help="access token is essential for your generate code")

    def post(self):
        data = self.parser.parse_args()
        nm_organisasi = data['nm_organisasi']
        password = data['password']
        access_token = create_access_token(identity=nm_organisasi)
        cross_check = Organisasi.query.filter_by(nm_organisasi=nm_organisasi).first()
        try:
            if sha256_crypt.verify(password, cross_check.password):
                return jsonify({
                    'id_organisasi': cross_check.id,
                    'success': "OK",
                    'nm_organisasi' : nm_organisasi,
                    'password' : password,
                    'access_token' : access_token,
                    })
            else:
                return jsonify({'error' : "You're not register yet"})
        except:
            return jsonify({"error": "Have you registered?"})


class CandidateName(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('nm_pemilihan', help='Entry name of voting event')
        self.parser.add_argument('jumlah_kandidat', help='how many participant')
        self.parser.add_argument('id', help='Otomatis')

    def post(self, id):
        data = self.parser.parse_args()
        nm_pemilihan = data['nm_pemilihan']
        jumlah_kandidat = data['jumlah_kandidat']
        if nm_pemilihan == '':
            return jsonify({
                'error' : 'Please entry something'
            })
        try:
            organisasi_table = Organisasi.query.filter_by(id=id).first()
            k_table = Kandidat.query.filter_by(id_organisasi=organisasi_table.id).first()


            if k_table is not None:
                k_table.nm_pemilihan =nm_pemilihan
                k_table.jumlah_kandidat = jumlah_kandidat
                db.session.add(k_table)
                db.session.commit()
                return jsonify({
                    'id_kandidat': k_table.id,
                    'success': 'Data event has been updated',
                })
            
            query = Kandidat(nm_pemilihan=nm_pemilihan, organisasi=organisasi_table, jumlah_kandidat=jumlah_kandidat)
            db.session.add(query)
            db.session.commit()

            queries = Kandidat.query.filter_by(id_organisasi=organisasi_table.id).first()
            return jsonify({
                'id_kandidat': queries.id,
                'nm_pemilihan' : nm_pemilihan,
                'jadwal': str(queries.jadwal),
                'success': 'Your entry has saved in database, please entry identity of candidate in thereunder'
            })

        except:
            return jsonify({
                'error': 'OK'
            })

class SentMail(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
    
    def post(self, nm_organisasi):
        try:
            data = Ref_User()
            email_sistem = data.sendEmail(nm_organisasi)
            
            for i in range(len(email_sistem)):
                mails = email_sistem[i]['Email']
                names = email_sistem[i]['Nama']
                tokens = email_sistem[i]['access_token']
                # msg = Message(
                #         'VoteApps Team',
                #         sender ='akhmadfaizal13@gmail.com',
                #         recipients = [mails]
                #     )
                # msg.body = f"Hello {names} \nNow you have access to our system\nOrganization Name: {nm_organisasi}\nToken: {tokens}"
                # mail.send(msg)
                requests.post(
		            "https://api.mailgun.net/v3/dsc-app.tech/messages",
		            auth=("api", "6422881fa3233a254b201534bef4e65a-10eedde5-3b7c5fcd"),
                        data={"from": "management@dsc-app.tech",
                            "to": [mails],
                            "subject": "VotingApps Team",
                            "text": f"Dear {names}, \nNow you have access to our system, let voting your leader in https://voteapp-v2.herokuapp.com/ \nOrganization : {nm_organisasi} \nToken : {tokens}"
                        }
                    )
            return jsonify({
                'success': 'Email has sending'
            })
        except:
            return jsonify({
                    'error':"System can't response"
                })


class InputFile(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('url', type=str, help='This form so essential')
        self.parser.add_argument('type', type=str, help='This form so essential')
        self.parser.add_argument('nm_organisasi', type=str, help='Completed Your access token')

    def post(self, nm_organisasi):
        data = self.parser.parse_args()
        file = data['url']
        typeFile = data['type']
        organisasi = Organisasi.query.filter_by(nm_organisasi=nm_organisasi).first()
        try:
            engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}/{database}")
            if typeFile == 'excel':
                path = 'https://drive.google.com/uc?export=download&id='+file.split('/')[-2]
                df = pd.read_excel(path)
                df['access_token'] = df['Nama'].apply(lambda _: str(uuid.uuid4()))
                df.to_sql(organisasi.nm_organisasi,con=engine, if_exists='replace') 
                return jsonify({
                    'file': 'File success convert'
                })
            elif typeFile == 'csv':
                path = 'https://drive.google.com/uc?export=download&id='+file.split('/')[-2]
                df = pd.read_csv(path)
                df['access_token'] = df['Nama'].apply(lambda _: str(uuid.uuid4()))
                df.to_sql(organisasi.nm_organisasi,con=engine, if_exists='replace')
                return jsonify({
                    'file': 'File success convert'
                })
        except:
            return jsonify({'error' : "Please check type file csv or excel"})

    def get(self, nm_organisasi):
        model_table = Ref_User()
        try:    
            y = model_table.selectAll(nm_organisasi) 
        # if y:
        #     return jsonify({
        #         'user': y,
        #     }) 
            o_table = Organisasi.query.filter_by(nm_organisasi=nm_organisasi).first()
            k_table = Kandidat.query.filter_by(id_organisasi=o_table.id).first()
            ki_table = Kandidat_identity.query.filter_by(id_kandidat=k_table.id).first()
            yx = model_table.selectQuery(o_table.id)
            for i in range(len(yx)):
                x = str(yx[i]['jadwal'])
                split_1 = x.split('-')
                convert_1 = datetime(int(split_1[0]), int(split_1[1]), int(split_1[2]))

                #jeda
                jeda = str(convert_1.date() + timedelta(days=6))
                split_2 = jeda.split('-')
                convert_2 = datetime(int(split_2[0]), int(split_2[1]), int(split_2[2]))
                
                #selisih
                now = str(datetime.date(datetime.now()))
                split_3 = now.split('-')
                convert_3 = datetime(int(split_3[0]), int(split_3[1]), int(split_3[2]))
                
                yz = convert_2.date() - convert_3.date()
                if now!=jeda or int(yz.days) != 0:
                    return jsonify({
                        'user': y
                    })
                elif now==jeda or int(yz.days) == 0:
                    xdb = Ref_User()
                    xdb.deleteThreeTable(o_table.id, ki_table.id)
                    xdb.dropDB(nm_organisasi)
                    return jsonify({
                        'error': 'Data has reached the time limit'
                    })   
        except:
            return jsonify({
                'error' : 'Your table unknown'
            })
    
class CandidateIdentity(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('id_kandidat', help='System authomatically entry with session')
        self.parser.add_argument('nama', help='Please entry name of candidate')
        self.parser.add_argument('foto', help='Please entry foto of candidate')
        self.parser.add_argument('visi_misi', help='Please entry it')
        self.parser.add_argument('no_kandidat', help='Please entry number of candidate')
        self.parser.add_argument('fakultas', help='Please entry faculty of candidate')

    def find_file(self, basedir, filename):
        for dirname, dirs, files in os.walk(basedir):
            if filename in files:
                yield(os.path.join(dirname, filename))

    def post(self, id):
        data = self.parser.parse_args()
        nama = data['nama']
        foto = data['foto'].encode()
        visi_misi = data['visi_misi']
        no_kandidat = data['no_kandidat']
        fakultas = data['fakultas']
        try:
            k_table = Kandidat.query.filter_by(id=id).first()
            data = Ref_User()
            target = data.kandidat_identity_table(id)

            ki_table = Kandidat_identity.query.filter_by(no_kandidat=no_kandidat).filter_by(id_kandidat=id).first()
            if ki_table is not None:
                ki_table.foto = foto 
                ki_table.nama = nama 
                ki_table.visi_misi = visi_misi
                ki_table.fakultas = fakultas
                ki_table.no_kandidat = no_kandidat
                db.session.add(ki_table)
                db.session.commit()
                return jsonify({
                    'error': 'Data candidate has been updated'
                })

            if k_table.jumlah_kandidat == len(target):
                return jsonify({
                    'error': 'Data reaches the limit according to your event input'
                })

            query_add = Kandidat_identity(kandidat_identity=k_table, foto=foto, nama=nama, visi_misi=visi_misi, no_kandidat=no_kandidat, fakultas=fakultas)
            db.session.add(query_add)
            db.session.commit()

            return jsonify({
                'success': f'Candidate {nama} has saved in database',
            })
        except:
            return jsonify({'error' : 'System fail detect'})


class UserSignin(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('access_token', help="Please don't forget to input your token here")
        self.parser.add_argument('nm_organisasi', help="Input your organization")

    def post(self):
        data = self.parser.parse_args()
        access_token = data['access_token']
        organisasi = data['nm_organisasi']
        organisasi_table = Organisasi.query.filter_by(nm_organisasi=organisasi).first()
        db_target = Ref_User()
        try:
            nama_privasi = db_target.SelectNama(organisasi_table.nm_organisasi, access_token)
            x = db_target.Select(organisasi_table.nm_organisasi, access_token)
            k_table = Kandidat.query.filter_by(id_organisasi=organisasi_table.id).first()
            if k_table is None:
                return jsonify({
                    'error': "Admin hasn't uploaded candidate data"
                })
            if x: 
                return jsonify({
                    'id_organisasi': organisasi_table.id,
                    'nm_organisasi' : organisasi,
                    'access_token' : access_token,
                    'nama' : nama_privasi,
                    'success' : "Ok, your identity has ben our detected"
                })
            else:
                return jsonify({'error' : "Are you sure?"})
        except: 
            return jsonify({'error' : "Voting time is over"})

class FieldVoting(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('no_choice', help='Entry choice for completed data')

    def post(self, access_token, id):
        data = self.parser.parse_args()
        choice = data['no_choice']
        # o_table = Organisasi.query.filter_by(id=id).first()
        k_table =Kandidat.query.filter_by(id_organisasi=id).first()
        table_kandidat = Kandidat_identity.query.filter_by(no_kandidat=int(choice)).filter_by(id_kandidat=k_table.id).first()
        if table_kandidat is None:
            return jsonify({'error': 'Data loose'})
        try:
            voting_table_select = Voting.query.filter_by(access_token=access_token).first()
            if voting_table_select is not None:
                return jsonify({
                    'error': 'You have choosen candidate'
                })
            else:
                voting_table = Voting(your_choice=table_kandidat, access_token=access_token)
                db.session.add(voting_table)
                db.session.commit()
                return jsonify({
                    'success': 'You have successfully selected a candidate'
                })
        except:
            return jsonify({
                'error':'System lost your data'
            })

    def get(self, nama):
        organisasi_table = Organisasi.query.filter_by(nm_organisasi=nama).first()
        db = Ref_User()

        y = db.selectQuery(organisasi_table.id)
        for i in range(len(y)):
            y[i]['jadwal'] = str(y[i]['jadwal'])
            y[i]['foto'] = y[i]['foto'].decode()

        try:
            k_table = Kandidat.query.filter_by(id_organisasi=organisasi_table.id).first()
            ki_table = Kandidat_identity.query.filter_by(id_kandidat=k_table.id).first()
            yx = db.selectQuery(organisasi_table.id)
            for i in range(len(yx)):
                x = str(yx[i]['jadwal'])
                split_1 = x.split('-')
                convert_1 = datetime(int(split_1[0]), int(split_1[1]), int(split_1[2]))

                #jeda
                jeda = str(convert_1.date() + timedelta(days=6))
                split_2 = jeda.split('-')
                convert_2 = datetime(int(split_2[0]), int(split_2[1]), int(split_2[2]))
                
                #selisih
                now = str(datetime.date(datetime.now()))
                split_3 = now.split('-')
                convert_3 = datetime(int(split_3[0]), int(split_3[1]), int(split_3[2]))
                
                yz = convert_2.date() - convert_3.date()
                if now==jeda or int(yz.days) == 0:
                    xdb = Ref_User()
                    xdb.deleteThreeTable(organisasi_table.id, ki_table.id)
                    return jsonify({
                        'error': 'Data has reached the maximum timeout'
                    })
                else:
                    return jsonify({
                        'nm_pemilihan': k_table.nm_pemilihan,
                        'voting': y
                    })
        except: 
            return jsonify({
                'error': 'Data not found'
            })

class fieldVisual(Resource):
    def get(self, id):
        data = Ref_User()
        y = data.votingField(id)
        try:
            if len(y) != 0:
                nama = [y[i]['calon'] for i in range(len(y))]
                total = [y[i]['total_suara'] for i in range(len(y))]
                event = [y[i]['kegiatan'] for i in range(len(y))]
                return jsonify({
                    'nama_kandidat': nama,
                    'total': total,
                    'event': event[0]
                })
            else:
                return jsonify({
                    'error': 'No voting yet'
                })
        except:
            return jsonify({
                'error': 'Error detect, contact your admin now'
            })