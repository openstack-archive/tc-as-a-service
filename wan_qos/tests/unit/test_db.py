from neutron import context as ctx
from neutron.tests import base
from neutron.tests.unit import testlib_api

from oslo_config import cfg

from wan_qos.db import wan_qos_db
from wan_qos.services import plugin


class TestTcDb(testlib_api.SqlTestCase):
    def setUp(self):
        super(TestTcDb, self).setUp()
        self.db = wan_qos_db.WanTcDb()
        self.context = ctx.get_admin_context()

    def test_add_class(self):
        wtc_class = {
            'direction': 'both',
            'min': '1mbit'
        }
        wtc_class_db = self.db.create_wan_tc_class(self.context, wtc_class)

        assert wtc_class_db is not None

    def test_get_class_by_id(self):

        class_db_1 = self._add_class(None, 'both', '1mbit', '2mbit')
        class_db_2 = self._add_class(class_db_1['id'], 'both', '2mbit',
                                     '3mbit')
        class_db_3 = self._add_class(class_db_2['id'], 'both', '3mbit',
                                     '4mbit')

        class_by_id = self.db.get_class_by_id(self.context, class_db_1['id'])
        # class_by_id = self.db.get_class_by_id(self.context, '111')
        print (class_by_id)

    def test_get_class_tree(self):

        class_db_1 = self._add_class(None, 'both', '1mbit', '2mbit')
        class_db_2 = self._add_class(class_db_1['id'], 'both', '2mbit',
                                     '3mbit')
        class_db_3 = self._add_class(class_db_2['id'], 'both', '3mbit',
                                     '4mbit')

        class_tree = self.db.get_class_tree()
        assert class_tree is not None
        print (class_tree)

        class_tree = self.db.get_class_tree(class_db_1['id'])
        assert class_tree is not None
        print (class_tree)

        class_tree = self.db.get_class_tree(class_db_2['id'])
        assert class_tree is not None
        print (class_tree)

        class_tree = self.db.get_class_tree(class_db_3['id'])
        assert class_tree is not None
        print (class_tree)

    def test_get_classes(self):
        self.test_add_class()
        all_classes = self.db.get_all_classes(self.context)
        print ('all classes: %s' % all_classes)

    def _add_class(self, parent, direction, min, max):
        wtc_class = {
            'direction': direction,
        }
        if min:
            wtc_class['min'] = min
        if parent:
            wtc_class['parent'] = parent
        if max:
            wtc_class['max'] = max

        return self.db.create_wan_tc_class(self.context, wtc_class)


class TestPlugin(testlib_api.SqlTestCase):
    def setUp(self):
        super(TestPlugin, self).setUp()
        self.plugin = plugin.WanQosPlugin()

    def test_create_class(self):
        wtc_class = {
            'wan_tc_class': {
                'direction': 'both',
                'min': '1mbit'
            }
        }

        wan_tc = self.plugin.create_wan_tc_class(ctx.get_admin_context(),
                                                 wtc_class)

        assert wan_tc is not None
        print (wan_tc)

    def test_get_class_by_id(self):

        class_db_1 = self._add_class(None, 'both', '1mbit', '2mbit')
        class_db_2 = self._add_class(class_db_1['id'], 'both', '2mbit',
                                     '3mbit')
        class_db_3 = self._add_class(class_db_2['id'], 'both', '3mbit',
                                     '4mbit')

        tc_class = self.plugin.get_wan_tc_class(ctx.get_admin_context(),
                                                class_db_1['id'])

        print(tc_class)
        filters = {'id': [class_db_1['id']]}
        tc_classes = self.plugin.get_wan_tc_classs(ctx.get_admin_context())

        print(tc_classes)

    def test_get_all_classes_by_id(self):

        class_db_1 = self._add_class(None, 'both', '1mbit', '2mbit')
        print ('class_1: %s ' % class_db_1)

        filters = {'id': [class_db_1['id']]}
        # filters = {'id': ['11']}
        # filters = {'name': ['111']}

        tc_classes = self.plugin.get_wan_tc_classs(ctx.get_admin_context(),
                                                   filters=filters)

        print(tc_classes)

        filters = {'name': ['111']}

        tc_classes = self.plugin.get_wan_tc_classs(ctx.get_admin_context(),
                                                   filters=filters)

        print(tc_classes)







    def test_add_filter(self):

        class_db = self._add_class(None, 'both', '1mbit', '2mbit')
        filter = self._get_filter(class_db['id'])
        filter_db = self.plugin.create_wan_tc_filter(ctx.get_admin_context(),
                                                     filter)

        print ('filter: %s' % filter_db)

        filters = {
            'id': [filter_db['id']]
            # 'name': ['123']
        }
        filter_by_id = self.plugin.get_wan_tc_filters(ctx.get_admin_context(),
                                                      filters=filters)

        print('filter by id: %s' % filter_by_id)

    def _get_filter(self, class_id):

        filter = {'wan_tc_filter': {
            'protocol': 'vxlan',
            'match': 'vni=123',
            'class_id': class_id
        }
        }

        return filter

    def _add_class(self, parent, direction, min, max):
        wtc_class = {
            'direction': direction,
        }
        if min:
            wtc_class['min'] = min
        if parent:
            wtc_class['parent'] = parent
        if max:
            wtc_class['max'] = max

        return self.plugin.db.create_wan_tc_class(ctx.get_admin_context(),
                                                  wtc_class)
