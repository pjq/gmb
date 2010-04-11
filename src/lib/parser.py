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


import re
from HTMLParser import HTMLParser
import logging
from utils import get_attrs_value_by_name

import xml.dom.minidom

log = logging.getLogger('lib.parser')


class XmlAlbumParser():
    '''解析专辑'''
    def __init__(self):
        self.songlist = []
        self.songtemplate = {
            'title':'',
            'artist':'',
            'album':'',
            'id':''}
        self.tmpsong = self.songtemplate.copy()
        self.albuminfo = {
            'title':'',
            'artist':'',
            'time':'',
            'company':''}
        self.dom = None

    def feed(self, str_xml):
        self.dom = xml.dom.minidom.parseString(str_xml)
        self.albuminfo['title'] = self.__read_dom_text('name')
        self.albuminfo['artist'] = self.__read_dom_text('artist')
        self.albuminfo['time'] = self.__read_dom_text('releaseDate')
        self.albuminfo['cover'] = self.__read_dom_text('thumbnailLink').replace("size=2", "size=4")
        self.__read_song()

    def __read_dom_text(self, key):
        '''读dom中的节点值'''
        if self.dom.getElementsByTagName(key):
            return self.dom.getElementsByTagName(key)[0].childNodes[0].data

    def __read_song(self):
        for song in self.dom.getElementsByTagName('song'):
            if 'true' == song.getElementsByTagName('canBeDownloaded')[0].firstChild.data:
                self.tmpsong['id'] = song.getElementsByTagName('id')[0].firstChild.data
                self.tmpsong['title'] = song.getElementsByTagName('name')[0].firstChild.data
                self.tmpsong['artist'] = u'、'.join([
                    node.firstChild.data for node in song.getElementsByTagName('artist')])
                self.tmpsong['album'] = song.getElementsByTagName('album')[0].firstChild.data
                self.songlist.append(self.tmpsong)
                self.tmpsong = self.songtemplate.copy()

class ListParser(HTMLParser):
    '''解析榜单列表页面的类'''
    
    def __init__(self):
        HTMLParser.__init__(self)
        self.songlist = []
        self.songtemplate = {
            'title':'',
            'artist':'',
            'album':'',
            'id':''}
        self.tmpsong = self.songtemplate.copy()
        (self.isa, self.ispan, self.insongtable, self.tdclass) = (0, 0, 0, '')
        self.albuminfo = {
            'title':'',
            'artist':'',
            'time':'',
            'company':''}
        self.inalbumtable = 0
        self.albumisfirsttitle = True
        self.albumdescriptiontimes = 0    
    
    def handle_starttag(self, tag, attrs):
        '''处理标签开始的函数'''
        if tag == 'a':
            self.isa = 1
            if self.insongtable and 'Icon' in self.tdclass:
                if get_attrs_value_by_name(attrs,'title')==u'下载':
                    self.tmpsong['id'] = re.match(r'.*id%3D(.*?)\\x26.*',
                        get_attrs_value_by_name(attrs, 'onclick'), re.S).group(1)
                    self.songlist.append(self.tmpsong)
        if tag == 'table':
            if get_attrs_value_by_name(attrs,'id') == 'song_list':
                self.insongtable = 1
            if get_attrs_value_by_name(attrs,'id') == 'album_item':
                self.inalbumtable = 1

        if self.insongtable and tag == 'td':
            self.tdclass = get_attrs_value_by_name(attrs, 'class')
            if 'Title' in self.tdclass:
                self.tmpsong = self.songtemplate.copy()
        if self.inalbumtable and tag == 'td':
            self.tdclass = get_attrs_value_by_name(attrs, 'class')
        if tag == 'span':
            self.ispan = 1

    def handle_endtag(self, tag):
        '''处理标签结束的函数'''
        if tag == 'a':
            self.isa = 0
        if tag == 'table':
            self.insongtable = 0
            self.inalbumtable = 0            
        if tag == 'span':
            self.ispan = 0

    def handle_data(self, data):
        '''处理html节点数据的函数'''
        if self.insongtable and (self.isa or self.ispan):
            if 'Title' in self.tdclass:
                self.tmpsong['title'] += data
            elif 'Artist' in self.tdclass:
                self.tmpsong['artist'] += (u'、' if self.tmpsong['artist'] else '') + data
            elif 'Album' in self.tdclass:
                self.tmpsong['album'] = data

        if self.inalbumtable:
            if self.tdclass and 'Title' in self.tdclass and self.albumisfirsttitle:
                self.albuminfo['title'] = data
                if self.albuminfo['title'].startswith(u'《'):
                    self.albuminfo['title'] = self.albuminfo['title'].replace(u'《','')
                    self.albuminfo['title'] = self.albuminfo['title'].replace(u'》','')
                self.albumisfirsttitle = False
            if self.tdclass == 'Description':
                if self.albumdescriptiontimes == 1:
                    self.albuminfo['artist'] = data
                elif self.albumdescriptiontimes == 3:
                    self.albuminfo['time'] = data
                elif self.albumdescriptiontimes == 4:
                    self.albuminfo['company'] = data
                self.albumdescriptiontimes += 1
                
    def __str__(self):
        return '\n'.join(['Title="%s" Artist="%s" ID="%s"'%
            (song['title'],song['artist'],song['id']) for song in self.songlist]) \
            +u'\n共 '+str(len(self.songlist))+u' 首歌.'

    
class SongParser(HTMLParser):
    '''解析歌曲页面,得到真实的歌曲下载地址'''
    def __init__(self):
        HTMLParser.__init__(self)
        self.url = ''
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for (n, v) in attrs:
                if n == 'href' and re.match(r'/music/top100/url.*', v):
                    self.url = 'http://www.google.cn' + v
    def __str__(self):
        return self.url

class AlbumListParser(HTMLParser):
    '''解析专辑列表页面,得到专辑名字和ID'''
    def __init__(self):
        HTMLParser.__init__(self)
        self.albumlist = []
        self.albumtemplate = {
            'name':'',
            'memo':'',
            'id':''}
        self.inAlbumInfoTable, self.inTitleTd, self.inMemoTd, self.inLinkA = False, False, False, False
    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            if get_attrs_value_by_name(attrs, 'class') == 'AlbumInfo':
                self.inAlbumInfoTable = True
        if tag == 'td':
            if get_attrs_value_by_name(attrs, 'class') == 'Title':
                self.inTitleTd = True
            if get_attrs_value_by_name(attrs, 'class') == 'Tracks':
                self.inMemoTd = True
        if tag == 'a':
            if get_attrs_value_by_name(attrs, 'name') == 'LandingPageLink':
                self.inLinkA = True
                href = get_attrs_value_by_name(attrs, 'href')
                self.tmpalbum = self.albumtemplate.copy()
                self.tmpalbum['id'] = re.match(r'.*id%3D(.*?)&resnum.*', href, re.S).group(1)
    def handle_data(self, data):
        if self.inLinkA:
            self.tmpalbum['name'] = data.replace(u'《', '').replace(u'》', '')
        if self.inMemoTd:
            self.tmpalbum['memo'] = data
            self.albumlist.append(self.tmpalbum)
    def handle_endtag(self, tag):
        if tag == 'a':
            self.inLinkA = False
        if tag == 'table':
            self.inAlbumInfoTable = False
        if tag == 'td':
            self.inTitleTd, self.inMemoTd = False, False
    
if __name__ == '__main__':
    #p=ListParser()
    #p.feed(open("search_res.html").read())
    p = XmlAlbumParser()
    p.feed(open("B5da7060c09165b61.xml").read())
    print p.songlist, p.albuminfo
