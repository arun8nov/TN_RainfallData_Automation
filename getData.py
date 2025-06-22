import os
import time 
from datetime import datetime
from datetime import timedelta
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings("ignore")

# Re-index Function
# This function resets the index of a DataFrame and sets the index name to 'id'
def re_index(df):
    df = df.reset_index(drop=True)
    df.index.name = 'id'
    return df
    
history_df = pd.read_csv('tnRainfallData.csv', index_col=0)
history_df.date = pd.to_datetime(history_df.date)

# Create Empty DataFrame to store the values

column_Name = ['dept', 'dist', 'station', 'value', 'date']
Search_Rain_Fall_Data = pd.DataFrame(columns=column_Name)
Search_Rain_Fall_Data.index.name = 'id'

# Get date input from the DataFrame and today's date as required format

Start_Date = history_df.date.tail(1).dt.strftime('%d-%m-%Y').values[0]
End_Date = datetime.today().strftime('%d-%m-%Y')

# Change date format
sd = datetime.strptime(Start_Date,"%d-%m-%Y").date()
ed = datetime.strptime(End_Date,"%d-%m-%Y").date()

# Get all list of date between start date and end date

List_date_format = [] 
while sd <= ed:
    List_date_format.append(sd)
    sd = sd+timedelta(days = 1)
    
# Change into object method

List_Object_format = [i.strftime("%d-%m-%Y") for i in List_date_format ]


# Open the browser and enter the site 

driver = webdriver.Chrome()
driver.get("https://beta-tnsmart.rimes.int/index.php/Rainfall/daily_data")

# Get the html code from the web and looping over the date

for i in List_Object_format:  
    # Drop down Selection 
    dropdown = driver.find_element(By.ID, "type")
    select = Select(dropdown)
    select.select_by_index(1)

    Date = i
    # Date selection
    date = driver.find_element(By.ID, "date")
    date.clear()
    date.send_keys(Date)
    
    #search the selection
    #search = driver.find_element(By.XPATH, '//*[@id="submit"]')
    search = driver.find_element(By.NAME,"submit")
    search.click()
        
    #Get HTML code & Save as a file
    
    html_code = driver.page_source
    
    
    # Date find in the html code
    
    
    soup = BeautifulSoup(html_code, 'html')
    Da = soup.find(class_ = "panel-heading")
    
    if Da != None:
        
        # Read the date from html code and tranform into required format
        
        Da = Da.text.strip().replace("District wise observed Rainfall\n                    data on ","")
        month = { "Jan" : "01", "Feb" : "02", "Mar" : "03", "Apr" : "04", "May" : "05", "Jun" : "06", "Jul" : "07",
                  "Aug" : "08", "Sep" : "09", "Oct" : "10", "Nov" : "11", "Dec" : "12"}
        Date = Da.replace(Da[3:6],month[Da[3:6]])
        
        # Find table content in html and transform into DataFrame then proceed it to required format
        
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
        
        # Add date to every rows
        
        DL = [Date] 
        for i in range (len(df1)):
            DL.append(DL[0])
        C_Date = pd.DataFrame(DL,columns= ['date'])
        C_Date.date = pd.to_datetime(C_Date.date, format = "%d-%m-%Y")
        df3 = df1.join(C_Date)
        Search_Rain_Fall_Data = pd.concat([Search_Rain_Fall_Data,df3])
    else: 
        # No rainfall occured in the search
        # create empty DF with the date 
        E = {
            'dept' : 'All',
            'dist' : 'All',
            'station' : 'All',
            'value' : 0,
            'date' : Date
        }
        df2 = pd.DataFrame(pd.Series(E)).T
        df2.value = df2.value.astype(float)
        df2.date = pd.to_datetime(df2.date,format = "%d-%m-%Y")
        df2.index.name = 'id'
        df3 = df2
        Search_Rain_Fall_Data = pd.concat([Search_Rain_Fall_Data,df3])
    
driver.quit()  
re_index(Search_Rain_Fall_Data)
final_df = pd.concat([history_df, Search_Rain_Fall_Data])
final_df = final_df.drop_duplicates()
final_df = final_df.sort_values(by='date')
final_df = re_index(final_df)
# Save the final DataFrame to a CSV file
final_df.to_csv('tnRainfallData.csv')
# Print the final DataFrame
print(final_df)
