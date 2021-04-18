from pyrad.client import Client
from pyrad.dictionary import Dictionary
import socket
import pyrad.packet


class RADIUSManager:
    @property
    def host(self):
        return self.__host

    @host.setter
    def host(self, value):
        self.__host = value

    @property
    def port(self):
        return self.__port

    @port.setter
    def port(self, value):
        self.__port = value

    @property
    def secret(self):
        return self.__secret

    @secret.setter
    def secret(self, value):
        self.__secret = value

    @property
    def enabled(self):
        return self.__enabled

    @enabled.setter
    def enabled(self, value):
        self.__enabled = value

    @property
    def dictionary(self):
        return self.__dictionary

    @dictionary.setter
    def dictionary(self, value):
        self.__dictionary = value

    @property
    def error_message(self):
        return self.__error_message

    @error_message.setter
    def error_message(self, value):
        self.__error_message = value

    def __init__(self):
        self.__host = ''
        self.__port = 0
        self.__secret = ''
        self.__enabled = False
        self.__dictionary = ''
        self.__error_message = ''

    def authenticate(self, username, password):
        self.error_message = ''
        client = self.__get_client()
        request = client.CreateAuthPacket(code=pyrad.packet.AccessRequest, User_Name=username)
        request["User-Password"] = request.PwCrypt(password)

        try:
            response = client.SendPacket(request)
            if response.code == pyrad.packet.AccessAccept:
                return True
        except pyrad.client.Timeout:
            self.error_message = 'Timeout - Could not connect to RADIUS Server'
        except socket.error as error:
            self.error_message = 'Network error: {0}'.format(error[1])

        return False

    def test_connection(self):
        self.error_message = ''
        client = self.__get_client()
        request = client.CreateAuthPacket(code=pyrad.packet.AccessRequest, User_Name="snitchdnsusertest")
        request["User-Password"] = request.PwCrypt("snitchdnspasswordtest")

        try:
            response = client.SendPacket(request)
            if response.code in [pyrad.packet.AccessAccept, pyrad.packet.AccessReject]:
                return True
        except pyrad.client.Timeout:
            self.error_message = 'Timeout - Could not connect to RADIUS Server'
        except socket.error as error:
            self.error_message = 'Network error: {0}'.format(error[1])

        return False

    def __get_client(self):
        return Client(server=self.host, authport=self.port, secret=self.secret.encode('utf8'), dict=Dictionary(self.dictionary), retries=1)