# Copyright (c) 2016 Red Hat, Inc.
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

import mock
import testtools

from neutron.tests import base

import wan_qos.agent.ovsdb.impl_idl as impl_idl
import wan_qos.agent.ovsdb.commands as cmd


class OvsdbIdlTestCase(base.BaseTestCase):
    def setUp(self):
        super(OvsdbIdlTestCase, self).setUp()
        self.vsctl_timeout = 10
        self.ovsdb_idl = impl_idl.OvsdbQosIdl(self, 'tcp:127.0.0.1:6640', 30)
        self.ovsdb_idl.ovsdb_connection.start()
        self.idl = self.ovsdb_idl.ovsdb_connection.idl

    def test1(self):
        assert self.ovsdb_idl.br_exists('tc-br').execute()==True

    def get_queue_list(self):
        print (cmd.GetQueueIdList(self.ovsdb_idl, 'enp1s0f1').execute())

    def add_queue(self):
        print (cmd.AddQueue(self.ovsdb_idl, 'enp1s0f1', 1, '1000000', '1000000')
               .execute())
