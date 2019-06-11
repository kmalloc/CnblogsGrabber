# -*- coding: utf8 -*-
import sys
import os
import urllib2

from bs4 import element
from bs4 import BeautifulSoup

class FileSystemSaver:
    def StoreTxtFile(self, path, content):
        folder = os.path.dirname(path)
        self.__create_folder__(folder)
        self.__write_text__(path, content)

    def StoreBinFile(self, path, content):
        folder = os.path.dirname(path)
        self.__create_folder__(folder)
        self.__write_binary__(path, content)

    def __create_folder__(self, folder):
        try:
            if not os.path.isdir(folder):
                os.mkdir(folder)
        except Exception as e:
            print "failed to create folder:", folder
            print "error:%s"%e

        return folder

    def __write_text__(self, path, content):
        try:
            with open(path, 'wb') as fh:
                fh.write(content)
        except Exception as e:
            print "failed to write file:", path
            print "error:", e

    def __write_binary__(self, path, content):
        try:
            with open(path, 'wb') as fh:
                fh.write(content)
        except Exception as e:
            print "failed to write file:", path
            print "error:", e


class GrabCnblogPost():
    def __init__(self, name, saver):
        self.url = 'http://www.cnblogs.com/' + name
        self.saver = saver
        self.url_list = []
        self.error_url = []

    def __get_url__(self, url):

        try:
            response = urllib2.urlopen(url, timeout=16)
        except Exception as e:
            self.error_url.append(url)
            info = "Failed to connect to cnblogs, url:", url, ", error:" + str(e)
            print info
            return info

        soup = BeautifulSoup(response.read().decode('utf-8', 'ignore'), "html.parser")
        for a in soup.find_all('a', attrs={'class' : 'postTitle2'}):
            self.url_list.append(a.get('href').encode('utf-8'))

        next_page = soup.find(id = 'nav_next_page')
        if next_page:
            next_page = next_page.find('a').get('href')
        else:
            pager = soup.find('div', attrs= {'class' : 'pager'})
            if not pager:
                return
            pages = pager.find_all('a')

            for page in pages:
                if page.get_text().encode("utf-8") == '下一页':
                    next_page = page.get('href')
                    break

        if next_page:
            self.__get_url__(next_page)

    def __extract_post_content__(self, post):
        ret = ""
        for art in post.children:
            if isinstance(art, element.NavigableString):
                if  art.string.encode('utf-8') != '\n':
                    ret = ret + art.string.encode('utf-8')
                continue

            s = ""
            child_num = len(list(art.children))
            if child_num:
                s = self.__extract_post_content__(art)

            if art.name == "img":
                s = s + " [" + art.get("src").encode('utf-8') + "]"
            elif art.name == "br":
                s = s + "\n"
            elif art.name == "a":
                s = s + " [" + art.get("href").encode('utf-8') + "]"
            elif art.name == "p" or art.name == "pre":
                s = s + "\n"
            elif art.name == "h1" or art.name == "h2" or art.name == "h3" or art.name == "h4":
                s = "\n" + s + "\n\n"
            elif art.name == "tr":
                s = s + "\n"
            elif art.name == "td":
                s = s + "  |"

            ret = ret + s

        return ret

    def __get_blog__(self, output_path, url_list):

        num = 0
        for url in url_list:
            try:
                response = urllib2.urlopen(url, timeout=16)
            except Exception as e:
                self.error_url.append(url)
                info = "Failed to fetch post page, url:", url, ", error:" + str(e)
                print info
                continue

            soup = BeautifulSoup(response.read().decode('utf-8','ignore'), "html.parser")
            title = soup.find(id='cb_post_title_url').string.encode('utf-8')
            post = soup.find(id='cnblogs_post_body')
            if not post:
                return

            num += 1
            folder = os.path.join(output_path, title)
            content = "\n" + title + "\n\n" + self.__extract_post_content__(post)

            txt_file = os.path.join(folder, title)

            print "%d:file path:%s"%(num, txt_file)
            self.saver.StoreTxtFile(txt_file.decode("utf-8"), content)

            # grab image files
            img_links = post.find_all('img')
            for img_link in img_links:
                img_url = img_link.get('src').encode('utf-8')
                img = urllib2.urlopen(img_url).read()
                file = self.__extract_file_name__(img_url)
                path = os.path.join(folder, file)
                self.saver.StoreBinFile(path.decode("utf-8"), img)

        return num

    def __extract_file_name__(self, link):
        for s in range(1, len(link)+ 1):
            if link[-s] == '/':
                return link[-s + 1:]

    def set_name(self, name):
        self.url = 'http://www.cnblogs.com/' + name
        self.url_list = []

    def get_all_post(self, output_path):
        self.__get_url__(self.url)
        return self.get_post_by_url(self.url_list, output_path)

    def get_post_by_url(self, url, output_path):
		self.error_url = []
		num = self.__get_blog__(output_path, url)
		ret = str(num) + " posts are saved, followings are failed (" + str(len(self.error_url)) + "):\n"
		
		for url in self.error_url:
		    ret += url + "\n"
		return ret

if __name__ == "__main__":
    saver = FileSystemSaver()
    grabber = GrabCnblogPost('catch', saver)
    try:
        info = grabber.get_all_post('C:\\Users\\miliao\\blogs')
        print info
    except Exception as e:
        print "error occurs, please check, msg:", str(e)
