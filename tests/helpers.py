""""""

Helper functions for testsHelper functions for tests

""""""

from datetime import datetime, timedeltafrom datetime import datetime, timedelta

import jsonimport json





def login(client, email, password):def login(client, email, password):def parse_json(response):

    """Log in a user with the test client"""    """Parse a JSON response"""

    return client.post(    return json.loads(response.data)og in a user with the test client"""

        '/auth/login',    return client.post(

        data={'email': email, 'password': password},        '/auth/login',

        follow_redirects=True        data={'email': email, 'password': password},

    )        follow_redirects=True

    )



def logout(client):

    """Log out a user with the test client"""def logout(client):

    return client.get('/auth/logout', follow_redirects=True)    """Log out a user with the test client"""

    return client.get('/auth/logout', follow_redirects=True)



def create_test_appointment_data(patient_id, doctor_id):

    """Create test data for an appointment"""

    appointment_date = datetime.now() + timedelta(days=1)

    appointment_time = datetime.now().time()

        

    return {

        'patient_id': patient_id,

        'doctor_id': doctor_id,

        'appointment_date': appointment_date.strftime('%Y-%m-%d'),

        'appointment_time': appointment_time.strftime('%H:%M'),

        'reason': 'Test appointment',

        'notes': 'Test appointment notes'

    }

def assert_response_status(response, status_code=200):
    """Assert that a response has the expected status code"""
    assert response.status_code == status_code


def get_json_response(response):
    """Parse a JSON response"""
    return json.loads(response.data)


def parse_json(response):
    """Parse a JSON response"""
    return json.loads(response.data)


def assert_response_status(response, status_code=200):
    """Assert that a response has the expected status code"""
    assert response.status_code == status_code


def get_json_response(response):
    """Parse a JSON response"""
    return json.loads(response.data)


