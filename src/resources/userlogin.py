from models.user import UserModel
from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity
)
from werkzeug.security import safe_str_cmp

class UserLogin(Resource):
    # defining the request parser and expected arguments in the request
    parser = reqparse.RequestParser()
    parser.add_argument('username',
                        type=str,
                        required=True,
                        help="This field cannot be blank."
                        )
    parser.add_argument('password',
                        type=str,
                        required=True,
                        help="This field cannot be blank."
                        )

    def post(self):
        data = self.parser.parse_args()
        # read from database to find the user and then check the password
        user = UserModel.find_by_username(data['username'])

        if user and safe_str_cmp(user[0].password, data['password']):
            # when authenticated, return a fresh access token and a refresh token
            access_token = create_access_token(identity=user[0].id, fresh=True)
            refresh_token = create_refresh_token(user[0].id)
            return {
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 200

        return {"message": "Invalid Credentials!"}, 401


class TokenRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        # retrive the user's identity from the refresh token using a Flask-JWT-Extended built-in method
        current_user = get_jwt_identity()
        # return a non-fresh token for the user
        new_token = create_access_token(identity=current_user, fresh=False)
        return {'access_token': new_token}, 200

