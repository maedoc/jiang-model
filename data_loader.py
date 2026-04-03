"""
Data loading and preprocessing for real-world geopolitical resource dynamics.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

try:
    import pycountry

    HAS_PYCOUNTRY = True
except ImportError:
    HAS_PYCOUNTRY = False
    print("Warning: pycountry not installed. Using fallback country mapping.")
import requests
import json
import os

# Region definitions (12 regions)
REGIONS = [
    "North America",
    "Europe",
    "Russia",
    "Middle East",
    "China",
    "India",
    "Japan",
    "Southeast Asia",
    "Australia/New Zealand",
    "Africa (sub-Saharan)",
    "South America",
    "Central Asia/Caucasus",
]


# Mapping from country ISO3 codes to region index
# We'll build this mapping using pycountry and custom groupings
def build_region_mapping() -> Dict[str, int]:
    """Return dict mapping ISO3 code to region index (0-11)."""
    mapping = {}

    # Helper to add countries
    def add_countries(codes, region_idx):
        for code in codes:
            mapping[code] = region_idx

    # North America: USA, Canada, Mexico
    add_countries(["USA", "CAN", "MEX"], 0)

    # Europe: EU countries + UK, Norway, Switzerland, etc.
    europe_codes = [
        "GBR",
        "FRA",
        "DEU",
        "ITA",
        "ESP",
        "NLD",
        "BEL",
        "GRC",
        "PRT",
        "SWE",
        "FIN",
        "DNK",
        "IRL",
        "AUT",
        "POL",
        "CZE",
        "HUN",
        "SVK",
        "SVN",
        "HRV",
        "ROU",
        "BGR",
        "EST",
        "LVA",
        "LTU",
        "LUX",
        "MLT",
        "CYP",
        "NOR",
        "CHE",
        "ISL",
        "ALB",
        "BIH",
        "MKD",
        "MNE",
        "SRB",
        "KOS",  # Kosovo XKX not ISO
    ]
    add_countries(europe_codes, 1)

    # Russia
    add_countries(["RUS"], 2)

    # Middle East: GCC + Iran + Iraq + others
    middle_east_codes = [
        "SAU",
        "ARE",
        "QAT",
        "KWT",
        "BHR",
        "OMN",
        "IRN",
        "IRQ",
        "SYR",
        "JOR",
        "LBN",
        "ISR",
        "PSE",
        "YEM",
        "TUR",
        "EGY",  # Egypt sometimes considered Africa
    ]
    add_countries(middle_east_codes, 3)

    # China (including Taiwan? We'll treat as China)
    add_countries(["CHN", "TWN", "HKG", "MAC"], 4)

    # India
    add_countries(["IND"], 5)

    # Japan
    add_countries(["JPN"], 6)

    # Southeast Asia: ASEAN members
    asean_codes = [
        "IDN",
        "MYS",
        "SGP",
        "THA",
        "VNM",
        "PHL",
        "MMR",
        "KHM",
        "LAO",
        "BRN",
        "TLS",  # Timor-Leste
    ]
    add_countries(asean_codes, 7)

    # Australia/New Zealand
    add_countries(["AUS", "NZL"], 8)

    # Africa (sub-Saharan): all African countries except North Africa
    # North Africa: Egypt, Libya, Tunisia, Algeria, Morocco, Sudan, South Sudan?
    # We'll include North Africa in Middle East? Usually MENA. Let's keep sub-Saharan only.
    sub_saharan_codes = [
        "AGO",
        "BEN",
        "BWA",
        "BFA",
        "BDI",
        "CMR",
        "CPV",
        "CAF",
        "TCD",
        "COM",
        "COD",
        "COG",
        "CIV",
        "DJI",
        "GNQ",
        "ERI",
        "ETH",
        "GAB",
        "GMB",
        "GHA",
        "GIN",
        "GNB",
        "KEN",
        "LSO",
        "LBR",
        "MDG",
        "MWI",
        "MLI",
        "MRT",
        "MUS",
        "MOZ",
        "NAM",
        "NER",
        "NGA",
        "RWA",
        "STP",
        "SEN",
        "SYC",
        "SLE",
        "SOM",
        "ZAF",
        "SSD",
        "SDN",
        "SWZ",
        "TZA",
        "TGO",
        "UGA",
        "ZMB",
        "ZWE",
    ]
    add_countries(sub_saharan_codes, 9)

    # South America
    south_america_codes = [
        "ARG",
        "BOL",
        "BRA",
        "CHL",
        "COL",
        "ECU",
        "GUY",
        "PRY",
        "PER",
        "SUR",
        "URY",
        "VEN",
    ]
    add_countries(south_america_codes, 10)

    # Central Asia/Caucasus
    central_asia_codes = ["KAZ", "KGZ", "TJK", "TKM", "UZB", "AZE", "ARM", "GEO"]
    add_countries(central_asia_codes, 11)

    # Additional mappings for missing codes (e.g., 'OWID_WRL' for World)
    # We'll ignore non-country entities for region aggregation

    return mapping


def load_oil_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load oil production and consumption data from CSV files.
    Returns (production_df, consumption_df) with columns: Entity, Code, Year, Oil.
    """
    # Load from local CSV files (downloaded via download_data.py)
    prod = pd.read_csv("oil_production.csv")
    cons = pd.read_csv("oil_consumption.csv")
    return prod, cons


def load_fertilizer_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load fertilizer production and consumption data.
    Currently only have consumption (use). Production approximated later.
    """
    use = pd.read_csv("fertilizer_total_use.csv")
    # Production data not yet available; will approximate using consumption + trade
    return use, None


def aggregate_region_data(
    df: pd.DataFrame, region_mapping: Dict[str, int], year: int = 2023
) -> np.ndarray:
    """Aggregate country-level data to region totals for given year.

    Args:
        df: DataFrame with columns Entity, Code, Year, Value
        region_mapping: ISO3 -> region index
        year: target year (default 2023)

    Returns:
        array of shape (n_regions,) with aggregated values.
    """
    n_regions = len(REGIONS)
    region_totals = np.zeros(n_regions)

    # Filter for target year
    df_year = df[df["Year"] == year].copy()

    for _, row in df_year.iterrows():
        code = row["Code"]
        if pd.isna(code):
            # Some rows have empty code (aggregated regions like 'Africa')
            # Skip or handle separately
            continue
        # Some codes are not ISO3 (e.g., 'OWID_WRL')
        if code not in region_mapping:
            continue
        region_idx = region_mapping[code]
        # Column name may vary; assume last column is the value
        value_col = df.columns[-1]
        value = row[value_col]
        if pd.isna(value):
            continue
        region_totals[region_idx] += value

    return region_totals


def compute_trade_matrices() -> Tuple[np.ndarray, np.ndarray]:
    """Compute oil and fertilizer trade matrices between regions.
    Placeholder: will use UN Comtrade data.
    Returns (oil_trade_matrix, fertilizer_trade_matrix) shape (n_regions, n_regions).
    """
    n = len(REGIONS)
    # For now, create simple heuristic based on production/consumption imbalance
    # Will be filled later
    oil_trade = np.zeros((n, n))
    fertilizer_trade = np.zeros((n, n))
    return oil_trade, fertilizer_trade


def compute_water_trade_flow(water_availability, water_consumption):
    """Compute water trade matrix based on surplus/deficit.

    Args:
        water_availability: array shape (n_regions,) in km³/year
        water_consumption: array shape (n_regions,) in km³/year

    Returns:
        water_trade matrix shape (n_regions, n_regions) where element (i,j)
        is flow from region j to region i.
    """
    n = len(water_availability)
    surplus = water_availability - water_consumption
    water_trade = np.zeros((n, n))

    deficit_mask = surplus < 0
    surplus_mask = surplus > 0
    deficit_regions = np.where(deficit_mask)[0]
    surplus_regions = np.where(surplus_mask)[0]

    for i in deficit_regions:
        deficit = -surplus[i]
        total_surplus = surplus[surplus_mask].sum()
        if total_surplus > 0:
            for j in surplus_regions:
                share = surplus[j] / total_surplus
                flow = deficit * share
                water_trade[i, j] = flow
    # No self-trade
    np.fill_diagonal(water_trade, 0)
    return water_trade


def compute_capital_flow(trade_matrices, stability):
    """Compute capital flow matrix for financial contagion.

    Capital flows are proportional to trade volume and stability of destination.

    Args:
        trade_matrices: list of trade matrices (oil, fertilizer, water) each shape (n,n)
        stability: array shape (n,) political stability index 0-1

    Returns:
        capital_flow matrix shape (n,n) where element (i,j) is capital flow
        from region j to i (proportional to investment attractiveness).
    """
    n = stability.shape[0]
    # Sum absolute trade flows (directionless) as proxy for economic connectivity
    total_trade = np.zeros((n, n))
    for mat in trade_matrices:
        total_trade += np.abs(
            mat
        )  # consider both directions? trade matrices are directional from j->i
    # Normalize by max
    if total_trade.max() > 0:
        total_trade = total_trade / total_trade.max()
    # Capital flow from j to i increases with trade volume and stability of i
    capital_flow = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            # Attractiveness of i for capital from j: stability[i] * trade connectivity
            capital_flow[i, j] = total_trade[i, j] * stability[i]
    # Scale to reasonable magnitude (0-0.1)
    if capital_flow.max() > 0:
        capital_flow = capital_flow / capital_flow.max() * 0.1
    return capital_flow


def compute_financial_coupling(trade_matrices, stability):
    """Compute financial coupling matrix for interest/exchange rate spillovers.

    Coupling strength proportional to trade volume and financial integration.

    Args:
        trade_matrices: list of trade matrices
        stability: political stability

    Returns:
        financial_coupling matrix shape (n,n) where element (i,j) is coupling
        strength from region j to i (for spillover effects).
    """
    n = stability.shape[0]
    total_trade = np.zeros((n, n))
    for mat in trade_matrices:
        total_trade += np.abs(mat)
    # Normalize
    if total_trade.max() > 0:
        total_trade = total_trade / total_trade.max()
    # Coupling strength proportional to trade volume, scaled by stability similarity?
    coupling = total_trade * 0.05  # arbitrary scaling
    np.fill_diagonal(coupling, 0)
    return coupling


def fetch_wgi_data(indicator="PV.EST", year=2023):
    """Fetch Worldwide Governance Indicators from World Bank API.

    Args:
        indicator: one of 'VA', 'PV', 'GE', 'RQ', 'RL', 'CC'
        year: latest year available (2023 is latest as of 2025)

    Returns:
        Dict mapping ISO3 country codes to values (range approx -2.5 to 2.5).
    """
    try:
        import wbdata
    except ImportError:
        print("wbdata not installed, using placeholder data.")
        return {}

    # Set up data source
    indicators = {indicator: f"WGI_{indicator}"}
    try:
        data = wbdata.get_dataframe(indicators, country="all", date=str(year))
    except Exception as e:
        print(f"Error fetching WGI data: {e}")
        return {}

    # Convert to dict: index is country ISO3 code
    result = {}
    for idx, row in data.iterrows():
        # idx is tuple (country_code, date)
        country_code = idx[0]
        value = row[f"WGI_{indicator}"]
        if pd.isna(value):
            continue
        result[country_code] = float(value)
    return result


def load_political_stability() -> np.ndarray:
    """Load political stability index (World Bank WGI) for regions.
    Returns array of shape (n_regions,) normalized to 0-1.
    """
    # Try to fetch real data
    wgi_data = fetch_wgi_data("PV", year=2023)
    if not wgi_data:
        # Fallback to placeholder
        n = len(REGIONS)
        stability = np.array(
            [
                0.8,  # North America
                0.9,  # Europe
                0.6,  # Russia
                0.4,  # Middle East
                0.7,  # China
                0.6,  # India
                0.9,  # Japan
                0.7,  # Southeast Asia
                0.9,  # Australia/NZ
                0.5,  # Africa
                0.6,  # South America
                0.5,  # Central Asia
            ]
        )
        return stability

    # Aggregate by region
    region_mapping = build_region_mapping()
    n = len(REGIONS)
    region_values = []
    region_counts = []
    for _ in range(n):
        region_values.append(0.0)
        region_counts.append(0)

    for country_code, value in wgi_data.items():
        if country_code not in region_mapping:
            continue
        region_idx = region_mapping[country_code]
        # WGI values range -2.5 to 2.5; normalize to 0-1
        normalized = (value + 2.5) / 5.0
        region_values[region_idx] += normalized
        region_counts[region_idx] += 1

    # Compute average per region
    stability = np.zeros(n)
    for i in range(n):
        if region_counts[i] > 0:
            stability[i] = region_values[i] / region_counts[i]
        else:
            # Default fallback
            stability[i] = 0.5

    return stability


def load_water_data() -> Tuple[np.ndarray, np.ndarray]:
    """Load water availability and consumption data.
    Returns (water_availability, water_consumption) in km³/year.
    Placeholder: use regional estimates based on population and climate.
    """
    n = len(REGIONS)
    # Placeholder values: water availability per region (km³/year)
    # Rough estimates: North America 2500, Europe 2000, Russia 4000, Middle East 500,
    # China 2800, India 1900, Japan 400, Southeast Asia 3000, Australia/NZ 500,
    # Africa 4000, South America 12000, Central Asia 500
    availability = np.array(
        [
            2500.0,  # North America
            2000.0,  # Europe
            4000.0,  # Russia
            500.0,  # Middle East
            2800.0,  # China
            1900.0,  # India
            400.0,  # Japan
            3000.0,  # Southeast Asia
            500.0,  # Australia/New Zealand
            4000.0,  # Africa (sub-Saharan)
            12000.0,  # South America
            500.0,  # Central Asia/Caucasus
        ]
    )
    # Consumption as 70% of availability (agricultural use dominant)
    consumption = availability * 0.7
    return availability, consumption


def load_military_data() -> Tuple[np.ndarray, np.ndarray]:
    """Load military expenditure and production capacity.
    Returns (military_expenditure, military_production) as % of GDP.
    Placeholder: SIPRI data estimates.
    """
    n = len(REGIONS)
    # Military expenditure as % of GDP (2023 estimates)
    expenditure = (
        np.array(
            [
                3.2,  # North America (USA ~3.5%)
                1.6,  # Europe (NATO average)
                4.1,  # Russia
                5.8,  # Middle East (GCC average)
                1.7,  # China
                2.5,  # India
                1.0,  # Japan
                1.8,  # Southeast Asia
                1.9,  # Australia/New Zealand
                1.4,  # Africa
                1.3,  # South America
                2.2,  # Central Asia
            ]
        )
        / 100.0
    )  # Convert to fraction
    # Production capacity: fraction of military spending that is domestic production
    production = np.array(
        [
            0.8,  # North America
            0.6,  # Europe
            0.7,  # Russia
            0.3,  # Middle East (import heavy)
            0.9,  # China
            0.5,  # India
            0.2,  # Japan (constitution limits)
            0.4,  # Southeast Asia
            0.3,  # Australia/New Zealand
            0.2,  # Africa
            0.3,  # South America
            0.4,  # Central Asia
        ]
    )
    return expenditure, production


def load_inequality_data() -> np.ndarray:
    """Load inequality (Gini coefficient) data.
    Returns array of Gini coefficients (0-1 scale).
    """
    # World Bank Gini estimates (latest available)
    gini = np.array(
        [
            0.41,  # North America
            0.30,  # Europe
            0.37,  # Russia
            0.39,  # Middle East
            0.38,  # China
            0.35,  # India
            0.33,  # Japan
            0.42,  # Southeast Asia
            0.34,  # Australia/New Zealand
            0.45,  # Africa
            0.46,  # South America
            0.35,  # Central Asia
        ]
    )
    return gini


def load_debt_data() -> np.ndarray:
    """Load sovereign debt-to-GDP ratios.
    Returns array of debt/GDP ratios (e.g., 1.2 = 120%).
    """
    debt_to_gdp = np.array(
        [
            1.32,  # North America (USA ~132%)
            0.90,  # Europe (EU average)
            0.18,  # Russia (low debt)
            0.45,  # Middle East
            0.77,  # China
            0.83,  # India
            2.62,  # Japan (high)
            0.60,  # Southeast Asia
            0.56,  # Australia/New Zealand
            0.65,  # Africa
            0.85,  # South America
            0.30,  # Central Asia
        ]
    )
    return debt_to_gdp


def load_price_data() -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Load initial commodity prices.
    Returns (oil_price, fertilizer_price, water_price) in USD per unit.
    """
    n = len(REGIONS)
    # Oil price USD/barrel (regional variations)
    oil_price = np.full(n, 80.0)  # baseline
    # Fertilizer price USD/tonne
    fertilizer_price = np.full(n, 500.0)
    # Water price USD/m³ (approximate)
    water_price = np.full(n, 0.5)
    return oil_price, fertilizer_price, water_price


def load_financial_data() -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Load financial variables.
    Returns (inflation, interest_rate, exchange_rate, bond_yield).
    inflation: annual % (e.g., 0.02 = 2%)
    interest_rate: central bank policy rate %
    exchange_rate: local currency per USD (e.g., 0.92 for EUR)
    bond_yield: 10-year sovereign yield %
    """
    n = len(REGIONS)
    inflation = np.array(
        [
            0.03,  # North America
            0.025,  # Europe
            0.07,  # Russia
            0.08,  # Middle East
            0.02,  # China
            0.05,  # India
            0.01,  # Japan
            0.04,  # Southeast Asia
            0.04,  # Australia/New Zealand
            0.10,  # Africa
            0.08,  # South America
            0.09,  # Central Asia
        ]
    )
    interest_rate = np.array(
        [
            0.05,  # North America
            0.04,  # Europe
            0.16,  # Russia
            0.06,  # Middle East
            0.035,  # China
            0.065,  # India
            0.005,  # Japan
            0.045,  # Southeast Asia
            0.045,  # Australia/New Zealand
            0.10,  # Africa
            0.12,  # South America
            0.11,  # Central Asia
        ]
    )
    exchange_rate = np.array(
        [
            1.0,  # North America (USD)
            0.92,  # Europe (EUR/USD)
            92.0,  # Russia (RUB/USD)
            3.67,  # Middle East (AED/USD, but using USD peg)
            7.2,  # China (CNY/USD)
            83.0,  # India (INR/USD)
            150.0,  # Japan (JPY/USD)
            1.35,  # Southeast Asia (weighted)
            1.5,  # Australia/New Zealand (AUD/USD)
            18.0,  # Africa (weighted)
            5.0,  # South America (weighted)
            450.0,  # Central Asia (KZT/USD)
        ]
    )
    bond_yield = np.array(
        [
            0.042,  # North America
            0.028,  # Europe
            0.125,  # Russia
            0.055,  # Middle East
            0.025,  # China
            0.072,  # India
            0.008,  # Japan
            0.050,  # Southeast Asia
            0.045,  # Australia/New Zealand
            0.12,  # Africa
            0.11,  # South America
            0.10,  # Central Asia
        ]
    )
    return inflation, interest_rate, exchange_rate, bond_yield


def real_world_parameters(year: int = 2023) -> Dict:
    """Generate parameter dictionary from real-world data.

    Returns:
        Dict with keys similar to default_parameters but for 12 regions.
    """
    region_mapping = build_region_mapping()
    oil_prod_df, oil_cons_df = load_oil_data()
    fert_use_df, _ = load_fertilizer_data()

    # Aggregate oil production and consumption
    oil_production = aggregate_region_data(oil_prod_df, region_mapping, year)
    oil_consumption = aggregate_region_data(oil_cons_df, region_mapping, year)

    # Fertilizer consumption (use)
    fertilizer_consumption = aggregate_region_data(fert_use_df, region_mapping, year)
    # Approximate production as consumption * 1.1 (global surplus)
    fertilizer_production = fertilizer_consumption * 1.1

    # Political stability index
    stability = load_political_stability()

    # Trade matrices (placeholder)
    oil_trade, fertilizer_trade = compute_trade_matrices()

    # Stability dynamics parameters (arbitrary but could be calibrated)
    stability_decay = np.full(len(REGIONS), 0.01)
    stability_gain = np.full(len(REGIONS), 0.05)

    # Stability coupling matrix (placeholder)
    stability_coupling = np.zeros((len(REGIONS), len(REGIONS)))

    # Convert to JAX arrays
    params = {}
    params["oil_production"] = np.array(oil_production)
    params["oil_consumption"] = np.array(oil_consumption)
    params["fertilizer_production"] = np.array(fertilizer_production)
    params["fertilizer_consumption"] = np.array(fertilizer_consumption)
    params["stability_decay"] = np.array(stability_decay)
    params["stability_gain"] = np.array(stability_gain)
    params["oil_trade"] = np.array(oil_trade)
    params["fertilizer_trade"] = np.array(fertilizer_trade)
    params["stability_coupling"] = np.array(stability_coupling)
    params["political_stability"] = np.array(stability)

    # New variables
    water_availability, water_consumption = load_water_data()
    params["water_availability"] = np.array(water_availability)
    params["water_consumption"] = np.array(water_consumption)

    military_expenditure, military_production = load_military_data()
    params["military_expenditure"] = np.array(military_expenditure)
    params["military_production"] = np.array(military_production)

    inequality = load_inequality_data()
    params["inequality"] = np.array(inequality)

    debt_to_gdp = load_debt_data()
    params["debt_to_gdp"] = np.array(debt_to_gdp)

    oil_price, fertilizer_price, water_price = load_price_data()
    params["oil_price"] = np.array(oil_price)
    params["fertilizer_price"] = np.array(fertilizer_price)
    params["water_price"] = np.array(water_price)

    inflation, interest_rate, exchange_rate, bond_yield = load_financial_data()
    params["inflation"] = np.array(inflation)
    params["interest_rate"] = np.array(interest_rate)
    params["exchange_rate"] = np.array(exchange_rate)
    params["bond_yield"] = np.array(bond_yield)

    return params


def download_data(force=False):
    """Download required datasets from external sources."""
    import urllib.request

    files = [
        (
            "oil_production.csv",
            "https://ourworldindata.org/grapher/oil-production-by-country.csv",
        ),
        (
            "oil_consumption.csv",
            "https://ourworldindata.org/grapher/oil-consumption-by-country.csv",
        ),
        (
            "fertilizer_total_use.csv",
            "https://ourworldindata.org/grapher/fertilizer-total-use.csv",
        ),
    ]
    for filename, url in files:
        if force or not os.path.exists(filename):
            print(f"Downloading {filename}...")
            urllib.request.urlretrieve(url, filename)
        else:
            print(f"{filename} already exists, skipping download.")
    print("Data download complete.")


if __name__ == "__main__":
    # Example usage
    download_data()
    params = real_world_parameters()
    print("Oil production:", params["oil_production"])
    print("Oil consumption:", params["oil_consumption"])
    print("Fertilizer production:", params["fertilizer_production"])
    print("Fertilizer consumption:", params["fertilizer_consumption"])
