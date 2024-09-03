import pandas as pd
import json

with open('c.json', 'r', encoding='utf-8') as f:
  text = f.read()

df = pd.json_normalize(json.loads(text))

ndf = pd.DataFrame()
ndf['Code'] = df['cca2']
ndf['Alpha3'] = df['cca3']
ndf['Num'] = df['ccn3']
ndf['Tld']  = df['tld']
ndf['Name'] = df['translations.spa.common']
ndf['Name_en'] = df['name.common']
ndf['Continent'] = df['continents']
ndf['Prefix'] = df['idd.root']
ndf['Suffix'] = df['idd.suffixes']

ndf = ndf.sort_values(by='Code')
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
print(ndf)

ndf.to_excel('c.xlsx')


