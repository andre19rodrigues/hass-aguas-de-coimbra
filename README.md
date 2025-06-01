
# Águas de Coimbra - Home Assistant Integration

[![Validate with hassfest](https://github.com/andre19rodrigues/hass-aguas-de-coimbra/actions/workflows/hassfest.yaml/badge.svg)](https://github.com/andre19rodrigues/hass-aguas-de-coimbra/actions/workflows/hassfest.yaml)
[![License](https://img.shields.io/github/license/andre19rodrigues/hass-aguas-de-coimbra)](https://github.com/andre19rodrigues/hass-aguas-de-coimbra/blob/main/LICENSE)
![Version](https://img.shields.io/github/v/tag/andre19rodrigues/hass-aguas-de-coimbra?label=version)

**Disclaimer:** This integration is not affiliated with Águas de Coimbra.

This Home Assistant integration retrieves telemetry data from your water meter as published on the [Águas de Coimbra website](https://bdigital.aguasdecoimbra.pt/uPortal2/coimbra/index.html).

For precise and real-time water usage, consider installing a dedicated sensor. [Home Assistant](https://www.home-assistant.io/docs/energy/water/) provides several examples.

![adc](https://github.com/user-attachments/assets/4f541035-b1f5-420f-8475-97ab15539409)


## 💧 Sensors


The integration comprises the following sensors:

| Sensor Name | Unit | Description | Max. update frequency |
|----------------|---------------|------------------|------------|
| `today_consumption` | Litre (L) | Today's water consumption. Sum of all the readings available for the day — typically one per hour, but often inconsistent, with readings occurring only a few times per day. | Once per hour |
| `yesterday_consumption` | Litre (L) | Yesterday's water consumption. Sum of all readings from the previous day. | Once per day |
| `meter_reading` | Cubic meter (m³) | Official meter reading from Águas de Coimbra. Updated once per day around midnight. Although stored as a float, the meter appears to report only the integer part. This is the value that will appear on your invoice. | Once per day |
| `billing_cycle_consumption` | Cubic meter (m³) | Water consumption during the current billing cycle. | Once per hour |
| `billing_cycle_cost` | Euro (€)  | Cost of the billing cycle. | Once per hour |


**Notes:** 
 - To prevent abuse of the Águas de Coimbra portal, this integration retrieves data only once per hour and fetches only essential information.
 - The billing cycle cost shown is only an estimate. Please note that the actual amount on your invoice may differ. This may be due to variations in the billing cycle length (which can range from 28 to 30 days), inaccuracies in the calculation formula, or outdated or incorrect pricing. This estimate is provided for informational purposes only, and I cannot be held responsible for any discrepancies.

## 🛠 Installation

### Option 1: HACS (Recommended)

1. Go to **HACS > Integrations**.
2. Click **⋮(three dots) > Custom Repositories**.
3. Add this repository URL and select **Integration** as the category.
4. Click **Add**.
5. Restart Home Assistant.
6. Go to the **Integrations** page and click **Add Integration**
7. Search for **Águas de Coimbra** and install it.


### Option 2: Manual

1. Download the contents of this repository.
2. Copy the folder `aguas_de_coimbra` to your Home Assistant config folder under `custom_components/aguas_de_coimbra/`
3. Restart Home Assistant.
4. Go to the Integrations page and click Add Integration
5. Search for Águas de Coimbra and install it.


## ⚙️ Setup

To configure the integration, please enter your credentials for the Águas de Coimbra portal. You may also optionally specify a custom billing cycle start date (default is day 1) and indicate whether the social tariff should be applied.