# %%

import pandas as pd

from shapely.geometry import shape

from service_request_map.utils.socrata import socrata_api_query


# %%
def get_sr_socrata(
        date_start: str = '2026-01-25',
        date_end: str = '2026-01-31',
        complaint_type: str = 'heat'
    ):
    """Get service request data from Socrata API."""
    where_str = (
        f"(date_trunc_ymd(created_date) >= '{date_start}')"
        f" AND (date_trunc_ymd(created_date) <= '{date_end}')"
    )
    if complaint_type == 'heat':
        where_str = (
            where_str 
            + f" AND ("
            + f"(CONTAINS(LOWER(complaint_type), 'heat'))"
            + f" OR (CONTAINS(LOWER(descriptor), 'hot water'))"
            + f")"
        )

    select_str = (
        'unique_key, created_date, closed_date, agency, agency_name, complaint_type, descriptor, location_type, '
        'incident_zip, incident_address, street_name, cross_street_1, cross_street_2, intersection_street_1, '
        'intersection_street_2, address_type, city, landmark, facility_type, status'
    )

    dataset_id = 'erm2-nwe9'
    timeout = 480
    where = where_str,
    select = select_str
    
    
    sr_df = socrata_api_query(
        dataset_id=dataset_id,
        timeout=timeout,
        where=where,
        select=select,
        limit=1000000,
    )

    for date_var in ['created_date', 'closed_date']:
        sr_df[f'{date_var}_dt'] = pd.to_datetime(sr_df[date_var]).dt.date
    
    return sr_df


if __name__ == '__main__':
    sr_df = get_sr_socrata()
    # print(sr_df.head()) 
# %%
