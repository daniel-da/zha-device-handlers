"""Tuya temp and humidity sensors."""

from typing import Any

################## clean this up
import zigpy.types as t
from zigpy.zcl import foundation
from zhaquirks.tuya import TuyaTimePayload, TuyaCommand
import datetime
from typing import Tuple, Optional, Union
##################

from zigpy.profiles import zha
from zigpy.quirks import CustomDevice
from zigpy.zcl.clusters.general import Basic, Groups, Ota, Scenes, Time, Identify
from zigpy.zcl.clusters.measurement import (
    RelativeHumidity,
    SoilMoisture,
    TemperatureMeasurement,
)

from zhaquirks.const import (
    DEVICE_TYPE,
    ENDPOINTS,
    INPUT_CLUSTERS,
    MODELS_INFO,
    OUTPUT_CLUSTERS,
    PROFILE_ID,
    SKIP_CONFIGURATION,
)
from zhaquirks.tuya import TuyaLocalCluster, TuyaPowerConfigurationCluster2AAA, PowerConfiguration 
from zhaquirks.tuya.mcu import DPToAttributeMapping, TuyaMCUCluster


class TuyaTemperatureMeasurement(TemperatureMeasurement, TuyaLocalCluster):
    """Tuya local TemperatureMeasurement cluster."""

class TuyaTemperatureMeasurementD(TemperatureMeasurement, TuyaLocalCluster):
    """Tuya local TemperatureMeasurement cluster."""

    def update_attribute(self, attr_name: str, value: Any) -> None:
        """Apply a correction factor to value."""

        self.debug("DANY3: %s, %s", attr_name, value)
        if attr_name == "measured_value":
            value = 1500
        
        return super().update_attribute(attr_name, value)

class TuyaSoilMoisture(SoilMoisture, TuyaLocalCluster):
    """Tuya local SoilMoisture cluster with a device RH_MULTIPLIER factor if required."""


class TuyaRelativeHumidity(RelativeHumidity, TuyaLocalCluster):
    """Tuya local RelativeHumidity cluster with a device RH_MULTIPLIER factor."""

    def update_attribute(self, attr_name: str, value: Any) -> None:
        """Apply a correction factor to value."""

        if attr_name == "measured_value":
            value = value * (
                self.endpoint.device.RH_MULTIPLIER
                if hasattr(self.endpoint.device, "RH_MULTIPLIER")
                else 100
            )
        return super().update_attribute(attr_name, value)


class TemperatureHumidityManufCluster(TuyaMCUCluster):
    """Tuya Manufacturer Cluster with Temperature and Humidity data points."""

    dp_to_attribute: dict[int, DPToAttributeMapping] = {
        1: DPToAttributeMapping(
            TuyaTemperatureMeasurement.ep_attribute,
            "measured_value",
            converter=lambda x: x * 10,  # decidegree to centidegree
        ),
        2: DPToAttributeMapping(
            TuyaRelativeHumidity.ep_attribute,
            "measured_value",
            # converter=lambda x: x * 10,  --> move conversion to TuyaRelativeHumidity cluster
        ),
        4: DPToAttributeMapping(
            TuyaPowerConfigurationCluster2AAA.ep_attribute,
            "battery_percentage_remaining",
            converter=lambda x: x * 2,  # double reported percentage
        ),
    }

    data_point_handlers = {
        1: "_dp_2_attr_update",
        2: "_dp_2_attr_update",
        4: "_dp_2_attr_update",
    }


class TemperatureHumidityBatteryStatesManufCluster(TuyaMCUCluster):
    """Tuya Manufacturer Cluster with Temperature and Humidity data points. Battery states 25, 50 and 100%."""

    dp_to_attribute: dict[int, DPToAttributeMapping] = {
        1: TemperatureHumidityManufCluster.dp_to_attribute[1],
        2: TemperatureHumidityManufCluster.dp_to_attribute[2],
        3: DPToAttributeMapping(
            TuyaPowerConfigurationCluster2AAA.ep_attribute,
            "battery_percentage_remaining",
            converter=lambda x: {0: 25, 1: 50, 2: 100}[x],  # double reported percentage
        ),
    }

    data_point_handlers = {
        1: "_dp_2_attr_update",
        2: "_dp_2_attr_update",
        3: "_dp_2_attr_update",
    }


class TuyaTempHumiditySensor(CustomDevice):
    """Custom device representing tuya temp and humidity sensor with e-ink screen."""

    # RelativeHumidity multiplier
    RH_MULTIPLIER = 10

    signature = {
        # <SimpleDescriptor endpoint=1, profile=260, device_type=81
        # device_version=1
        # input_clusters=[4, 5, 61184, 0]
        # output_clusters=[25, 10]>
        MODELS_INFO: [
            ("_TZE200_bjawzodf", "TS0601"),
            ("_TZE200_zl1kmjqx", "TS0601"),
        ],
        ENDPOINTS: {
            1: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.SMART_PLUG,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    Groups.cluster_id,
                    Scenes.cluster_id,
                    TemperatureHumidityManufCluster.cluster_id,
                ],
                OUTPUT_CLUSTERS: [Ota.cluster_id, Time.cluster_id],
            }
        },
    }

    replacement = {
        SKIP_CONFIGURATION: True,
        ENDPOINTS: {
            1: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.TEMPERATURE_SENSOR,
                INPUT_CLUSTERS: [
                    TemperatureHumidityManufCluster,  # Single bus for temp, humidity, and battery
                    TuyaTemperatureMeasurement,
                    TuyaRelativeHumidity,
                    TuyaPowerConfigurationCluster2AAA,
                ],
                OUTPUT_CLUSTERS: [Ota.cluster_id, Time.cluster_id],
            }
        },
    }


class TuyaTempHumiditySensorVar02(CustomDevice):
    """Custom device representing tuya temp and humidity sensor with e-ink screen."""

    signature = {
        # <SimpleDescriptor endpoint=1, profile=260, device_type=81
        # device_version=1
        # input_clusters=[4, 5, 61184, 0]
        # output_clusters=[25, 10]>
        MODELS_INFO: [
            ("_TZE200_zppcgbdj", "TS0601"),  # Conecto TH
        ],
        ENDPOINTS: {
            1: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.SMART_PLUG,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    Groups.cluster_id,
                    Scenes.cluster_id,
                    TemperatureHumidityManufCluster.cluster_id,
                ],
                OUTPUT_CLUSTERS: [Ota.cluster_id, Time.cluster_id],
            }
        },
    }

    replacement = {
        SKIP_CONFIGURATION: True,
        ENDPOINTS: {
            1: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.TEMPERATURE_SENSOR,
                INPUT_CLUSTERS: [
                    TemperatureHumidityManufCluster,  # Single bus for temp, humidity, and battery
                    TuyaTemperatureMeasurement,
                    TuyaRelativeHumidity,
                    TuyaPowerConfigurationCluster2AAA,
                ],
                OUTPUT_CLUSTERS: [Ota.cluster_id, Time.cluster_id],
            }
        },
    }


class TuyaTempHumiditySensor_Square(CustomDevice):
    """Custom device representing tuya temp and humidity sensor with e-ink screen."""

    # RelativeHumidity multiplier
    # RH_MULTIPLIER = 100

    signature = {
        MODELS_INFO: [
            ("_TZE200_qoy0ekbd", "TS0601"),
            ("_TZE200_znbl8dj5", "TS0601"),
        ],
        ENDPOINTS: {
            1: {
                # "profile_id": 260, "device_type": "0x0302",
                # "in_clusters": ["0x0000","0x0001","0x0402","0x0405"],
                # "out_clusters": ["0x000a","0x0019"]
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.TEMPERATURE_SENSOR,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    TuyaPowerConfigurationCluster2AAA.cluster_id,
                    TemperatureMeasurement.cluster_id,
                    RelativeHumidity.cluster_id,
                ],
                OUTPUT_CLUSTERS: [Ota.cluster_id, Time.cluster_id],
            }
        },
    }

    replacement = {
        SKIP_CONFIGURATION: True,
        ENDPOINTS: {
            1: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.TEMPERATURE_SENSOR,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    TuyaPowerConfigurationCluster2AAA,
                    TemperatureHumidityManufCluster,
                    TuyaTemperatureMeasurement,
                    TuyaRelativeHumidity,
                ],
                OUTPUT_CLUSTERS: [Ota.cluster_id, Time.cluster_id],
            }
        },
    }


class TuyaTempHumiditySensorVar03(CustomDevice):
    """Tuya temp and humidity sensor (variation 03)."""

    signature = {
        # "profile_id": 260,
        # "device_type": "0x0051",
        # "in_clusters": ["0x0000","0x0004","0x0005","0xef00"],
        # "out_clusters": ["0x000a","0x0019"]
        MODELS_INFO: [
            ("_TZE200_qyflbnbj", "TS0601"),
        ],
        ENDPOINTS: {
            1: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.SMART_PLUG,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    Groups.cluster_id,
                    Scenes.cluster_id,
                    TemperatureHumidityManufCluster.cluster_id,
                ],
                OUTPUT_CLUSTERS: [Ota.cluster_id, Time.cluster_id],
            }
        },
    }

    replacement = {
        SKIP_CONFIGURATION: True,
        ENDPOINTS: {
            1: {
                DEVICE_TYPE: zha.DeviceType.TEMPERATURE_SENSOR,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    Groups.cluster_id,
                    Scenes.cluster_id,
                    TemperatureHumidityManufCluster,
                    TuyaTemperatureMeasurement,
                    TuyaRelativeHumidity,
                    TuyaPowerConfigurationCluster2AAA,
                ],
                OUTPUT_CLUSTERS: [Ota.cluster_id, Time.cluster_id],
            }
        },
    }


class TuyaTempHumiditySensorVar04(CustomDevice):
    """Tuya temp and humidity sensor (variation 04)."""

    signature = {
        # "profile_id": 260,
        # "device_type": "0x0051",
        # "in_clusters": ["0x0000","0x0004","0x0005","0xef00"],
        # "out_clusters": ["0x000a","0x0019"]
        MODELS_INFO: [
            ("_TZE200_yjjdcqsq", "TS0601"),
            ("_TZE200_9yapgbuv", "TS0601"),
            ("_TZE204_yjjdcqsq", "TS0601"),
            ("_TZE200_utkemkbs", "TS0601"),
            ("_TZE204_utkemkbs", "TS0601"),
        ],
        ENDPOINTS: {
            1: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.SMART_PLUG,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    Groups.cluster_id,
                    Scenes.cluster_id,
                    TemperatureHumidityManufCluster.cluster_id,
                ],
                OUTPUT_CLUSTERS: [Ota.cluster_id, Time.cluster_id],
            }
        },
    }

    replacement = {
        SKIP_CONFIGURATION: True,
        ENDPOINTS: {
            1: {
                DEVICE_TYPE: zha.DeviceType.TEMPERATURE_SENSOR,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    Groups.cluster_id,
                    Scenes.cluster_id,
                    TemperatureHumidityBatteryStatesManufCluster,
                    TuyaTemperatureMeasurement,
                    TuyaRelativeHumidity,
                    TuyaPowerConfigurationCluster2AAA,
                ],
                OUTPUT_CLUSTERS: [Ota.cluster_id, Time.cluster_id],
            }
        },
    }

TUYA_SET_TIME = 0x24

class TuyaPowerConfigurationCluster3AAA(PowerConfiguration, TuyaLocalCluster):
    """PowerConfiguration cluster for devices with 3 AAA."""

    BATTERY_SIZES = 0x0031
    BATTERY_QUANTITY = 0x0033
    BATTERY_RATED_VOLTAGE = 0x0034

    _CONSTANT_ATTRIBUTES = {
        BATTERY_SIZES: 4,
        BATTERY_QUANTITY: 3,
        BATTERY_RATED_VOLTAGE: 15,
    }

class TemperatureUnitConvert(t.enum8):
    """Tuya Temp unit convert enum."""

    Celsius = 0x00
    Fahrenheit = 0x01

class TemperatureHumidityBatteryStatesManufCluster3(TuyaMCUCluster):
    """Tuya Manufacturer Cluster with Temperature and Humidity data points. Battery states 25, 50 and 100%."""

    dp_to_attribute: dict[int, DPToAttributeMapping] = {
        1: TemperatureHumidityManufCluster.dp_to_attribute[1],
        2: TemperatureHumidityManufCluster.dp_to_attribute[2],
        3: DPToAttributeMapping(
            TuyaPowerConfigurationCluster3AAA.ep_attribute,
            "battery_percentage_remaining",
            converter=lambda x: {0: 50, 1: 100, 2: 200}[x],  # double reported percentage
        ),
        9: DPToAttributeMapping(
            TuyaTemperatureMeasurement.ep_attribute,
            "temp_unit_convert",
            converter=lambda x: TemperatureUnitConvert(x)
        ),
    }

    data_point_handlers = {
        1: "_dp_2_attr_update",
        2: "_dp_2_attr_update",
        3: "_dp_2_attr_update",
        9: "_dp_2_attr_update",
    }
    
    def handle_set_time_request(self, sequence_number: t.uint16_t) -> foundation.Status:
        payload = TuyaTimePayload()

        utc_now = datetime.datetime.utcnow()
        now = datetime.datetime.now()

        offset_time = datetime.datetime(self.set_time_offset, 1, 1)

        utc_timestamp = int((utc_now - offset_time).total_seconds())
        local_timestamp = int((now - offset_time).total_seconds())
        
        payload.extend(utc_timestamp.to_bytes(4, "big", signed=False))
        payload.extend(local_timestamp.to_bytes(4, "big", signed=False))
        
        self.debug("handle_set_time_request response: %s", payload)
        
        self.create_catching_task(
            self.command(TUYA_SET_TIME, payload, manufacturer=foundation.ZCLHeader.NO_MANUFACTURER_ID, expect_reply=False)
        )

        return foundation.Status.SUCCESS

class TuyaTempHumiditySensorVar05(CustomDevice):
    """Tuya temp and humidity sensor (variation 05)."""

    signature = {
        # "profile_id": 260,
        # "device_type": "0x0051",
        # "in_clusters": ["0x0000","0x0004","0x0005","0xef00"],
        # "out_clusters": ["0x000a","0x0019"]
        MODELS_INFO: [
            ("_TZE200_cirvgep4", "TS0601"),
        ],
        ENDPOINTS: {
            1: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.SMART_PLUG,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    Groups.cluster_id,
                    Scenes.cluster_id,
                    TemperatureHumidityManufCluster.cluster_id,
                ],
                OUTPUT_CLUSTERS: [Ota.cluster_id, Time.cluster_id],
            }
        },
    }

    replacement = {
        SKIP_CONFIGURATION: True,
        ENDPOINTS: {
            1: {
                DEVICE_TYPE: zha.DeviceType.TEMPERATURE_SENSOR,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    Groups.cluster_id,
                    Scenes.cluster_id,
                    TemperatureHumidityBatteryStatesManufCluster3,
                    TuyaTemperatureMeasurement,
                    TuyaRelativeHumidity,
                    TuyaPowerConfigurationCluster3AAA,
                ],
                OUTPUT_CLUSTERS: [Ota.cluster_id, Time.cluster_id],
            }
        },
    }

class SoilManufCluster(TuyaMCUCluster):
    """Tuya Manufacturer Cluster with Temperature and Humidity data points."""

    dp_to_attribute: dict[int, DPToAttributeMapping] = {
        5: DPToAttributeMapping(
            TuyaTemperatureMeasurement.ep_attribute,
            "measured_value",
            converter=lambda x: x * 100,
        ),
        3: DPToAttributeMapping(
            TuyaSoilMoisture.ep_attribute,
            "measured_value",
            converter=lambda x: x * 100,
        ),
        15: DPToAttributeMapping(
            TuyaPowerConfigurationCluster2AAA.ep_attribute,
            "battery_percentage_remaining",
            converter=lambda x: x * 2,  # double reported percentage
        ),
    }

    data_point_handlers = {
        3: "_dp_2_attr_update",
        5: "_dp_2_attr_update",
        15: "_dp_2_attr_update",
    }


class TuyaSoilSensor(CustomDevice):
    """Tuya temp and humidity sensor (variation 03)."""

    signature = {
        # "profile_id": 260,
        # "device_type": "0x0051",
        # "in_clusters": ["0x0000","0x0004","0x0005","0xef00"],
        # "out_clusters": ["0x000a","0x0019"]
        MODELS_INFO: [
            ("_TZE200_myd45weu", "TS0601"),
            ("_TZE200_ga1maeof", "TS0601"),
            ("_TZE200_9cqcpkgb", "TS0601"),
        ],
        ENDPOINTS: {
            1: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.SMART_PLUG,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    Groups.cluster_id,
                    Scenes.cluster_id,
                    TemperatureHumidityManufCluster.cluster_id,
                ],
                OUTPUT_CLUSTERS: [Ota.cluster_id, Time.cluster_id],
            }
        },
    }

    replacement = {
        SKIP_CONFIGURATION: True,
        ENDPOINTS: {
            1: {
                DEVICE_TYPE: zha.DeviceType.TEMPERATURE_SENSOR,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    Groups.cluster_id,
                    Scenes.cluster_id,
                    SoilManufCluster,
                    TuyaTemperatureMeasurement,
                    TuyaSoilMoisture,
                    TuyaPowerConfigurationCluster2AAA,
                ],
                OUTPUT_CLUSTERS: [Ota.cluster_id, Time.cluster_id],
            }
        },
    }



class TuyaTempHumiditySensorVar06(CustomDevice):
    """Tuya temp and humidity sensor (variation 06)."""

    signature = {
        # "profile_id": 260,
        # "device_type": "0x0update_attribute051",
        # "in_clusters": ["0x0000","0x0001","0x0003","0x0402","0x0405"],
        # "out_clusters": ["0x0003"]
        MODELS_INFO: [
            ("_TZE200_a8sdabtg", "TS0601"),
        ],
        ENDPOINTS: {
            1: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.TEMPERATURE_SENSOR,
                INPUT_CLUSTERS: [
                    Basic.cluster_id, # 0x0000
                    TuyaPowerConfigurationCluster2AAA.cluster_id, # 0x0001
                    Identify.cluster_id, # 0x0003
                    TemperatureMeasurement.cluster_id, # 0x0402
                    RelativeHumidity.cluster_id, # 0x0405
                ],
                OUTPUT_CLUSTERS: [Identify.cluster_id],
            }
        },
    }

    replacement = {
        SKIP_CONFIGURATION: True,
        ENDPOINTS: {
            1: {
                DEVICE_TYPE: zha.DeviceType.TEMPERATURE_SENSOR,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    TuyaPowerConfigurationCluster2AAA,
                    Identify.cluster_id, # 0x0003
                    #TemperatureHumidityManufCluster,
                    TuyaTemperatureMeasurementD,
                    TuyaRelativeHumidity,
                ],
                OUTPUT_CLUSTERS: [Identify.cluster_id],
            }
        },
    }
