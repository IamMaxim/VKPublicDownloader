import json

import time

import vkapi

vk = vkapi.VKApi(open('access_token.txt').read().strip('\n'))

step = 500  # should be <= 500
i = 531000
i_max = 0xFFFFFFFF

out = open('groups.txt', 'w+')

def getIDs(offset: int):
    return ','.join(map(lambda n: str(n), range(offset, offset + step).__iter__()))


while i < i_max:
    print(i)
    publics = json.loads(vk.sendRequest('groups.getById', True, ['group_ids=' + getIDs(i)]))['response']
    for p in publics:
        try:
            if p['can_post'] == 1:
                out.write(json.dumps({'id': p['id'], 'name': p['name'], 'members_count': p['members_count']}) + '\n')
                print('adding group')
        except Exception:
            pass
    time.sleep(0.334)
    i += step
