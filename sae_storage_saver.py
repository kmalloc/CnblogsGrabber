# -*- coding: utf-8 -*-
import sys
import web
import datetime
from sae.storage import Bucket
from GrabCnblogPost import GrabCnblogPost


g_backup_path = "blog/"
g_max_back_up_list = 32
g_sae_storage_bucket = "blogbackup"


class SaeStorageSaver:
    def __init__(self, key):
        self.bucket = Bucket(key)
        
    def StoreTxtFile(self, path, content):
        self.bucket.put_object(path, content)

    def StoreBinFile(self, path, content):
        self.bucket.put_object(path, content)
        
    def GetObjectByPath(self, path):
        return self.bucket.get_object_contents(path)
        
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


class BlogSaver:
    def Save(self):
        time = str(datetime.datetime.now())
        print "now to backup my blog, time:", time
        
        saver = SaeStorageSaver(g_sae_storage_bucket)
        grabber = GrabCnblogPost('catch', saver)
        res = grabber.get_all_post(g_backup_path + time)
        
        all_backup = saver.GetBackupList()
        
        info = format_storage_item(all_backup)
        
        return res + "\ndetail information of my blog:\n" + info


class BlogShower:
    def Show(self):
        saver = SaeStorageSaver(g_sae_storage_bucket)
        all_backup = saver.GetBackupList()
        return format_storage_item(all_backup)
    def ShowPost(self, path):
        if path == "":
           return "invalid post path."
        print "try to get post:", path
        saver = SaeStorageSaver(g_sae_storage_bucket)
        try:
            return saver.GetObjectByPath(path)
        except Exception as e:
        	return str(e)

class BlogCleaner:
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
    
    def Clean(self):
        saver = SaeStorageSaver(g_sae_storage_bucket)
        all_backup = saver.GetBackupList()
        sz = len(all_backup)
        if sz <= g_max_back_up_list:
            return

        info = self.DeleteOld(saver, all_backup)
        left = saver.GetBackupList()
        
        return info + format_storage_item(left)
    

class BlogHandler:
    def GET(self):
        info = ""
        data = web.input(op="None", p="")
        if data.op == "save":
            save = BlogSaver()
            info = save.Save()
        elif data.op == "clean":
            cleaner = BlogCleaner()
            info = cleaner.Clean()
        elif data.op == "show":
            show = BlogShower()
            info = show.Show()
        elif data.op == "showpost":
            path = data.p
            show = BlogShower()
            info = show.ShowPost(path)
        else:
            info = "Welcome to my secret blog handler, please contact me by my email: kmalloc@live.com, thanks."
            
        info = info.replace("\n", "<br>")
        return "<!DOCTYPE html><head><meta charset=\"UTF-8\"><title>miliao's secret blog handler</title></head><body>%s</body></html>" % info
    
