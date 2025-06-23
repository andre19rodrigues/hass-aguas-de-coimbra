from datetime import timedelta

DOMAIN = "aguas_de_coimbra"
DEFAULT_UPDATE_INTERVAL = timedelta(minutes=30)
BALCAO_DIGITAL_URL = "https://bdigital.aguasdecoimbra.pt/"

# --- PRICES AND FEES ---

# -- WATER

# min and max are diameter values in millimeters
# prices are in euros
WATER_FIXED_FEE = [
    {"min": 0, "max": 25, "price": 0.1388},
    {"min": 25, "max": 30, "price": 0.5197},
    {"min": 30, "max": 50, "price": 1.4031},
    {"min": 50, "max": 100, "price": 3.9},
    {"min": 100, "max": float("inf"), "price": 7.4104},
]
WATER_FIXED_FEE__SOCIAL_TARIFF = 0

# min and max values are in cubic meters
# prices are in euros per cubic meter
# price are in a tiered structure
WATER_CONSUMPTION = [
    {"min": 0, "max": 5, "price": 0.5952},
    {"min": 5, "max": 15, "price": 0.8765},
    {"min": 15, "max": 25, "price": 1.7529},
    {"min": 25, "max": float("inf"), "price": 2.6294},
]
WATER_CONSUMPTION__SOCIAL_TARIFF = [
    {"min": 0, "max": 15, "price": 0.52},
    {"min": 15, "max": 25, "price": 1.54},
    {"min": 25, "max": float("inf"), "price": 2.31},
]

# Price in euros per cubic meter of water consumed
WATER_RESOURCES_TAX = 0.0402


# -- SEWAGE

# Price in euros per day in the billing cycle
SEWAGE_FIXED_FEE = 0.1049
SEWAGE_FIXED_FEE__SOCIAL_TARIFF = 0

# WATER_CONSUMPTION in euros x SEWAGE_CONSUMPTION (108.1%)
SEWAGE_CONSUMPTION = 1.081
SEWAGE_CONSUMPTION__SOCIAL_TARIFF = 0

# Price in euros per cubic meter of water consumed
SEWAGE_RESOURCES_TAX = 0.0169


# -- SOLID_WASTE

# Price in euros per day in the billing cycle
SOLID_WASTE_FIXED_FEE = 0.0992
SOLID_WASTE_FIXED_FEE__SOCIAL_TARIFF = 0

# Price in euros per cubic meter of water consumed
SOLID_WASTE_CONSUMPTION = 0.5998
SOLID_WASTE_CONSUMPTION__SOCIAL_TARIFF = 0.3203

# Price in euros per cubic meter of water consumed
SOLID_WASTE_MANAGEMENT_TAX = 0.13


# -- VAT

VAT_RATE = 0.06
