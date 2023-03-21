# ###################################################
# Imports
# ###################################################

import pandas as pd

# ###################################################
# Functions
# ###################################################

def resourceType(code):

    if len(code) < 13:
        return 'piso'
    elif len(code) < 18:
        return 'habitacion'
    else:
        return 'plaza'
    

def parentCode(code):

    if len(code) < 13:
        return None
    elif len(code) < 18:
        return code[:12]
    else:
        return code[:16]


# ###################################################
# Main
# ###################################################

def load_resources(apiClient, dbClient, df_resources):

    # Return values
    result = ''
    log = ''

    # Query
    query = """
    { 
        buildings: Building_BuildingList { id Code } 
        providers: Provider_ProviderList { id Name } 
        flat_types: Resource_Resource_flat_typeList { id Code } 
        place_types: Resource_Resource_place_typeList { id Code } 
        rates: Billing_Pricing_rateList { id Code } 
    }
    """
    data = apiClient.call(query)
    log += 'Recuperando valores de referencia...\n'

    # Get codes
    df_buildings = pd.json_normalize(data['buildings'])
    df_providers = pd.json_normalize(data['providers'])
    df_flat_types = pd.json_normalize(data['flat_types'])
    df_place_types = pd.json_normalize(data['place_types'])
    df_rates = pd.json_normalize(data['rates'])

    # Final result
    df = pd.DataFrame()
    df['id'] = range(1, len(df_resources) + 1)

    # Copy simple columns
    log += 'Copiando columnas...\n'
    for k in df_resources.keys():
        if isinstance(k, str):
            if not '.' in str(k):
                df[str(k)] = df_resources[str(k)]

    # Find parent id
    log += 'Calculando parent id...\n'
    df['Parent_code'] = df['Code'].apply(parentCode)
    df['Parent_id'] = None
    for index, row in df.iterrows():
        if row['Parent_code'] != None:
            result = df.loc[df['Code'] == row['Parent_code']]
            df.loc[index, 'Parent_id'] = result.iloc[0]['id']
    df.drop('Parent_code', axis=1, inplace=True)

    # Look for providers id
    log += 'Obteniendo ids de propietario...\n'
    df_merge = pd.merge(df_providers, df_resources, left_on='Name', right_on='Provider.Name', how='inner')
    df['Owner_id'] = df_merge['id']

    # Look for flat types id
    log += 'Obteniendo ids de tipo de piso...\n'
    df_merge = pd.merge(df_flat_types, df_resources, left_on='Code', right_on='Resource_flat_type.Code', how='right')
    df['Flat_type_id'] = df_merge['id']

    # Look for place types id
    log += 'Obteniendo ids de tipo de plaza...\n'
    df_merge = pd.merge(df_place_types, df_resources, left_on='Code', right_on='Resource_place_type.Code', how='right')
    df['Place_type_id'] = df_merge['id']

    # Look for building id
    log += 'Obteniendo ids de edificio...\n'
    df_merge = pd.merge(df_buildings, df_resources['Code'].str[:6], left_on='Code', right_on='Code', how='right')
    df['Building_id'] = df_merge['id']

    # Look for rate id
    log += 'Obteniendo ids de tarifas...\n'
    df_merge = pd.merge(df_rates, df_resources, left_on='Code', right_on='Pricing_rate.Code', how='right')
    df['Rate_id'] = df_merge['id']

    # Resource type
    log += 'Calculando tipo de recurso...\n'
    df['Resource_type'] = df_resources['Code'].apply(resourceType)

    # Address
    log += 'Calculando dirección de recurso...\n'
    df['Address'] = (df_resources['Address'] + ' ' + df_resources['Code'].str[13:]).str.strip()

    # Return
    print(df)
    result = 'OK!'
    log += result
    return result, log, df