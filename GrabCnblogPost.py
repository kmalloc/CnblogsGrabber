# -*- coding: utf-8 -*-
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
            print "error:", e

        return folder

    def __write_text__(self, path, content):
        try:
            with open(path, 'wb') as fh:
                fh.write(content)
        except Exception as e:
            print "error:", e
            print "failed to write file:", path

    def __write_binary__(self, path, content):
        try:
            with open(path, 'wb') as fh:
                fh.write(content)
        except Exception as e:
            print "error:", e
            print "failed to write file:", path


class GrabCnblogPost():
    def __init__(self, name, saver):
        self.url = 'http://www.cnblogs.com/' + name
        self.saver = saver
        self.url_list = []

    def __get_url__(self, url):
        response = urllib2.urlopen(url, timeout=1500)
        soup = BeautifulSoup(response.read(), "html.parser")
        for a in soup.find_all('a', attrs={'class' : 'postTitle2'}):
            self.url_list.append(a.get('href'))

        next_page = soup.find(id = 'nav_next_page')
        if next_page:
            next_page = next_page.find('a').get('href')
        else:
            pager = soup.find('div', attrs= {'class' : 'pager'})
            if not pager:
                return
            pages = pager.find_all('a')

            for page in pages:
                if page.get_text() == u'下一页':
                    next_page = page.get('href')
                    break

        if next_page:
            self.__get_url__(next_page)

    def __extract_post_content__(self, post):
        ret = ""
        for art in post.children:
            if isinstance(art, element.NavigableString):
                if  art.string != '\n':
                    ret = ret + art.string
                continue

            s = ""
            child_num = len(list(art.children))
            if child_num:
                s = self.__extract_post_content__(art)

            if art.name == "img":
                s = s + " [" + art.get("src") +"]"
            elif art.name == "br":
                s = s + "\n"
            elif art.name == "a":
                s = s + " [" + art.get("href") + "]"
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
            response = urllib2.urlopen(url, timeout=1500)
            soup = BeautifulSoup(response.read(), "html.parser")
            title = soup.find(id='cb_post_title_url').string
            post = soup.find(id='cnblogs_post_body')
            if not post:
                return

            num += 1
            folder = os.path.join(output_path, title)
            content = "\n" + title + "\n\n" + self.__extract_post_content__(post)

            txt_file = os.path.join(folder, title)
            self.saver.StoreTxtFile(txt_file, content.encode("utf-8"))

            # grab image files
            img_links = post.find_all('img')
            for img_link in img_links:
                img_url = img_link.get('src')
                img = urllib2.urlopen(img_url).read()
                file = self.__extract_file_name__(img_url)
                path = os.path.join(folder, file)
                self.saver.StoreBinFile(path, img)

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
        return self.__get_blog__(output_path, self.url_list)


if __name__ == "__main__":
    saver = FileSystemSaver()
    grabber = GrabCnblogPost('catch', saver)
    num = grabber.get_all_post('/home/miliao/blog')
    print "(", num, ") posts are saved.\n"

