# Copyright 2016 Huawei corp.
# All Rights Reserved.
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

from subprocess import call
from subprocess import check_call

from oslo_log import log as logging

from neutron_lib import exceptions

import agent_api

LOG = logging.getLogger(__name__)


class TcDriver(agent_api.AgentInterface):
    def __init__(self):
        self.ports = {}

    def set_ports(self, lan_port, wan_port):
        self.ports['lan_port'] = lan_port
        self.ports['wan_port'] = wan_port

    def get_ports(self):
        return self.ports

    def clear_all(self):
        for port in self.ports.values():
            call('sudo tc qdisc del dev %s root' % port, shell=True)

    def set_root_queue(self, tc_dict):
        check_call('sudo tc qdisc add dev %s handle 1: root htb' %
                   self.ports[tc_dict['port_side']], shell=True)
        class_str = 'sudo tc class add dev %s parent 1: classid 1:1 ' \
                    'htb rate %s ceil %s'
        check_call(class_str % (self.ports[tc_dict['port_side']],
                                str(tc_dict['max_rate']),
                                str(tc_dict['max_rate'])), shell=True)

    def create_traffic_class(self, tc_dict):
        """ Create new traffic class.
        Parameters:
            port_side - lan_port / wan_port
            parent - the parent class
            child - the class id
            min - minimum traffic rate (CIR)
            max - maximum traffic rate. if not provide, the maximum rate will
                be limitted by parent maximum rate.
        """
        LOG.debug('got request for new class: %s' % tc_dict)
        tc_dict['command'] = 'add'
        self._create_or_update_class(tc_dict)
        LOG.debug('new class created.')

    def update_traffic_class(self, tc_dict):
        tc_dict['command'] = 'change'
        self._create_or_update_class(tc_dict)

    def remove_traffic_class(self, tc_dict, with_filter=False):
        if with_filter:
            self.remove_filter(tc_dict)
        cmd = 'sudo tc class del dev %s classid 1:%s' % (
            self.ports[tc_dict['port_side']],
            tc_dict['child']
        )
        check_call(cmd, shell=True)

    def _create_or_update_class(self, tc_dict):
        cmd = 'sudo tc class %s dev %s parent 1:%s classid 1:%s htb' % (
            tc_dict['command'],
            self.ports[tc_dict['port_side']],
            tc_dict['parent'], tc_dict['child']

        )
        if 'min' in tc_dict:
            cmd += ' rate %s' % tc_dict['min']
        else:
            cmd += ' rate 1kbit'
        if 'max' in tc_dict:
            cmd += ' ceil %s' % tc_dict['max']
        check_call(cmd, shell=True)

    def create_filter(self, tc_dict):

        if tc_dict['protocol'] == 'vxlan':
            self._create_vxlan_filter(tc_dict)
            return

        raise exceptions.BadRequest(msg='Protocol not supported')

    def _create_vxlan_filter(self, tc_dict):
        vni = tc_dict['match'].split('=')[1]
        cmd = 'sudo tc filter add dev %s parent 1:0' % (
            self.ports[tc_dict['port_side']])
        cmd += ' protocol ip prio 1 u32'
        cmd += ' match ip protocol 17 0xFF'  # UDP
        cmd += ' match u16 0x12B5 0xFFFF at 22'  # VxLAN port
        cmd += ' match u32 0x%0.6X00 0xFFFFFF00 at 32' % int(vni)
        cmd += ' flowid 1:%s' % tc_dict['child']
        LOG.debug('creating filter: %s' % cmd)
        check_call(cmd, shell=True)

    def remove_filter(self, tc_dict):
        cmd = 'sudo tc filter del dev %s ' % self.ports[tc_dict['port_side']]
        cmd += ' parent 1:0 protocol ip prio 1 u32'
        cmd += ' flowid 1:%s' % tc_dict['child']
        check_call(cmd, shell=True)
