from dateutil import parser
from datetime import datetime
from enum import Enum

class ERR_TYPE(Enum):
    REQUIER = 1
    TYPE = 2
    NON_EMPTY = 3
    EXCEPT = 4
    RANGE = 5
    LEN_RANGE = 6

def custom_errmsg_format(err_type, item, exception=None):
    return None

def default_errmsg_format(err_type, item, exception=None):
    err_msg = custom_errmsg_format(err_type, item, exception)
    if err_msg is not None:
        return err_msg
    if err_type == ERR_TYPE.REQUIER:
        err_msg = '%s is not in form' % item['desc']
    elif err_type == ERR_TYPE.TYPE:
        err_msg = '%s must be %s' % (item['desc'], item['type'].__name__)
    elif err_type == ERR_TYPE.NON_EMPTY:
        err_msg = '%s can not be empty' % item['desc']
    elif err_type == ERR_TYPE.EXCEPT:
        err_msg = '%s can not be a value of %s' % (item['value'], item['desc'])
    elif err_type == ERR_TYPE.RANGE:
        err_msg = 'value of %s must in range[%s, %s]' % (item['desc'], *item['range'])
    elif err_type == ERR_TYPE.LEN_RANGE:
        err_msg = 'length of value of %s must in range[%s, %s]' % (item['desc'], *item['len_range'])
    return err_msg

def form_validation(form, schema):
    err = _form_validation(form, schema)
    return (400, err) if err else None

def register_custom_errmsg(custom):
    global custom_errmsg_format
    custom_errmsg_format = custom

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
            return default_errmsg_format(ERR_TYPE.REQUIER, item)

        
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
                        return default_errmsg_format(ERR_TYPE.TYPE, item, e)
                else:
                    try: 
                        form[name] = item['value'] = item['type'](form[name])
                    except Exception as e: 
                        return default_errmsg_format(ERR_TYPE.TYPE, item, e)

        ## check non_empty
        if 'non_empty' in item and item['non_empty']:
            if form[name] == item['type']() or form[name] is None:
                return default_errmsg_format(ERR_TYPE.NON_EMPTY, item)

        ### check except
        if 'except' in item:
            if form[name] in item['except']:
                return default_errmsg_format(ERR_TYPE.EXCEPT, item)
        
        ### check range
        if 'range' in item:
            if not (item['range'][0] <= form[name] <= item['range'][1]):
                return default_errmsg_format(ERR_TYPE.RANGE, item)

        ### check len_range
        if 'len_range' in item:
            if not (item['len_range'][0] <= len(form[name]) <= item['len_range'][1]):
                return default_errmsg_format(ERR_TYPE.LEN_RANGE, item)

        ### check check_dict
        if 'check_dict' in item:
            err = form_validation(form[name], item['check_dict'])
            if err: return err

    return None

