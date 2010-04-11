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


class album_page:
    """
    album page
    """
    
    def __init__(self, main_layout):
        """
        init
        """
        print 'init album_page'
        
        self.main_layout = main_layout
        #album page init
        self.music_album_treeview = self.main_layout.get_widget(music_album_treeview);  
        self.music_album_combo = self.main_layout.get_widget(music_album_combo); 
        self.music_album_liststore = gtk.ListStore(bool, str, str, str, str)
        self.music_album_treeview.set_model(self.music_album_liststore)  
        self.music_album_treeview.connect("button-press-event", self.music_album_treeview_clicked_check)
        self.addMusicColumn(self.music_album_treeview, music_column_list)
        self.addMusicAlbumCombo(self.music_album_combo)
        
        #Get progressbar
        self.progressbar = self.main_layout.get_widget(progressbar); 
        
        
    def addMusicColumn(self, treeview, column_list=music_column_list):
        """
        Add all the column to the treeview.
        """
        treeview.get_selection().set_mode(gtk.SELECTION_SINGLE)
        i = 0
        while i < column_list.__len__():            
            self.addOneMusicColumn(treeview, i, column_list[i])
            i = i + 1
             
        
        #column = gtk.TreeViewColumn(title, gtk.CellRendererText()
        #    , text=columnId)
        #column.set_resizable(True)        
        #column.set_sort_column_id(columnId)
        #self.wineView.append_column(column)
        
    def addOneMusicColumn(self, treeview , columnId, title):
        """
        Add just one Column
        """
        #selected
        if title == music_column_list[0]:
            renderer = gtk.CellRendererToggle()
            renderer.connect('toggled', self.selected_toggled)
            #column = gtk.TreeViewColumn("选中", renderer,active=COL_STATUS)
            #column = gtk.TreeViewColumn("选中", renderer,text=COL_STATUS)
            column = gtk.TreeViewColumn(title, renderer)
            column.set_resizable(True)
            treeview.append_column(column) 
        else:
            #ID,music,singer,details         
            renderer = gtk.CellRendererText()
            renderer.set_data("column", columnId)
            column = gtk.TreeViewColumn(title, renderer, text=columnId)
            column.set_resizable(True)
            treeview.append_column(column) 
            
            
    def selected_toggled(self, cell, path):
        # get toggled iter
        iter = self.music_list_liststore.get_iter((int(path),))
        fixed = self.music_list_liststore.get_value(iter, COL_STATUS)
        # do something with the value
        fixed = not fixed

        print "Now is Selected= ", fixed

        if not fixed:
            print 'Select[row]:', path
        else:
            print 'Invert Select[row]:', path

        # set new value
        self.music_list_liststore.set(iter, COL_STATUS, fixed)      
        
        
    def createMusicItem(self, selected, id, music, singer, detail):
        """
        Create a music item,and can add it to the music list
        """
        #checkbox = gtk.CheckButton()
        return [selected, id, music, singer, detail]
    
   
              
    def addMusicAlbumCombo(self, combo):
        """
        Add all the music type to the combox list
        """
        store = gtk.ListStore(str)
        
        store.append(['-Select-'])
        
        [store.append([alist]) for alist in albums_lists]
        
        combo.set_model(store)
        cell = gtk.CellRendererText()
        combo.pack_start(cell, True)
        combo.add_attribute(cell, 'text', 0)
        combo.set_active(0)
        combo.connect("changed", self.getMusicAlbumlistThread)
        
    def getMusicAlbumlistThread(self, widget):
        """
        Get Music Albumlist Thread
        """
        thead = threading.Thread(target=self.getMusicAlbumlist, args=(widget, None))
        thead.start()
                
    def getMusicAlbumlist(self, widget, data):
        """
        get the music list according to the selected music type
        """
        text = widget.get_active_text().decode('utf8')
        
        if text != '-Select-':
            self.music_album_combo.set_sensitive(False)
            print 'Selected music type=', text
            gmbox.get_album_IDs(text, self.updatePageDownloadProgress, self.updateMusicAlbumTreeView)
     
    def updatePageDownloadProgress(self, current_page=0, total_pages=100):
        """
        Update the download progress bar.
        """
        
        print 'updatePageDownloadProgress,count=', current_page, "total=", total_pages
        
        self.progressbar.set_fraction(float(current_page) / total_pages)

            
    def updateMusicAlbumTreeView(self, songlist):
        """
        After get the songlist,should update the treeview
        """
        print 'updateTreeView,songlist=', songlist
        self.music_album_liststore.clear()
        self.music_album_combo.set_sensitive(True)
        i = 1
       
        for song in songlist:
            #print song
            music = song['name']
            singer = song['memo']
            detail = albums_list_url_template%song['id']
            print music, singer,detail
            self.music_album_liststore.append(self.createMusicItem(False, i, music, singer , detail)) 
            i = i + 1   
        
        
    def music_album_treeview_clicked_check(self, view, event):
        """
        When click the right button of the mouse,run here.
        """
        print 'treeview_clicked_check'
        
        self.get_album_current_location(event.x, event.y)
        
        if event.button == 3:
            if gmbox.albumlist != None:
                self.showMusicAlbumPopUPMenu()  
                
                
    def get_album_current_location(self, x, y):
        '''Used for save path of mouse click position'''

        pth = self.music_album_treeview.get_path_at_pos(int(x), int(y))

        if pth:
            path, col, cell_x, cell_y = pth
            self.album_current_selection = int(path[0])
            #log.debug('select index : %d' % self.album_current_selection)
        else:
            self.album_current_selection = None      
            
            
        
    def showMusicAlbumPopUPMenu(self):
        """
        Show PopUP Menu when click the right button of the mouse.
        """
        print 'showPopUPMenu'
        time = gtk.get_current_event_time()
        popupmenu = gtk.Menu()
        menuitem = gtk.MenuItem('下载')
        menuitem.connect('activate', lambda w:self.downloadAlbumSelection(self.album_current_selection))
        popupmenu.append(menuitem)
        
        popupmenu.show_all()
        popupmenu.popup(None, None, None, 0, time)
        
        
    def downloadAlbumSelection(self, selection):
        """
        Start to download the selection song.
        """
        print 'downloadSelection,selection=', selection, "type of selection=", type(selection)
        
        
        if type(selection) == int:
            #print "type of selection=int"
            down_thread = threading.Thread(target=gmbox.downalbum, args=(selection, None))
            #Should add the callback 
            #down_thread = threading.Thread(target=gmbox.downone, args=(selection, self.updateProgress))
        else:
            down_thread = threading.Thread(target=gmbox.down_listed, args=(selection, self.updateProgress))
        
        down_thread.start()
        
    def updateProgress(self, current_page=0, total_pages=100):
        """
        Update the download progress bar.
        """
        
        print 'updateProgress,count=', current_page, "total=", total_pages
        
        self.progressbar.set_fraction(float(current_page) / total_pages)
