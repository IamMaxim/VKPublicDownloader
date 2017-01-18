import urllib.request
import json
import time


class VKApi:
    def __init__(self, token: str):
        self.token = token
        self.messages = Messages(self)
        self.users = Users(self, True, True)
        self.friends = Friends(self, False)

    def sendRequest(self, name: str, use_token: bool, args: list):
        req = 'https://api.vk.com/method/' + name + "?v=5.60"
        if use_token:
            req += '&' + self.token
        for arg in args:
            req += '&' + arg
        return self.sendRequestByURL(req)

    def sendRequestByURL(self, req):
        req = req.replace('\n', '').replace(' ', '%20')
        res = urllib.request.urlopen(req).read()
        while res.startswith(b'{"error"'):
            errcode = json.loads(res.decode('utf8'))['error']['error_code']
            # check if this is "too many requests per second" error
            if errcode != 6:
                return 'err'
            time.sleep(0.4)
            res = urllib.request.urlopen(req).read()
        return res.decode('utf8')


class Messages:
    def __init__(self, vk_api):
        self.vk = vk_api

    def send(self, user_id, message):
        self.vk.sendRequest('messages.send', True, ['user_id=' + user_id, 'message=' + message])


class Users:
    def __init__(self, vk_api: VKApi, cache_users: bool, use_token: bool):
        self.vk = vk_api
        self.cache_users = cache_users
        self.use_token = use_token
        if cache_users:
            self.users = {}

    # def get(self, user_id: str):
    #     return self.get(int(user_id))

    def get(self, user_id: int):
        if self.cache_users:
            if self.users.__contains__(user_id):
                user = self.users[user_id]
            else:
                user = json.loads(self.vk.sendRequest('users.get', self.use_token, ['user_id=' + str(user_id)]))['response'][0]
                self.users[user_id] = user
        else:
            user = json.loads(self.vk.sendRequest('users.get', self.use_token, ['user_id=' + str(user_id)]))['response'][0]
        return user

    def load_into_DB(self, user_ids: list):
        users = json.loads(self.vk.sendRequest('users.get', self.use_token, ['user_ids=' + ','.join(user_ids)]))['response']
        for u in users:
            self.users[u['id']] = u

    def loadDB(self):
        print('loading users DB from disk...')
        try:
            file = open('users.db', 'r+')
            while file:
                str = file.readline()
                if str:
                    u = json.loads(str)
                    self.users[u['id']] = u
                else:
                    break
            file.close()
        except FileNotFoundError:
            print('DB file not found.')

    def saveDB(self):
        print('saving users DB to disk...')
        file = open('users.db', 'w+')
        for u in self.users.values():
            file.write((json.dumps(u) + '\n'))
        file.close()


class Friends:
    def __init__(self, vk_api: VKApi, use_token: bool):
        self.vk = vk_api
        self.use_token = use_token

    def get(self, user_id: int):
        res = self.vk.sendRequest('friends.get', self.use_token, ['user_id=' + str(user_id)])
        # couldn't get friend list
        if res == 'err':
            return []
        return json.loads(res)['response']['items']
