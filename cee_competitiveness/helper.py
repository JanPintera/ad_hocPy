import pandas as pd
import numpy as np
import functools
import pycountry

### Following is intended as a future shared source of utility code

visegrad = {'CZ': "Czech Republic", 'HU': "Hungary", 'PL': "Poland", 'SK': "Slovak Republic"}
CEE_non_core = {'RO': 'Romania', 'BG': 'Bulgaria', 'EE': 'Estonia', 'LT': 'Lithuania', 'LV': 'Latvia', 'SI': 'Slovenia'}
#eu_balkan = {'RO': 'Romania', 'BG': 'Bulgaria'}
germany_plus = {'DE': 'Germany', 'AT': "Austria"}
southern = {'IT': 'Italy', 'ES': 'Spain', 'PT': 'Portugal', 'GR': 'Greece'}
west = {'NL': 'Netherlands', 'BE': 'Belgium', 'GB': 'Great Britain', 'UK': 'United Kingdom', 'FR': 'France', 'LU': 'Luxembourg', 'IR': 'Ireland'}
north = {'NOR': 'Norway', 'SE': 'Sweden', 'DK': 'Denmark', 'FI': 'Finland'}
emu = {'AT': 'Austria', 'BE': 'Belgium', 'CYP': 'Cyprus', 'EE': 'Estonia', 'FI': 'Finland', 'FR': 'France',
       'DE': 'Germany', 'GR': 'Greece', 'IR': 'Ireland', 'IT': 'Italy', 'LV': 'Latvia', 'LT': 'Lithuania', 'LU': 'Luxembourg',
        'MLT': 'Malta', 'NL': 'Netherlands', 'PT': 'Portugal', 'SK': "Slovak Republic", "SI": "Slovenia", "ES": "Spain"}
eu = {'CZ': "Czech Republic", 'HU': "Hungary", 'PL': "Poland", 'SE': 'Sweden', 'DK': 'Denmark', 'AT': 'Austria', 'BE': 'Belgium', 'CYP': 'Cyprus', 'EE': 'Estonia', 'FI': 'Finland', 'FR': 'France',
      'DE': 'Germany', 'GR': 'Greece', 'IR': 'Ireland', 'IT': 'Italy', 'LV': 'Latvia', 'LT': 'Lithuania', 'LU': 'Luxembourg',
      'MLT': 'Malta', 'NL': 'Netherlands', 'PT': 'Portugal', 'SK': "Slovak Republic", "SI": "Slovenia", "ES": "Spain", 'RO': 'Romania', 'BG': 'Bulgaria'}


def oecd_res2df(res: dict) -> pd.DataFrame:
    "Reads as raw OECD api query response and converts into pandas df"

    base = []
    cols = ['country']
    
    print(f"Downloading OECD table: {res['structure']['name']}")
    for st in res['structure']['dimensions']['observation']:
        if st['name'] == 'Country':
            for j in st['values']:
                base.append([j['name']])
                    
        elif st['name'] == 'Time':
            cols.extend([i['id'] for i in st['values']]) # we assume they are ordered!
    

    last_row = None
    for key, val in res['dataSets'][0]['observations'].items():
        row = int(key.split(':')[0])
        col = int(key.split(':')[-1])
            
        if last_row != row:
            base[row].extend([np.nan] * (len(cols) - 1))
            
        base[row][col+1] = val[0]
                
        last_row = row


    return pd.DataFrame(np.array(base), columns=cols)


def harmonise_base_year(gr, yr: int):
    base_val = gr.loc[lambda x: x['year'] == yr, 'value_deflator'].values[0]
    gr[f'deflator_{yr}'] = gr['value_deflator'] / base_val
    return gr

@functools.lru_cache(None)
def do_fuzzy_search(country):
    try:
        result = pycountry.countries.search_fuzzy(country)
    except Exception:
        return np.nan
    else:
        return result[0].alpha_2

def get_regions(df, country_col):
    df['region'] = np.where(df[country_col].isin(visegrad), "visegrad", 
                            np.where(df[country_col].isin(southern), 'south',
                                     np.where(df[country_col].isin(germany_plus), 'DE_AT',
                                              np.where(df[country_col].isin(west), 'west', 
                                                       np.where(df[country_col].isin(north), 'north',
                                                                np.where(df[country_col].isin(CEE_non_core), 'CEE_non_core', 'rest')
                                                                )
                                                      )
                                              )
                                    )
                            )
    return df
