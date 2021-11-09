import pymysql
from backend.variableDB import user,password,host,database

db = cursor = None


class Ref_User:
    def openDB(self):
        global db, cursor
        db = pymysql.connect(
                host=host,
                user=user,
                password=password,
                database='dsc-voting-db',
                ssl={"fake_flag_to_enable_tls":True}
            )
        cursor = db.cursor()

    def closeDB(self):
        global db 
        db.close()

    def Select(self, db, name):
        self.openDB()
        cursor.execute(f"SELECT access_token from {db} where access_token='{name}'")
        fetch = cursor.fetchone()
        self.closeDB()
        return fetch
    
    def SelectNama(self, db, name):
        self.openDB()
        cursor.execute(f"SELECT nama from {db} where access_token='{name}'")
        fetch = cursor.fetchone()
        self.closeDB()
        return fetch

    def selectAll(self, name):
        db = pymysql.connect(
                host=host,
                user=user,
                password=password,
                database='dsc-voting-db',
                ssl={"fake_flag_to_enable_tls":True}
            )
        cursor = db.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f"SELECT * FROM 'dsc-voting-db'.`{name}`")
        fetch = cursor.fetchall()
        # del fetch[0]['index']
        return fetch

    def selectQuery(self, id):
        db = pymysql.connect(
                host=host,
                user=user,
                password=password,
                database='dsc-voting-db',
                ssl={"fake_flag_to_enable_tls":True}
            )
        cursor = db.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f"SELECT ki.id, ki.foto, ki.nama, ki.visi_misi, ki.no_kandidat, ki.fakultas, k.nm_pemilihan, k.jadwal FROM kandidat_identity ki, kandidat k where ki.id_kandidat=k.id AND k.id_organisasi='{id}'")
        fetch = cursor.fetchall()
        return fetch

    def sendEmail(self, nm_organisasi):
        db = pymysql.connect(
                host=host,
                user=user,
                password=password,
                database='dsc-voting-db',
                ssl={"fake_flag_to_enable_tls":True}
            )
        cursor = db.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f"SELECT * FROM `dsc-voting-db`.{nm_organisasi}")
        fetch = cursor.fetchall()
        return fetch

    def kandidat_identity_table(self, id):
        db = pymysql.connect(
                host=host,
                user=user,
                password=password,
                database='dsc-voting-db',
                ssl={"fake_flag_to_enable_tls":True}
            )
        cursor = db.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f"SELECT * from kandidat_identity ki, kandidat k where ki.id_kandidat=k.id and ki.id_kandidat={id}")
        fetch = cursor.fetchall()
        return fetch
    
    def votingQuery(self,kandidat, id, event):
        db = pymysql.connect(
                host=host,
                user=user,
                password=password,
                database='dsc-voting-db',
                ssl={"fake_flag_to_enable_tls":True}
            )
        cursor = db.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f"SELECT v.access_token from kandidat k, kandidat_identity ki, voting v where k.id=ki.id_kandidat and v.id_choice=ki.id and ki.no_kandidat='{kandidat}' and k.id_organisasi='{id}' and k.id={event}")
        fetch = cursor.fetchone()
        return fetch

    def deleteThreeTable(self, id1, id2):
        db = pymysql.connect(
                host=host,
                user=user,
                password=password,
                database='dsc-voting-db',
                ssl={"fake_flag_to_enable_tls":True}
            )
        cursor = db.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f"delete from kandidat where id_organisasi='{id1}'")
        cursor.execute(f"delete from kandidat_identity where id='{id2}'")
        cursor.execute(f"delete from voting where id_choice='{id2}'")
        db.commit()

    def dropDB(self, nm_organisasi):
        db = pymysql.connect(
                host=host,
                user=user,
                password=password,
                database='dsc-voting-db',
                ssl={"fake_flag_to_enable_tls":True}
            )
        cursor.execute(f"DROP TABLE `dsc-voting-db`.{nm_organisasi}")
        db.commit()   

    def votingField(self, id):
        db = pymysql.connect(
                host=host,
                user=user,
                password=password,
                database='dsc-voting-db',
                ssl={"fake_flag_to_enable_tls":True}
            )
        cursor = db.cursor(pymysql.cursors.DictCursor)
        # cursor.execute(f"select count(v.access_token) as total, ki.nama as nama_kandidat, k.nm_pemilihan as event from voting v, kandidat_identity ki, kandidat k where v.id_choice=ki.id and k.id_organisasi={id} and k.id=ki.id_kandidat group by ki.nama")
        cursor.execute(f"""
            select
                k.nm_pemilihan AS kegiatan,
                ki.nama AS calon,
                cte.total_suara as total_suara
            from
	            `dsc-voting-db`.kandidat_identity AS ki
                join `dsc-voting-db`.kandidat as k on (ki.id_kandidat=k.id)
                join `dsc-voting-db`.organisasi as org on (k.id_organisasi=org.id)
                join 
                (
                    select 
                        distinct (id_choice) as id_calon,
                        count(id_choice) as total_suara
                    from
                        `dsc-voting-db`.voting
                    group by id_calon
                    ) as cte
                on (cte.id_calon=ki.id and k.id_organisasi={id})
        """) 
        fetch = cursor.fetchall()
        return fetch


