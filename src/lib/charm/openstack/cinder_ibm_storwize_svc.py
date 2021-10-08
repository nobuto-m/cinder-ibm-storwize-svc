import charms_openstack.charm
import charmhelpers.core.hookenv as ch_hookenv  # noqa

charms_openstack.charm.use_defaults("charm.default-select-release")


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

    stateless = True

    # Specify any config that the user *must* set.
    mandatory_config = []

    def cinder_configuration(self):
        volume_driver = ""
        driver_options = [
            ("volume_driver", volume_driver),
            # Add config options that needs setting on cinder.conf
        ]
        return driver_options
