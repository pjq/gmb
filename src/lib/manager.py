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



class DownloadLists(Abs_Lists):
    '''下载列表管理'''
    def __init__(self):
        Abs_Lists.__init__(self)

    def get_list(self):
        pass

    def add(self,title,artist,id):
        self.tmplist['artist']=artist
        self.tmplist['title']=title
        self.tmplist['id']=id
        self.songlist.append(self.tmplist.copy())
        self.tmplist=self.songtemplate.copy()
        self.downone(len(self.songlist)-1)

class FileList(Abs_Lists):
    '''本地文件列表'''
    def __init__(self,top):
        Abs_Lists.__init__(self)

    def get_list(self,top):
        self.walktree(top,self.visitfile)

    def walktree(self,top, callback):
        for log in os.listdir(top):
            pathname = os.path.join(top, log)
            mode = os.stat(pathname)[ST_MODE]
            if S_ISDIR(mode):
                # It's a directory, recurse into it
                self.walktree(pathname, callback)
            elif S_ISREG(mode):
                # It's a file, call the callback function
                callback(pathname)
            else:
                # Unknown file type, print a message
                print 'Skipping %s' % pathname

    def visitfile(self,file):
        size = os.path.getsize(file)
        mt = time.ctime(os.stat(file).st_mtime);
        ct = time.ctime(os.stat(file).st_ctime);
        if os.path.basename(file).split('.')[-1]=='cache':
            print 'ignoring '+os.path.basename(file)
            return
        if os.path.basename(file).split('.')[-1]=='downloading':
            print 'ignoring '+os.path.basename(file)
            return
        self.tmplist['artist']=os.path.basename(file).split('-')[1].split('.')[0]
        self.tmplist['title']=os.path.basename(file).split('-')[0]
        self.tmplist['id']=len(self.songlist)
        self.songlist.append(self.tmplist.copy())
        self.tmplist=self.songtemplate.copy()
        print 'adding '+os.path.basename(file)

    def delete_file(self,i):
        filename=self.get_filename()
        filename = unicode(filename,'utf8')
        local_uri = musicdir + filename
        os.remove(local_uri)

class PlayList(Abs_Lists):
    '''读写歌词文件'''
    #def __init__(self,config_file=gmbox_home+'default.xml'):
    def __init__(self,config_file=playlist_path):
        Abs_Lists.__init__(self)

        if os.path.exists(config_file):
            self.xmldoc = minidom.parse(config_file)
            items = self.xmldoc.getElementsByTagName('item')
            for item in items:
                title = item.getAttribute('title')
                artist = item.getAttribute('artist')
                id = item.getAttribute('id')
                self.tmplist['artist']=artist
                self.tmplist['title']=title
                self.tmplist['id']=id
                self.songlist.append(self.tmplist.copy())
                self.tmplist=self.songtemplate.copy()
        else:
            impl = minidom.getDOMImplementation()
            self.xmldoc = impl.createDocument(None, 'playlist', None)
            f = file(config_file,'w')
            writer = codecs.lookup('utf-8')[3](f)
            self.xmldoc.writexml(writer)
            writer.close
        self.root = self.xmldoc.documentElement

    def add(self,title,artist,id):
        item = self.xmldoc.createElement('item')
        item.setAttribute('title',title)
        item.setAttribute('artist',artist)
        item.setAttribute('id',id)
        self.root.appendChild(item)
        f = file(gmbox_home+'default.xml','w')
        writer = codecs.lookup('utf-8')[3](f)
        self.xmldoc.writexml(writer)
        writer.close

    def delete(self,index):
        item = self.getElementByIndex(index)
        self.root.removeChild(item)
        f = file(gmbox_home+'default.xml','w')
        writer = codecs.lookup('utf-8')[3](f)
        self.xmldoc.writexml(writer)
        writer.close

    def get_information(self,index):
        items = self.xmldoc.getElementsByTagName('item')
        print "the first item is :"
        print items[index].toxml()
    def getElementByIndex(self,index):
        items = self.xmldoc.getElementsByTagName('item')
        return items[index]
