# Copyright (C) 2007 Samuel Abels, http://debain.org
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2, as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
import os
from Trackable      import Trackable
from AbstractMethod import AbstractMethod

True  = 1
False = 0

class Action(Trackable):
    def __init__(self, *args, **kwargs):
        Trackable.__init__(self)
        self.debug = kwargs.get('debug', 0)
        self.name  = kwargs.get('name',  None)


    def execute(self, global_lock, global_context, local_context):
        AbstractMethod(self)
