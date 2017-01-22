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

import sys

from oslo_config import cfg
from oslo_service import service

from neutron.agent.common import config
from neutron.common import config as common_config
from neutron import service as neutron_service

from wan_qos.common import topics

import eventlet
eventlet.monkey_patch()

WANTC_OPTS = [
    cfg.StrOpt('lan_port_name',
               default='eth0',
               help="The name of the port facing the LAN"),
    cfg.StrOpt('lan_max_rate',
               default='10mbit',
               help="The maximum rate of the LAN port"),
    cfg.StrOpt('wan_port_name',
               default='eth1',
               help="The name of the port facing the WAN"),
    cfg.StrOpt('wan_max_rate',
               default='10mbit',
               help="The maximum rate of the WAN port")
]


def main():
    cfg.CONF.register_opts(WANTC_OPTS, 'WANTC')
    common_config.init(sys.argv[1:])
    config.setup_logging()
    server = neutron_service.Service.create(
        binary='tc_agent2',
        topic=topics.TC_AGENT,
        report_interval=10,
        manager='wan_qos.agent.tc_manager.TcAgentManager')
    service.launch(cfg.CONF, server).wait()

if __name__ == '__main__':
    main()
