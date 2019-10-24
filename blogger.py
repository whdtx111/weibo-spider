import requests
import requests.exceptions as reqerr
import os
import os.path as os_path

import const


class Blogger(object):

    def __init__(self, blog_id):
        self.id = blog_id
        self.folder = os_path.join(os.getcwd(), self.id)
        self.img_count = 0
        self.error_count = 0

    def create_folder(self):
        if not os_path.exists(self.folder):
            os.mkdir(self.folder)

    def request(self, index):
        payload = {
            "display": 0,
            "containerid": "230413" + self.id,
            "page_type": "03",
            "page": index
        }
        try:
            with requests.get(const.BLOG_TITLE, params=payload, timeout=const.TIME_OUT) as r:
                if self.error_count > 0:
                    self.error_count -= 1
                return self.query_pics(r.json())
        except reqerr.ConnectionError as err:
            print(err)
            self.error_count += 1
            if self.error_count >= const.MAX_ERROR_COUNT:
                return False
            return True

    def save_picture(self, url):
        suffix = url[-4:]
        new_url = url.replace(const.ORIGIN_GRAPH_BED_PATH, const.NEW_GRAPH_BED_PATH)
        req_img = requests.get(new_url)
        img = req_img.content
        self.img_count += 1
        file_path = os_path.join(self.folder, str(self.img_count) + suffix)
        with open(file_path, 'wb+') as f:
            f.write(img)

    def save_pictures(self, pictures):
        for pic in pictures:
            self.save_picture(pic["url"])

    def requests(self):
        flag = True
        i = 0
        while flag:
            flag = self.request(i)
            i += 1

    # data type: dict
    def query_pics(self, data):
        cards = data["data"]["cards"]
        for card in cards:
            if "mblog" in card:
                mblog = card["mblog"]
                if "pics" in mblog:
                    self.save_pictures(mblog["pics"])
                if "retweeted_status" in mblog and "pics" in mblog["retweeted_status"]:
                    self.save_pictures(mblog["retweeted_status"]["pics"])

            elif "name" in card:
                if card["name"] == const.NO_MORE_PICTURES:
                    return False
        return True
