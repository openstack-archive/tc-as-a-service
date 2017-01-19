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

import threading

from oslo_utils import uuidutils
from oslo_utils import timeutils
from oslo_log import log as logging

from neutron.db.models import segment

from wan_qos.db.models import wan_tc as models
from wan_qos.common import constants

LOG = logging.getLogger(__name__)


class WanTcDb(object):
    _last_class_ext_id = None

    def __init__(self):
        self._lock = threading.Lock()

    def agent_up_notification(self, context, host_info):
        device = context.session.query(models.WanTcDevice).filter_by(
            host=host_info['host']
        ).first()

        with context.session.begin(subtransactions=True):
            if not device:
                LOG.debug('New device connected: %s' % host_info)
                now = timeutils.utcnow()
                wan_tc_device = models.WanTcDevice(
                    id=uuidutils.generate_uuid(),
                    host=host_info['host'],
                    lan_port=host_info['lan_port'],
                    wan_port=host_info['wan_port'],
                    uptime=now,
                    heartbeat_timestamp=now
                )
                return context.session.add(wan_tc_device)
            else:
                LOG.debug('updating uptime for device: %s' % host_info['host'])
                device.uptime = timeutils.utcnow()

    def device_heartbeat(self, context, host):
        device = context.session.query(models.WanTcDevice).filter_by(
            host=host
        ).first()
        if device:
            with context.session.begin(subtransactions=True):
                device.heartbeat_timestamp = timeutils.utcnow()
        else:
            LOG.error('Got heartbeat for non-existing device: %s' % host)

    def get_all_devices(self, context):
        device_list = context.session.query(models.WanTcDevice).all()
        device_list_dict = []
        for device in device_list:
            device_list_dict.append(self._device_to_dict(device))

        return device_list_dict

    def get_last_class_ext_id(self, context):

        self._lock.acquire()
        if not self._last_class_ext_id:
            last_class_ext_id_db, = context.session.query(
                models.WanTcClass.class_ext_id).order_by(
                models.WanTcClass.class_ext_id.desc()).first()
            if last_class_ext_id_db:
                self._last_class_ext_id = last_class_ext_id_db
            else:
                self._last_class_ext_id = 10
        self._last_class_ext_id += 1
        next_id = self._last_class_ext_id
        self._lock.release()
        return next_id

    def create_wan_tc_class(self, context, wtc_class):

        wtc_class_db = models.WanTcClass(
            id=uuidutils.generate_uuid(),
            direction=wtc_class['direction'],
            class_ext_id=self.get_last_class_ext_id(context)
        )

        parent = wtc_class['parent']
        if parent:
            wtc_class_db.parent = parent
        else:
            wtc_class_db.parent = wtc_class_db.id

        with context.session.begin(subtransactions=True):

            if wtc_class['min']:
                wtc_class_db.min = wtc_class['min']
            if wtc_class['max']:
                wtc_class_db.max = wtc_class['max']

            context.session.add(wtc_class_db)
            return self._class_to_dict(wtc_class_db)

    def delete_wtc_class(self, context, id):
        wtc_class_db = context.session.query(models.WanTcClass).filter_by(
            id=id).first()
        if wtc_class_db:
            with context.session.begin(subtransactions=True):
                context.session.delete(wtc_class_db)

    def get_class_by_id(self, context, id):
        wtc_class = context.session.query(models.WanTcClass).filter_by(
            id=id).first()
        if wtc_class:
            return self._class_to_dict(wtc_class)

    def get_all_classes(self, context):
        wtc_classes_db = context.session.query(models.WanTcClass).all()
        wtc_classes = []
        for wtc_class in wtc_classes_db:
            wtc_classes.append(self._class_to_dict(wtc_class))
        return wtc_classes

    def _class_to_dict(self, wtc_class):

        class_dict = {
            'id': wtc_class.id,
            'direction': wtc_class.direction,
            'min': wtc_class.min,
            'max': wtc_class.max
        }

        if wtc_class.parent == wtc_class.id:
            class_dict['parent'] = ''
        else:
            class_dict['parent'] = wtc_class.parent

        return class_dict

    def _device_to_dict(self, device):
        device_dict = {
            'id': device.id,
            'host': device.host,
            'lan_port': device.lan_port,
            'wan_port': device.wan_port,
            'uptime': device.uptime,
            'last_seen': device.heartbeat_timestamp
        }

        return device_dict

    def delete_wan_tc_device(self, context, id):
        device = context.session.query(models.WanTcDevice).filter_by(
            id=id
        ).first()
        if device:
            with context.session.begin(subtransactions=True):
                context.session.delete(device)
        else:
            LOG.error('Trying to delete none existing device. id=%s' % id)

    def get_device(self, context, id):
        device = context.session.query(models.WanTcDevice).filter_by(
            id=id
        ).first()
        if device:
            return self._device_to_dict(device)
