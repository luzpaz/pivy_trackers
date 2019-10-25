# -*- coding: utf-8 -*-
#**************************************************************************
#*                                                                     *
#* Copyright (c) 2019 Joel Graff <monograff76@gmail.com>               *
#*                                                                     *
#* This program is free software; you can redistribute it and/or modify*
#* it under the terms of the GNU Lesser General Public License (LGPL)  *
#* as published by the Free Software Foundation; either version 2 of   *
#* the License, or (at your option) any later version.                 *
#* for detail see the LICENCE text file.                               *
#*                                                                     *
#* This program is distributed in the hope that it will be useful,     *
#* but WITHOUT ANY WARRANTY; without even the implied warranty of      *
#* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the       *
#* GNU Library General Public License for more details.                *
#*                                                                     *
#* You should have received a copy of the GNU Library General Public   *
#* License along with this program; if not, write to the Free Software *
#* Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307*
#* USA                                                                 *
#*                                                                     *
#***********************************************************************
"""
Drag traits for Tracker objects
"""

from ..trait.select import Select
from ..trait.enums import DragStyle

from ..tracker.drag_tracker import DragTracker

class Drag():
    """
    Drag traits for tracker classes
    """

    #prototypes from Base, Select, and Event
    base = None
    name = ''
    mouse_state = None
    view_state = None
    select = None

    def is_selected(self): """prototype"""; pass
    def add_mouse_event(self, callback): """prototype"""; pass
    def add_button_event(self, callback): """prototype"""; pass

    #prototype to be implemented by inheriting class
    def update_drag_center(self): """prototype"""; pass

    #Class static reference to global DragTracker
    drag_tracker = None

    def __init__(self):
        """
        Constructor
        """

        assert(self.select is not None), \
            """
            Select must precede Drag in method resolution order
            """

        self.add_mouse_event(self.drag_mouse_event)
        self.add_button_event(self.drag_button_event)

        # instances / initializes singleton DragTracker on first inherit, 
        # and adds callback for global tracker updating
        if not Drag.drag_tracker:
            Drag.drag_tracker = DragTracker(self.base)
            Drag.drag_tracker.update_center_fn = self.update_drag_center

        self.drag_copy = None

        super().__init__()

    def drag_mouse_event(self, user_data, event_cb):
        """
        Drag mouse movement event callback, called at start of drag event
        """

        if not self.is_selected() or not self.mouse_state.button1.dragging:
            return

        #enabling sinks mouse events at the drag tracker
        Drag.drag_tracker.dragging = True
        Drag.drag_tracker.drag_center = self.update_drag_center()

        for _v in Select.selected:
            _v.drag_copy = _v.geometry.copy()
            Drag.drag_tracker.insert_full_drag(_v.drag_copy)

    def drag_button_event(self, user_data, event_cb):
        """
        Drag button event callback
        """

        #only trap button up events during a drag oepration
        if self.mouse_state.button1.pressed:
            return

        if not self.drag_tracker.dragging:
            return

        for _v in Select.selected:

            _points = self.view_state.transform_points(
                _v.get_coordinates(), _v.drag_copy.getChild(1)
            )

            print('updating {} to {}'.format(_v.name, str(_points)))
            _v.update(_points)
            _v.drag_copy = None
