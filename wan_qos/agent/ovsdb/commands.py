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


def _get_queue_id_list(api, port_name):
    port_row = idlutils.row_by_value(api.idl, 'Port', 'name', port_name)
    if port_row and port_row.qos:
        qos_row = api._tables['QoS'].rows[port_row.qos[0].uuid]
        if qos_row:
            queues = idlutils.get_column_value(qos_row, 'queues')
            return queues.keys()


class GetQueueIdList(cmd.BaseCommand):
    def __init__(self, api, port_name):
        super(GetQueueIdList, self).__init__(api)
        self.port_name = port_name

    def run_idl(self, txn):
        self.result = _get_queue_id_list(self.api, self.port_name)


class AddQueue(cmd.BaseCommand):
    def __init__(self, api, port_name, queue_id, min_rate, max_rate):
        super(AddQueue, self).__init__(api)
        self.port_name = port_name
        self.queue_id = queue_id
        self.min_rate = min_rate
        self.max_rate = max_rate

    def run_idl(self, txn):
        port_row = idlutils.row_by_value(self.api.idl, 'Port', 'name',
                                         self.port_name)
        qos_row = self.api._tables['QoS'].rows[port_row.qos[0].uuid]
        queues = getattr(qos_row, 'queues', [])
        if self.queue_id in queues.keys():
            raise Exception
        queue_row = txn.insert(self.api._tables['Queue'])
        queue_row.other_config = {'min-rate': self.min_rate,
                                  'max-rate': self.max_rate}
        queues[self.queue_id] = queue_row
        qos_row.verify('queues')
        qos_row.queues = queues

        self.result = 'Done'
