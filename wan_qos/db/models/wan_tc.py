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

from neutron_lib.db import model_base
import sqlalchemy as sa


class WanTcClass(model_base.BASEV2,
                  model_base.HasId, model_base.HasProject):
    __tablename__ = 'wan_tc_class'
    class_ext_id = sa.Column(sa.Integer)
    parent_class = sa.Column(sa.String(36),
                             sa.ForeignKey('wan_tc_class.id',
                                           ondelete='CASCADE'),
                             nullable=True)
    network_id = sa.Column(sa.String(36),
                           sa.ForeignKey('networks.id',
                                         ondelete='CASCADE'),
                           nullable=False,
                           unique=True,
                           primary_key=True)
    min_rate = sa.Column(sa.String(15), nullable=False)
    max_rate = sa.Column(sa.String(15))


class WanTcSelector(model_base.BASEV2,
                     model_base.HasId, model_base.HasProject):
    __tablename__ = 'wan_tc_selector'
    class_id = sa.Column(sa.String(36),
                         sa.ForeignKey('wan_tc_class.id',
                                       ondelete='CASCADE'),
                         nullable=False,
                         primary_key=True)
    protocol = sa.Column(sa.String(15))
    match = sa.Column(sa.String(15))

