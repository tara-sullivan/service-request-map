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
    import folium
    import branca.colormap as cm
    import pathlib

    return cm, folium, gpd, mo, pathlib, pd


@app.cell
def _(mo):
    import datetime

    mo.md(f"""
    Last updated: {datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')}
    """)
    return


@app.cell
def _(gpd, mo, pathlib, pd):
    # _base = pathlib.Path(mo.notebook_location()).parents[0]
    # sr_df = pd.read_parquet(_base / 'data' / 'sr_data.parquet')
    # zip_gdf = gpd.read_parquet(_base / 'data' / 'zip_geo.parquet')
    sr_df = pd.read_parquet('data/sr_data.parquet')
    zip_gdf = gpd.read_parquet('data/zip_geo.parquet')
    return sr_df, zip_gdf


@app.cell
def _(mo):
    mo.md(f"""
    Notice that the dropdown below doesn't update; this is because the notebook is **static**.
    If the notebook were dynamically hosted, the numbers and map below would update with the dropdown selections.
    """)
    return


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
        value=sr_df['created_date_dt'].min(),
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
