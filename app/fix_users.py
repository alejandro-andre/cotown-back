# ###################################################
# Data migration
# ---------------------------------------------------
# Fix users email
# ###################################################

# #####################################
# Imports
# #####################################

# System includes
from datetime import datetime
import pandas as pd

# Cotown includes
from library.services.config import settings
from library.services.dbclient import DBClient


# #####################################
# Main
# #####################################

# DB API
dbClient = DBClient(
  host=settings.SERVER,
  dbname=settings.DATABASE,
  user=settings.DBUSER,
  password=settings.DBPASS,
  sshuser=settings.SSHUSER,
  sshpassword=settings.get('SSHPASS', None),
  sshprivatekey=settings.get('SSHPKEY', None)
)
dbClient.connect()
print('ACCESO A BD')


# #####################################
# Customers & Users
# #####################################

print('\nCLIENTES')
df_customers = pd.read_csv('./migration/customers.in.csv', delimiter=';', encoding='utf-8')
df_customers = df_customers[['Customer_id', 'Email']].rename(columns={'Customer_id': 'id', 'Email': 'email_customer'})

print('\nUSUARIOS')
df_users = pd.read_csv('./migration/users.in.csv', delimiter=';', encoding='utf-8')
df_users = df_users[['requester_id', 'email']].rename(columns={'requester_id': 'id', 'email': 'email_user'})

merged_df = pd.merge(df_customers, df_users, on='id')
merged_df['emails_differ'] = merged_df['email_customer'] != merged_df['email_user']
different_emails_df = merged_df[merged_df['emails_differ']].drop_duplicates().drop(columns={'id', 'emails_differ'})
print(different_emails_df.to_csv(index=False))
