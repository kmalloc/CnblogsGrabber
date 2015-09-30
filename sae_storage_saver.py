# -*- coding: utf-8 -*-
import sys
import datetime
from sae.storage import Bucket
from GrabCnblogPost import GrabCnblogPost


g_backup_path = "blog/"

g_max_back_up_list = 5


class SaeStorageSaver:
    def __init__(self, key):
        self.bucket = Bucket(key)
        
    def StoreTxtFile(self, path, content):
        self.bucket.put_object(path, content)

    def StoreBinFile(self, path, content):
        self.bucket.put_object(path, content)
        
    def GetItemUnder(self, path):
        return [x for x in self.bucket.list(path)]
    
    def GetBackupList(self):
        return self.GetItemUnder(g_backup_path)
    
    def DeleteObject(self, obj):
        self.bucket.delete_object(obj)


def categorize_post(items):
    entry = {}
    for p in items:
        name = p[u"name"]
        seg = name.split("/")
        
        if len(seg) < 2:
        	continue
            
        if seg[1] not in entry:
            entry[seg[1]] = []
                    
        entry[seg[1]].append(name)

    return entry
    
def format_storage_item(items):
    entry = categorize_post(items)
    key_ls = entry.keys()
    key_ls.sort(key=lambda x: x, reverse=True)
    info = "\n\n" + str(len(key_ls)) + " backup are available:\n\n"
    for key in key_ls:
        info += "\n" + key + "(" + str(len(entry[key])) + "):\n\n"
        for item in entry[key]:
            info += item + "\n"                                
    return info


class SaeAppSaveBlog:
    def GET(self):
        time = str(datetime.datetime.now())
        print "now to backup my blog, time:", time
        
        saver = SaeStorageSaver("blogbackup")
        grabber = GrabCnblogPost('catch', saver)
        res = grabber.get_all_post(g_backup_path + time)
        
        all_backup = saver.GetBackupList()
        
        info = format_storage_item(all_backup)
        
        return res + "\nbackup available:\n" + info
    

class SaeAppCleanOldBackup:
    def DeleteOld(self, saver, items):
        entry = categorize_post(items)
        key_ls = entry.keys()
        key_ls.sort(key=lambda x: x, reverse=True)
        
        stay = key_ls[:g_max_back_up_list]
        to_del = key_ls[g_max_back_up_list:]
        
        file_ls = []
        for k in to_del:
            it = entry[k]
            file_ls.extend(it)
        
        info = "\n\n" + str(len(to_del)) + " backup will be deleted, "
        info += str(len(file_ls)) +  " files in total:\n\n"
        
        for it in file_ls:
            info += it + "\n"
            saver.DeleteObject(it)
        return info
    
    def GET(self):
        saver = SaeStorageSaver("blogbackup")
        all_backup = saver.GetBackupList()
        sz = len(all_backup)
        if sz <= g_max_back_up_list:
            return

        info = self.DeleteOld(saver, all_backup)
        left = saver.GetBackupList()
        
        return info + format_storage_item(left)
        
