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
from neutron_lib import exceptions

from oslo_config import cfg
from oslo_log import log as logging
from oslo_utils import importutils

import oslo_messaging as messaging

from wan_qos.common import api
from wan_qos.common import constants
from wan_qos.common import topics
from wan_qos.extensions import wanqos
from wan_qos.db import wan_qos_db

LOG = logging.getLogger(__name__)


class PluginRpcCallback(object):
    target = messaging.Target(version='1.0')

    def __init__(self, plugin):
        super(PluginRpcCallback, self).__init__()
        self.plugin = plugin
        LOG.debug('rpc callback started.')

    def agent_up_notification(self, context, host_info):
        LOG.debug('got up notification from %s' % host_info['host'])
        self.plugin.agent_up_notification(context, host_info)

    def device_heartbeat(self, context, host):
        self.plugin.db.device_heartbeat(context, host)


class WanQosPlugin(wanqos.WanQosPluginBase):
    supported_extension_aliases = ["wan-tc"]

    def __init__(self):
        self.db = wan_qos_db.WanTcDb()
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
        return constants.WANTC

    def get_plugin_description(self):
        """Get description of the plugin."""
        return 'Plugin for rate limiting on WAN links.'

    def get_wan_tc(self, context, id, fields=None):
        pass

    def get_wan_tcs(self, context, filters=None, fields=None,
                    sorts=None, limit=None, marker=None,
                    page_reverse=False):
        return self.db.get_all_classes(context)

    def delete_wan_tc(self, context, id):
        pass

    def update_wan_tc(self, context, id, wan_qos):
        pass

    def create_wan_tc(self, context, wan_qos):
        pass
        # self.agent_rpc.create_wan_qos(context, wan_qos)

        # tenant_id = self._get_tenant_id_for_create(context, wan_qos_class)

    @staticmethod
    def _get_tenant_id_for_create(self, context, resource):
        """Get tenant id for creation of resources."""
        if context.is_admin and 'tenant_id' in resource:
            tenant_id = resource['tenant_id']
        elif ('tenant_id' in resource and
                      resource['tenant_id'] != context.tenant_id):
            reason = 'Cannot create resource for another tenant'
            raise exceptions.AdminRequired(reason=reason)
        else:
            tenant_id = context.tenant_id
        return tenant_id

    def agent_up_notification(self, context, host_info):
        LOG.debug('agent %s is up' % host_info['host'])
        self.db.agent_up_notification(context, host_info)
