#!/usr/bin/env python
# -*- coding: utf-8 -*-

# gmbox, Google music box.
# Copyright (C) 2009, gmbox team
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os, sys, copy, time, re, logging, urllib, urllib2, hashlib
import xml.dom.minidom as minidom

from parser import XmlAlbumParser, ListParser, SongParser, AlbumListParser
from const import *
from utils import *
from config import config

log = logging.getLogger('lib.core')

class Gmbox:
    '''核心模块,初始化完成以后,成为一个全局变量.
    功能包括:获取榜单,搜索歌曲,并维护一个当前列表,
    并且可以下载当前列表中的部分或全部歌曲,并集成缓存.'''
    
    def __init__(self):
        '''初始化一个空的gmbox对象'''
        self.songlist = []
        self.albumlist = []
        self.cached_list = {}
        self.albuminfo = {}
        self.downalbumnow = False

    def __str__(self):
        '''print对象的时候调用,由于win下可能会中文乱码,建议使用 listall 方法代替'''
        return '\n'.join(['Title="%s" Artist="%s" ID="%s"' % 
            (song['title'], song['artist'], song['id']) for song in self.songlist])

    def listall(self):
        '''打印当前列表信息'''
        print '\n'.join(['Num=%d Title="%s" Artist="%s" ID="%s"' % 
            (self.songlist.index(song) + 1, song['title'], song['artist'], song['id']) 
            for song in self.songlist])
    def listallalbum(self):
        '''打印当前专辑列表信息'''
        print '\n'.join(['Num=%d Name="%s" Memo="%s" ID="%s"' % 
            (self.albumlist.index(album) + 1, album['name'], album['memo'], album['id']) 
            for album in self.albumlist])
    def setup_file_info(self, songname, artist, isalbum, albumname, albumartist, albumnum):
        '''根据设置，组装歌曲信息，返回 [全文件名,路径,文件名]'''
        path = config.item['savedir']
        if config.item['makeartistdir']:
            path = os.path.join(path, artist)
            filename = songname + '.mp3'
        else:
            filename = songname + '-' + artist + '.mp3'
        if isalbum and config.item['makealbumdir']:
            path = os.path.join(path, albumname + '-' + albumartist)
        if isalbum and config.item['addalbumnum']:
            filename = '%02d.%s' % (albumnum, filename)
        filename = str(filename).translate(None, '''\/:*?<>|'"''')
        if len(filename) > 243:
            print u'警告：由于文件名过长，已被截断', filename,
            filename = filename[:238] + '.mp3'
            print '-->', filename
        return [os.path.join(path, filename), path, filename]
        
    def createdir_getfilename(self, i=0):
        '''创建必要的目录，并返回当前列表的第i首歌曲的文件名（含路径）'''
        song = self.songlist[i]
        info = self.setup_file_info(song['title'], song['artist'], self.downalbumnow,
            self.albuminfo['title'] if self.downalbumnow else None,
            self.albuminfo['artist'] if self.downalbumnow else None, i + 1)

        if not os.path.exists(info[1]):
            os.makedirs(info[1])
        return info

    def get_url_html(self, url, need_pre_deal=True):
        '''获取指定url的html'''
        try:
            html = urllib2.urlopen(url).read()
        except urllib2.URLError:
            print '网络错误,请检查网络...'
            return
        except:
            print '未知错误!请到这里报告bug: http://code.google.com/p/gmbox/issues/entry'
            return
        if need_pre_deal:
            #预处理HTML(XML模式不需要)
            html = re.sub(r'&#([0-9]{2,5});', unistr, html)
            html = re.sub(r'</?b>', '', html)
            html = entityref.sub(entityrefstr, html)
        return html
        
    def find_final_uri(self, i=0):
        '''找到最终真实下载地址，以供下一步DownLoad类下载'''
        song = self.songlist[i]
        songurl = song_url_template % (song['id'],)
        html = self.get_url_html(songurl)
        s = SongParser()
        s.feed(html)
        return s.url
    
    def get_lyric_url(self, sid):
        '''获取歌词下载地址，按照flash播放器所用的歌词xml信息'''
        sig = hashlib.md5(flash_player_key + sid).hexdigest()
        xml_url = song_streaming_url_template % (sid, sig)
        try:
            xml_string = self.get_url_html(xml_url, False)
            dom = minidom.parseString(xml_string)
            url = dom.getElementsByTagName('lyricsUrl')[0].childNodes[0].data
        except:
            return None
        return url
    
    def downone(self, i=0, callback=None):
        '''下载当前列表中的一首歌曲 '''
        nameinfo = self.createdir_getfilename(i)
        lyric_filename = os.path.splitext(nameinfo[0])[0] + ".lrc"
        if config.item['lyric']:
            if not os.path.exists(lyric_filename):
                lyric_url = self.get_lyric_url(self.songlist[i]['id'])
                if lyric_url:
                    self.download(lyric_url, lyric_filename, self.update_null)
                else:
                    print nameinfo[2], u'的歌词不存在!'

        if os.path.exists(nameinfo[0]):
            print nameinfo[2], u'已存在!'
            return
        
        url = self.find_final_uri(i)
        if url:
            print u'正在下载:', nameinfo[2]
            if self.downalbumnow and callback:
                numinfo = "(%d of %d)" % (i + 1, len(self.songlist))
                callback(-1, nameinfo[2], numinfo) #-1做为开始信号
            self.download(url, nameinfo[0], callback=callback)
        else:   #下载页有验证码时url为空
            print u'出错了,也许是google加了验证码,请换IP后再试或等24小时后再试...'

        if config.item['id3utf8']:
            #在Linux下转换到UTF 编码，现在只有comment里还是乱码
            os.system('mid3iconv -e gbk "' + nameinfo[0] + '"')

    def downall(self, callback=None):
        '''下载当然列表中的所有歌曲'''
        [self.downone(i, callback) for i in range(len(self.songlist))]

    def down_listed(self, songids, callback=None):
        '''下载当然列表的特定几首歌曲,传入序号的列表指定要下载的歌'''
        if not songids or not isinstance(songids, list):
            return
        [self.downone(i, callback) for i in songids if i in range(len(self.songlist))]
            
    def download(self, remote_uri, local_uri, callback=None):
        '''下载remote_uri到local_uri'''
        cache_uri = local_uri + '.downloading'
        self.T = self.startT = time.time()
        (self.D, self.speed) = (0, 0)
        c = callback if callback else self.update_progress
        if not self.downalbumnow:
            c(-1, os.path.basename(local_uri), '') #-1做为开始信号
        urllib.urlretrieve(remote_uri, cache_uri, c)
        c(-2, os.path.basename(local_uri), '') #-2做为结束信号
        speed = os.stat(cache_uri).st_size / (time.time() - self.startT)

        if callback == None:
            print '\r[' + '=' * 50 + '] 100.00%%  %s/s       ' % sizeread(speed)
        os.rename(cache_uri, local_uri)

    def update_progress(self, blocks, block_size, total_size):
        '''默认的进度显示的回调函数'''
        if total_size > 0 and blocks >= 0:
            percentage = float(blocks) / (total_size / block_size + 1) * 100
            if int(time.time()) != int(self.T):
                self.speed = (blocks * block_size - self.D) / (time.time() - self.T)
                (self.D, self.T) = (blocks * block_size, time.time())
            print '\r[' + '=' * (int)(percentage / 2) + '>' + \
                ' ' * (int)(50 - percentage / 2) + \
                (']  %0.2f%%  %s/s    ' % (percentage, sizeread(self.speed))),
    def update_null(self, arg1, arg2, arg3):
        '''下载歌词或封面时用的回调函数，啥都不显示'''
        pass
        
    def get_list(self, stype, callback=None, updateTreeView=None):
        '''获取特定榜单'''
        self.downalbumnow = False
        if stype in self.cached_list:
            self.songlist = copy.copy(self.cached_list[stype])
            return
        
        if stype in songlists:
            p = ListParser()
            print u'正在获取"' + stype + u'"的歌曲列表',
            sys.stdout.flush()
            for i in range(0, songlists[stype][1], 25):
                html = self.get_url_html(list_url_template % (songlists[stype][0], i))
                p.feed(html)
                print '.',
                sys.stdout.flush()
                if callback:
                    callback(int(i / 25) + 1, (songlists[stype][1] / 25))
            print 'done!'
            self.songlist = p.songlist
            self.cached_list[stype] = copy.copy(p.songlist)
            
            updateTreeView(p.songlist)
            
        else:
            #TODO:raise Exception
            print u'未知列表:"' + str(stype) + u'",仅支持以下列表: ' + u'、'.join(
            ['"%s"' % key for key in songlists])
            log.debug('Unknow list:"' + str(stype))
    
    def get_album_IDs(self, albumlist_name, callback=None, updateTreeView=None):
        '''获取专辑列表中的专辑ID'''
        if 'aid_' + albumlist_name in self.cached_list:
            self.albumlist = copy.copy(self.cached_list['aid_' + albumlist_name])
            return
        if albumlist_name in albums_lists:
            p = AlbumListParser()
            print u'正在获取"' + albumlist_name + u'"的专辑列表',
            sys.stdout.flush()
            for i in range(0, albums_lists[albumlist_name][1], 10):
                html = self.get_url_html(albums_list_url_template % (albums_lists[albumlist_name][0], i))
                p.feed(html)
                print '.',
                sys.stdout.flush()
                if callback:
                    callback(int(i / 10) + 1, (albums_lists[albumlist_name][1] / 10))
            print 'done!'
            self.albumlist = p.albumlist
            
            updateTreeView(p.albumlist)
            self.cached_list['aid_' + albumlist_name] = copy.copy(p.albumlist)
        else:
            #TODO:raise Exception
            print u'未知专辑列表:"' + str(albumlist_name) + u'",仅支持以下列表: ' + u'、'.join(
            ['"%s"' % key for key in albums_lists])

    def get_albumlist(self, albumnum):
        '''获取专辑的信息，包括专辑名、歌手名和歌曲列表'''
        albumid = self.albumlist[albumnum]['id']
        self.downalbumnow = True
        if 'a_' + albumid in self.cached_list:
            self.songlist = copy.copy(self.cached_list['a_' + albumid][0])
            self.albuminfo = copy.copy(self.cached_list['a_' + albumid][1])
            return
        
        #p = ListParser()
        p = XmlAlbumParser()
        print u'正在获取专辑信息',
        sys.stdout.flush()
        #html = self.get_url_html(album_song_list_url_template%albumid)
        #p.feed(html)
        #统一用get_url_html读取数据,日后如果要换user-agent之类也方便维护
        xml = self.get_url_html(xml_album_song_list_url_template % albumid, need_pre_deal=False)
        p.feed(xml)

        print 'done!'
        self.songlist = p.songlist
        self.albuminfo = p.albuminfo
        self.cached_list['a_' + albumid] = copy.copy((p.songlist, p.albuminfo))

    def downalbums(self, albumids=[], callback=None):
        '''下载专辑列表的特定几个专辑,传入序号的列表指定要下载的专辑'''
        [self.downalbum(i, callback) for i in albumids if i in range(len(self.albumlist))]
    def downallalbum(self, callback=None):
        '''下载专辑列表的所有专辑'''
        [self.downalbum(i, callback) for i in range(len(self.albumlist))]

    def downalbum(self, albumnum, callback=None):
        '''下载整个专辑'''
        self.get_albumlist(albumnum)
        print u'专辑名:' + self.albuminfo['title']
        print u'歌手名:' + self.albuminfo['artist']
        self.listall()

        if config.item['cover']:
            nameinfo = self.createdir_getfilename(0)
            cover_filename = os.path.join(os.path.dirname(nameinfo[0]), "cover.jpg")
            if not os.path.exists(cover_filename):
                self.download(self.albuminfo['cover'], cover_filename, self.update_null)

        self.downall(callback)
        
    def __get_pnum_by_html(self, html):
        next_page_match = re.match(r'.*href="(.*?)" id="next_page"', html, re.S)
        if next_page_match:
            next_page_href = next_page_match.group(1)
            next_page_num = re.match(r'.*start%3D(\d*?)&', next_page_href).group(1)
            return int(next_page_num)
        else:
            return None
        
    def search(self, key, callback=None):
        '''搜索关键字'''
        self.downalbumnow = False
        if 's_' + key in self.cached_list:
            self.songlist = copy.copy(self.cached_list['s_' + key])
            return

        key = re.sub((r'\ '), '+', key)
        p = ListParser()
        print u'正在获取"' + key + u'"的搜索结果列表...',
        sys.stdout.flush()
        pnum = 0
        while isinstance(pnum, int):
            html = self.get_url_html(search_url_template % (key, pnum))
            p.feed(html)
            pnum = self.__get_pnum_by_html(html)
            print '.',
            sys.stdout.flush()
        print 'done!'
        self.songlist = p.songlist
        self.cached_list['s_' + key] = copy.copy(p.songlist)
        
        if callback:
            callback(self.songlist)
               
    def searchalbum(self, key,callback=None):
        '''搜索关键字'''
        if 'said_' + key in self.cached_list:
            self.albumlist = copy.copy(self.cached_list['said_' + key])
            return

        key = re.sub((r'\ '), '+', key)
        p = AlbumListParser()
        print u'正在获取"' + key + u'"的专辑搜索结果列表...',
        sys.stdout.flush()
        pnum = 0
        while isinstance(pnum, int):
            html = self.get_url_html(albums_search_url_template % (key, pnum))
            p.feed(html)
            pnum = self.__get_pnum_by_html(html)
            print '.',
            sys.stdout.flush()
        print 'done!'
        self.albumlist = p.albumlist
        self.cached_list['said_' + key] = copy.copy(p.albumlist)
        
        if callback:
            callback(p.albumlist)
        
#全局实例化
gmbox = Gmbox()
