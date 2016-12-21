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

from oslo_config import cfg
from oslo_log import log as logging

from wan_qos.agent import tc_driver

LOG = logging.getLogger(__name__)


class TcAgentManager:
    def __init__(self, host, conf=None):
        self.agent = tc_driver.TcDriver()
        if not conf:
            conf = cfg.CONF
        lan_port = conf.WANQOS.lan_port
        wan_port = conf.WANQOS.wan_port
        self.agent.set_ports(lan_port, wan_port)

    def init_host(self):
        """Handle initialization if this is a standalone service.

        """
        pass

    def after_start(self):
        LOG.info("WAN QoS agent started")

    def periodic_tasks(self, context, raise_on_error=False):
        pass