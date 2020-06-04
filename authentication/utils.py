import json
import random
import string
import uuid
import requests

from jose import jwt
from django.conf import settings


def random_number_generator(size=120, chars=string.ascii_letters + string.digits):
    """
    For generating random alphanumeric string of a given size

    :param size:
    :param chars:
    :return:
    """
    return ''.join(random.choice(chars) for _ in range(size))


def hex_uuid():
    """
    Returns hex representation of uuid4

    :return:
    """
    return uuid.uuid4().hex


def decode_jwt_token(token):
    """
    Decodes a jwt token

    :param token:
    :return:
    """

    rsa_key = settings.RSA_KEYS

    try:
        decoded_token_body = jwt.decode(token, rsa_key, "RS256", audience="account")
        return decoded_token_body
    except:
        # One of reasons for token decode failure is the because of access token expiry.
        return None


def iam_get_user_token(username, password, client_id, realm):
    """
    For getting an access token for a provided user credentials
    This function can be used for login functionality of users in iam

    Returns a tuple containing http status code and response text

    :param username:
    :param password:
    :return:
    """
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = 'username={}&password={}&grant_type=password&client_id={}'.format(username, password, client_id)
    response = requests.post(
        settings.IAM_URL + "/auth/realms/{}/protocol/openid-connect/token".format(realm), data=data,
        headers=headers)

    return (response.status_code, response.text)


def iam_register_user(fullname, username, email, password, admin_access_token):
    """
    For registering a user to IAM

    Returns a tuple of status code and response text

    If status code is None, then request failed
    Status code will be 201 if user is created

    :param fullname:
    :param username:
    :param email:
    :param password:
    :return:
    """

    # retrieving the admin access token for registering the users
    # status_code, admin_token_rsp_text = iam_get_user_token(settings.IAM_ADMIN_USERNAME, settings.IAM_ADMIN_PASSWORD,
    #                                                        "admin-cli")
    # 
    # if status_code != 200:
    #     return (None, None)
    # 
    # admin_token_rsp_json = json.loads(admin_token_rsp_text)

    headers = {'Authorization': 'Bearer {}'.format(admin_access_token), 'Content-Type': 'application/json'}

    data = {
        "username": username,
        "email": email,
        "firstName": fullname,
        "lastName": "",
        "enabled": True,
        "credentials": [
            {
                "type": "password",
                "value": password
            }
        ]
    }
    response = requests.post(settings.IAM_URL + "/auth/admin/realms/{}/users".format(settings.IAM_REALM),
                             data=json.dumps(data), headers=headers)

    return (response.status_code, response.text)


def iam_unregister_user(iam_user_id, admin_access_token):
    """
    Deletes a user from iam

    Returns a tuple of http status code and http response text
    Status code will be 204 if user is deleted

    :param iam_user_id:
    :param admin_access_token:
    :return:
    """
    headers = {'Authorization': 'Bearer {}'.format(admin_access_token)}
    response = requests.delete(settings.IAM_URL + "/admin/realms/{}/users/{}".format(settings.IAM_REALM, iam_user_id),
                               headers=headers)

    return (response.status_code, response.text)


def iam_update_user_info(fullname, iam_user_id, admin_access_token):
    """
    Updates user info in iam

    For now, we only allow updating fullname

    Returns a tuple of http status code and http response text
    Status code will be 201 if user info is updated

    :param fullname:
    :param iam_user_id:
    :param admin_access_token:
    :return:
    """
    headers = {'Authorization': 'Bearer {}'.format(admin_access_token)}
    response = requests.put(settings.IAM_URL + "/admin/realms/{}/users/{}".format(settings.IAM_REALM, iam_user_id),
                            data={
                                "firstName": fullname
                            },
                            headers=headers)

    return (response.status_code, response.text)


def iam_search_user_by_email(email, admin_access_token):
    """
    Searches user by email in iam
    
    Returns a tuple of http status code and http response text
    
    Response will be a dict
    
    Sample response
    
    
    {
        "id": "e48c4d99-507c-40f4-99c5-1dded5758be9",
        "createdTimestamp": 1591209056787,
        "username": "george2@yopmail.com",
        "enabled": true,
        "totp": false,
        "emailVerified": false,
        "firstName": "George J Padayatti",
        "lastName": "",
        "email": "george2@yopmail.com",
        "disableableCredentialTypes": [
            "password"
        ],
        "requiredActions": [],
        "notBefore": 0,
        "access": {
            "manageGroupMembership": true,
            "view": true,
            "mapRoles": true,
            "impersonate": true,
            "manage": true
        }
    }
    
    
    
    :param username: 
    :param admin_access_token: 
    :return: 
    """
    headers = {'Authorization': 'Bearer {}'.format(admin_access_token)}
    response = requests.get(
        settings.IAM_URL + "/auth/admin/realms/{}/users?email={}".format(settings.IAM_REALM, email),
        headers=headers)

    print(response.json())

    if response.status_code == 200:
        if len(response.json()) > 0:
            return (response.status_code, response.json()[0])

    return (response.status_code, None)


def iam_logout_user(iam_refresh_token, iam_client_id):
    """
    Logs out user from IAM

    Returns a tuple of http status code and http response text
    Status code will be 204 if logged out successfully

    :param iam_refresh_token:
    :param iam_client_id:
    :return:
    """
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = "refresh_token={}&client_id={}".format(iam_refresh_token, iam_client_id)
    response = requests.put(
        settings.IAM_URL + "/auth/realms/{}/protocol/openid-connect/logout".format(settings.IAM_REALM), data=data,
        headers=headers)

    return (response.status_code, response.text)


def iam_refresh_user_token(iam_refresh_token, iam_client_id):
    """
    Refresh user's access token

    Returns a tuple of http status code and http response text
    Status code will be 200 if refreshed successfully

    :param iam_refresh_token:
    :param iam_client_id:
    :return:
    """

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = "refresh_token={}&grant_type=refresh_token&client_id={}".format(iam_refresh_token, iam_client_id)
    response = requests.post(
        settings.IAM_URL + "/auth/realms/{}/protocol/openid-connect/token".format(settings.IAM_REALM), data=data,
        headers=headers)

    return (response.status_code, response.text)


def iam_reset_password_for_user(new_password, iam_user_id, admin_access_token):
    """
    Reset's user password in iam

    Returns a tuple of http status code and http response text
    Status code will be 204 if password reset successfully

    :param new_password:
    :param iam_user_id:
    :return:
    """

    headers = {'Authorization': 'Bearer {}'.format(admin_access_token), 'Content-Type': 'application/json'}
    response = requests.put(
        settings.IAM_URL + "/auth/admin/realms/{}/users/{}/reset-password".format(settings.IAM_REALM, iam_user_id),
        data={
            "type": "password",
            "value": new_password,
            "temporary": False
        }, headers=headers)

    return (response.status_code, response.text)


def iam_forgot_password_for_user(iam_user_id, admin_access_token):
    """
    Triggers forgot password email to users email

    :param iam_user_id:
    :param admin_access_token:
    :return:
    """
    headers = {'Authorization': 'Bearer {}'.format(admin_access_token), 'Content-Type': 'application/json'}
    data = "[\"UPDATE_PASSWORD\"]"
    response = requests.put(
        settings.IAM_URL + "/auth/admin/realms/{}/users/{}/execute-actions-email".format(settings.IAM_REALM,
                                                                                         iam_user_id),
        data=data, headers=headers)

    return (response.status_code, response.text)
