# %%
from service_request_map.extract.get_sr_socrata import get_sr_socrata
from service_request_map.extract.get_zip_geojson import get_zip_geojson

from service_request_map.utils.config_paths import DATA_DIR

# %%
def fetch_data() -> None:
    sr_df = get_sr_socrata(complaint_type='heat')
    zip_gdf = get_zip_geojson()

    sr_df.to_parquet(DATA_DIR / 'sr_data.parquet')
    zip_gdf.to_parquet(DATA_DIR / 'zip_geo.parquet')

if __name__ == "__main__":
    fetch_data()

# %%

def main() -> None:
    fetch_data()

if __name__ == "__main__":
    main()

# %%
