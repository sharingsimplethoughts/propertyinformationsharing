import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
cred = credentials.Certificate("my-project-firebase.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://PropInfoShare-ios-hi.firebaseio.com'
})


def createNode(first_name, last_name, id, profile_image):
    firebase_admin.get_app()
    root = db.reference('Users')
    new_user = root.child('user_'+str(id)).set({
        'id':id,
        'name': first_name+' ' +last_name,
        'profile_image': profile_image
    })


def updateNode(first_name, last_name, id, profile_image):
    firebase_admin.get_app()
    root = db.reference('Users')
    new_user = root.child('user_'+str(id)).update({

        'name': first_name+' ' +last_name,
        'profile_image':profile_image
    })


def deleteNode(id):
    firebase_admin.get_app()
    root = db.reference('Users')
    new_user = root.child('user_'+str(id)).delete()