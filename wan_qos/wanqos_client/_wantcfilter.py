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


from neutronclient._i18n import _

from neutronclient.common import extension
from neutronclient.common import exceptions

from wan_qos.common import constants


class WanTcFilter(extension.NeutronClientExtension):
    resource = constants.WAN_TC_FILTER
    resource_plural = '%ss' % constants.WAN_TC_FILTER
    path = constants.WAN_TC_FILTER_PATH
    object_path = '/%s' % path
    resource_path = '/%s/%%s' % path
    versions = ['2.0']


class WanTcFilterShow(extension.ClientExtensionShow, WanTcFilter):
    shell_command = 'wan-tc-filter-show'


class WanTcFilterList(extension.ClientExtensionList, WanTcFilter):
    shell_command = 'wan-tc-filter-list'
    list_columns = ['id', 'protocol', 'match', 'class_id']
    pagination_support = True
    sorting_support = True


class WanTcFilterCreate(extension.ClientExtensionCreate, WanTcFilter):
    shell_command = 'wan-tc-filter-create'

    def add_known_arguments(self, parser):
        parser.add_argument(
            'protocol', metavar='<protocol>',
            choices=['vxlan'],
            help=_('Protocol name to select'))
        parser.add_argument(
            'match', metavar='<MATCH>',
            help=_('match fields for protocol name to select'))
        parser.add_argument(
            'class_id', metavar='<CLASS>',
            help=_('Class ID to attach the filter to'))

    def args2body(self, parsed_args):
        body = {
            'protocol': parsed_args.protocol,
            'match': parsed_args.match,
            'class_id': parsed_args.class_id
        }

        return {self.resource: body}


class WanTcFilterDelete(extension.ClientExtensionDelete, WanTcFilter):
    shell_command = 'wan-tc-filter-delete'


class WanTcFilterUpdate(extension.ClientExtensionUpdate, WanTcFilter):
    shell_command = 'wan-tc-filter-update'

    def add_known_arguments(self, parser):
        pass

    def args2body(self, parsed_args):
        body = {}
        return {self.resource: body}
