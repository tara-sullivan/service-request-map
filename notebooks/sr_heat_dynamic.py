import marimo

__generated_with = "0.20.4"
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
    import pathlib
    import openlayers as ol
    import json
    import requests

    return gpd, mo, ol, pd


@app.cell
def _(mo):
    import datetime

    mo.md(f"""
    Last updated: {datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')}
    """)
    return


@app.cell
def _(gpd, pd):
    # _base = pathlib.Path(mo.notebook_location()).parents[0]
    # sr_df = pd.read_parquet(_base / 'data' / 'sr_data.parquet')
    # zip_gdf = gpd.read_parquet(_base / 'data' / 'zip_geo.parquet')
    # sr_df = pd.read_parquet('data/sr_data.parquet')
    zip_gdf = gpd.read_parquet('data/zip_geo.parquet')

    parquet_file = r'https://raw.githubusercontent.com/tara-sullivan/service-request-map/main/data/sr_data.parquet'
    sr_df = pd.read_parquet(parquet_file, engine='auto')

    # parquet_file = r'https://raw.githubusercontent.com/tara-sullivan/service-request-map/main/data/zip_geo.parquet'
    # reponse = requests.get(parquet_file)
    # # zip_gdf = gpd.read_parquet(io.BytesIO(resp.content))
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
        value=sr_df['created_date_dt'].max(),
    )

    mo.hstack([complaint_dropdown, start_date, end_date])
    return complaint_dropdown, end_date, start_date


@app.cell
def _(complaint_dropdown, end_date, mo, pd, sr_df, start_date):
    group_by_filter = pd.Series(index=sr_df.index, data=True)

    if complaint_dropdown.value is not None:
        complaint_filter = (sr_df['complaint_type'] == complaint_dropdown.value)
    else:
        complaint_filter = pd.Series(index=sr_df.index, data=True)

    date_filter = (
        (sr_df['created_date_dt'] >= start_date.value) &
        (sr_df['created_date_dt'] < (end_date.value + pd.Timedelta(1, 'D')))
    )

    filter_df = sr_df.loc[(group_by_filter & complaint_filter & date_filter), ['unique_key', 'incident_zip']]

    group_by_df = (
        filter_df.groupby('incident_zip')['unique_key'].count()
        .reset_index()
        .rename(columns={'unique_key': 'count', 'incident_zip': 'zip'})
    )

    _cards = [
        mo.stat(label='Total service requests', value=len(filter_df), bordered=True),
        mo.stat(label='Start date', value=start_date.value, bordered=True),
        mo.stat(label='End date', value=end_date.value, bordered=True)
    ]

    mo.hstack(_cards, widths='equal', align='center')
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
def _(ol, zip_count_gdf):
    map = ol.MapWidget(ol.View(center=(-73.94, 40.70), zoom=10))

    min_count = int(zip_count_gdf['count'].min())
    max_count = int(zip_count_gdf['count'].max())

    zip_style = ol.FlatStyle(
        fill_color=[
            "interpolate", ["linear"],
            ["get", "count"],
            min_count, "rgba(255, 245, 235, 0.8)",   # low  → light orange
            max_count, "rgba(179, 0, 0, 0.8)",        # high → dark red
        ],
        stroke_color="#555555",
        stroke_width=1.0,
    )

    # zip_style = ol.FlatStyle(
    #     fill_color="rgba(100, 149, 237, 0.3)",  # semi-transparent blue fill
    #     stroke_color="#3355aa",
    #     stroke_width=1.5,
    # )
    zip_vector = ol.VectorSource(geojson=ol.gdf_to_geojson(zip_count_gdf))

    zip_layer = ol.VectorLayer(
        source=zip_vector,
        style=zip_style,
    )

    map.add_layer(zip_layer)

    # adds count and zip for hover
    map.add_tooltip()

    map
    return


if __name__ == "__main__":
    app.run()
