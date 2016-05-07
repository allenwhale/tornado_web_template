from include import include
class Api:
    pass
include(Api, "./api/")
urls = [
    ('/api/simple/', Api.ApiSimpleHandler),
]
