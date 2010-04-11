#!/usr/bin/env python
#*_*-coding:utf8-*_*

'''
Created on 2010-4-9

@author: pjq
'''
import gtk
import gtk.glade
import threading
import gobject
import os, sys, copy, time, re, logging, urllib, urllib2
import utils

from lib.parser import *
from lib.core import gmbox

from lib.utils import find_image_or_data,module_path

from music_page import music_page
from album_page import album_page
from music_search_page import music_search_page
from config import *

class gmb:
    """
    This is the main class form GMB:Google Music Box
    """
    
    def __init__(self):
        """
        do some initialization here.
        """
        print '__init__'
        self.main_layout = gtk.glade.XML(gmb_main_layout)
        
        self.main_window=self.main_layout.get_widget(main_window)
        
        ui_logo = gtk.gdk.pixbuf_new_from_file(find_image_or_data('gmbox.png', module_path()))
        self.main_window.set_icon(ui_logo)
         
        music_page(self.main_layout)
        music_search_page(self.main_layout)
        album_page(self.main_layout)
        
        #Get progressbar
        self.progressbar = self.main_layout.get_widget(progressbar); 

  


def main():
    gtk.main()


if __name__ == '__main__':
    print 'gmb main'
    gobject.threads_init()
    gmb()
    gtk.main()
