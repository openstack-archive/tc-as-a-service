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
import oslo_messaging as messaging

from neutron import context as ctx
from neutron import manager
from neutron_lib import exceptions

from wan_qos.agent import tc_driver
from wan_qos.common import api
from wan_qos.common import topics

LOG = logging.getLogger(__name__)


class TcAgentManager(manager.Manager):
    target = messaging.Target(version='1.0')

    def __init__(self, host=None, conf=None):
        self.agent = tc_driver.TcDriver()
        if not conf:
            self.conf = cfg.CONF
        else:
            self.conf = conf
        if not host:
            self.host = self.conf.host
        else:
            self.host = host
        lan_port = self.conf.WANTC.lan_port_name
        wan_port = self.conf.WANTC.wan_port_name
        self.agent.set_ports(lan_port, wan_port)
        self.plugin_rpc = api.TcPluginApi(host, topics.TC_PLUGIN)
        self.plugin_rpc.agent_up_notification(ctx.get_admin_context(),
                                              self.agent.get_ports())

    def init_host(self):
        self.agent.clear_all()
        tc_dict = {
            'port_side': 'lan_port',
            'max_rate': self.conf.WANTC.lan_max_rate
        }
        self.agent.set_root_queue(tc_dict)
        tc_dict = {
            'port_side': 'wan_port',
            'max_rate': self.conf.WANTC.wan_max_rate
        }
        self.agent.set_root_queue(tc_dict)
        context = ctx.get_admin_context()
        agent_conf = self.plugin_rpc.get_configuration_from_db(
            context)
        class_tree = agent_conf['class_tree']
        if class_tree['id'] == 'root':
            self.init_child_classes(class_tree['child_list'])

            if 'filters' in agent_conf:
                for filter in agent_conf['filters']:
                    self.create_wtc_filter(context, filter)
            return
        raise exceptions.InvalidInput(error_message='Did not get root class')

    def init_child_classes(self, child_list):
        for child in child_list:
            self.create_wtc_class(None, child)
            self.init_child_classes(child['child_list'])

    def after_start(self):
        LOG.info("WAN QoS agent started")

    def periodic_tasks(self, context, raise_on_error=False):
        LOG.info("periodic task")
        self.plugin_rpc.device_heartbeat(context, self.host)

    def create_wtc_class(self, context, wtc_class_dict):
        LOG.debug('got request for new class: %s' % wtc_class_dict)
        class_dict = {
            'parent': wtc_class_dict['parent_class_ext_id'],
            'child': wtc_class_dict['class_ext_id']

        }

        if wtc_class_dict['min']:
            class_dict['min'] = wtc_class_dict['min']
        if wtc_class_dict['max']:
            class_dict['max'] = wtc_class_dict['max']
        if wtc_class_dict['direction'] == 'in' or wtc_class_dict[
            'direction'] == 'both':
            class_dict['port_side'] = 'lan_port'
            self._create_wtc_class(class_dict)
        if wtc_class_dict['direction'] == 'out' or wtc_class_dict[
            'direction'] == 'both':
            class_dict['port_side'] = 'wan_port'
            self._create_wtc_class(class_dict)

    def _create_wtc_class(self, class_dict):
        self.agent.create_traffic_class(class_dict)

    def delete_wtc_class(self, context, wtc_class_tree):
        for child in wtc_class_tree['child_list']:
            self.delete_wtc_class(context, child)
        self._delete_wtc_class(wtc_class_tree)

    def _delete_wtc_class(self, wtc_class):
        tc_dict = {
            'parent': wtc_class['parent_class_ext_id'],
            'child': wtc_class['class_ext_id']
        }

        if wtc_class['direction'] == 'in' or wtc_class['direction'] == 'both':
            tc_dict['port_side'] = 'lan_port'
            self.agent.remove_traffic_class(tc_dict)
        if wtc_class['direction'] == 'out' or wtc_class['direction'] == 'both':
            tc_dict['port_side'] = 'wan_port'
            self.agent.remove_traffic_class(tc_dict)

    def create_wtc_filter(self, context, wtc_filter):

        wtc_class = self.plugin_rpc.get_class_by_id(context,
                                                    wtc_filter['class_id'])

        tc_dict = {
            'child': wtc_class['class_ext_id'],
            'protocol': wtc_filter['protocol'],
            'match': wtc_filter['match']
        }

        port_side = wtc_class['direction']

        if port_side == 'both' or port_side == 'in':
            tc_dict['port_side'] = 'lan_port'
            self.agent.create_filter(tc_dict)
        if port_side == 'both' or port_side == 'out':
            tc_dict['port_side'] = 'wan_port'
            self.agent.create_filter(tc_dict)

    def delete_wtc_filter(self, context, wtc_filter):

        wtc_class = wtc_filter['class']
        port_side = wtc_class['direction']

        tc_dict = {
            'child': wtc_class['class_ext_id']
        }

        if port_side == 'both' or port_side == 'in':
            tc_dict['port_side'] = 'lan_port'
            self.agent.remove_filter(tc_dict)
        if port_side == 'both' or port_side == 'out':
            tc_dict['port_side'] = 'wan_port'
            self.agent.remove_filter(tc_dict)
