from dateutil import parser
from datetime import datetime


global ERR_FORMAT
ERR_FORMAT = {}
ERR_FORMAT['REQUIRE'] = '{desc} not in form'
ERR_FORMAT['TYPE'] = '{desc}: {exception}'
ERR_FORMAT['NON_EMPTY'] = '{desc} cannot be empty'
ERR_FORMAT['EXCEPT'] = '{desc} cannot be one of {except}'
ERR_FORMAT['RANGE'] = '{desc} must in range {range}'
ERR_FORMAT['LEN_RANGE'] = 'length of {desc} must in range {len_range}'


def form_validation(form, schema):
    err = _form_validation(form, schema)
    return (400, err) if err else None

def register_err_format(err_format):
    ERR_FORMAT.update(err_format)

def _form_validation(form, schema):
    '''
    schema:
        [{
            # require
            'name': <str> # +<str> means require, default is optional
            # optional
            'desc': <str>
            'type': <class>
            'non_empty': <bool> # for str, list
            'except': <list>
            'range': <tuple> # t[0] <= value <= t[1]
            'len_range': <tuple> # t[0] <= len(value) <= t[1]
            'check_dict': <dict> # for dict
            ...
        }]
    int
    str
    list
    set
    dict
    datetime
    '''
    key = list(form.keys())
    for item in key:
        exist = False
        for x in schema:
            if x['name'] == item or (x['name'][0] == '+' and x['name'][1:] == item):
                exist = True
        if not exist:
            del form[item]


    for item in schema:
        require = True if item['name'][0] == '+' else False
        name = item['name'] = item['name'][1:] if require else item['name']
        desc = item['desc'] = item.get('desc') or name

        # check require
        if require and (name not in form or form[name] is None):
            return ERR_FORMAT['REQUIRE'].format(**item)

        
        if not require and (name not in form or form[name] is None):
            form[name] = None
            continue

        item['value'] = form[name]

        ### check value type
        if 'type' in item:
            if not isinstance(form[name], item['type']):
                if item['type'] == datetime:
                    try: 
                        form[name] = item['value'] = parser.parse(form[name])
                    except Exception as e: 
                        item['exception'] = e
                        return ERR_FORMAT['TYPE'].format(**item)
                else:
                    try: 
                        form[name] = item['value'] = item['type'](form[name])
                    except Exception as e: 
                        item['exception'] = e
                        return ERR_FORMAT['TYPE'].format(**item)

        ## check non_empty
        if 'non_empty' in item and item['non_empty']:
            if form[name] == item['type']() or form[name] is None:
                return ERR_FORMAT['NON_EMPTY'].format(**item)

        ### check except
        if 'except' in item:
            if form[name] in item['except']:
                return ERR_FORMAT['EXCEPT'].format(**item)
        
        ### check range
        if 'range' in item:
            if not (item['range'][0] <= form[name] <= item['range'][1]):
                return ERR_FORMAT['RANGE'].format(**item)

        ### check len_range
        if 'len_range' in item:
            if not (item['len_range'][0] <= len(form[name]) <= item['len_range'][1]):
                return ERR_FORMAT['LEN_RANGE'].format(**item)

        ### check check_dict
        if 'check_dict' in item:
            err = form_validation(form[name], item['check_dict'])
            if err: return err

    return None
