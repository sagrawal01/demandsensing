from ml_training import run_training
from dateutil.relativedelta import relativedelta
import numpy as np
import pandas as pd
import sys

def create_pivot(com, sc):
    sc.drop(columns=['Actual_Outs'], inplace=True)
    pivot_sc = pd.DataFrame(sc.groupby(['InitialDate', 'Year', 'Month']).aggregate({'Demand': np.sum, 'PredictionXGBoost': np.sum}).reset_index().values.tolist())
    pivot_sc.columns = ['InitialDate', 'Year', 'Month', 'Demand', 'Prediction_XGBoost']
    pivot_sc['PredictionDate'] = pd.to_datetime(pivot_sc[['Month', 'Year']].assign(day=1))
    pivot_sc = pivot_sc[pivot_sc['PredictionDate'] >= pivot_sc['InitialDate']]
    pivot_sc.drop(['Year', 'Month'], axis=1, inplace=True)
    pivot_sc['Country']=sys.argv[1]
    pivot_sc['Product_Key'] = sys.argv[2]
    pivot_sc = pivot_sc[['Country', 'Product_Key', 'InitialDate', 'PredictionDate', 'Demand', 'Prediction_XGBoost']]

    pivot_com = pd.DataFrame(com.groupby(['InitialDate', 'Year', 'Month']).aggregate({'Demand': np.sum, 'PredictionXGBoost': np.sum}).reset_index().values.tolist())
    pivot_com.columns = ['InitialDate', 'Year', 'Month', 'Demand', 'Prediction_XGBoost']
    pivot_com['PredictionDate'] = pd.to_datetime(pivot_com[['Month', 'Year']].assign(day=1))
    pivot_com = pivot_com[pivot_com['PredictionDate'] >= pivot_com['InitialDate']]
    pivot_com.drop(['Year', 'Month'], axis=1, inplace=True)
    pivot_com['Country']=sys.argv[1]
    pivot_com['Presentation_Key'] = sys.argv[2]
    pivot_com = pivot_com[['Country', 'Product_Key', 'InitialDate', 'PredictionDate', 'Demand', 'Prediction_XGBoost']]


    return pivot_com, pivot_sc


def calculate_metrics_adjusted(pivotlist, final_output, inclusive_start, exclusive_end, column_num):
    prediction = {}
    actual = {}
    for i in range(0, len(pivotlist)):
        for j in range(inclusive_start, exclusive_end):
            if pivotlist.iloc[i, 2] + relativedelta(months=j) == pivotlist.iloc[i, 3]:
                key = (pivotlist.iloc[i, 0], pivotlist.iloc[i, 1], pivotlist.iloc[i, 2])
                adjusted_key = (pivotlist.iloc[i, 0], pivotlist.iloc[i, 1],
                                pivotlist.iloc[i, 2] + relativedelta(months=(exclusive_end - 1)))
                prediction[adjusted_key] = prediction.get(adjusted_key, 0.0) + pivotlist.iloc[i, column_num]
                actual[adjusted_key] = actual.get(adjusted_key, 0.0) + pivotlist.iloc[i, 4]
    for key in prediction.keys():
        if actual[key] != 0:
            final_output[(key, 'FA', inclusive_start, exclusive_end)] = round(
                (100 * (1 - abs(prediction[key] - actual[key]) / actual[key])), 3)
            final_output[(key, 'Deviation', inclusive_start, exclusive_end)] = prediction[key] - actual[key]
            final_output[(key, 'Actual', inclusive_start, exclusive_end)] = actual[key]

        else:
            final_output[(key, 'FA', inclusive_start, exclusive_end)] = 0
            final_output[(key, 'Deviation', inclusive_start, exclusive_end)] = 0
            final_output[(key, 'Actual', inclusive_start, exclusive_end)] = 0
    return final_output

def process_metrics(pivotlist, source):
    metrics = {}
    for i in range(5, len(pivotlist.columns)):
        final_output = {}
        dictlist = []
        final_output = calculate_metrics_adjusted(pivotlist, final_output, 0, 1, i)
        # New MT:
        final_output = calculate_metrics_adjusted(pivotlist, final_output, 4, 5, i)
        for key, value in final_output.items():
            if i == 5:
                model_name = "XGBoost"
            metrics[(key, model_name)] = value
    metrics_keys = []
    for key in metrics:
        values = []
        # print(key[0][0][0])
        values.append(key[0][0][0])
        values.append(key[0][0][1])
        values.append(key[0][0][2])
        # values.append(key[0][0][3])
        values.append(key[0][1])
        values.append(key[0][2])
        values.append(key[0][3])
        values.append(key[1])
        metrics_keys.append(values)
    metrics_output = pd.DataFrame(metrics_keys)
    metrics_values = []
    for value in metrics.values():
        metrics_values.append(value)
    metrics_output['Value'] = metrics_values
    # metrics.columns=['country','plant','presentation_key','date','metric','inclusive_start','exclusive_end','Model','Value']
    metrics_output.columns = ['Country', 'Product_Key', 'Date', 'Metric', 'Inclusive_start',
                                'Exclusive_end', 'Model', 'Value']

    # metrics_original['Value']=np.where((metrics_original['Value']>100)|(metrics_original['Value']<0),0,metrics_original['Value'])
    metrics_output['Aggregation'] = np.where(metrics_output['Inclusive_start'] == 0, 'ST', 'NEWMT')
    metrics_output['Source'] = source

            # metrics['aggregation']=np.where(metrics['inclusive_start']==0,'ST','1-6M')
            # metrics['aggregation']=np.where(metrics['inclusive_start']==4,'NEWMT',metrics['aggregation'])

    return metrics_output

if __name__ == '__main__':
    output_com, output_sc=run_training()
    pivot_com, pivot_sc=create_pivot(output_com, output_sc)
    print(pivot_com.head())
    print(pivot_sc.head())
    metrics_sc=process_metrics(pivot_sc, 'Demand')
    metrics_com = process_metrics(pivot_com, 'Commercial')
    metrics_final = metrics_sc.append(metrics_com, ignore_index=True)
    metrics_final.sort_values(by=['Country', 'Product_Key', 'Inclusive_start', 'Date'], inplace=True)
    metrics_final['Input'] = sys.argv[7]
    metrics_final.to_csv('metrics_'+sys.argv[2] + '.csv')