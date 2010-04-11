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




class music_page:
    """
    music  page 
    """

    
    def __init__(self, main_layout):
        """
        music  init
        """
        self.main_layout = main_layout
  
        #music page init
        self.music_list_treeview = self.main_layout.get_widget(music_list_treeview);  
        self.music_list_combo = self.main_layout.get_widget(music_list_combo); 
        self.music_list_liststore = gtk.ListStore(bool, str, str, str, str)
        self.music_list_treeview.set_model(self.music_list_liststore)  
        self.music_list_treeview.connect("button-press-event", self.music_list_treeview_clicked_check)
        self.addMusicColumn(self.music_list_treeview, music_column_list)
        self.addMusicListCombo(self.music_list_combo)
        
        #Get progressbar
        self.progressbar = self.main_layout.get_widget(progressbar); 
        
        self.music_page_download_selected = self.main_layout.get_widget(music_page_download_selected)
        self.music_page_download_selected.connect("clicked", self.on_music_page_download_selected)

        
        
    def on_music_page_download_selected(self, widget):
        print 'music_page_download_selected'
        
    def music_list_treeview_clicked_check(self, view, event):
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

        pth = self.music_list_treeview.get_path_at_pos(int(x), int(y))

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
        
        popupmenu.show_all()
        popupmenu.popup(None, None, None, 0, time)
        
    def downloadSelection(self, selection):
        """
        Start to download the selection song.
        """
        print 'downloadSelection,selection=', selection, "type of selection=", type(selection)
        
        
        if type(selection) == int:
            #print "type of selection=int"
            down_thread = threading.Thread(target=gmbox.downone, args=(selection, self.updateProgress))
            #Should add the callback 
            #down_thread = threading.Thread(target=gmbox.downone, args=(selection, self.updateProgress))
        else:
            down_thread = threading.Thread(target=gmbox.down_listed, args=(selection, self.updateProgress))
        
        down_thread.start()
                
                
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
    
    def getMusiclistThread(self, widget):
        """
        Get the Music List in a thread
        """
        print 'getMusiclistThread'
       
        
        thread = threading.Thread(target=self.getMusiclist, args=(widget, None))
        thread.start()
        
        
                
    def getMusiclist(self, widget, data):
        """
        get the music list according to the selected music type
        """
       
        text = widget.get_active_text().decode('utf8')
        
        if text != '-Select-':
            self.music_list_combo.set_sensitive(False)
            print 'Selected music type=', text
            gmbox.get_list(text, self.updatePageDownloadProgress, self.updateTreeView)
            
    def updateTreeView(self, songlist):
        """
        After get the songlist,should update the treeview
        """
        print 'updateTreeView'
        
        self.music_list_combo.set_sensitive(True)
        self.music_list_liststore.clear()
        
        #songlist = gmbox.songlist
        i = 1
       
        for song in songlist:
            #print song
            music = song['title']
            singer = song['artist']
            detail = song['album'] + ' ' + song['id']
            print music, singer, song_url_template % detail
            self.music_list_liststore.append(self.createMusicItem(False, i, music, singer , song_url_template % detail)) 
            i = i + 1        

    def createMusicItem(self, selected, id, music, singer, detail):
        """
        Create a music item,and can add it to the music list
        """
        #checkbox = gtk.CheckButton()
        return [selected, id, music, singer, detail]
    
    def updatePageDownloadProgress(self, current_page=0, total_pages=100):
        """
        Update the download progress bar.
        """
        
        print 'updatePageDownloadProgress,count=', current_page, "total=", total_pages
        
        self.progressbar.set_fraction(float(current_page) / total_pages)
        
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
    print 'music  page'
