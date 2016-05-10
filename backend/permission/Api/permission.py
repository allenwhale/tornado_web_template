class Permission:
    def get(req):
        args = ['token']
        meta = req.get_args(args)
        if meta['token'] != 'token':
            return (403, 'Permission Denied')
        return None
