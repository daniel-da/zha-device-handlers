"""Device handler for ZBMINIL2 SONOFF."""
from zigpy.profiles import zha
from zigpy.quirks import CustomDevice
from zigpy.zcl.clusters.general import Basic, Identify, OnOff, OnOffConfiguration, PowerConfiguration, Ota, Groups
from zigpy.zcl.clusters.homeautomation import Diagnostic

from zhaquirks.const import (
    DEVICE_TYPE,
    ENDPOINTS,
    INPUT_CLUSTERS,
    MODELS_INFO,
    OUTPUT_CLUSTERS,
    PROFILE_ID,
)

SONOFF_CLUSTER_ID = 0xFC57

class SonoffZBMINIL2(CustomDevice):
    """Custom device representing sonoff devices."""

    signature = {
        MODELS_INFO: [("SONOFF", "ZBMINIL2")],
        ENDPOINTS: {
            1: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.ON_OFF_OUTPUT,
                INPUT_CLUSTERS: [
                    Basic.cluster_id, # "0x0000",
                    PowerConfiguration.cluster_id, # "0x0001",
                    Identify.cluster_id, # "0x0003",
                    OnOff.cluster_id, # "0x0006",
                    OnOffConfiguration.cluster_id, # "0x0007",
                    Diagnostic.cluster_id,# "0x0b05",
                    SONOFF_CLUSTER_ID, # "0xfc57"
                ],
                OUTPUT_CLUSTERS: [
                    Ota.cluster_id,
                ],
            },
        },
    }

    replacement = {
        ENDPOINTS: {
            1: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.ON_OFF_LIGHT,
                INPUT_CLUSTERS: [
                    Basic.cluster_id, # "0x0000",
                    PowerConfiguration.cluster_id, # "0x0001",
                    Identify.cluster_id, # "0x0003",
                    Groups.cluster_id,
                    OnOff.cluster_id, # "0x0006",
                    OnOffConfiguration.cluster_id, # "0x0007",
                    Diagnostic.cluster_id,# "0x0b05",
                    SONOFF_CLUSTER_ID, # "0xfc57"
                ],
                OUTPUT_CLUSTERS: [
                    Ota.cluster_id,
                ],
            },
        }
    }

