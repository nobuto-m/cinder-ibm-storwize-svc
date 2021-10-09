IBM Spectrum Virtualize Family Storage Backend for Cinder
---------------------------------------------------------

Overview
========

This charm provides a IBM Spectrum Virtualize Family (formerly known as
IBM Storwize) storage backend for use with the Cinder charm.

To use:

    juju deploy cinder
    juju deploy cinder-ibm-storwize-svc
    juju add-relation cinder-ibm-storwize-svc cinder

Configuration
=============

See config.yaml for details of configuration options.
