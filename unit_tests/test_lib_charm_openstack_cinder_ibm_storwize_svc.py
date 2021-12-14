# Copyright 2016 Canonical Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import
from __future__ import print_function

import charmhelpers

import charm.openstack.cinder_ibm_storwize_svc as cinder_ibm_storwize_svc

import charms_openstack.test_utils as test_utils


class TestCinderIBMStorwizeSVCCharm(test_utils.PatchHelper):
    def _patch_config_and_charm(self, config):
        self.patch_object(charmhelpers.core.hookenv, "config")

        def cf(key=None):
            if key is not None:
                return config[key]
            return config

        self.config.side_effect = cf
        c = cinder_ibm_storwize_svc.CinderIBMStorwizeSVCCharm()
        return c

    def test_cinder_base(self):
        charm = self._patch_config_and_charm({})
        self.assertEqual(charm.name, "cinder_ibm_storwize_svc")
        self.assertEqual(charm.version_package, "cinder-common")
        self.assertEqual(charm.packages, ["", "multipath-tools", "sysfsutils"])

    def test_cinder_configuration_missing_mandatory_config(self):
        charm = self._patch_config_and_charm(
            {
                "volume-backend-name": "my_backend_name",
                "protocol": "iscsi",
                "san-ip": "192.0.2.1",
                "san-login": "superuser",
                "san-password": None,
                "storwize-svc-volpool-name": "cinder_pool1",
            }
        )
        config = charm.cinder_configuration()
        self.assertEqual(config, [])

    def test_cinder_configuration_iscsi(self):
        charm = self._patch_config_and_charm(
            {
                "volume-backend-name": "my_backend_name",
                "protocol": "iscsi",
                "san-ip": "192.0.2.1",
                "san-login": "superuser",
                "san-password": "my-password",
                "storwize-svc-volpool-name": "cinder_pool1",
            }
        )
        config = charm.cinder_configuration()
        self.assertEqual(
            config,
            [
                ("volume_backend_name", "my_backend_name"),
                (
                    "volume_driver",
                    "cinder.volume.drivers.ibm.storwize_svc.storwize_svc_iscsi.StorwizeSVCISCSIDriver",  # noqa
                ),
                ("san_ip", "192.0.2.1"),
                ("san_login", "superuser"),
                ("san_password", "my-password"),
                ("storwize_svc_volpool_name", "cinder_pool1"),
            ],
        )

    def test_cinder_configuration_fc(self):
        charm = self._patch_config_and_charm(
            {
                "volume-backend-name": "my_backend_name",
                "protocol": "fc",
                "san-ip": "192.0.2.1",
                "san-login": "superuser",
                "san-password": "my-password",
                "storwize-svc-volpool-name": "cinder_pool1",
            }
        )
        config = charm.cinder_configuration()
        self.assertEqual(
            config,
            [
                ("volume_backend_name", "my_backend_name"),
                (
                    "volume_driver",
                    "cinder.volume.drivers.ibm.storwize_svc.storwize_svc_fc.StorwizeSVCFCDriver",  # noqa
                ),
                ("san_ip", "192.0.2.1"),
                ("san_login", "superuser"),
                ("san_password", "my-password"),
                ("storwize_svc_volpool_name", "cinder_pool1"),
            ],
        )

    def test_cinder_configuration_no_explicit_backend_name(self):
        self.patch_object(charmhelpers.core.hookenv, "service_name")
        self.service_name.return_value = "cinder-myapp-name"
        charm = self._patch_config_and_charm(
            {
                "volume-backend-name": None,
                "protocol": "iscsi",
                "san-ip": "192.0.2.1",
                "san-login": "superuser",
                "san-password": "my-password",
                "storwize-svc-volpool-name": "cinder_pool1",
            }
        )
        config = charm.cinder_configuration()
        self.assertEqual(
            config,
            [
                ("volume_backend_name", "cinder-myapp-name"),
                (
                    "volume_driver",
                    "cinder.volume.drivers.ibm.storwize_svc.storwize_svc_iscsi.StorwizeSVCISCSIDriver",  # noqa
                ),
                ("san_ip", "192.0.2.1"),
                ("san_login", "superuser"),
                ("san_password", "my-password"),
                ("storwize_svc_volpool_name", "cinder_pool1"),
            ],
        )

    def test_cinder_configuration_enable_multipath(self):
        charm = self._patch_config_and_charm(
            {
                "volume-backend-name": "my_backend_name",
                "use-multipath": True,
                "protocol": "iscsi",
                "san-ip": "192.0.2.1",
                "san-login": "superuser",
                "san-password": "my-password",
                "storwize-svc-volpool-name": "cinder_pool1",
            }
        )
        config = charm.cinder_configuration()
        self.assertEqual(
            config,
            [
                ("volume_backend_name", "my_backend_name"),
                (
                    "volume_driver",
                    "cinder.volume.drivers.ibm.storwize_svc.storwize_svc_iscsi.StorwizeSVCISCSIDriver",  # noqa
                ),
                ("san_ip", "192.0.2.1"),
                ("san_login", "superuser"),
                ("san_password", "my-password"),
                ("storwize_svc_volpool_name", "cinder_pool1"),
                ("use_multipath_for_image_xfer", True),
                ("enforce_multipath_for_image_xfer", True),
                ("storwize_svc_multipath_enabled", True),
            ],
        )

    def test_cinder_configuration_san_secondary_ip(self):
        charm = self._patch_config_and_charm(
            {
                "volume-backend-name": "my_backend_name",
                "protocol": "iscsi",
                "san-ip": "192.0.2.1",
                "storwize-san-secondary-ip": "192.0.2.2",
                "san-login": "superuser",
                "san-password": "my-password",
                "storwize-svc-volpool-name": "cinder_pool1",
            }
        )
        config = charm.cinder_configuration()
        self.assertEqual(
            config,
            [
                ("volume_backend_name", "my_backend_name"),
                (
                    "volume_driver",
                    "cinder.volume.drivers.ibm.storwize_svc.storwize_svc_iscsi.StorwizeSVCISCSIDriver",  # noqa
                ),
                ("san_ip", "192.0.2.1"),
                ("san_login", "superuser"),
                ("san_password", "my-password"),
                ("storwize_svc_volpool_name", "cinder_pool1"),
                ("storwize_san_secondary_ip", "192.0.2.2"),
            ],
        )

    def test_cinder_configuration_mirror_pool(self):
        charm = self._patch_config_and_charm(
            {
                "volume-backend-name": "my_backend_name",
                "protocol": "iscsi",
                "san-ip": "192.0.2.1",
                "san-login": "superuser",
                "san-password": "my-password",
                "storwize-svc-volpool-name": "cinder_pool1",
                "storwize-preferred-host-site": "site1:iqn1,site2:iqn2&wiqn3",
                "storwize-svc-mirror-pool": "pool2",
            }
        )
        config = charm.cinder_configuration()
        self.assertEqual(
            config,
            [
                ("volume_backend_name", "my_backend_name"),
                (
                    "volume_driver",
                    "cinder.volume.drivers.ibm.storwize_svc.storwize_svc_iscsi.StorwizeSVCISCSIDriver",  # noqa
                ),
                ("san_ip", "192.0.2.1"),
                ("san_login", "superuser"),
                ("san_password", "my-password"),
                ("storwize_svc_volpool_name", "cinder_pool1"),
                (
                    "storwize_preferred_host_site",
                    "site1:iqn1,site2:iqn2&wiqn3",
                ),
                ("storwize_svc_mirror_pool", "pool2"),
            ],
        )

    def test_cinder_configuration_stretched_cluster(self):
        charm = self._patch_config_and_charm(
            {
                "volume-backend-name": "my_backend_name",
                "protocol": "iscsi",
                "san-ip": "192.0.2.1",
                "san-login": "superuser",
                "san-password": "my-password",
                "storwize-svc-volpool-name": "cinder_pool1",
                "storwize-svc-stretched-cluster-partner": "my_pool2",
            }
        )
        config = charm.cinder_configuration()
        self.assertEqual(
            config,
            [
                ("volume_backend_name", "my_backend_name"),
                (
                    "volume_driver",
                    "cinder.volume.drivers.ibm.storwize_svc.storwize_svc_iscsi.StorwizeSVCISCSIDriver",  # noqa
                ),
                ("san_ip", "192.0.2.1"),
                ("san_login", "superuser"),
                ("san_password", "my-password"),
                ("storwize_svc_volpool_name", "cinder_pool1"),
                ("storwize_svc_stretched_cluster_partner", "my_pool2"),
            ],
        )

    def test_cinder_configuration_stretched_advanced(self):
        charm = self._patch_config_and_charm(
            {
                "volume-backend-name": "my_backend_name",
                "protocol": "iscsi",
                "san-ip": "192.0.2.1",
                "san-login": "superuser",
                "san-password": "my-password",
                "storwize-svc-volpool-name": "cinder_pool1",
                "storwize-svc-vol-compression": True,
                "storwize-svc-vol-iogrp": 2,
            }
        )
        config = charm.cinder_configuration()
        self.assertEqual(
            config,
            [
                ("volume_backend_name", "my_backend_name"),
                (
                    "volume_driver",
                    "cinder.volume.drivers.ibm.storwize_svc.storwize_svc_iscsi.StorwizeSVCISCSIDriver",  # noqa
                ),
                ("san_ip", "192.0.2.1"),
                ("san_login", "superuser"),
                ("san_password", "my-password"),
                ("storwize_svc_volpool_name", "cinder_pool1"),
                ("storwize_svc_vol_compression", True),
                ("storwize_svc_vol_iogrp", 2),
            ],
        )
