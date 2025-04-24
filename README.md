# Águas de Coimbra - Home Assistant Integration

**Disclaimer:** This integration is not affiliated with Águas de Coimbra.

This Home Assistant integration retrieves telemetry data from your water meter as published on the [Águas de Coimbra website](https://bdigital.aguasdecoimbra.pt/uPortal2/coimbra/index.html).  
For precise and real-time water usage, consider installing a dedicated sensor. [Home Assistant](https://www.home-assistant.io/docs/energy/water/) provides several examples.

## Sensors

The integration comprises the following sensors:
| Sensor Name | Unit | Description | Max. update frequency                                                                                        
|--|--|--|--|
| `today_consumption`| Litre (L)| Today's water consumption. Sum of all the readings available for the day — typically one per hour, but often inconsistent, with readings occurring only a few times per day. | Once per hour
| `yesterday_consumption` | Litre (L) | Yesterday's water consumption. Sum of all readings from the previous day.| Once per day
| `meter_reading_official`| Cubic meter (m³) | Official meter reading from Águas de Coimbra. Updated once per day around midnight. Although it is stored as a float, the meter appears to only report the integer part. | Once per day
| `meter_reading_estimated`| Cubic meter (m³) | An estimate calculated by this integration: `meter_reading_official` + `today_consumption`. It’s only an approximation, as `meter_reading_official` is an integer and `today_consumption` is not real-time. Suitable for use in [Home Assistant Energy](https://www.home-assistant.io/docs/energy/) to provide more frequent updates. A value jump is expected shortly after midnight when `meter_reading_official` updates. | Once per hour

**Note:** To prevent abuse of the Águas de Coimbra portal, this integration retrieves data only once per hour and fetches only essential information.
