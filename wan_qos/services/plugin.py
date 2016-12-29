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

from neutron.common import rpc as n_rpc
from neutron.db import agents_db

from oslo_config import cfg
from oslo_log import log as logging
from oslo_utils import importutils
import oslo_messaging as messaging

from wan_qos.common import api
from wan_qos.common import constants
from wan_qos.common import topics
from wan_qos.extensions import wanqos

LOG = logging.getLogger(__name__)


class PluginRpcCallback(object):
    target = messaging.Target(version='1.0')

    def __init__(self, plugin):
        super(PluginRpcCallback, self).__init__()
        self.plugin = plugin
        LOG.debug('rpc callback started.')

    def agent_up_notification(self, context, host):
        LOG.debug('got up notification from %s' % host)
        self.plugin.agent_up_notification(host)


class WanQosPlugin(wanqos.WanQosPluginBase):

    supported_extension_aliases = ["wan-qos"]

    def __init__(self):
        rpc_callback = importutils.import_object(
            'wan_qos.services.plugin.PluginRpcCallback', self)
        endpoints = (
            [rpc_callback, agents_db.AgentExtRpcCallback()])
        self.agent_rpc = api.TcAgentApi(cfg.CONF.host)
        self.conn = n_rpc.create_connection()
        self.conn.create_consumer(topics.TC_PLUGIN,
                                  endpoints,
                                  fanout=False)
        self.conn.consume_in_threads()

    def get_plugin_type(self):
        """Get type of the plugin."""
        return constants.WANQOS

    def get_plugin_description(self):
        """Get description of the plugin."""
        return 'Plugin for rate limiting on WAN links.'

    def get_wan_qos(self, id):
        pass

    def get_wan_qoss(self):
        pass

    def delete_wan_qos(self, context, id):
        pass

    def update_wan_qos(self, context, id, wan_qos):
        pass

    def create_wan_qos(self, context, wan_qos):
        pass
        # self.agent_rpc.create_wan_qos(context, wan_qos)

    def agent_up_notification(self, host):
        LOG.debug('agent %s is up' % host)
        return 'OK'
