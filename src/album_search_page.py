#!/usr/bin/env python
#*_*-coding:utf8-*_*
'''
Created on 2010-4-11

@author: pjq
'''

import gtk
import threading
from config import *

from lib.core import gmbox
from utils import select_all

class album_search_page:
    """
    music search page 
    """
    
    def __init__(self, main_layout):
        """
        music search init
        """
        print 'init music_search_page'
        self.main_layout = main_layout
             
        #music page init
        self.album_search_page_treeview = self.main_layout.get_widget(album_search_page_treeview);  
        self.album_search_page_go = self.main_layout.get_widget(album_search_page_go); 
        self.album_search_page_entry = self.main_layout.get_widget(album_search_page_entry);
        self.album_search_page_download_selected = self.main_layout.get_widget(album_search_page_download_selected)
        self.album_search_page_selectall = self.main_layout.get_widget(album_search_page_selectall) 
               
        self.album_search_liststore = gtk.ListStore(bool, str, str, str, str)
        self.album_search_page_treeview.set_model(self.album_search_liststore)  
        
        self.album_search_page_treeview.connect("button-press-event", self.album_search_page_treeview_clicked_check)
        self.album_search_page_selectall.connect('toggled', self.on_album_search_page_selectall)
        
        self.addMusicColumn(self.album_search_page_treeview, music_column_list)
        
        self.on_album_search_page_download_selected.connect('clicked', self.on_album_search_page_download_selected)
        self.album_search_page_go.connect("clicked", self.album_search)        
        self.album_search_page_entry.connect("key-press-event", self.on_album_search_page_entry_key_press)  
                
        #Get progressbar
        self.progressbar = self.main_layout.get_widget(progressbar);        
 
    def on_album_search_page_entry_key_press(self, window, event):  
        """
        Music search entry press key handle,here just handle "Enter" key.Press "Enter" to do the search
        """
        keyname = gtk.gdk.keyval_name(event.keyval)  
        #print 'keyname=', keyname
        if keyname == "Return":  
            print 'Is Enter,start search'
            self.album_search()  
    
    def album_search(self, widget=None):
        """
        Press the "Go" Button will search music with the key
        """
        key_words = self.album_search_page_entry.get_text()
        
        print 'Search Album:', key_words
        self.getMusicAlbumThread(key_words)   
    
    def on_album_search_page_selectall(self, widget):
        """
        Select all
        """
        select_all(self.album_search_liststore, widget)    
        
    def album_search_page_treeview_clicked_check(self, view, event):
        """
        When click the right button of the mouse,run here.
        """
        print 'treeview_clicked_check'
        
        self.get_current_location(event.x, event.y) 
        
        if event.button == 3:
            if gmbox.songlist != None:
                self.showPopUPMenu()

    def get_current_location(self, x, y):
        '''Used for save path of mouse click position'''

        pth = self.album_search_page_treeview.get_path_at_pos(int(x), int(y))

        if pth:
            path, col, cell_x, cell_y = pth
            self.current_selection = int(path[0])
            #log.debug('select index : %d' % self.current_selection)
        else:
            self.current_selection = None
                
    def showPopUPMenu(self):
        """
        Show PopUP Menu when click the right button of the mouse.
        """
        print 'showPopUPMenu'
        time = gtk.get_current_event_time()
        popupmenu = gtk.Menu()
        menuitem = gtk.MenuItem('下载')
        menuitem.connect('activate', lambda w:self.downloadSelection(self.current_selection))
        popupmenu.append(menuitem)
        
        menuitem = gtk.MenuItem('试听')
        menuitem.connect('activate', lambda w:self.listenSelection(self.current_selection))
        popupmenu.append(menuitem)
        
        popupmenu.show_all()
        popupmenu.popup(None, None, None, 0, time)
        
    def on_album_search_page_download_selected(self, widget):
        print 'on_album_search_page_download_selected'
        length = len(self.album_search_liststore)
        
        selected = [i for i in range(length) \
                         if self.album_search_liststore.get_value \
                         (self.album_search_liststore.get_iter((i,)), COL_STATUS) ]
        
        self.downloadSelection(selected)
        
    def downloadSelection(self, selection):
        """
        Start to download the selection song.
        """
        print 'downloadSelection,selection=', selection, "type of selection=", type(selection)
        
        
        if type(selection) == int:
            #print "type of selection=int"
            down_thread = threading.Thread(target=gmbox.downalbum, args=(selection, self.updateProgress))
            #Should add the callback 
            #down_thread = threading.Thread(target=gmbox.downone, args=(selection, self.updateProgress))
        else:
            down_thread = threading.Thread(target=gmbox.down_listed, args=(selection, self.updateProgress))
        
        down_thread.start()
        
    def listenSelection(self, selection):
        """
        Listen the selected music
        """
        print 'listenSelection,selection=', selection
                
                
    def addMusicColumn(self, treeview, column_list=music_column_list):
        """
        Add all the column to the treeview.
        """
        treeview.get_selection().set_mode(gtk.SELECTION_SINGLE)
        i = 0
        while i < column_list.__len__():            
            self.addOneMusicColumn(treeview, i, column_list[i])
            i = i + 1

        
    def addOneMusicColumn(self, treeview , columnId, title):
        """
        Add just one Column
        """
        #selected
        if title == music_column_list[0]:
            renderer = gtk.CellRendererToggle()
            renderer.connect('toggled', self.selected_toggled)
            renderer.set_active(True)
            #column = gtk.TreeViewColumn("选中", renderer,active=COL_STATUS)
            #column = gtk.TreeViewColumn("选中", renderer,text=COL_STATUS)
            column = gtk.TreeViewColumn(title, renderer, active=COL_STATUS)
            column.set_resizable(True)
            treeview.append_column(column) 
        else:
            #ID,music,singer,details         
            renderer = gtk.CellRendererText()
            renderer.set_data("column", columnId)
            column = gtk.TreeViewColumn(title, renderer, text=columnId)
            column.set_resizable(True)
            treeview.append_column(column) 
    
            
    def addMusicListCombo(self, combo):
        """
        Add all the music type to the combox list
        """
        print 'Init combox'        
        store = gtk.ListStore(str)
        
        store.append(['-Select-'])
        
        [store.append([alist]) for alist in songlists]
        
        combo.set_model(store)
        cell = gtk.CellRendererText()
        combo.pack_start(cell, True)
        combo.add_attribute(cell, 'text', 0)
        combo.set_active(0)
        combo.connect("changed", self.getMusiclistThread)
        
    def selected_toggled(self, cell, path):
        # get toggled iter
        iter = self.album_search_liststore.get_iter((int(path),))
        fixed = self.album_search_liststore.get_value(iter, COL_STATUS)
        # do something with the value
        fixed = not fixed

        print "Now is Selected= ", fixed

        if not fixed:
            print 'Select[row]:', path
        else:
            print 'Invert Select[row]:', path

        # set new value
        self.album_search_liststore.set(iter, COL_STATUS, fixed)    
    
    def getMusicAlbumThread(self, keywords):
        """
        Search  the Album and get the list  in a thread
        """
        print 'getMusicAlbumThread'
       
        self.album_search_page_go.set_sensitive(False)
        thread = threading.Thread(target=self.getAlbumlist, args=(keywords, None))
        thread.start()
        
        
                
    def getAlbumlist(self, keywords, data):
        """
        get the album list according to the key words
       """
              
        if keywords != None:
            #gmbox.search(keywords, self.updateTreeView)
            gmbox.searchalbum(keywords, self.updateTreeView)
            
    def updateTreeView(self, songlist):
        """
        After get the Album list,should update the treeview
        """
        print 'updateTreeView'
        
        self.album_search_page_go.set_sensitive(True)
        self.album_search_liststore.clear()
        
        #songlist = gmbox.songlist
        i = 1
       
        for song in songlist:
            #print song
            music = song['name']
            singer = song['memo']
            detail = album_song_list_url_template % (song['id'])
            print music, singer, detail
            print music, singer, detail
            self.album_search_liststore.append(self.createMusicItem(False, i, music, singer , detail)) 
            i = i + 1        

    def createMusicItem(self, selected, id, music, singer, detail):
        """
        Create a music item,and can add it to the music list
        """
        #checkbox = gtk.CheckButton()
        return [selected, id, music, singer, detail]
    
    def updateProgress(self, blocks, block_size, total_size):
        """
        Update the download progress bar.
        """
        
        #print 'updateProgress,blocks=', blocks, 'block_size=', block_size, "total_size=", total_size
        if blocks == -1:
            self.progressbar.set_fraction(0)
        elif blocks == -2:
            print ''
            self.progressbar.set_fraction(1)
        else :
            self.progressbar.set_fraction(float(block_size * blocks) / total_size)


if __name__ == '__main__':
    print 'music search page'
