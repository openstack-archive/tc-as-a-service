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

import sqlalchemy as sa

from neutron_lib.db import model_base


class WanTcDevice(model_base.BASEV2,
                  model_base.HasId):
    __tablename__ = 'wan_tc_device'
    host = sa.Column(sa.String(100), nullable=False)
    lan_port = sa.Column(sa.String(15), nullable=False)
    wan_port = sa.Column(sa.String(15), nullable=False)
    uptime = sa.Column(sa.DateTime())
    heartbeat_timestamp = sa.Column(sa.DateTime())


class WanTcClass(model_base.BASEV2,
                 model_base.HasId, model_base.HasProject):
    __tablename__ = 'wan_tc_class'
    device_id = sa.Column(sa.String(36),
                          sa.ForeignKey('wan_tc_device.id',
                                        ondelete='CASCADE'),
                          nullable=True)
    direction = sa.Column(sa.String(4), nullable=False)
    class_ext_id = sa.Column(sa.Integer)
    parent = sa.Column(sa.String(36),
                       sa.ForeignKey('wan_tc_class.id',
                                     ondelete='CASCADE'),
                       nullable=True)
    parent_class_ext_id = sa.Column(sa.Integer)
    min = sa.Column(sa.String(15))
    max = sa.Column(sa.String(15))


class WanTcFilter(model_base.BASEV2,
                  model_base.HasId, model_base.HasProject):
    __tablename__ = 'wan_tc_filter'
    class_id = sa.Column(sa.String(36),
                         sa.ForeignKey('wan_tc_class.id',
                                       ondelete='CASCADE'),
                         nullable=False)
    network = sa.Column(sa.String(36),
                        sa.ForeignKey('networks.id',
                                      ondelete='CASCADE'))
    protocol = sa.Column(sa.String(15))
    match = sa.Column(sa.String(15))
