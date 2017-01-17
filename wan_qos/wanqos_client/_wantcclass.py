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


class WanTcClass(extension.NeutronClientExtension):
    resource = constants.WAN_TC_CLASS
    resource_plural = '%ss' % constants.WAN_TC_CLASS
    path = constants.WAN_TC_CLASS_PATH
    object_path = '/%s' % path
    resource_path = '/%s/%%s' % path
    versions = ['2.0']


class WanTcShow(extension.ClientExtensionShow, WanTcClass):
    shell_command = 'wan-tc-class-show'


class WanTcList(extension.ClientExtensionList, WanTcClass):
    shell_command = 'wan-tc-class-list'
    list_columns = ['id', 'parent', 'direction', 'min', 'max']
    pagination_support = True
    sorting_support = True


class WanTcCreate(extension.ClientExtensionCreate, WanTcClass):
    shell_command = 'wan-tc-class-create'

    def add_known_arguments(self, parser):
        parser.add_argument(
            'direction', metavar='<DIRECTION>',
            choices=['both', 'in', 'out'],
            help=_('The direction for the limiter. Can be both/in/out'))
        parser.add_argument(
            '--min',
            dest='min',
            help=_('Set committed rate. (mbit / kbit)'))
        parser.add_argument(
            '--max',
            dest='max',
            help=_('Set maximum rate. (mbit / kbit)'))
        parser.add_argument(
            '--parent',
            dest='parent',
            help=_('Set the parent class of this class. Omit if root.'))

    def args2body(self, parsed_args):

        body = {
            'direction': parsed_args.direction
        }

        if parsed_args.min:
            body['min'] = parsed_args.min
        else:
            if not parsed_args.max:
                raise exceptions.BadRequest('Either min or max must be set')

        if parsed_args.max:
            body['max'] = parsed_args.max

        if parsed_args.parent:
            body['parent'] = parsed_args.parent

        return {self.resource: body}


class WanTcDelete(extension.ClientExtensionDelete, WanTcClass):
    shell_command = 'wan-tc-class-delete'


class WanTcUpdate(extension.ClientExtensionUpdate, WanTcClass):
    shell_command = 'wan-tc-class-update'

    def add_known_arguments(self, parser):
        pass

    def args2body(self, parsed_args):
        body = {}
        return {self.resource: body}
