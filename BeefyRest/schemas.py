from ninja import Schema


class LoginBody(Schema):
    email: str = 'admin'
    password: str = 'mimin123'

class RefreshBody(Schema):
    token_refresh: str = 'token'

class Validbody(Schema):
    token: str = 'token'

class ForgotPasswordBody(Schema):
    email: str
    new_password: str