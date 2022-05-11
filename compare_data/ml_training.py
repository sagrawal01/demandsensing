from processdata import create_merged_data
from datetime import datetime
import xgboost as xgb
import sys
import pandas as pd

#Add in one-hot encoding and lagged variables in future

def create_training_data (train_with_com_demand, input_date=sys.argv[5]):
    train_data_filtered=train_with_com_demand.loc[train_with_com_demand.Date<=(datetime.strptime(input_date,'%Y-%m-%d'))]
    train_data_filtered = train_data_filtered[['Date', 'Week', 'Month', 'Quarter', 'Year', 'DaysfromDate', 'Comm_data', 'Demand']]
    train_data_filtered.drop_duplicates(subset=['Date'], keep='last', inplace=True)
    train_data_filtered = train_data_filtered[train_data_filtered['Demand'].notna()].reset_index(drop=True)

    test_data_filtered = train_with_com_demand.loc[train_with_com_demand.Date > (datetime.strptime(input_date, '%Y-%m-%d'))]
    test_data_filtered = test_data_filtered[['Date', 'Week', 'Month', 'Quarter', 'Year', 'DaysfromDate', 'Comm_data', 'Demand']]
    test_data_filtered = test_data_filtered[test_data_filtered['Demand'].notna()].reset_index(drop=True)
    test_data_filtered.drop_duplicates(subset=['Date'], keep='last', inplace=True)

    return train_data_filtered, test_data_filtered

def create_com_data(train_data_filtered,test_data_filtered):
    X_test_com = test_data_filtered[['Week', 'Month', 'Quarter', 'Year', 'DaysfromDate', 'Comm_data']]
    X_train_com = train_data_filtered[['Week', 'Month', 'Quarter', 'Year', 'DaysfromDate', 'Comm_data']]
    Y_train_com = train_data_filtered[['Demand']]
    Y_test_com = test_data_filtered[['Demand']]

    return X_train_com, Y_train_com, X_test_com, Y_test_com

def create_orig_data(train_data_filtered,test_data_filtered):
    X_test= test_data_filtered[['Week', 'Month', 'Quarter', 'Year', 'DaysfromDate']]
    X_train = train_data_filtered[['Week', 'Month', 'Quarter', 'Year', 'DaysfromDate']]
    Y_train = train_data_filtered[['Demand']]
    Y_test = test_data_filtered[['Demand']]

    return X_train, Y_train, X_test, Y_test

def xgboost_training(X_train, Y_train, X_test, Y_test, test_data_filtered, input_date=sys.argv[5]):
    data_dmatrix = xgb.DMatrix(data=X_train, label=Y_train)
    xg_reg = xgb.XGBRegressor(objective='reg:squarederror')
    xg_reg.fit(X_train, Y_train)
    pred_XG_boost = xg_reg.predict(X_test)
    predlist = []
    for i in range(0, len(pred_XG_boost)):
        predlist.append(pred_XG_boost[i])
    predlist = pd.DataFrame({'PredictionXGBoost': predlist})
    initialresult=pd.concat([test_data_filtered, predlist], axis=1, sort=False)
    initialresult = initialresult[initialresult['PredictionXGBoost'].notna()].reset_index(drop=True)
    initialresult = initialresult[initialresult['Demand'].notna()].reset_index(drop=True)
    #initialresult['InitialDate'] = (pd.Timestamp(datetime.strptime(input_date,'%Y-%m-%d'))+pd.DateOffset(months=1)).to_numpy().astype('datetime64[M]')

    return initialresult




def run_training():
    input_date=sys.argv[5]
    train_with_com_demand=create_merged_data()
    # train, test=create_training_data(train_with_com_demand)
    # X_train_com, Y_train_com, X_test_com, Y_test_com=create_com_data(train, test)
    # X_train, Y_train, X_test, Y_test = create_orig_data(train, test)
    # result_com=xgboost_training(X_train_com, Y_train_com, X_test_com, Y_test_com, test)
    # result_sc=xgboost_training(X_train, Y_train, X_test, Y_test, test)
    # result_sc['InitialDate'] = (pd.Timestamp(datetime.strptime(input_date,'%Y-%m-%d'))+pd.DateOffset(months=1)).to_numpy().astype('datetime64[M]')

    # print(result_sc)
    output_com = pd.DataFrame()
    output_sc=pd.DataFrame()
    #print((pd.Timestamp(datetime.strptime(input_date,'%Y-%m-%d'))+pd.DateOffset(months=int(sys.argv[6]))))
    for i in range(0, int(sys.argv[6])):
        output_date=(pd.Timestamp(datetime.strptime(input_date,'%Y-%m-%d'))+pd.DateOffset(months=i)).strftime('%Y-%m-%d')
        train, test = create_training_data(train_with_com_demand, output_date)
        X_train_com, Y_train_com, X_test_com, Y_test_com = create_com_data(train, test)
        X_train, Y_train, X_test, Y_test = create_orig_data(train, test)
        result_com = xgboost_training(X_train_com, Y_train_com, X_test_com, Y_test_com, test)
        result_com['InitialDate'] = (pd.Timestamp(datetime.strptime(output_date, '%Y-%m-%d')) + pd.DateOffset(months=1)).to_numpy().astype('datetime64[M]')
        output_com=output_com.append(result_com, ignore_index=True)
        result_sc = xgboost_training(X_train, Y_train, X_test, Y_test, test)
        result_sc['InitialDate'] = (pd.Timestamp(datetime.strptime(output_date, '%Y-%m-%d')) + pd.DateOffset(months=1)).to_numpy().astype('datetime64[M]')
        output_sc=output_sc.append(result_sc, ignore_index=True)
    return output_com, output_sc