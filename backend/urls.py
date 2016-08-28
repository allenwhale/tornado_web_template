from utils.include import include
class Handler:
    pass
include(Handler, "./handler/")
urls = [
    # ('/api/users/signup/', Handler.api.UserSignUp),
    # ('/api/users/signin/', Handler.api.UserSignIn),
    # ('/api/users/signout/', Handler.api.UserSignOut),
    #('/api/users/me/', Handler.api.UsersMe),
    #('/api/users/(\d+)/', Handler.api.User),
    ('/', Handler.web.index.Index),
    #('/users/signin/', Handler.web.SignIn),
    #('/users/signup/', Handler.web.SignUp),
    #('/users/', Handler.web.Users),
    #('/users/(\d+)/', Handler.web.User),
    ('/assets/(.*)', Handler.web.asset.Asset, {'path': './../http'}),
    ('/(.*)', Handler.web.notfound.NotFound),
]
