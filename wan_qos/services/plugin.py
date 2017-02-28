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

from neutron_lib.plugins import directory
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
from wan_qos.db import wan_qos_db
from wan_qos.extensions import wantcfilter
from wan_qos.extensions import wantcdevice
from wan_qos.extensions import wantcclass
from wan_qos.extensions import wantc

LOG = logging.getLogger(__name__)


class PluginRpcCallback(object):
    target = messaging.Target(version='1.0')

    def __init__(self, plugin):
        super(PluginRpcCallback, self).__init__()
        self.plugin = plugin
        LOG.debug('rpc callback started.')

    def agent_up_notification(self, context, host_info):
        LOG.debug('got up notification from %s' % host_info['host'])
        self.plugin.db.agent_up_notification(context, host_info)

    def device_heartbeat(self, context, host):
        self.plugin.db.device_heartbeat(context, host)

    def get_configuration_from_db(self, context, host):
        conf = {
            'class_tree': self.plugin.db.get_class_tree(),
            'filters': self.plugin.db.get_wan_tc_filters(context)
        }

        return conf

    def get_class_by_id(self, context, id):
        return self.plugin.db.get_class_by_id(context, id)


class WanQosPlugin(wantcfilter.WanTcFilterPluginBase,
                   wantcdevice.WanTcDevicePluginBase,
                   wantcclass.WanTcClassPluginBase,
                   wantc.WanTcPluginBase):
    supported_extension_aliases = ['wan-tc-filter', 'wan-tc-device',
                                   'wan-tc-class', 'wan-tc']

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

    @property
    def _core_plugin(self):
        return directory.get_plugin()

    def delete_wan_tc_device(self, context, id):
        self.db.delete_wan_tc_device(context, id)

    def get_wan_tc_device(self, context, id, fields=None):
        return self.db.get_device(context, id)

    def get_wan_tc_devices(self, context, filters=None, fields=None,
                           sorts=None, limit=None, marker=None,
                           page_reverse=False):
        return self.db.get_all_devices(context, filters, fields, sorts, limit,
                                       marker, page_reverse)

    def get_wan_tc_class(self, context, id, fields=None):
        return self.db.get_class_by_id(context, id)

    def update_wan_tc_class(self, context, id, wan_tc_class):
        pass

    def create_wan_tc_class(self, context, wan_tc_class):
        LOG.debug('got new class request: %s' % wan_tc_class)
        wtc_class_db = self.db.create_wan_tc_class(context,
                                                   wan_tc_class[
                                                       'wan_tc_class'])
        self.agent_rpc.create_wtc_class(context, wtc_class_db)
        return wtc_class_db

    def delete_wan_tc_class(self, context, id):
        LOG.debug('Got request to delete class id: %s' % id)
        class_tree = self.db.get_class_tree(id)
        self.db.delete_wtc_class(context, id)
        self.agent_rpc.delete_wtc_class(context, class_tree)

    def get_wan_tc_classs(self, context, filters=None, fields=None, sorts=None,
                          limit=None, marker=None, page_reverse=False):
        return self.db.get_all_classes(context, filters, fields, sorts, limit,
                                       marker, page_reverse)

    def delete_wan_tc_filter(self, context, id):
        wtc_filter = self.get_wan_tc_filter(context, id)
        if wtc_filter:
            wtc_class = self.get_wan_tc_class(context, wtc_filter['class_id'])
            self.db.delete_wan_tc_filter(context, id)
            wtc_filter['class'] = wtc_class
            self.agent_rpc.delete_wtc_filter(context, wtc_filter)

    def get_wan_tc_filters(self, context, filters=None, fields=None,
                           sorts=None, limit=None, marker=None,
                           page_reverse=False):
        return self.db.get_wan_tc_filters(context, filters, fields, sorts,
                                          limit,
                                          marker, page_reverse)

    def create_wan_tc_filter(self, context, wan_tc_filter):
        wtc_filter = self.db.create_wan_tc_filter(context,
                                                  wan_tc_filter[
                                                      'wan_tc_filter'])
        # wtc_class = self.get_wan_tc_class(context, wtc_filter['class_id'])
        # wtc_filter['class'] = wtc_class
        self.agent_rpc.create_wtc_filter(context, wtc_filter)
        return wtc_filter

    def update_wan_tc_filter(self, context, id, wan_tc_filter):
        pass

    def get_wan_tc_filter(self, context, id, fields=None):
        return self.db.get_wan_tc_filter(context, id, fields)

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

    def get_wan_tc(self, context, id, fields=None):
        filter_db = self.get_wan_tc_filter(context, id, fields)
        class_db = self.get_wan_tc_class(context, filter_db['class_id'])
        filter_db['min'] = class_db['min']
        filter_db['max'] = class_db['max']
        return filter_db

    def get_wan_tcs(self, context, filters=None, fields=None, sorts=None,
                    limit=None, marker=None, page_reverse=False):
        filters = self.get_wan_tc_filters(context, filters, fields, sorts,
                                          limit, marker, page_reverse)
        for filter_db in filters:
            class_db = self.get_wan_tc_class(context, filter_db['class_id'])
            filter_db['min'] = class_db['min']
            filter_db['max'] = class_db['max']

        return filters

    def create_wan_tc(self, context, wan_tc):
        LOG.debug('got WAN_TC: %s' % wan_tc)
        wan_tc_req = wan_tc['wan_tc']

        filter_db = self.get_wan_tc_filters(context, filters={
            'network': [wan_tc_req['network']]})
        if filter_db:
            raise exceptions.InvalidInput(
                error_message='Network already has limiter')

        network = self._core_plugin.get_network(context, wan_tc_req['network'])
        if network['provider:network_type'] != 'vxlan':
            raise exceptions.InvalidInput()
        vni = network['provider:segmentation_id']
        tc_class = {'wan_tc_class': {
            'direction': 'both',
            'min': wan_tc_req['min']
        }
        }

        if 'max' in wan_tc_req:
            tc_class['wan_tc_class']['max'] = wan_tc_req['max']

        tc_class_db = self.create_wan_tc_class(context, tc_class)
        tc_filter_req = {'wan_tc_filter': {
            'protocol': 'vxlan',
            'match': 'vni=%s' % vni,
            'class_id': tc_class_db['id'],
            'network': network['id']
        }
        }
        tc_filter_db = self.create_wan_tc_filter(context, tc_filter_req)
        tc_filter_db['min'] = tc_class_db['min']
        tc_filter_db['max'] = tc_class_db['max']
        return tc_filter_db

    def update_wan_tc(self, context, id, wan_tc):
        raise exceptions.BadRequest(msg='Not implemented yet!')

    def delete_wan_tc(self, context, id):
        LOG.debug('Deleting TC: %s' % id)
        tc_filter = self.get_wan_tc_filter(context, id)
        class_id = tc_filter['class_id']
        self.delete_wan_tc_filter(context, id)
        self.delete_wan_tc_class(context, class_id)
