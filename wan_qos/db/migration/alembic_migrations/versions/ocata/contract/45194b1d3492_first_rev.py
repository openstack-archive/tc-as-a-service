# Copyright 2017 <PUT YOUR NAME/COMPANY HERE>
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
#

"""first rev

Revision ID: 45194b1d3492
Revises: None
Create Date: 2017-01-04 13:46:13.433909

"""

# revision identifiers, used by Alembic.
revision = '45194b1d3492'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('wan_tc_class',
                    sa.Column('id', sa.String(length=36), nullable=False),
                    sa.Column('parent', sa.String(length=36)),
                    sa.Column('device_id', sa.String(length=36)),
                    sa.Column('direction', sa.String(length=4),
                              nullable=False),
                    sa.Column('project_id', sa.String(length=36)),
                    sa.Column('class_ext_id', sa.Integer()),
                    sa.Column('parent_class_ext_id', sa.Integer()),
                    sa.Column('min', sa.String(length=15)),
                    sa.Column('max', sa.String(length=15)),
                    sa.PrimaryKeyConstraint('id')
                    )

    op.create_foreign_key(
        'fk_wtc_class',
        'wan_tc_class', 'wan_tc_class',
        ['parent'], ['id'], ondelete='CASCADE'
    )

    op.create_table('wan_tc_filter',
                    sa.Column('id', sa.String(length=36), nullable=False),
                    sa.Column('project_id', sa.String(length=36)),
                    sa.Column('class_id', sa.String(length=36),
                              nullable=False),
                    sa.Column('network', sa.String(length=36)),
                    sa.Column('protocol', sa.String(length=15)),
                    sa.Column('match', sa.String(length=15)),
                    sa.PrimaryKeyConstraint('id')
                    )

    op.create_foreign_key(
        'fk_wan_tc__filter_class',
        'wan_tc_filter', 'wan_tc_class',
        ['class_id'], ['id'],
    )

    op.create_foreign_key(
        'fk_wan_tc_filter_networks',
        'wan_tc_filter', 'networks',
        ['network'], ['id'],
    )

    op.create_table(
        'wan_tc_device',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('host', sa.String(100), nullable=False),
        sa.Column('lan_port', sa.String(15), nullable=False),
        sa.Column('wan_port', sa.String(15), nullable=False),
        sa.Column('uptime', sa.DateTime()),
        sa.Column('heartbeat_timestamp', sa.DateTime())
    )
