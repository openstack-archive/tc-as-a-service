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

import oslo_messaging

from neutron.common import rpc as n_rpc

from wan_qos.common import topics


class TcPluginApi(object):
    def __init__(self, host, topic=topics.TC_PLUGIN):
        self.host = host
        target = oslo_messaging.Target(topic=topic, version='1.0')
        self.client = n_rpc.get_client(target)

    def agent_up_notification(self, context, ports):
        cctxt = self.client.prepare()
        host_info = {
            'host': self.host,
            'lan_port': ports['lan_port'],
            'wan_port': ports['wan_port']
        }
        cctxt.cast(context, 'agent_up_notification',
                   host_info=host_info)

    def device_heartbeat(self, context, host):
        cctxt = self.client.prepare()
        cctxt.cast(context, 'device_heartbeat',
                   host=host)

    def get_configuration_from_db(self, context):
        cctxt = self.client.prepare()
        return cctxt.call(context, 'get_configuration_from_db', host=self.host)

    def get_class_by_id(self, context, id):
        cctxt = self.client.prepare()
        return cctxt.call(context, 'get_class_by_id', id=id)


class TcAgentApi(object):
    def __init__(self, host, topic=topics.TC_AGENT):
        self.host = host
        target = oslo_messaging.Target(topic=topic, version='1.0')
        self.client = n_rpc.get_client(target)

    def create_wtc_class(self, context, wtc_class_dict):
        cctxt = self.client.prepare()
        return cctxt.call(context,
                          'create_wtc_class',
                          wtc_class_dict=wtc_class_dict)

    def delete_wtc_class(self, context, wtc_class_tree):
        cctxt = self.client.prepare()
        return cctxt.call(context,
                          'delete_wtc_class',
                          wtc_class_tree=wtc_class_tree)

    def create_wtc_filter(self, context, wtc_filter):
        cctxt = self.client.prepare()
        return cctxt.call(context,
                          'create_wtc_filter',
                          wtc_filter=wtc_filter)

    def delete_wtc_filter(self, context, wtc_filter):
        cctxt = self.client.prepare()
        return cctxt.call(context,
                          'delete_wtc_filter',
                          wtc_filter=wtc_filter)