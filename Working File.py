
import time
start_time=time.time()
import pandas as pd
import numpy as np
import os
from datetime import datetime


os.chdir("C:\\Users\\user\\Desktop\\Ninjacart\\Returns Analysis(Customer Fraud Detection)")

raw_data=pd.read_csv("Returns2monthsDump-Master.csv")
raw_data=pd.DataFrame(raw_data)

os.chdir("C:\\Users\\user\\Desktop\\Ninjacart\\Returns Analysis(Customer Fraud Detection)\\Working File")
datetoday=input("Enter date (in mm/dd/yyyy format) : ")

list1=[]
customer=raw_data.CustomerName.unique()
for i in range (len(customer)):
    customerdata=raw_data[raw_data.CustomerName==customer[i]]
    dates=customerdata.DeliveryDate.unique()
    for j in range(len(dates)):
        datedata=customerdata[customerdata.DeliveryDate==dates[j]]
        datedata=datedata.reset_index(drop=True)
        date=datedata.SOCreatedTime.unique()
        date=pd.DataFrame(date)
        date=date[0][0]
        t=datetime.strptime(date,"%m/%d/%Y %H:%M")
        beforereturn=0
        aftertruereturn=0
        afterreturn=0
        if(len(datedata)!=0):
            for k in range(len(datedata)):
                beforereturn=beforereturn+datedata['BilledQty'][k]*datedata['WeightFactor'][k]
                if(datedata['Code'][k]==4 or datedata['Code'][k]==5 or datedata['Code'][k]==7 or datedata['Code'][k]==9 or datedata['Code'][k]==12):
                    aftertruereturn=aftertruereturn+datedata['BilledQty'][k]*datedata['WeightFactor'][k]
                else:
                    aftertruereturn=aftertruereturn+datedata['FulfilledQty'][k]*datedata['WeightFactor'][k]
                afterreturn=afterreturn+datedata['FulfilledQty'][k]*datedata['WeightFactor'][k]
            k=""
            if(t.hour<19):
                k="ordered before 7:30"
            elif(t.hour==19 and t.minute<30):
                k="ordered before 7:30"
            elif(t.hour==19 and t.minute>30):
                k="ordered after 7:30"
            else:
                k="ordered after 7:30"
            list1.append([customer[i],dates[j],beforereturn,aftertruereturn,afterreturn,len(datedata),k])



list2=[]
customer=raw_data.CustomerName.unique()
returndata=[]
claim="True"
for i in range(len(customer)):
    customerdata=raw_data[raw_data.CustomerName==customer[i]]
    sku=customerdata.SKU.unique()
    for j in range(len(sku)):
        skudata=customerdata[customerdata.SKU==sku[j]]
        skudata=skudata.reset_index(drop=True)
        for k in range(len(skudata)):
            if(skudata['ReturnQty'][k]!=0 and k>1):
                if(skudata['Code'][k]==4 or skudata['Code'][k]==5 or skudata['Code'][k]==7 or skudata['Code'][k]==9 or skudata['Code'][k]==12 ):
                    claim="False"
                else:
                    claim="True"
                salepricetoday=skudata['SalePrice'][k]
                avgsalepricelasttwotimes=(skudata['SalePrice'][k-1]+skudata['SalePrice'][k-2])/2.0
                percentincrease=(salepricetoday-avgsalepricelasttwotimes)/avgsalepricelasttwotimes
                if(percentincrease>0.2):
                    list2.append([customer[i],sku[j],skudata['DeliveryDate'][k],salepricetoday,avgsalepricelasttwotimes,claim])







#Market price analysis
customer=raw_data.CustomerName.unique()
list3=[]
for i in range(len(customer)):
    customerdata=raw_data[raw_data.CustomerName==customer[i]]
    sku=customerdata.SKU.unique()
    for j in range(len(sku)):
        skudata=customerdata[customerdata.SKU==sku[j]]
        skudata=skudata.reset_index(drop=True)
        cases=skudata[skudata.SalePrice>=1.2*skudata.MarketPrice]
        if(len(cases)!=0):
            returncases=cases[cases.ReturnQty!=0]
            returncases=returncases.reset_index(drop=True)
            fraudreturncases=0
            for k in range(len(returncases)):
                if(returncases['Code'][k]==4 or returncases['Code'][k]==5 or returncases['Code'][k]==7 or returncases['Code'][k]==9 or returncases['Code'][k]==12):
                    fraudreturncases=fraudreturncases+1
                
            list3.append([customer[i],sku[j],len(cases),len(returncases),fraudreturncases])
            



list4=[]
cutomer=raw_data.CustomerName.unique()
for i in range(len(customer)):
    customerdata=raw_data[raw_data.CustomerName==customer[i]]
    sku=customerdata.SKU.unique()
    for j in range(len(sku)):
        skudata=customerdata[customerdata.SKU==sku[j]]
        skudata=skudata.reset_index(drop=True)
        cases=skudata[skudata.ReturnValue!=0]
        trueclaimcases=cases[cases.Code==6]
        trueclaimcases=trueclaimcases.reset_index(drop=True)
        for k in range(len(trueclaimcases)):
            list4.append([customer[i],sku[j],trueclaimcases['DeliveryDate'][k],trueclaimcases['SalePrice'][k],trueclaimcases['MarketPrice'][k],trueclaimcases['SalePrice'][k]-trueclaimcases['MarketPrice'][k]])
        



list1=pd.DataFrame(list1,columns=['CustomerName','Delivery Date','BilledQty','AfterTrueReturn','FulfilledQty','TotalSKUOrdered','OrderTime'])
list2=pd.DataFrame(list2,columns=['Customername','SKU','DeliveryDate','Salepricetoday','Avgsalepricelasttwodays','Claim'])
list3=pd.DataFrame(list3,columns=['CustomerName','SKU','Number of Cases','Total return Cases','Total fraud return cases'])
list4=pd.DataFrame(list4,columns=['Customername','SKU','DeliveryDate','Saleprice','MarketPrice','PriceDifference'])
writer=pd.ExcelWriter('report.xlsx')
list1.to_excel(writer,'MinimumQty or minimumSKU',index=False)
list2.to_excel(writer,'Steep Price Increase',index=False)
list3.to_excel(writer,'High NC Price',index=False)
list4.to_excel(writer,'Bad quality True Claim',index=False)
writer.save()



basketconstraint=[]
for i in range(len(list1)):
    if(list1['OrderTime'][i]=="ordered before 7:30"):
        if(list1['AfterTrueReturn'][i]>=50 and list1['FulfilledQty'][i]<50):
            basketconstraint.append([list1['CustomerName'][i],list1['Delivery Date'][i],list1['BilledQty'][i],list1['AfterTrueReturn'][i],list1['FulfilledQty'][i],list1['TotalSKUOrdered'][i],list1['OrderTime'][i]])
    else:
         if(list1['AfterTrueReturn'][i]>=25 and list1['FulfilledQty'][i]<25):
            basketconstraint.append([list1['CustomerName'][i],list1['Delivery Date'][i],list1['BilledQty'][i],list1['AfterTrueReturn'][i],list1['FulfilledQty'][i],list1['TotalSKUOrdered'][i],list1['OrderTime'][i]])
        
basketconstraint=pd.DataFrame(basketconstraint,columns=['CustomerName','Delivery Date','BilledQty','AfterTrueReturn','FulfilledQty','TotalSKUOrdered','OrderTime'])            
            
        
    






cases=raw_data[raw_data.DeliveryDate==datetoday]
returncases=cases[cases.ReturnValue!=0]
returncases=returncases.reset_index(drop=True)
returncases['ReasonGiven']=""
for i in range(len(returncases)):
    if(returncases['Code'][i]==4 or returncases['Code'][i]==5 or returncases['Code'][i]==7 or returncases['Code'][i]==9 or returncases['Code'][i]==12):
        if(returncases['SalePrice'][i]>1.2* returncases['MarketPrice'][i]):
            returncases['ReasonGiven'][i]="High NC Price"
        steeppricetoday=list2[list2.DeliveryDate==datetoday]
        steeppricetoday=steeppricetoday.reset_index(drop=True)
        for j in range(len(steeppricetoday)):
            if(steeppricetoday['Customername'][j]==returncases['CustomerName'][i] and steeppricetoday['SKU'][j]==returncases['SKU'][i]):
                if(returncases['ReasonGiven'][i]==""):
                    returncases['ReasonGiven'][i]="Steep Price Increase"
                else:
                    returncases['ReasonGiven'][i]="High NC Price, Steep price increase"
    


returncases=returncases[returncases.ReasonGiven!=""]
returncases=returncases.reset_index(drop=True)
final=[]
for i in range(len(returncases)):
    final.append([returncases['CustomerName'][i],returncases['SKU'][i],returncases['DeliveryDate'][i],returncases['ReasonGiven'][i]])


final=pd.DataFrame(final,columns=["CustomerName","SKU","DeliveryDate","ListingReason"])
workingfile=pd.ExcelWriter('Working File.xlsx')
basketconstraint.to_excel(workingfile,'CustomerLevel(BasketConstraint)',index=False)
final.to_excel(workingfile,'CustomerSKUlevel',index=False)
workingfile.save()







