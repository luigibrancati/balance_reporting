import pandas as pd
import numpy as np
import glob
import json
from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.allow):
    campi:dict
    formato_data:str
    valore_base:float


with open("./config/config.json") as file:
    config = Config(**json.load(file))
direzione_names = ['Entrate', 'Uscite']


def non_blank_col(df):
    return list(filter(lambda c: "Unnamed" not in c, df.columns))

def strip_strings(df: pd.DataFrame):
    df_temp = df.copy(deep=True)
    for col in df.select_dtypes('object').columns:
        df_temp[col] = df_temp[col].astype('str').apply(lambda s: s.strip())
    return df_temp

def add_date_info(df, date_field: pd.Timestamp, date_prefix: str=''):
    return df.assign(**{
                date_prefix+'Anno': df[date_field].apply(lambda d: d.year),
                date_prefix+'Mese': df[date_field].apply(lambda d: d.month),
                date_prefix+'Settimana': df[date_field].apply(lambda d: d.week),
                date_prefix+'Giorno': df[date_field].apply(lambda d: d.day),
                date_prefix+'GDS': df[date_field].apply(lambda d: d.dayofweek)
            })

def convert_dates(df, null_val='Non contabilizzato'):
    df_temp = df.copy(deep=True)
    for field in [config.campi['data_valuta'], config.campi['data_contabile']]:
        df_temp[field].replace(to_replace=null_val, value=pd.to_datetime('today').strftime(config.formato_data), inplace=True)
        df_temp[field] = pd.to_datetime(df_temp[field], format=config.formato_data)
    
    df_temp.sort_values(by=config.campi['data_valuta'], ascending=False, inplace=True)
    df_temp.set_index(np.array(range(1,len(df)+1,1)), inplace=True)
    df_temp['Contabilizzato'] = df_temp[config.campi['data_contabile']] >= df_temp[config.campi['data_valuta']]
    return df_temp

def import_df():
    try:
        file = open(config.cartella+"/"+config.cartella_estratto_conto+"/fulldf.csv")
        print("Trovato file fulldf.csv, carico i dati da lì")
        print(f"Per aggiornare i dati, eliminare il file fulldf.csv dalla cartella {config.cartella_estratto_conto}")
        df = pd.read_csv(file, delimiter=',', index_col=False)
    except FileNotFoundError:
        files = glob.glob(config.cartella+"/"+config.cartella_estratto_conto+'/*.xls')
        print(f"Files: {files}")
        df = pd.concat([pd.read_excel(file, index_col=None, header=8) for file in files])
        df_abi = pd.read_csv(config.cartella+'/abi.csv', delimiter='|', index_col=None)
        df = df[non_blank_col(df)]
        df_abi = df_abi[non_blank_col(df_abi)]
        df = df.merge(df_abi, how='left', left_on='Causale ABI', right_on='ABI', suffixes=(None,'_ABI')).drop('ABI', axis=1)
        df.to_csv(config.cartella+"/"+config.cartella_estratto_conto+'/fulldf.csv', index=False)
    global orig_cols
    orig_cols = list(df.columns)
    return df
    
def preprocess_df(df):
    # Strip spaces
    df = strip_strings(df)
    # Replace void ABIs
    df[config.campi['abi']].replace(to_replace=['-', ' '], value='NA', inplace=True)
    # Fix dates
    df = convert_dates(df)
    # drop
    df.drop_duplicates(inplace=True)
    # Extract date info
    df = add_date_info(df, config.campi['data_contabile'])
    df['Direzione'] = df[config.campi['importo']].apply(lambda v: direzione_names[0] if v>=0 else direzione_names[1])
    df[config.campi['importo']+'_abs'] = np.abs(df[config.campi['importo']])
    return df
