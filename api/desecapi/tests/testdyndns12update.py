from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from utils import utils
from django.db import transaction
import base64


class DynDNS12UpdateTest(APITestCase):
    owner = None
    token = None
    username = None
    password = None

    def setUp(self):
        self.owner = utils.createUser()
        self.token = utils.createToken(user=self.owner)
        transaction.commit()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

        url = reverse('domain-list')
        data = {'name': utils.generateDynDomainname(), 'dyn': True}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['dyn'], True)

        self.username = response.data['name']
        self.password = self.token
        self.client.credentials(HTTP_AUTHORIZATION='Basic ' + base64.b64encode(self.username + ':' + self.password))

    def assertIP(self, ipv4=None, ipv6=None):
        old_credentials = self.client._credentials['HTTP_AUTHORIZATION']
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.password)
        url = reverse('domain-detail/byName', args=(self.username,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if ipv4 is not None:
            self.assertEqual(response.data['arecord'], ipv4)
        if ipv6 is not None:
            self.assertEqual(response.data['aaaarecord'], ipv6)
        self.client.credentials(HTTP_AUTHORIZATION=old_credentials)

    def testDynDNS1UpdateDDClientSuccess(self):
        # /nic/dyndns?action=edit&started=1&hostname=YES&host_id=foobar.dedyn.io&myip=10.1.2.3
        url = reverse('dyndns12update')
        response = self.client.get(url,
                                   {
                                       'action': 'edit',
                                       'started': 1,
                                       'hostname': 'YES',
                                       'host_id': self.username,
                                       'myip': '10.1.2.3'
                                   })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, 'good')
        self.assertIP(ipv4='10.1.2.3')

    def testDynDNS1UpdateDDClientIPv6Success(self):
        # /nic/dyndns?action=edit&started=1&hostname=YES&host_id=foobar.dedyn.io&myipv6=::1337
        url = reverse('dyndns12update')
        response = self.client.get(url,
                                   {
                                       'action': 'edit',
                                       'started': 1,
                                       'hostname': 'YES',
                                       'host_id': self.username,
                                       'myipv6': '::1337'
                                   })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, 'good')
        self.assertIP(ipv6='::1337')

    def testDynDNS2UpdateDDClientIPv4Success(self):
        #/nic/update?system=dyndns&hostname=foobar.dedyn.io&myip=10.2.3.4
        url = reverse('dyndns12update')
        response = self.client.get(url,
                                   {
                                       'system': 'dyndns',
                                       'hostname': self.username,
                                       'myip': '10.2.3.4'
                                   })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, 'good')
        self.assertIP(ipv4='10.2.3.4')

    def testDynDNS2UpdateDDClientIPv6Success(self):
        #/nic/update?system=dyndns&hostname=foobar.dedyn.io&myipv6=::1338
        url = reverse('dyndns12update')
        response = self.client.get(url,
                                   {
                                       'system': 'dyndns',
                                       'hostname': self.username,
                                       'myipv6': '::1338'
                                   })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, 'good')
        self.assertIP(ipv6='::1338')

    def testFritzBoxIPv6(self):
        #/
        url = reverse('dyndns12update')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, 'good')
        self.assertIP(ipv4='127.0.0.1')

    def testManualIPv6(self):
        #/update?username=foobar.dedyn.io&password=secret
        self.client.credentials(HTTP_AUTHORIZATION='')
        url = reverse('dyndns12update')
        response = self.client.get(url,
                                   {
                                       'username': self.username,
                                       'password': self.token,
                                   })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, 'good')
        self.assertIP(ipv4='127.0.0.1')