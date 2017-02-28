# Copyright 2017 Huawei corp.
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


class WanTc(extension.NeutronClientExtension):
    resource = constants.WAN_TC
    resource_plural = '%ss' % constants.WAN_TC
    path = constants.WAN_TC_PATH
    object_path = '/%s' % path
    resource_path = '/%s/%%s' % path
    versions = ['2.0']


class WanTcShow(extension.ClientExtensionShow, WanTc):
    shell_command = 'wan-tc-show'


class WanTcList(extension.ClientExtensionList, WanTc):
    shell_command = 'wan-tc-list'
    list_columns = ['id', 'network', 'min', 'max']
    pagination_support = True
    sorting_support = True


class WanTcCreate(extension.ClientExtensionCreate, WanTc):
    shell_command = 'wan-tc-create'

    def add_known_arguments(self, parser):
        parser.add_argument(
            'network', metavar='<network>',
            help=_('Network ID'))
        parser.add_argument(
            '--min',
            dest='min',
            help=_('Set committed rate. (mbit / kbit)'))
        parser.add_argument(
            '--max',
            dest='max',
            help=_('Set maximum rate. (mbit / kbit)'))

    def args2body(self, parsed_args):

        body = {
            'network': parsed_args.network
        }

        if parsed_args.min:
            body['min'] = parsed_args.min
        else:
            raise exceptions.BadRequest('min must be set')

        if parsed_args.max:
            body['max'] = parsed_args.max

        return {self.resource: body}


class WanTcDelete(extension.ClientExtensionDelete, WanTc):
    shell_command = 'wan-tc-delete'


class WanTcUpdate(extension.ClientExtensionUpdate, WanTc):
    shell_command = 'wan-tc-update'

    def add_known_arguments(self, parser):
        pass

    def args2body(self, parsed_args):
        body = {}
        return {self.resource: body}
