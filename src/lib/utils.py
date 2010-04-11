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


import logging
import os, sys, re

def module_path():
    """ This will get us the program's directory,
    even if we are frozen using py2exe"""
    if hasattr(sys, "frozen"):
        return os.path.dirname(unicode(sys.executable, sys.getfilesystemencoding( )))
    return os.path.dirname(unicode(__file__, sys.getfilesystemencoding( )))
    
def find_image_or_data(file_name, basedir=None, dirname='pixbufs'):
    """Using the iamge_name, search in the common places. Return the path for
    the image or None if the image couldn't be found."""

    # the order is the priority, so keep global paths before local paths
    if not basedir:
        current_dir = os.path.abspath(os.path.dirname(__file__))
    else:
        current_dir = basedir
    common_paths = [
            os.path.join(current_dir, '..', dirname),
            os.path.join(current_dir, '..', '..', dirname),
            os.path.join(current_dir, dirname),
            os.path.join(sys.prefix, 'share', 'gmbox', dirname)]

    for path in common_paths:
        filename = os.path.join(path, file_name)
        if os.access(filename, os.F_OK):
            return filename
    print 'not found:', file_name
    return None

def unistr(match):
    '''给re.sub做第二个参数,返回&#nnnnn;对应的中文'''
    return unichr(int(match.group(1)))

def sizeread(size):
    '''传入整数,传出B/KB/MB'''
    #FIXME:这个有现成的函数没?
    if size > 1024*1024:
        return '%0.2fMB' % (float(size)/1024/1024)
    elif size > 1024:
        return '%0.2fKB' % (float(size)/1024)
    else:
        return '%dB' % size

def deal_input(string):
    if os.name == 'nt':
        return string.decode('GBK')
    else:
        return string.decode('UTF-8')

def get_attrs_value_by_name(attrs, name):
    if not attrs:
        return None
    (n, v) = zip(*attrs)
    n, v = list(n), list(v)
    return v[n.index(name)] if name in n else None
    
entityref = re.compile('&([a-zA-Z][a-zA-Z0-9]*);')
import htmlentitydefs
entityrefs = htmlentitydefs.name2codepoint.copy()
del(entityrefs['quot'])
def entityrefstr(m):
    '''给re.sub做第二个参数,返回&eacute;等对应的中文'''
    if m.group(1) in entityrefs:
        return unichr(entityrefs[m.group(1)])
    else:
        return '&'+m.group(1)+';'

