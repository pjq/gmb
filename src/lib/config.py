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

import xml.dom.minidom
import os,shutil,codecs
from utils import find_image_or_data,module_path

class Config():
    def __init__(self):
        '''初始化'''
        self.item={}
        userhome = os.path.expanduser('~')
        self.config_folder = os.path.join(userhome,'.gmbox')
        self.config_file = os.path.join(self.config_folder,'config.xml')
        if not os.path.isdir(self.config_folder):
            os.mkdir(self.config_folder)
        if not os.path.exists(self.config_file):
            config_sample_file=find_image_or_data('config.xml.sample',module_path(),'data')
            print module_path()
            print config_sample_file
            shutil.copy(config_sample_file,self.config_file)
            if not os.path.exists(self.config_file):
                print u'创建配置文件失败!',self.config_file
            else:
                print u'创建配置文件成功!',self.config_file
                self.read_config()
                
                self.savedir_changed(self.item['savedir'])
                if os.name!='posix':
                    self.id3utf8_changed('False')
        else:
            self.read_config()
    
    def read_config(self):
        '''读配置文件'''
        self.dom=xml.dom.minidom.parse(self.config_file)
        self.item['savedir']=self.__read_dom_text('savedir')
        self.item['id3utf8']=self.__read_dom_text('id3utf8')=='True'
        self.item['makealbumdir']=self.__read_dom_text('makealbumdir')=='True'
        
    def __read_dom_text(self,key):
        '''读dom中的节点值'''
        if self.dom.getElementsByTagName(key):
            return self.dom.getElementsByTagName(key)[0].childNodes[0].data
    def __set_dom_text(self,key,value):
        '''写dom中的节点值,同步到文件'''
        if self.dom.getElementsByTagName(key):
            self.dom.getElementsByTagName(key)[0].childNodes[0].data=value
        else:
            self.__add_an_option(key,value)
        self.write_to_file()
    def __add_an_option(self,key,value):
        '''在配置文件中增加一项,用于在老版本的配置文件里插入新的配置项'''
        impl=xml.dom.minidom.getDOMImplementation()
        doc=impl.createDocument(None, key, None)
        elmt=doc.documentElement
        text=doc.createTextNode(value)
        elmt.appendChild(text)
        self.dom.getElementsByTagName('gmbox')[0].appendChild(elmt)
        
    def savedir_changed(self,newvalue):
        '''更改歌曲保存目录'''
        v=os.path.abspath(os.path.expanduser(newvalue))
        if os.path.exists(v):
            if not os.path.isdir(v):
                print u'错误:',v,u'已存在!'
                return
        else:
            try:
                os.mkdir(v)
            except OSError:
                print u'错误:',v,u'创建目录失败!'
                return
        print u'配置: savedir =>',v
        self.item['savedir'] = v
        self.__set_dom_text('savedir',v)
    def id3utf8_changed(self,newvalue):
        '''更改是否更新ID3信息'''
        v=True if newvalue in [True,'True','true','1','on'] else False
        print u'配置: id3utf8 =>',v
        self.item['id3utf8'] = v
        self.__set_dom_text('id3utf8',str(v))
    def makealbumdir_changed(self,newvalue):
        '''更改是否更新ID3信息'''
        v=True if newvalue in [True,'True','true','1','on'] else False
        print u'配置: makealbumdir =>',v
        self.item['makealbumdir'] = v
        self.__set_dom_text('makealbumdir',str(v))
        
    def write_to_file(self):
        '''把dom写到配置文件'''
        f = file(self.config_file, 'wb')
        writer = codecs.lookup('utf-8')[3](f)
        self.dom.writexml(writer, encoding = 'utf-8')
config=Config()
"""
from xml.dom import minidom
import codecs
import os

from gmbox import *

# more work:
# 1.ConfigFile inherit from minidom
# 2.Use logging modudle instead of print sentence
# 3.Get music dir from preference tab
# 4.more comments make other's work better
# 5.take some attribute open and close more
# 6.maybe ini file is better!!!


musicdir=userhome+'/Music/google_music/top100/'
playlist_path=gmbox_home+'default.xml'
gmbox_home=userhome+'/.gmbox/'

class ConfigFile():
    '''读写配置文件'''
    def __init__(self):

        configfile = os.path.expanduser('~/.gmbox/gmboxrc')
        
        if os.path.exists(configfile):
            print "found config file 'gmboxrc' , begin to init..."
            self.xmldoc = minidom.parse(configfile)
            self.set_musicdir()
            self.set_playlist_path()
        else:
            print "No config file 'gmboxrc' found, so create it..."
            self.init_configfile()
            

    def init_configfile(self):

        impl = minidom.getDOMImplementation()
        self.xmldoc = impl.createDocument(None, 'gmbox_config', None)
        root = self.xmldoc.documentElement
        node = self.xmldoc.createElement("music_dir")
        node.setAttribute("id","e1")
        text = self.xmldoc.createTextNode(musicdir)
        node.appendChild(text)
        root.appendChild(node)
        node = self.xmldoc.createElement("playlist_path")
        node.setAttribute("id","e2")
        text = self.xmldoc.createTextNode(playlist_path)
        node.appendChild(text)
        root.appendChild(node)
        f = file(gmbox_home+'gmboxrc','w')
        writer = codecs.lookup('utf-8')[3](f)
        #self.xmldoc.writexml(writer,"  ", "","\n    ","UTF-8")
        #self.xmldoc.writexml(writer,"  ", "","\n","UTF-8")
        self.xmldoc.writexml(writer)
        writer.close

        
    def set_keybing(self):
        
        actions = self.xmldoc.getElementsByTagName('action')
        for action in actions:
            name = item.getAttribute('name')

            
    def set_musicdir(self):

        root = self.xmldoc.documentElement
        #node = root.getElementById('e1')
        #node = root.getElementsByTagName('music_dir')
        #node = root.firstChild
        #musicdir = node.data
        musicdir = self.getTagText(root,"music_dir")
        print u'歌曲目录:',musicdir

        
    def set_playlist_path(self):
        
        root = self.xmldoc.documentElement
        #node = root.getElementByTagId('e2')
        #node = root.getElementsByTagName('playlist_path')
        #node = root.firstChild
        #playlist_path = node.data
        playlist_path = self.getTagText(root,"playlist_path")
        print u'播放列表:',playlist_path

        
    def getTagText(self,root,tag):
        '''得到文本节点的值'''
        
        node = root.getElementsByTagName(tag)[0]
        rc = ""
        for node in node.childNodes:
            #if node.nodeType in ( node.TEXT_NODE, node.CDATA_SECTION_NODE):
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
        return rc"""
