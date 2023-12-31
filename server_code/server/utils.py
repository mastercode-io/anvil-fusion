# Server module for utility functions
import anvil.server
import anvil.users
from importlib import import_module
from anvil.tables import app_tables
import anvil.secrets
import uuid
# from openai import OpenAI


@anvil.server.callable
def init_user_session():
    
    user = anvil.users.get_user()
    
    if user is None:
        return None

    user_dict = dict(user)
    anvil.server.session['user_uid'] = user_dict['uid']
    anvil.server.session['user_timezone'] = user_dict['timezone']
    anvil.server.session['user_name'] = (user_dict.get('first_name', '') + ' ' + user_dict.get('last_name', '')).strip()
    anvil.server.session['user_email'] = user_dict['email']
    anvil.server.session['user_permissions'] = user_dict.get('permissions') or {}
    tenant_row = app_tables.tenants.get(uid=user_dict['tenant_uid'])
    tenant_uid = ''
    tenant_name = ''
    if anvil.server.session['user_permissions'].get('super_admin', False):
        tenant_uid = '00000000-0000-0000-0000-000000000000'
        tenant_name = 'Super Admin'
        anvil.server.session['tenant_uid'] = '00000000-0000-0000-0000-000000000000'
        anvil.server.session['tenant_name'] = 'Super Admin'
    if (not anvil.server.session['user_permissions'].get('super_admin', False)
            or anvil.server.session['user_permissions'].get('locked_tenant', False)):
        tenant_uid = tenant_row['uid']
        tenant_name += f": {tenant_row['name']}" if tenant_name else tenant_row['name']
        tenant_row = app_tables.tenants.get(uid=user_dict['tenant_uid'])
    anvil.server.session['tenant_uid'] = tenant_uid
    anvil.server.session['tenant_name'] = tenant_name
    return get_logged_user()


@anvil.server.callable
def check_session(tag=None):
    print(f'session check {tag}', anvil.server.session)
    

@anvil.server.callable
def get_logged_user():
    logged_user = {
        'tenant_uid': anvil.server.session['tenant_uid'],
        'tenant_name': anvil.server.session['tenant_name'],
        'user_uid': anvil.server.session['user_uid'],
        'user_name': anvil.server.session['user_name'],
        'email': anvil.server.session['user_email'],
        'timezone': anvil.server.session['user_timezone'],
        'permissions': anvil.server.session['user_permissions'],
    }
    return logged_user


@anvil.server.callable
def set_tenant(tenant_uid=None, tenant_name=None):
    user = anvil.users.get_user()
    user_row = app_tables.users.get(uid=user['uid'])
    user_permissions = user['permissions'] or {}
    if tenant_uid is None and tenant_name is None:
        tenant_uid = '00000000-0000-0000-0000-000000000000'
        tenant_name = 'Super Admin'
        anvil.server.session['tenant_uid'] = tenant_uid
        anvil.server.session['tenant_name'] = 'Super Admin'
        user_permissions.pop('locked_tenant', None)
        user_row.update(tenant_uid='00000000-0000-0000-0000-000000000000', permissions=user_permissions)
    else:
        if tenant_uid is None:
            tenant_row = app_tables.tenants.get(name=tenant_name)
        else:
            tenant_row = app_tables.tenants.get(uid=tenant_uid)
        user_permissions['locked_tenant'] = True
        user_row.update(tenant_uid=tenant_row['uid'], permissions=user_permissions)
        tenant_uid = tenant_row['uid']
        tenant_name = 'Super Admin: ' + tenant_row['name']
    anvil.server.session['tenant_uid'] = tenant_uid
    anvil.server.session['tenant_name'] = tenant_name
    anvil.server.session['user_permissions'] = user_permissions
    return get_logged_user()


@anvil.server.callable
def signup_user(email, password, tenant_uid):
    try:
        user_row = anvil.users.signup_with_email(email, password)
        user_row['tenant_uid'] = tenant_uid
        user_row['uid'] = str(uuid.uuid4())
        # user_row['first_name'] = user_instance['first_name']
        # user_row['last_name'] = user_instance['last_name']
        # user_row['enabled'] = user_instance['enabled']
        return {
            'status': 'success',
            'error': None,
            'uid': user_row['uid'],
        }
    except Exception as e:
        print('error', e)
        return {
            'status': 'error',
            'error': str(e),
            'uid': None,
        }


@anvil.server.callable
def init_model_enumerations(module, model_list):
    models = import_module(module)
    for model, props in model_list.items():
        # print(model, props)
        view_config = {
            'model': props['model'],
            'columns': [{'name': props['name_field']}],
        }
        cls = getattr(models, view_config['model'], None)
        if cls:
            search_queries = props['search_queries'] if 'search_queries' in props else []
            filters = props['filters'] if 'filters' in props else {}
            model_list[model]['options'] = cls.get_grid_view(view_config, search_queries, filters)
            if props['name_field'] != 'name':
                # name_field = props['name_field'].split('.', 1)[0]
                for option in model_list[model]['options']:
                    option['name'] = option[props['name_field'].replace('.', '__')]
    return model_list


@anvil.server.callable
def check_table(table_name=None):
    try:
        table = getattr(app_tables, table_name)
        return table.list_columns()
    except Exception as e:
        return None


@anvil.server.callable
def get_secrets(*secret_names):
    return {secret: anvil.secrets.get_secret(secret) for secret in secret_names}


@anvil.server.callable
def set_cookie(name, value):
    anvil.server.cookies.local[name] = value


@anvil.server.callable
def set_cookies(cookies):
    for name, value in cookies.items():
        anvil.server.cookies.local[name] = value


@anvil.server.callable
def get_cookie(name):
    return anvil.server.cookies.local.get(name, None)


@anvil.server.callable
def get_cookies():
    return anvil.server.cookies.local


# @anvil.server.callable
# def get_openai_client(api_key):
#     return OpenAI(api_key=api_key)

