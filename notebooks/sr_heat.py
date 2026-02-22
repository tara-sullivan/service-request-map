import marimo

__generated_with = "0.20.1"
app = marimo.App(width="medium")

@app.cell
def _(mo):
    mo.md(f"""
    # 311 Heat and Hot Water service requests
    ## January 2026 snow storm
    Note that app actively queries Open Data when opened, and will take a minute to load.
    """)
    return


@app.cell
def _():
    import pandas as pd
    import marimo as mo

    import geopandas as gpd
    import folium
    import branca.colormap as cm

    from service_request_map.extract.get_sr_socrata import get_sr_socrata
    from service_request_map.extract.get_zip_geojson import get_zip_geojson

    return cm, folium, get_sr_socrata, get_zip_geojson, mo, pd


@app.cell
def _(get_sr_socrata):
    sr_df = get_sr_socrata(complaint_type='heat')
    return (sr_df,)


@app.cell
def _(get_zip_geojson):
    zip_gdf = get_zip_geojson()
    return (zip_gdf,)


@app.cell
def _(mo, sr_df):
    complaint_dropdown = mo.ui.dropdown(
        list(sr_df['complaint_type'].unique()),
        label='Complaint Type:'
    )
    start_date = mo.ui.date(
        start=sr_df['created_date_dt'].min(),
        stop=sr_df['created_date_dt'].max(),
        label='Start Date:',
    )
    end_date = mo.ui.date(
        start=sr_df['created_date_dt'].min(),
        stop=sr_df['created_date_dt'].max(),
        label='End Date:',
    )

    mo.hstack([complaint_dropdown, start_date, end_date])
    return complaint_dropdown, end_date, start_date


@app.cell
def _(complaint_dropdown, end_date, pd, sr_df, start_date):
    group_by_filter = pd.Series(index=sr_df.index, data=True)

    if complaint_dropdown.value is not None:
        complaint_filter = (sr_df['complaint_type'] == complaint_dropdown.value)
    else:
        complaint_filter= pd.Series(index=sr_df.index, data=True)

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
    print(group_by_df.head())
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


if __name__ == "__main__":
    app.run()
