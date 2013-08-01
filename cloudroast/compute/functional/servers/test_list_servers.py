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

from cafe.drivers.unittest.decorators import tags
from cloudroast.compute.fixtures import ComputeFixture


class ServerListTest(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        super(ServerListTest, cls).setUpClass()
        # Creation of 3 servers needed for the tests
        active_server_response = cls.server_behaviors.create_active_server()
        cls.server = active_server_response.entity
        cls.resources.add(cls.server.id,
                          cls.servers_client.delete_server)

        active_server_response = cls.server_behaviors.create_active_server()
        cls.server_second = active_server_response.entity
        cls.resources.add(cls.server_second.id,
                          cls.servers_client.delete_server)

        active_server_response = cls.server_behaviors.create_active_server(
            image_ref=cls.image_ref_alt,
            flavor_ref=cls.flavor_ref_alt)
        cls.server_third = active_server_response.entity
        cls.resources.add(cls.server_third.id,
                          cls.servers_client.delete_server)

    @tags(type='smoke', net='no')
    def test_get_server(self):
        """Return the full details of a single server"""
        server_info_response = self.servers_client.get_server(self.server.id)
        server_info = server_info_response.entity
        self.assertEqual(200, server_info_response.status_code)
        self.assertEqual(self.server.name, server_info.name,
                         msg="Server name did not match")
        self.assertEqual(self.image_ref, server_info.image.id,
                         msg="Image id did not match")
        self.assertEqual(self.flavor_ref, server_info.flavor.id,
                         msg="Flavor id did not match")

    @tags(type='smoke', net='no')
    def test_list_servers(self):
        """All servers should be returned"""
        list_servers_response = self.servers_client.list_servers()
        servers_list = list_servers_response.entity
        self.assertEqual(200, list_servers_response.status_code)
        self.assertIn(self.server.min_details(), servers_list)
        self.assertIn(self.server_second.min_details(), servers_list)
        self.assertIn(self.server_third.min_details(), servers_list)

    @tags(type='smoke', net='no')
    def test_list_servers_with_detail(self):
        """Return a detailed list of all servers"""
        list_response = self.servers_client.list_servers_with_detail()
        list_servers_detail = list_response.entity
        self.assertEqual(200, list_response.status_code)
        servers_list = []
        for i in list_servers_detail:
            servers_list.append(i.id)
        self.assertIn(self.server.id, servers_list)
        self.assertIn(self.server_second.id, servers_list)
        self.assertIn(self.server_third.id, servers_list)

    @tags(type='positive', net='no')
    def test_list_server_details_using_marker(self):
        """The list of servers should start from the provided marker"""
        list_response = self.servers_client.list_servers_with_detail()
        list_server_detail = list_response.entity
        first_server = list_server_detail[0]

        # Verify the servers doesn't contain the server used as a marker
        params = first_server.id
        filtered_servers = self.servers_client.list_servers_with_detail(
            marker=params)
        self.assertEqual(200, filtered_servers.status_code)
        self.assertNotIn(first_server, filtered_servers.entity)

    @tags(type='positive', net='no')
    def test_list_servers_using_marker(self):
        """The list of servers should start from the provided marker"""
        list_server_info_response = self.servers_client.list_servers()
        list_server_info = list_server_info_response.entity
        first_server = list_server_info[0]

        # Verify the servers doesn't contain the server used as a marker
        params = first_server.id
        filtered_servers = self.servers_client.list_servers(
            marker=params)
        self.assertEqual(200, filtered_servers.status_code)
        self.assertNotIn(first_server, filtered_servers.entity)

    @tags(type='positive', net='no')
    def test_list_server_with_detail_limit_results(self):
        """Verify the expected number of servers are returned with details"""
        limit = 1
        params = limit
        response = self.servers_client.list_servers_with_detail(limit=params)
        servers = response.entity
        self.assertEqual(
            limit, len(response.entity),
            msg="({0}) servers returned. Expected {1} servers.".format(
                len(servers), limit))

    @tags(type='positive', net='no')
    def test_list_servers_filter_by_image(self):
        """Filter the list of servers by image"""
        params = self.image_ref
        list_servers_response = self.servers_client.list_servers(image=params)
        servers_list = list_servers_response.entity
        self.assertEqual(200, list_servers_response.status_code)

        self.assertIn(self.server.min_details(), servers_list)
        self.assertIn(self.server_second.min_details(), servers_list)
        self.assertNotIn(self.server_third.min_details(), servers_list)

    @tags(type='positive', net='no')
    def test_list_servers_filter_by_flavor(self):
        """Filter the list of servers by flavor"""
        params = self.flavor_ref_alt
        list_servers_response = self.servers_client.list_servers(flavor=params)
        servers_list = list_servers_response.entity
        self.assertEqual(200, list_servers_response.status_code)

        self.assertNotIn(self.server.min_details(), servers_list)
        self.assertNotIn(self.server_second.min_details(), servers_list)
        self.assertIn(self.server_third.min_details(), servers_list)

    @tags(type='positive', net='no')
    def test_list_servers_filter_by_server_name(self):
        """ Filter the list of servers by name """
        params = self.server.name
        list_servers_response = self.servers_client.list_servers(name=params)
        servers_list = list_servers_response.entity
        self.assertEqual(200, list_servers_response.status_code)
        self.assertIn(self.server.min_details(), servers_list)
        self.assertNotIn(self.server_second.min_details(), servers_list)
        self.assertNotIn(self.server_third.min_details(), servers_list)

    @tags(type='positive', net='no')
    def test_list_servers_filter_by_server_status(self):
        """ Filter the list of servers by server status """
        params = 'active'
        list_servers_response = self.servers_client.list_servers(status=params)
        list_servers = list_servers_response.entity
        self.assertEqual(200, list_servers_response.status_code)
        self.assertIn(self.server.min_details(), list_servers)
        self.assertIn(self.server_second.min_details(), list_servers)
        self.assertIn(self.server_third.min_details(), list_servers)

    @tags(type='positive', net='no')
    def test_list_servers_filter_by_changes_since(self):
        """Filter the list of servers by changes-since"""
        change_time = self.server_second.created
        params = change_time
        servers = self.servers_client.list_servers(changes_since=params)
        self.assertEqual(200, servers.status_code)
        servers_ids_list = []
        for i in servers.entity:
            servers_ids_list.append(i.id)
        self.assertNotIn(self.server.id, servers_ids_list)
        self.assertIn(self.server_second.id, servers_ids_list)
        self.assertIn(self.server_third.id, servers_ids_list)

    @tags(type='positive', net='no')
    def test_list_servers_detailed_filter_by_image(self):
        """Filter the detailed list of servers by image"""
        params = self.image_ref
        list_response = self.servers_client.list_servers_with_detail(
            image=params)
        self.assertEqual(200, list_response.status_code)
        servers_list = []
        for i in list_response.entity:
            servers_list.append(i.id)
        self.assertIn(self.server.id, servers_list)
        self.assertIn(self.server_second.id, servers_list)
        self.assertNotIn(self.server_third.id, servers_list)

    @tags(type='positive', net='no')
    def test_list_servers_detailed_filter_by_flavor(self):
        """Filter the detailed list of servers by flavor"""
        params = self.flavor_ref_alt
        list_response = self.servers_client.list_servers_with_detail(
            flavor=params)
        filtered_servers = list_response.entity
        self.assertEqual(200, list_response.status_code)

        self.assertNotIn(self.server, filtered_servers)
        self.assertNotIn(self.server_second, filtered_servers)
        self.assertIn(self.server_third, filtered_servers)

    @tags(type='positive', net='no')
    def test_list_servers_detailed_filter_by_server_name(self):
        """Filter the detailed list of servers by server name"""
        params = self.server.name
        list_response = self.servers_client.list_servers_with_detail(
            name=params)
        filtered_servers = list_response.entity
        self.assertEqual(200, list_response.status_code)

        self.assertIn(self.server, filtered_servers)
        self.assertNotIn(self.server_second, filtered_servers)
        self.assertNotIn(self.server_third, filtered_servers)

    @tags(type='positive', net='no')
    def test_list_servers_detailed_filter_by_server_status(self):
        """Filter the detailed list of servers by server status"""
        params = 'active'
        list_response = self.servers_client.list_servers_with_detail(
            status=params)
        filtered_servers = list_response.entity
        self.assertEqual(200, list_response.status_code)
        servers_list = []
        for i in filtered_servers:
            servers_list.append(i.id)
        self.assertIn(self.server.id, servers_list)
        self.assertIn(self.server_second.id, servers_list)
        self.assertIn(self.server_third.id, servers_list)

    @tags(type='positive', net='no')
    def test_list_servers_detailed_filter_by_changes_since(self):
        """Filter the detailed servers list with the changes-since filter"""
        change_time = self.server_second.created
        params = change_time

        # Filter the detailed list of servers by changes-since
        list_response = self.servers_client.list_servers_with_detail(
            changes_since=params)
        filtered_servers = list_response.entity
        self.assertEqual(200, list_response.status_code)
        servers_list = []
        for i in filtered_servers:
            servers_list.append(i.id)
        self.assertNotIn(self.server.id, servers_list)
        self.assertIn(self.server_second.id, servers_list)
        self.assertIn(self.server_third.id, servers_list)
