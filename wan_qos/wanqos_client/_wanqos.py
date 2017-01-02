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

from neutronclient.common import extension

from wan_qos.common import constants


def args2body(self, parsed_args):
    body = {'wan_tc': {}, }
    return body


class WanQos(extension.NeutronClientExtension):
    resource = constants.WAN_QOS
    resource_plural = '%ss' % constants.WAN_QOS
    path = constants.WAN_QOS_PATH
    object_path = '/%s' % path
    resource_path = '/%s/%%s' % path
    versions = ['2.0']


class WanQosShow(extension.ClientExtensionShow, WanQos):

    shell_command = 'wan-qos-show'


class WanQosList(extension.ClientExtensionList, WanQos):

    shell_command = 'wan-qos-list'
    list_columns = ['id', 'name', 'network']
    pagination_support = True
    sorting_support = True


class WanQosCreate(extension.ClientExtensionCreate, WanQos):

    shell_command = 'wan-qos-create'

    def add_known_arguments(self, parser):
        pass

    def args2body(self, parsed_args):
        body = args2body(self, parsed_args)
        if parsed_args.tenant_id:
            body['wan_qos']['tenant_id'] = parsed_args.tenant_id
        return body


class WanQosDelete(extension.ClientExtensionDelete, WanQos):

    shell_command = 'wan-qos-delete'


class WanQosUpdate(extension.ClientExtensionUpdate, WanQos):

    shell_command = 'wan-qos-update'

    def add_known_arguments(self, parser):
        pass

    def args2body(self, parsed_args):
        body = args2body(self, parsed_args)
        return body



