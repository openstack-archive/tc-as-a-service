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

import abc
import six


@six.add_metaclass(abc.ABCMeta)
class AgentInterface(object):
    """ Base class that defines the contract for TC agent"""

    @abc.abstractmethod
    def clear_all(self):
        """ delete all traffic control configurations """

    @abc.abstractmethod
    def set_ports(self, in_port, out_port):
        """ set the names of the LAN and WAN facing ports """

    @abc.abstractmethod
    def set_root_queue(self, tc_dict):
        """ sets the root qdisc with its max rate of the WAN link to be set
         as upper limit"""

    @abc.abstractmethod
    def create_traffic_class(self, tc_dict):
        """ Add traffic class using traffic information from the
        dictionary. """

    @abc.abstractmethod
    def update_traffic_class(self, tc_dict):
        """ update traffic control using information from tc dictionary. """

    @abc.abstractmethod
    def remove_traffic_class(self, tc_dict):
        """ update traffic control using information from tc dictionary. """

    @abc.abstractmethod
    def create_filter(self, tc_dict):
        """ create traffic filter that is used to route packets to the
        right queue"""

    @abc.abstractmethod
    def remove_filter(self, tc_dict):
        """ remove traffic filter """
