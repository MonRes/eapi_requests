from time import time

# Requires requests library. Install using pip
import requests

class EapiRequestsErr(Exception):
    pass

class EapiRequests(object):
    """Allows to make requests to EAPI on given setup."""

    def __init__(self, eapi_url, rui_url, user_name, user_password):
        """
        :param eapi_url: Eapi address on tested setup in following format: ^http[s]?:\/\/[a-z0-9\.-]+\.com$
        :type eapi_url: str
        :param rui_url: Rui address on tested setup in following format: ^http[s]?:\/\/[a-z0-9\.-]+\.com$
        :type rui_url: str
        :type user_name: str
        :type user_password: str
        """
        self.eapi_url = eapi_url + '/rest/'
        self.rui_url = rui_url + '/oauth/token'
        self.user_name = user_name
        self.user_password = user_password
        self.token = self._generate_token()

    def request(self, method, command, **kwargs):
        """Creates request to EAPI.
        See http://docs.python-requests.org/en/master/api/ for documentation on arguments.
        """
        response = requests.request(method.upper(), self.eapi_url + command, headers={
            'Authorization': self.token, 'Content-Type': 'application/json'}, verify=False,
                                    **kwargs)
        return response

    def _generate_token(self):
        """Returns token used for authentication"""
        return 'bearer ' + requests.post(url=self.rui_url,
                                         data={'grant_type': 'password',
                                               'password': self.user_password,
                                               'response_type': 'token',
                                               'username': self.user_name},
                                         verify=False
                                         ).json()['access_token']

    def test_get_alarms(self):
        response = eapi_requests.request('GET', '1.9/devices/F6BFE363F422/alarms')
        if response.status_code != 200:
            print("Mam Buga!!")
            return False
        print (response.json())

    def test_add_alarm_with_clear_status(self, id):
        response = eapi_requests.request('GET', '1.9/devices/F6BFE363F422/alarms')
        for record in response.json():
            if record['alarm_id']== str(id):
                print('Nie można dodać nowego alarmu ze statusem CLEAR')
                return False

        response = eapi_requests.request('PATCH', '1.9/devices/F6BFE363F422/alarms',
                                         json={
                                             "data": [
                                                 {
                                                     "alarm_id": id,
                                                     "action": "CLEAR",
                                                     "timestamp": int(time()) * 1000,
                                                     "severity": "EMERGENCY",
                                                     "description": "Device overheating",
                                                     "details": "Temperature is above safe levels",
                                                     "optional": {}
                                                 }
                                             ]
                                         })

        if response.status_code != 200:
            print('Mam buga!')
            return False


    def test_put_method(self):
        pass

    def test_delete_method(self):
        pass



    def test_patch_set_action(self, action):
        response = eapi_requests.request('PATCH', '1.9/devices/F6BFE363F422/alarms',
                                         json={
                                             "data": [
                                                 {
                                                     "alarm_id": "test_alarm_1",
                                                     "action": action,
                                                     "timestamp": int(time()) * 1000,
                                                     "severity": "EMERGENCY",
                                                     "description": "Device overheating",
                                                     "details": "Temperature is above safe levels",
                                                     "optional": {}
                                                 }
                                             ]
                                         })

        if response.status_code != 200:
            print('Wrong action: ', action, '. Allowed actions: SET, CLEAR')
            return False


    def test_patch_set_severity(self, severity):
        response = eapi_requests.request('PATCH', '1.9/devices/F6BFE363F422/alarms',
                                         json={
                                             "data": [
                                                 {
                                                     "alarm_id": "test_alarm_2",
                                                     "action": "SET",
                                                     "timestamp": int(time()) * 1000,
                                                     "severity": severity,
                                                     "description": "Device overheating",
                                                     "details": "Temperature is above safe levels",
                                                     "optional": {}
                                                 }
                                             ]
                                         })

        if response.status_code != 200:
            print('Alarm severity is invalid')
            return False


    def test_patch_set_timestamp(self, timestamp):
        response = eapi_requests.request('PATCH', '1.9/devices/F6BFE363F422/alarms',
                                         json={
                                             "data": [
                                                 {
                                                     "alarm_id": "test_alarm_2",
                                                     "action": "SET",
                                                     "timestamp": timestamp,
                                                     "severity": 'EMERGENCY',
                                                     "description": "Device overheating",
                                                     "details": "Temperature is above safe levels",
                                                     "optional": {}
                                                 }
                                             ]
                                         })

        if response.status_code != 200:
            print('Not an ISO-8601 timestamp')
            return False


# Example usage:


# Create EapiRequests object using given setup/user parameters
eapi_requests = EapiRequests(eapi_url='https://eapigeic-qa2.proximetry.com',
                             rui_url='https://geic-qa2.proximetry.com',
                             user_name='user01',
                             user_password='P@ssw0rd')
# Send request to retrieve details about first device from systems
systems_response = eapi_requests.request('GET', '1.9/systems', params={'limit': 1})
# Retrieve asdid from response
asdid = systems_response.json()[0]['asdid']
# Set alarm for device identified by asdid taken from system
set_alarm_response = eapi_requests.request('PATCH',
                                           '2.0/devices/{}/alarms'.format(asdid),
                                           json={
                                               "data": [
                                                   {
                                                       "alarm_id": "test_alarm_1",
                                                       "action": "SET",
                                                       "timestamp": int(time()) * 1000,
                                                       "severity": "EMERGENCY",
                                                       "description": "Device overheating",
                                                       "details": "Temperature is above safe levels",
                                                       "optional": {}
                                                   }
                                               ]
                                           }
                                           )


activation_codes = eapi_requests.request('GET', '1.9/activation_codes')
print(activation_codes.json())

client = eapi_requests.test_get_alarms()
client = eapi_requests.test_patch_set_action('SET')
client = eapi_requests.test_patch_set_severity('WARNING')
client = eapi_requests.test_add_alarm_with_clear_status('01')