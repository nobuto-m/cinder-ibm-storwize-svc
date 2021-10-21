import charms_openstack.charm
import charmhelpers.core.hookenv as ch_hookenv  # noqa

charms_openstack.charm.use_defaults("charm.default-select-release")

MULTIPATH_PACKAGES = [
    "multipath-tools",  # installed by default for disco+
    "sysfsutils",  # LP: #1947063
]

STORWIZE_SVC_DRIVER_ISCSI = "{}.{}".format(
    "cinder.volume.drivers.ibm.storwize_svc",
    "storwize_svc_iscsi.StorwizeSVCISCSIDriver",
)
STORWIZE_SVC_DRIVER_FC = "{}.{}".format(
    "cinder.volume.drivers.ibm.storwize_svc",
    "storwize_svc_fc.StorwizeSVCFCDriver",
)


class CinderIBMStorwizeSVCCharm(
    charms_openstack.charm.CinderStoragePluginCharm
):
    # The name of the charm
    name = "cinder_ibm_storwize_svc"

    # Package to determine application version. Use "cinder-common" when
    # the driver is in-tree of Cinder upstream.
    version_package = "cinder-common"

    # Package to determine OpenStack release name
    release_pkg = "cinder-common"

    # this is the first release in which this charm works
    release = "ussuri"

    # List of packages to install
    packages = [""]

    # make sure multipath related packages are installed
    packages.extend(MULTIPATH_PACKAGES)

    # https://docs.openstack.org/cinder/latest/reference/support-matrix.html#operation_active_active_ha
    # https://docs.openstack.org/cinder/latest/contributor/high_availability.html#enabling-active-active-on-drivers
    stateless = False

    # Specify any config that the user *must* set.
    mandatory_config = [
        "protocol",
        "san-ip",
        "san-login",
        "san-password",
        "storwize-svc-volpool-name",
    ]

    def cinder_configuration(self):
        mandatory_config_values = map(self.config.get, self.mandatory_config)
        if not all(list(mandatory_config_values)):
            return []

        protocol = self.config.get("protocol")
        if protocol == "iscsi":
            volume_driver = STORWIZE_SVC_DRIVER_ISCSI
        elif protocol == "fc":
            volume_driver = STORWIZE_SVC_DRIVER_FC

        if self.config.get("volume-backend-name"):
            volume_backend_name = self.config.get("volume-backend-name")
        else:
            volume_backend_name = ch_hookenv.service_name()

        driver_options = [
            ("volume_backend_name", volume_backend_name),
            ("volume_driver", volume_driver),
            ("san_ip", self.config.get("san-ip")),
            ("san_login", self.config.get("san-login")),
            ("san_password", self.config.get("san-password")),
            (
                "storwize_svc_volpool_name",
                self.config.get("storwize-svc-volpool-name"),
            ),
        ]

        if self.config.get("use-multipath"):
            driver_options.extend(
                [
                    ("use_multipath_for_image_xfer", True),
                    ("enforce_multipath_for_image_xfer", True),
                    ("storwize_svc_multipath_enabled", True),
                ]
            )

        if self.config.get("storwize-san-secondary-ip"):
            driver_options.append(
                (
                    "storwize_san_secondary_ip",
                    self.config.get("storwize-san-secondary-ip"),
                )
            )

        return driver_options
