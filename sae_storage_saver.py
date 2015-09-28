# -*- coding: utf-8 -*-
import GrabCnblogPost
import datetime
from sae.storage import Bucket

class SaeStorageSaver:
    def __init__(self, key):
        self.bucket = Bucket(key)
        self.bucket.put()

    def StoreTxtFile(self, path, content):
        self.bucket.put_object(path, content)

    def StoreBinFile(self, path, content):
        self.bucket.put_object(path, content)


class SaeAppSaveBlog:
    def GET(self):
        saver = SaeStorageSaver(str(datetime.datetime.now())
        grabber = GrabCnblogPost('catch', saver)
        num = grabber.get_all_post('blog/')
        return "(" + str(num) + ") posts are saved"


