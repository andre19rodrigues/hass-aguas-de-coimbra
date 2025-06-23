
# Águas de Coimbra - Home Assistant Integration

[![Validate with hassfest](https://github.com/andre19rodrigues/hass-aguas-de-coimbra/actions/workflows/hassfest.yaml/badge.svg)](https://github.com/andre19rodrigues/hass-aguas-de-coimbra/actions/workflows/hassfest.yaml)
[![License](https://img.shields.io/github/license/andre19rodrigues/hass-aguas-de-coimbra)](https://github.com/andre19rodrigues/hass-aguas-de-coimbra/blob/main/LICENSE)
![Version](https://img.shields.io/github/v/tag/andre19rodrigues/hass-aguas-de-coimbra?label=version)

**Disclaimer:** This integration is not affiliated with Águas de Coimbra.

This Home Assistant integration retrieves telemetry data from your water meter as published on the [Águas de Coimbra website](https://bdigital.aguasdecoimbra.pt/uPortal2/coimbra/index.html).

For precise and real-time water usage, consider installing a dedicated sensor. [Home Assistant](https://www.home-assistant.io/docs/energy/water/) provides several examples.

![sensors](https://github.com/user-attachments/assets/442bb382-05bb-4fc1-abfa-da802afb449a)


## 💧 Sensors


The integration comprises the following sensors:

| Sensor Name | Unit | Description | Max. update frequency |
|----------------|---------------|------------------|------------|
| `today_consumption` | Litre (L) | Today's water consumption. Sum of all the readings available for the day — typically one per hour, but often inconsistent, with readings occurring only a few times per day. | Every 30 minutes |
| `yesterday_consumption` | Litre (L) | Yesterday's water consumption. Sum of all readings from the previous day. | Once per day |
| `meter_reading` | Cubic meter (m³) | Official meter reading from Águas de Coimbra. Updated once per day around midnight. Although stored as a float, the meter appears to report only the integer part. This is the value that will appear on your invoice. | Once per day |
| `billing_cycle_consumption` | Cubic meter (m³) | Water consumption during the current billing cycle. | Every 30 minutes |
| `billing_cycle_cost` | Euro (€)  | Cost of the billing cycle. | Every 30 minutes |


**Notes:** 
 - To prevent abuse of the Águas de Coimbra portal, this integration retrieves data only every 30 minutes and limits requests to essential information.
 - The billing cycle cost shown is an estimate only. The actual amount on your invoice may differ due to factors such as:
   -  Missing or incomplete data;
   -   Use of an incorrect water meter diameter;
   -   Variations in the billing cycle length (which can range from 28 to 31 days);
   -   Potential inaccuracies in the calculation formula;
   -   Outdated or incorrect pricing information;

This estimate is provided for informational purposes only. Neither this integration nor its contributors accept responsibility for any discrepancies between this estimate and your actual bill.



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

![configuration](https://github.com/user-attachments/assets/1d6e536f-4c3b-4cf6-ad64-98f64ff19e0a)
