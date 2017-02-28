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

import sqlalchemy as sa

from neutron import context as ctx
from neutron.db.models import segment
from neutron_lib import exceptions

from wan_qos.db.models import wan_tc as models
from wan_qos.common import constants

LOG = logging.getLogger(__name__)


class WanTcDb(object):
    _last_class_ext_id = None

    def __init__(self):
        self._lock = threading.Lock()
        self._initialize_tables()

    def _initialize_tables(self):
        context = ctx.get_admin_context()
        root_class = context.session.query(models.WanTcClass).filter_by(
            id='root').first()
        if not root_class:
            with context.session.begin(subtransactions=True):
                root_class = models.WanTcClass(
                    id='root',
                    class_ext_id=1,
                    direction='both'
                )
                context.session.add(root_class)

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

    def get_all_devices(self, context, filters=None,
                        fields=None,
                        sorts=None, limit=None, marker=None,
                        page_reverse=False):
        marker_obj = self._get_marker_obj(
            context, 'wan_tc_device', limit, marker)
        return self._get_collection(context, models.WanTcDevice,
                                    self._device_to_dict,
                                    filters=filters, fields=fields,
                                    sorts=sorts, limit=limit,
                                    marker_obj=marker_obj,
                                    page_reverse=page_reverse)

    def get_last_class_ext_id(self, context):

        self._lock.acquire()
        if not self._last_class_ext_id:
            last_class_ext_id_db = context.session.query(
                models.WanTcClass.class_ext_id).order_by(
                models.WanTcClass.class_ext_id.desc()).first()
            if last_class_ext_id_db:
                self._last_class_ext_id, = last_class_ext_id_db
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

        if 'parent' in wtc_class and wtc_class['parent'] != '':
            parent = wtc_class['parent']
            parent_class = self.get_class_by_id(context, parent)
            if not parent_class:
                raise exceptions.BadRequest(msg='invalid parent id')
            wtc_class_db.parent = parent
            wtc_class_db.parent_class_ext_id = parent_class['class_ext_id']
        else:
            wtc_class_db.parent = 'root'
            wtc_class_db.parent_class_ext_id = 1

        with context.session.begin(subtransactions=True):

            if 'min' in wtc_class:
                wtc_class_db.min = wtc_class['min']
            if 'max' in wtc_class:
                wtc_class_db.max = wtc_class['max']

            context.session.add(wtc_class_db)
        class_dict = self._class_to_dict(wtc_class_db)
        class_dict['parent_class_ext_id'] = wtc_class_db.parent_class_ext_id
        return class_dict

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

    def get_all_classes(self, context, filters=None,
                        fields=None,
                        sorts=None, limit=None, marker=None,
                        page_reverse=False):
        marker_obj = self._get_marker_obj(
            context, 'wan_tc_class', limit, marker)
        all_classes = self._get_collection(context, models.WanTcClass,
                                           self._class_to_dict,
                                           filters=filters, fields=fields,
                                           sorts=sorts, limit=limit,
                                           marker_obj=marker_obj,
                                           page_reverse=page_reverse)
        if not filters:
            for wtc_class in all_classes:
                if wtc_class['id'] == 'root':
                    all_classes.remove(wtc_class)
                    break
        return all_classes

    def _class_to_dict(self, wtc_class, fields=None):

        class_dict = {
            'id': wtc_class.id,
            'direction': wtc_class.direction,
            'min': wtc_class.min,
            'max': wtc_class.max,
            'class_ext_id': wtc_class.class_ext_id,
            'parent': wtc_class.parent,
            'parent_class_ext_id': wtc_class.parent_class_ext_id
        }

        return class_dict

    def _device_to_dict(self, device, fields=None):
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

    def get_class_tree(self, start_from_id='root'):
        context = ctx.get_admin_context()
        root_class_db = context.session.query(models.WanTcClass).filter_by(
            id=start_from_id).first()
        root_class = self._class_to_dict(root_class_db)
        self._get_child_classes(context, root_class)
        return root_class

    def _get_child_classes(self, context, parent_class):
        child_classes_db = context.session.query(models.WanTcClass).filter_by(
            parent=parent_class['id']).all()
        parent_class['child_list'] = []
        for child_class_db in child_classes_db:
            child_class = self._class_to_dict(child_class_db)
            parent_class['child_list'].append(child_class)
            self._get_child_classes(context, child_class)

    def create_wan_tc_filter(self, context, wan_tc_filter):

        wtc_filter_db = models.WanTcFilter(
            id=uuidutils.generate_uuid(),
            protocol=wan_tc_filter['protocol'],
            match=wan_tc_filter['match'],
            class_id=wan_tc_filter['class_id']
        )

        if 'network' in wan_tc_filter:
            wtc_filter_db.network = wan_tc_filter['network']

        with context.session.begin(subtransactions=True):
            context.session.add(wtc_filter_db)

        return self._filter_to_dict(wtc_filter_db)

    def _filter_to_dict(self, wtc_filter_db, fields=None):
        wtc_filter = {
            'id': wtc_filter_db.id,
            'protocol': wtc_filter_db.protocol,
            'match': wtc_filter_db.match,
            'class_id': wtc_filter_db.class_id,
            'network': wtc_filter_db.network
        }

        return wtc_filter

    def get_wan_tc_filter(self, context, id, fields=None):

        wtc_filter_db = context.session.query(models.WanTcFilter).filter_by(
            id=id).first()
        if wtc_filter_db:
            return self._filter_to_dict(wtc_filter_db)
        return {}

    def get_wan_tc_filters(self, context, filters=None, fields=None,
                           sorts=None, limit=None, marker=None,
                           page_reverse=False):
        marker_obj = self._get_marker_obj(
            context, 'wan_tc_filter', limit, marker)
        return self._get_collection(context, models.WanTcFilter,
                                    self._filter_to_dict,
                                    filters=filters, fields=fields,
                                    sorts=sorts, limit=limit,
                                    marker_obj=marker_obj,
                                    page_reverse=page_reverse)

    def delete_wan_tc_filter(self, context, id):
        filter_db = context.session.query(models.WanTcFilter).filter_by(
            id=id
        ).first()
        if filter_db:
            with context.session.begin(subtransactions=True):
                context.session.delete(filter_db)
        else:
            LOG.error('Trying to delete none existing tc filter. id=%s' % id)

    def _get_collection(self, context, model, dict_func, filters=None,
                        fields=None, sorts=None, limit=None, marker_obj=None,
                        page_reverse=False):
        """Get collection object based on query for resources."""
        if not self._has_attribute(model, filters):
            return []
        query = self._get_collection_query(context, model, filters=filters,
                                           sorts=sorts,
                                           limit=limit,
                                           marker_obj=marker_obj,
                                           page_reverse=page_reverse)
        items = [dict_func(c, fields) for c in query]
        if limit and page_reverse:
            items.reverse()
        return items

    def _has_attribute(self, model, filters):
        if filters:
            for key in filters.keys():
                if not hasattr(model, key):
                    return False
        return True

    def _get_collection_query(self, context, model, filters=None,
                              sorts=None, limit=None, marker_obj=None,
                              page_reverse=False):
        """Get collection query for the models."""
        collection = self._model_query(context, model)
        collection = self._apply_filters_to_query(collection, model, filters)
        return collection

    def _get_marker_obj(self, context, resource, limit, marker):
        """Get marker object for the resource."""
        if limit and marker:
            return getattr(self, '_get_%s' % resource)(context, marker)
        return None

    def _model_query(self, context, model):
        """Query model based on filter."""
        query = context.session.query(model)
        query_filter = None
        if not context.is_admin and hasattr(model, 'tenant_id'):
            query_filter = (model.tenant_id == context.tenant_id)
        if query_filter is not None:
            query = query.filter(query_filter)
        return query

    def _apply_filters_to_query(self, query, model, filters):
        """Apply filters to query for the models."""
        if filters:
            for key, value in filters.items():
                column = getattr(model, key, None)
                if column:
                    query = query.filter(column.in_(value))
        return query
