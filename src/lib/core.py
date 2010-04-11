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

import os, sys, copy, time, re, logging, urllib, urllib2

from parser import *
from const import *
from utils import *
from config import *

log = logging.getLogger('lib.core')

class Gmbox:
    '''核心模块,初始化完成以后,成为一个全局变量.
    功能包括:获取榜单,搜索歌曲,并维护一个当前列表,
    并且可以下载当前列表中的部分或全部歌曲,并集成缓存.'''
    
    def __init__(self):
        '''初始化一个空的gmbox对象'''
        self.songlist = []
        
        self.search_songlist = []
        
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

    def get_filename(self, i=0):
        '''生成当前列表的第i首歌曲的文件名'''
        song = self.songlist[i]
        filename = song['title'] + '-' + song['artist'] + '.mp3'
        print 'filename=', filename
        return filename

    def get_url_html(self, url):
        '''获取指定url的html'''
        print 'get url=', url
        try:
            html = urllib2.urlopen(url).read()
        except urllib2.URLError:
            print '网络错误,请检查网络...'
            return
        except:
            print '未知错误!请到这里报告bug: http://code.google.com/p/gmbox/issues/entry'
            return
        #预处理HTML
        html = re.sub(r'&#([0-9]{2,5});', unistr, html)
        html = re.sub(r'</?b>', '', html)
        html = entityref.sub(entityrefstr, html)
        #open('search_res.html','w').write(html)
        return html
        
    def find_final_uri(self, i=0):
        '''找到最终真实下载地址，以供下一步DownLoad类下载'''
        song = self.songlist[i]
        songurl = song_url_template % (song['id'],)
        html = self.get_url_html(songurl)
        s = SongParser()
        s.feed(html)
        return s.url

    def downone(self, i=0, callback=None):
        '''下载当然列表中的一首歌曲 '''
        print 'downlone,i=', i
        filename = self.get_filename(i)
        if config.item['makealbumdir'] and self.downalbumnow:
            albumpath = os.path.join(config.item['savedir'],
                self.albuminfo['title'] + '-' + self.albuminfo['artist'])
            if not os.path.isdir(albumpath):
                os.mkdir(albumpath)
            localuri = os.path.join(albumpath, filename)
        else:
            localuri = os.path.join(config.item['savedir'], filename)
        if os.path.exists(localuri):
            print filename, u'已存在!'
            return
        
        url = self.find_final_uri(i)
        if url:
            print u'正在下载:', filename
            if self.downalbumnow and callback:
                numinfo = "(" + str(i + 1) + " of " + str(len(self.songlist)) + ")"
                callback(-1, os.path.basename(localuri), numinfo) #-1做为开始信号
            self.download(url, localuri, callback=callback)
        else:   #下载页有验证码时url为空
            print '出错了,也许是google加了验证码,请换IP后再试或等24小时后再试...'

    def downall(self, callback=None):
        '''下载当然列表中的所有歌曲'''
        [self.downone(i, callback) for i in range(len(self.songlist))]

    def down_listed(self, songids=[], callback=None):
        '''下载当然列表的特定几首歌曲,传入序号的列表指定要下载的歌'''
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
        #下载和试听模式都一样
        if callback == None:
            print '\r[' + ''.join(['=' for i in range(50)]) + \
                '] 100.00%%  %s/s       ' % sizeread(speed)
        os.rename(cache_uri, local_uri)
        #TODO:以后转码函数需要移到download外面成为独立的函数.
        if config.item['id3utf8']:
            '''在Linux下转换到UTF 编码，现在只有comment里还是乱码'''
            os.system('mid3iconv -e gbk "' + local_uri + '"')

    def update_progress(self, blocks, block_size, total_size):
        '''默认的进度显示的回调函数'''
        if total_size > 0 and blocks >= 0:
            percentage = float(blocks) / (total_size / block_size + 1) * 100
            if int(time.time()) != int(self.T):
                self.speed = (blocks * block_size - self.D) / (time.time() - self.T)
                (self.D, self.T) = (blocks * block_size, time.time())
            print '\r[' + ''.join(['=' for i in range((int)(percentage / 2))]) + '>' + \
                ''.join([' ' for i in range((int)(50 - percentage / 2))]) + \
                (']  %0.2f%%  %s/s    ' % (percentage, sizeread(self.speed))),

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
            #for i in range(0, 25, 25):
                html = self.get_url_html(list_url_template % (songlists[stype][0], i))
                #print 'html=',html
                p.feed(html)
                print '.',
                sys.stdout.flush()
                if callback:
                    print ''                    
                    callback(int(i / 25) + 1, (songlists[stype][1] / 25))
            print 'done!'
            if updateTreeView:
                updateTreeView(p.songlist)
            self.songlist = p.songlist
            self.cached_list[stype] = copy.copy(p.songlist)
        else:
            #TODO:raise Exception
            print u'未知列表:"' + str(stype) + u'",仅支持以下列表: ' + u'、'.join(
            ['"%s"' % key for key in songlists])
            log.debug('Unknow list:"' + str(stype))
    
    def get_album_IDs(self, albumlist_name, callback=None):
        '''获取专辑列表中的专辑ID'''
        if 'aid_' + albumlist_name in self.cached_list:
            self.albumlist = copy.copy(self.cached_list['aid_' + albumlist_name])
            return
        if albumlist_name in albums_lists:
            p = AlbumListParser()
            print u'正在获取"' + albumlist_name + u'"的专辑列表',
            sys.stdout.flush()
            #for i in range(0, albums_lists[albumlist_name][1], 10):
            for i in range(0, 10, 10):
                html = self.get_url_html(albums_list_url_template % (albums_lists[albumlist_name][0], i))
                p.feed(html)
                print '.',
                sys.stdout.flush()
                if callback:
                    print ''
                    #callback(int(i/10)+1,(albums_lists[albumlist_name][1]/10))
            print 'done!'
            
            callback(p.albumlist)
            self.albumlist = p.albumlist
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
        
        p = ListParser()
        print u'正在获取专辑信息',
        sys.stdout.flush()
        html = self.get_url_html('http://www.google.cn/music/album?id=%s' % albumid)
        
        print html
        
        p.feed(html)
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
        self.downall(callback)
        
        
    def search(self, key, callback=None):
        '''搜索关键字'''
        self.downalbumnow = False
        if 's_' + key in self.cached_list:
            self.songlist = copy.copy(self.cached_list['s_' + key])
            return

        key = re.sub((r'\ '), '+', key)
        p = ListParser()
        print u'正在获取"' + key + u'"的专辑搜索结果列表...',
        sys.stdout.flush()
        html = self.get_url_html(search_url_template % key)
        p.feed(html)
        print 'done!'
        
        self.songlist = p.songlist        
        self.search_songlist = p.songlist
        
        if callback:
           callback(self.search_songlist)
        
        self.cached_list['s_' + key] = copy.copy(p.songlist)
    def searchalbum(self, key):
        '''搜索关键字'''
        if 'said_' + key in self.cached_list:
            self.albumlist = copy.copy(self.cached_list['said_' + key])
            return

        key = re.sub((r'\ '), '+', key)
        p = AlbumListParser()
        print u'正在获取"' + key + u'"的搜索结果列表...',
        sys.stdout.flush()
        html = self.get_url_html(albums_search_url_template % key)
        p.feed(html)
        print 'done!'
        self.albumlist = p.albumlist
        self.cached_list['said_' + key] = copy.copy(p.albumlist)
        
#全局实例化
gmbox = Gmbox()
