"""
Copyright 2013 Rackspace

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from binascii import b2a_base64

from cafe.drivers.unittest.decorators import tags
from cloudroast.cloudkeep.barbican.rbac import RBACSecretRoles
from cloudroast.cloudkeep.barbican.rbac import RBACOrderRoles


class RBACObserverRoleForSecretAPI(RBACSecretRoles):

    @classmethod
    def setUpClass(cls):
        super(RBACObserverRoleForSecretAPI, cls).setUpClass(
            username=cls.rbac_config.observer,
            password=cls.rbac_config.observer_password)

    @tags(type='positive')
    def test_get_secret_metadata_as_observer(self):
        resp = self.admin_fixture.behaviors.create_secret_from_config()
        self.assertEqual(resp.status_code, 201)

        sec_resp = self.client.get_secret(secret_id=resp.id)
        self.assertEqual(sec_resp.status_code, 200)
        metadata = sec_resp.entity

        self.assertEqual(sec_resp.status_code, 200)
        self.assertEqual(metadata.name, self.config.name)
        self.assertEqual(metadata.mode, self.config.mode)

    @tags(type='positive')
    def test_get_secret_list_as_observer(self):
        # Create 10 secrets
        for i in range(0, 11):
            self.admin_fixture.behaviors.create_secret_from_config()

        get_resp = self.client.get_secrets()
        self._check_list_of_secrets(resp=get_resp, limit=10)

    @tags(type='positive')
    def test_get_secret_content_as_observer(self):
        resp = self.admin_fixture.behaviors.create_secret_from_config()
        self.assertEqual(resp.status_code, 201)

        sec_resp = self.client.get_secret(
            secret_id=resp.id,
            payload_content_type=self.config.payload_content_type)
        self.assertEqual(sec_resp.status_code, 200)
        self.assertIn(self.config.payload, b2a_base64(sec_resp.content))

    @tags(type='negative')
    def test_create_secret_as_observer(self):
        """Should return 401 as observer user doesn't have permission"""
        resp = self.behaviors.create_secret_from_config()
        self.assertEqual(resp.status_code, 401)

    @tags(type='negative')
    def test_update_secret_as_observer(self):
        resp = self.admin_fixture.behaviors.create_secret()
        self.assertEqual(resp.status_code, 201)

        # Update attempt should return 401
        update_resp = self.client.add_secret_payload(
            secret_id=resp.id,
            payload_content_type=self.config.payload_content_type,
            payload='testing_update_secret')
        self.assertEqual(update_resp.status_code, 401)

    @tags(type='negative')
    def test_delete_secret_as_observer(self):
        resp = self.admin_fixture.behaviors.create_secret_from_config()
        self.assertEqual(resp.status_code, 201)

        # Delete attempt should return 401
        resp = self.behaviors.delete_secret(resp.id)
        self.assertEqual(resp.status_code, 401)


class RBACObserverRoleForOrdersAPI(RBACOrderRoles):

    @classmethod
    def setUpClass(cls):
        super(RBACObserverRoleForOrdersAPI, cls).setUpClass(
            username=cls.rbac_config.observer,
            password=cls.rbac_config.observer_password)

    @tags(type='positive')
    def test_get_order_as_observer(self):
        # Create an order to try to get as observer user
        resp = self.admin_fixture.behaviors.create_order_from_config()
        self.assertEqual(resp.status_code, 202)

        get_resp = self.orders_client.get_order(resp.id)
        self.assertEqual(get_resp.status_code, 200)

    @tags(type='positive')
    def test_get_orders_as_observer(self):
        # Create 10 orders
        for i in range(0, 11):
            self.admin_fixture.behaviors.create_order_from_config()

        resp = self.orders_client.get_orders()
        self._check_list_of_orders(resp=resp, limit=10)

    @tags(type='negative')
    def test_create_order_as_observer(self):
        resp = self.behaviors.create_order_overriding_cfg()
        self.assertEqual(resp.status_code, 401)

    @tags(type='negative')
    def test_delete_order_as_observer(self):
        # Create an order to try to delete as audit user
        resp = self.admin_fixture.behaviors.create_order_from_config()
        self.assertEqual(resp.status_code, 202)

        resp = self.behaviors.delete_order(order_id=resp.id)
        self.assertEqual(resp.status_code, 401)
