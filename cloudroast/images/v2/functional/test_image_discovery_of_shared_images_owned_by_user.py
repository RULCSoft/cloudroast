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
from cloudcafe.images.common.types import ImageMemberStatus
from cloudroast.images.fixtures import ComputeIntegrationFixture


class ImageDiscoverySharedImagesOwnedByUserTest(ComputeIntegrationFixture):

    @classmethod
    def setUpClass(cls):
        super(ImageDiscoverySharedImagesOwnedByUserTest, cls).setUpClass()
        cls.images_list = cls.images_behavior.create_images_via_task(count=3)

    @tags(type='positive', regression='true')
    def test_image_discovery_of_shared_images_owned_by_user(self):
        """
        @summary: Image discovery of shared images owned by user

        1) Create three images as tenant
        2) List images owned by tenant, as tenant
        3) Verify that the returned list contains all three images
        4) List images owned by tenant, as alternate tenant
        5) Verify that the returned list of images does not contain any of the
        three images
        6) Add alternate tenant as a member of all three images
        7) Update membership of alternate tenant to 'Accepted' for image_one
        8) Update membership of alternate tenant to 'Rejected' for image_two
        9) List images owned by tenant, as alternate tenant
        10) Verify that the returned list of images now contains image_one only
        11) Verify that the returned list does not contain image_two or
        image_three
        12) List images via nova, as alternate tenant
        13) Verify that the response code is 200
        14) Verify that the returned list of images contains image_one
        15) Verify that the returns list does not contain image_two or
        image_three
        """

        tenant_id = self.tenant_id
        alt_tenant_id = self.alt_tenant_id

        images = self.images_behavior.list_images_pagination(owner=tenant_id)
        for image in self.images_list:
            self.assertIn(image, images)

        images = self.alt_images_behavior.list_images_pagination(
            owner=tenant_id)
        for image in self.images_list:
            self.assertNotIn(image, images)

        for image_id in [x.id_ for x in self.images_list]:
            response = self.images_client.add_member(
                image_id=image_id, member_id=alt_tenant_id)
            self.assertEqual(response.status_code, 200)
            member = response.entity
            self.assertEqual(member.member_id, alt_tenant_id)
            self.assertEqual(member.status, ImageMemberStatus.PENDING)

        image_one = self.images_list.pop()
        image_two = self.images_list.pop()
        image_three = self.images_list.pop()

        response = self.alt_images_client.update_member(
            image_id=image_one.id_, member_id=alt_tenant_id,
            status=ImageMemberStatus.ACCEPTED)
        self.assertEqual(response.status_code, 200)
        member = response.entity
        self.assertEqual(member.member_id, alt_tenant_id)
        self.assertEqual(member.status, ImageMemberStatus.ACCEPTED)

        response = self.alt_images_client.update_member(
            image_id=image_two.id_, member_id=alt_tenant_id,
            status=ImageMemberStatus.REJECTED)
        self.assertEqual(response.status_code, 200)
        member = response.entity
        self.assertEqual(member.member_id, alt_tenant_id)
        self.assertEqual(member.status, ImageMemberStatus.REJECTED)

        glance_images = self.alt_images_behavior.list_images_pagination(
            owner=tenant_id)
        self.assertIn(image_one, glance_images)
        self.assertNotIn(image_two, glance_images)
        self.assertNotIn(image_three, glance_images)

        response = self.alt_compute_images_client.list_images_with_detail()
        self.assertEqual(response.status_code, 200)
        nova_images = response.entity

        nova_image_names = [image.name for image in nova_images]

        self.assertIn(image_one.name, nova_image_names)
        self.assertNotIn(image_two.name, nova_image_names)
        self.assertNotIn(image_three.name, nova_image_names)
