import marimo

__generated_with = "0.20.1"
app = marimo.App(width="medium")


@app.cell
def _(mo):
    mo.md(f"""
    # 311 Heat and Hot Water service requests
    ## January 2026 snow storm
    """)
    return


@app.cell
def _():
    import pandas as pd
    import marimo as mo

    import geopandas as gpd
    import folium
    import branca.colormap as cm

    # from service_request_map.extract.get_sr_socrata import get_sr_socrata
    # from service_request_map.extract.get_zip_geojson import get_zip_geojson
    return cm, folium, gpd, mo, pd


@app.cell
def _(gpd, pd):
    sr_df = pd.read_parquet('data/sr_data.parquet')
    zip_gdf = gpd.read_parquet('data/zip_geo.parquet')
    return sr_df, zip_gdf


@app.cell
def _(mo, sr_df):
    complaint_dropdown = mo.ui.dropdown(
        list(sr_df['complaint_type'].unique()),
        label='Complaint Type:',
        value=None,
    )
    start_date = mo.ui.date(
        start=sr_df['created_date_dt'].min(),
        stop=sr_df['created_date_dt'].max(),
        label='Start Date:',
        value=None,
    )
    end_date = mo.ui.date(
        start=sr_df['created_date_dt'].min(),
        stop=sr_df['created_date_dt'].max(),
        label='End Date:',
        value=None,
    )

    # mo.hstack([complaint_dropdown, start_date, end_date])
    _cards = [
        mo.stat(label='Total service requests', value=len(sr_df), bordered=True),
        mo.stat(label='Start date', value=sr_df['created_date_dt'].min(), bordered=True),
        mo.stat(label='End date', value=sr_df['created_date_dt'].max(), bordered=True)
    ]

    mo.hstack(_cards, widths='equal', align='center')
    return


@app.cell
def _(pd, sr_df):
    group_by_filter = pd.Series(index=sr_df.index, data=True)

    complaint_filter= pd.Series(index=sr_df.index, data=True)

    date_filter = pd.Series(index=sr_df.index, data=True)

    filter_df = sr_df.loc[(group_by_filter & complaint_filter & date_filter), ['unique_key', 'incident_zip']]

    group_by_df = (
        filter_df.groupby('incident_zip')['unique_key'].count()
        .reset_index()
        .rename(columns={'unique_key': 'count', 'incident_zip': 'zip'})
    )
    return (group_by_df,)


@app.cell
def _(group_by_df, pd, zip_gdf):
    zip_count_gdf = pd.merge(
        left=zip_gdf[['GEOID', 'geometry']].rename(columns={'GEOID': 'zip'}),
        right=group_by_df, 
        on='zip',
        how='left', validate='1:1'
    )
    zip_count_gdf['count'] = zip_count_gdf['count'].fillna(0)
    return (zip_count_gdf,)


@app.cell
def _(cm, folium, zip_count_gdf):
    map = folium.Map(
        location=[40.70, -73.94],
        zoom_start=10,
        tiles="CartoDB positron"
    )

    colormap = cm.linear.YlOrRd_09.scale(
        zip_count_gdf['count'].min(),
        zip_count_gdf['count'].max()
    )

    folium.GeoJson(
        zip_count_gdf,
        style_function=lambda feature: {
            "fillColor": colormap(feature["properties"]["count"]),
            "color": "black",
            "weight": 0.5,
            "fillOpacity": 0.7,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["zip", "count"],
            aliases=["ZIP Code:", "Count:"],
            localize=True,
            sticky=False
        )
    ).add_to(map)

    colormap.add_to(map)

    map
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
