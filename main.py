# Import libraries
import os
import time 
from datetime import timedelta
import datetime
from datetime import date
import pandas as pd
from bs4 import BeautifulSoup
import requests
import warnings
warnings.filterwarnings("ignore")

# Function for resetting the index of a DataFrame
# and setting the index name to 'id'
def re_index(df):
    df = df.reset_index(drop=True)
    df.index.name = 'id'
    return df

current_Data = pd.read_csv("tnRainfallData.csv", index_col=0)
# Convert 'Date' column to datetime format
current_Data['date'] = pd.to_datetime(current_Data['date'])

# Get today's data from the websource
url = 'https://beta-tnsmart.rimes.int/index.php/Rainfall/daily_data'
response = requests.get(url)
if response.status_code == 200:
    print("The HTML file was imported successfully.")
    soup = BeautifulSoup(response.text, 'html')
else:
    print("An error occurred while importing the file.")
    soup = []
Da = soup.find(class_ = "panel-heading")
if Da != None:
    print("RainFall occurred in TN")
    Date = Da.text.strip().replace("District wise observed Rainfall\n                    data on ","")
    month = { "Jan" : "01", "Feb" : "02", "Mar" : "03", "Apr" : "04", "May" : "05", "Jun" : "06", "Jul" : "07",
          "Aug" : "08", "Sep" : "09", "Oct" : "10", "Nov" : "11", "Dec" : "12"}
    Da = Date.replace(Date[3:6],month[Date[3:6]])
    y = int(Da[6:11])
    m = int(Da[3:5])
    d = int(Da[0:2])
    Today_Date =datetime.date(y,m,d)
    if ((Today_Date == date.today())):
            print("Date match with current Date")
            table = soup.find('table', id = "data_table")
    else:
            print("Date not matched")
            table = soup.find('table', id = "data_table")
    table_tr = table.find_all('tr')
    list = [table_tr.text.strip().replace("\n\n", ",") for table_tr in table_tr][1:]
    datalist = []
    for i in range(len(list)):
        datalist.append(list[i].strip().replace("\n",","))
    df = pd.DataFrame(datalist, columns = ['A'])
    df1 = pd.DataFrame(df)
    df1 = df1.A.str.split(",",expand = True)


    df1 = df1.drop([len(df)-1])
    for i in df1.columns :
        if df1[i].isna().sum() == len(df1):
            df1 = df1.drop(columns= [i])
        else:
            df1 = df1
    delete_rows = df1[df1[4].isna()].index
    delete_rows = delete_rows.append(df1[-1:].index)
    df1 = df1.drop(delete_rows,axis=0)
    if len(df1.columns) > 6:
        A = df1[[3]]
        B = df1[4].str.extract('([a-zA-Z]+)').dropna()
        C = df1[5].str.extract('([a-zA-Z]+)').dropna()
        B.loc[C.index] = B.loc[C.index] +","+ C.loc[C.index]
        D = pd.DataFrame(A.loc[B.index].values + ","+ B.values)
        D.index = A.loc[B.index].index
        A.loc[B.index] = D.copy()
        df1[3] = A[3]
        E = df1[4].str.extract(r'(\d+\.?\d*)').dropna()
        F = df1[5].str.extract(r'(\d+\.?\d*)').dropna()
        G = df1[6].str.extract(r'(\d+\.?\d*)').dropna()
        H = pd.concat([E,F,G])
        df1[[4]] = H
    else:
        if len(df1.columns) >5:
            A = df1[[3]]
            B = df1[4].str.extract('([a-zA-Z]+)').dropna()
            C = pd.DataFrame(A.loc[B.index].values + ","+ B.values,index=B.index)
            A.loc[B.index] = C
            df1[3] = A[3]
            E = df1[4].str.extract(r'(\d+\.?\d*)').dropna()
            F = df1[5].str.extract(r'(\d+\.?\d*)').dropna()
            H = pd.concat([E,F])
            df1[[4]] = H
    for i in df1.columns :
        if len(df1.columns) !=5 :
            df1 = df1.drop(columns= [len(df1.columns)-1])
    df1 = df1.drop(columns = [0])
    column_Name = ['dept', 'dist', 'station', 'value']
    df1.columns = column_Name
    df1.value = df1.value.astype(float)
    df1 = df1.reset_index()
    df1 = df1.drop(columns = 'index')
    DL = [Da]
    for i in range (len(df1)):
        DL.append(DL[0])
    C_Date = pd.DataFrame(DL,columns= ['date'])
    C_Date.date = pd.to_datetime(C_Date.date, format = "%d-%m-%Y")
    Today_Rain_Fall = df1.join(C_Date)
    TN_Rain_Fall_History = current_Data.copy()
    TN_Rain_Fall_History.date = pd.to_datetime(TN_Rain_Fall_History.date, format = "%Y-%m-%d")
    if TN_Rain_Fall_History.tail(1).date.values != Today_Rain_Fall.head(1).date.values :
        Total_Rain_Fall_Data = pd.concat([TN_Rain_Fall_History,Today_Rain_Fall])
        print("Data Added")
    else :
        Total_Rain_Fall_Data = TN_Rain_Fall_History
        print("No Change")
    Total_Rain_Fall_Data = Total_Rain_Fall_Data.reset_index(drop = True)
    Total_Rain_Fall_Data.index.name = 'id'
    Total_Rain_Fall_Data.date = Total_Rain_Fall_Data.date.dt.strftime('%Y-%m-%d')
    Total_Rain_Fall_Data=Total_Rain_Fall_Data[['dept','dist','station','value','date']]
else:
    print("No Rain Fall today")
    DL = [str(date.today().day)+'-'+str(date.today().month)+'-'+str(date.today().year)]
    Empty_table= {'dept' : ['TN'], 'dist' : ['All'], 'station' : ['All'], 'value' : [0.0],'date' : DL}
    df = pd.DataFrame(Empty_table)
    df.index.name = 'id'
    df.date = pd.to_datetime(df.date, format = "%d-%m-%Y")
    Today_Rain_Fall = df.copy()
    TN_Rain_Fall_History = current_Data.copy()
    TN_Rain_Fall_History.date = pd.to_datetime(TN_Rain_Fall_History.date, format = "%Y-%m-%d")
    if TN_Rain_Fall_History.date.tail(1).dt.strftime('%d-%m-%Y').values[0]!=Today_Rain_Fall.date.head(1).dt.strftime('%d-%m-%Y').values[0] :
        Total_Rain_Fall_Data = pd.concat([TN_Rain_Fall_History,Today_Rain_Fall])
        print("Data Added")
    else :
        Total_Rain_Fall_Data = TN_Rain_Fall_History
        print("No Change")
    Total_Rain_Fall_Data = Total_Rain_Fall_Data.reset_index(drop = True)
    Total_Rain_Fall_Data.index.name = 'id'
    Total_Rain_Fall_Data.date = Total_Rain_Fall_Data.date.dt.strftime('%Y-%m-%d')
    Total_Rain_Fall_Data=Total_Rain_Fall_Data[['dept','dist','station','value','date']]
Total_Rain_Fall_Data.drop_duplicates(inplace=True)
Total_Rain_Fall_Data.dropna(inplace=True)
Total_Rain_Fall_Data = Total_Rain_Fall_Data.sort_values(by='date')
Total_Rain_Fall_Data = re_index(Total_Rain_Fall_Data)
# Save the DataFrame to a CSV file
Total_Rain_Fall_Data.to_csv("tnRainfallData.csv")
print("Data saved to tnRainfall.csv")
print(Total_Rain_Fall_Data)