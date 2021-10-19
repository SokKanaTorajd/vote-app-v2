from backend.config import app, api, db
from backend.apiHandle import (OrganisasiRegist, OrganisasiSigin, InputFile, 
                               UserSignin, CandidateName, CandidateIdentity,
                               SentMail, FieldVoting, fieldVisual)

api.add_resource(OrganisasiRegist, '/daftar', endpoint= 'regisOr')
api.add_resource(OrganisasiSigin, '/login', endpoint='loginOr')
api.add_resource(InputFile, '/inputFile/<nm_organisasi>', endpoint='fileMHS')
api.add_resource(UserSignin, '/userSignin', endpoint='user')
api.add_resource(CandidateName, '/candidate/<id>', endpoint='candidates')
api.add_resource(CandidateIdentity, '/identity/<id>', endpoint='identity')
api.add_resource(InputFile, '/getting/<nm_organisasi>', endpoint='usr')
api.add_resource(FieldVoting, '/vote/<nama>', endpoint='vote')
api.add_resource(SentMail, '/mail/<nm_organisasi>', endpoint='mail')
api.add_resource(FieldVoting, '/voting/<access_token>/<id>', endpoint='choice')
api.add_resource(fieldVisual, '/visual/<id>', endpoint='visual')

@app.route('/')
def index():
    return 'API oke!'

if __name__ == '__main__':
    app.run(debug=True)
    
    db.create_all()