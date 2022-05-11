import sys
import pandas as pd
from datetime import datetime, timedelta
from getdata import getapodata, getcomdata


def create_train(train=getapodata()):
    train[['Week', 'Year']] = train.Week.str.split(".", expand=True)
    train[['Month', 'Year2']] = train.Month.str.split(".", expand=True)
    # train[['Demand','Unit']] = train.Demand.str.split(" ", expand=True)
    train = train.drop(['Year2', 'Product_Name'], axis=1)
    # train['Demand'] = train['Demand'].str.replace(',', '').astype(float)
    train['Year'] = train['Year'].astype('int')
    train['Month'] = train['Month'].astype('int')
    train['Week'] = train['Week'].astype('int')
    # print(train.head(5))

    train["Date"] = pd.to_datetime(train.Week.astype(str) + train.Year.astype(str).add('-1'), format='%W%Y-%w')
    train = train.sort_values(by=['Product_Key', 'Date'])
    # print(train.tail())

    try:
        for i in range(0, len(train) - 1):
            if train.loc[train.index[i], 'Week'] == train.loc[train.index[i + 1], 'Week']:
                train.loc[train.index[i], 'PercentofDemand'] = train.loc[train.index[i], 'Demand'] / (
                            train.loc[train.index[i], 'Demand'] + train.loc[train.index[i + 1], 'Demand'])
                train.loc[train.index[i + 1], 'PercentofDemand'] = train.loc[train.index[i + 1], 'Demand'] / (
                            train.loc[train.index[i], 'Demand'] + train.loc[train.index[i + 1], 'Demand'])
            i = i + 2
        train['PercentofDemand'] = train['PercentofDemand'].fillna(1)
    except:
        train['PercentofDemand'] = 1.0
    weeksplit = train.copy()

    train = train.drop(['PercentofDemand'], axis=1)

    train_weekly = train.groupby(['Country', 'Presentation_Key', 'Date',
                                  'Week', 'Year'])[["Demand"]].sum()
    train_weekly_df = pd.DataFrame(train_weekly.reset_index().values.tolist())
    train_weekly_df.columns = ['Country', 'Presentation_Key', 'Date', 'Week', 'Year', 'Demand']
    # print(train_weekly_df.head(10))

    train2 = train_weekly_df[['Country', 'Presentation_Key', 'Date']]
    countrypresdict = train2.groupby(['Country', 'Presentation_Key'])
    countrypresdict = countrypresdict.agg(max_date=pd.NamedAgg(column='Date', aggfunc='max'),
                                          min_date=pd.NamedAgg(column='Date', aggfunc='min'))
    countrypreslist = countrypresdict.reset_index().values.tolist()

    train_use = pd.DataFrame()
    for i in range(0, len(countrypreslist)):
        # print(countrypreslist[i][0], countrypreslist[i][1], countrypreslist[i][2], countrypreslist[i][3], (datetime.strptime('2018-01-01','%Y-%m-%d')-countrypreslist[i][3]).days/7.0)
        newtraindata_1 = pd.date_range(countrypreslist[i][3], countrypreslist[i][2], freq='W-MON')
        newtraindata_1 = newtraindata_1.to_frame(index=False, name='Date')
        newtraindata_1['Country'] = countrypreslist[i][0]
        newtraindata_1['Product_Key'] = countrypreslist[i][1]
        train_use = train_use.append(newtraindata_1, ignore_index=True)

    train_use = pd.merge(train_use, train_weekly_df, how='left', on=['Country', 'Product_Key', 'Date'])
    train_use['Demand'] = train_use['Demand'].fillna(0)
    train_use['Week'] = train_use['Week'].fillna(train_use['Date'].dt.week)
    train_use['Year'] = train_use['Year'].fillna(train_use['Date'].dt.year)
    indextrain_use = train_use[(train_use.Date.dt.month == 12) & (train_use.Date.dt.week == 1)].index
    train_use.drop(indextrain_use, inplace=True)
    train_use['Demand'] = train_use['Demand'].astype('int')
    train_use['Year'] = train_use['Year'].astype('int')
    train_use['Week'] = train_use['Week'].astype('int')
    # print(train_use.dtypes)

    train_use_ML = pd.DataFrame()
    for i in range(0, len(countrypreslist)):
        newtraindata_1 = pd.date_range(countrypreslist[i][3], countrypreslist[i][2], freq='W-MON')
        newtraindata_1 = newtraindata_1.to_frame(index=False, name='Date')
        newtraindata_1['Country'] = countrypreslist[i][0]
        newtraindata_1['Product_Key'] = countrypreslist[i][1]
        train_use_ML = train_use_ML.append(newtraindata_1, ignore_index=True)

    train_use_ML = pd.merge(train_use_ML, train_weekly_df, how='left', on=['Country', 'Product_Key', 'Date'])
    train_use_ML['Demand'] = train_use_ML['Demand'].fillna(0)
    train_use_ML['Week'] = train_use_ML['Week'].fillna(train_use_ML['Date'].dt.week)
    train_use_ML['Month'] = train_use_ML['Date'].dt.month
    train_use_ML['Quarter'] = train_use_ML['Date'].dt.quarter
    train_use_ML['Year'] = train_use_ML['Year'].fillna(train_use_ML['Date'].dt.year)
    train_use_ML['DaysfromDate'] = (
                train_use_ML['Date'] - pd.to_datetime(datetime.strptime('2013-01-01', '%Y-%m-%d').date())).dt.days
    indextrain_use_ML = train_use_ML[(train_use_ML.Date.dt.month == 12) & (train_use_ML.Date.dt.week == 1)].index
    train_use_ML.drop(indextrain_use_ML, inplace=True)
    train_use_ML['Demand'] = train_use_ML['Demand'].astype('int')
    train_use_ML['Year'] = train_use_ML['Year'].astype('int')
    train_use_ML['Week'] = train_use_ML['Week'].astype('int')
    train_use_ML['Month'] = train_use_ML['Month'].astype('int')
    train_use_ML['Quarter'] = train_use_ML['Quarter'].astype('int')
    train_use_ML['DaysfromDate'] = train_use_ML['DaysfromDate'].astype('int')
    return train_use_ML

def create_com_data(com_demand=getcomdata(sys.argv[4])):
    com_demand = com_demand.drop(com_demand.columns[[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]], axis=1)
    com_demand.columns = ['Date', 'Comm_data']
    com_demand_grouped = pd.DataFrame(com_demand.groupby(['Date'])[["Comm_data"]].sum().reset_index().values.tolist())
    com_demand_grouped.columns = ['Date', 'Comm_data']
    com_demand_grouped['Date']=com_demand_grouped['Date'] + timedelta(days=1)
    return com_demand_grouped

def create_merged_data():
    train_use_ML = create_train()
    com_data_grouped = create_com_data()
    train_with_com_demand=pd.merge(com_data_grouped,train_use_ML, how='left', on=['Date'])
    train_with_com_demand.drop(columns=['Country', 'Product_Key'], inplace=True)
    train_with_com_demand['Comm_data'] = train_with_com_demand['Comm_data'].astype(float)
    return train_with_com_demand
