# Copyright (c) 2015 OpenStack Foundation
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from neutron.agent.ovsdb import api
from neutron.agent.ovsdb import impl_idl
from neutron.agent.ovsdb.native import commands as cmd
from neutron.agent.ovsdb.native import connection
from neutron.agent.ovsdb.native import idlutils
from neutron.agent.ovsdb.native import vlog


class OvsdbQosIdl(impl_idl.OvsdbIdl):
    def __init__(self, context, conn, timeout):
        super(OvsdbQosIdl, self).__init__(context)
        self.ovsdb_connection = connection.Connection(conn,
                                                      timeout,
                                                      'Open_vSwitch')

