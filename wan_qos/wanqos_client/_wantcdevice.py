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
    body = {constants.WAN_TC_DEVICE: {}, }
    return body


class WanTcDevice(extension.NeutronClientExtension):
    resource = constants.WAN_TC_DEVICE
    resource_plural = '%ss' % constants.WAN_TC_DEVICE
    path = constants.WAN_TC_DEVICE_PATH
    object_path = '/%s' % path
    resource_path = '/%s/%%s' % path
    versions = ['2.0']


class WanTcDeviceShow(extension.ClientExtensionShow, WanTcDevice):
    shell_command = 'wan-tc-device-show'


class WanTcDeviceList(extension.ClientExtensionList, WanTcDevice):
    shell_command = 'wan-tc-device-list'
    list_columns = ['id', 'host', 'lan_port', 'wan_port',
                    'uptime', 'last_seen']
    pagination_support = True
    sorting_support = True


class WanTcDeviceDelete(extension.ClientExtensionDelete, WanTcDevice):
    shell_command = 'wan-tc-device-delete'
