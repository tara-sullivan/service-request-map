# %%

import geopandas as gpd

url = "https://raw.githubusercontent.com/mattyschell/ZNZCTA/refs/heads/main/out/geojson/znzcta.geojson"

# %%
def get_zip_geojson():
    """Get zip code geojson data."""
    gdf = gpd.read_file(url)
    return gdf

if __name__ == '__main__':
    zip_gdf = get_zip_geojson()
    print(zip_gdf.head())   
# %%

if __name__ == '__main__':
    from service_request_map.utils.socrata import socrata_api_query

    from shapely.geometry import shape
    import matplotlib.pyplot as plt

    # get borough outline
    nybb_df = socrata_api_query(dataset_id='gthc-hcne')
    nybb_df['geometry'] = [shape(geo) for geo in nybb_df['the_geom']]

    nybb_gdf = gpd.GeoDataFrame(
        data=nybb_df,
        geometry='geometry',
        crs='EPSG:4326'
    )

    fig, ax = plt.subplots(figsize=(4, 3))
    nybb_gdf.plot(ax=ax, color='white', edgecolor='black', facecolor='none')

    zip_gdf.plot(ax=ax)

    xlim = ax.axes.get_xlim()
    ylim = ax.axes.get_ylim()
# %%
