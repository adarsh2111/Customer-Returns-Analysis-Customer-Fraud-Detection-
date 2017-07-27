# -*- coding: utf-8 -*-
"""
Created on Fri Jun 30 20:51:51 2017

@author: user
"""

#Python 3.6
import time
start_time=time.time()
import pandas as pd
import numpy as np
import os

os.chdir("C:\\Users\\user\\Desktop\\Ninjacart\\Returns Analysis(Customer Fraud Detection)")

raw_data=pd.read_csv("Returns2monthsDump-Master.csv")
raw_data=pd.DataFrame(raw_data)

os.chdir("C:\\Users\\user\\Desktop\\Ninjacart\\Returns Analysis(Customer Fraud Detection)\\Fraud Detection")
customerlist=[]
#Percentile Analysis
customer=raw_data.CustomerName.unique()
report=[]
for i in range(len(customer)):
    customerdata=raw_data[raw_data.CustomerName==customer[i]]
    customerdata=pd.DataFrame(customerdata)
    date=customerdata.DeliveryDate.unique()
    for j in range(len(date)):
        data=customerdata[customerdata.DeliveryDate==date[j]]
        data=pd.DataFrame(data)
        nsku=len(data)
        count_infavour=0
        count_fraud=0
        nreturn=0
        for k in data.index.values:
            if(data['ReturnQty'][k]!=0):
                nreturn=nreturn+1
                if(data.Code[k]==4 or data.Code[k]==5 or data.Code[k]==7 or data.Code[k]==9 or data.Code[k]==12):
                    count_fraud=count_fraud+1
                else:
                    count_infavour=count_infavour+1
        report.append([customer[i],date[j],nsku,nreturn,count_infavour,count_fraud])
report=pd.DataFrame(report,columns=['CustomerName','DeliveryDate','Number of SKU ordered','Total Returns','Returns in Favour','Fraud Return'])


customer=pd.DataFrame(customer)
returnlistCustWise=[]
for i in customer.index.values:
    customerdata=report[report.CustomerName==customer.ix[i].item()]
    customerdata=customerdata.reset_index(drop=True)
    norders=len(customerdata)
    n_fraud=len(customerdata[customerdata['Fraud Return']!=0])
    nreturn=len(customerdata[customerdata['Total Returns']!=0 ])
    if(norders!=0):
        returnlistCustWise.append([customer.ix[i].item(),norders,nreturn,n_fraud,n_fraud/norders,customerdata['DeliveryDate'][0],customerdata['DeliveryDate'][len(customerdata)-1]])
returnlistCustWise=pd.DataFrame(returnlistCustWise,columns=['CustomerName','Total Orders','Total Returns','Fraud Returns','Fraud Return%','First Order date','Last order date'])
returnlistCustWise.to_csv('ReturnListCustomerWise.csv',index=False)       


for i in range(len(returnlistCustWise)):
    if(returnlistCustWise['Total Orders'][i]>15):
        if(returnlistCustWise['Fraud Return%'][i]>np.percentile(returnlistCustWise['Fraud Return%'],80)):
            before_return=0
            after_return=0
            bv_truereturn=0
            customerdata=raw_data[raw_data.CustomerName==returnlistCustWise['CustomerName'][i]]
            for j in customerdata.index.values:
                before_return=before_return+customerdata['BilledQty'][j]*customerdata['SalePrice'][j]
                after_return=after_return+customerdata['FulfilledQty'][j]*customerdata['SalePrice'][j]
                if(customerdata['Code'][j]==4 or customerdata['Code'][j]==5 or customerdata['Code'][j]==7 or customerdata['Code'][j]==9 or customerdata['Code'][j]==12):
                    bv_truereturn=bv_truereturn+customerdata['BilledQty'][j]*customerdata['SalePrice'][j]
                else:
                    bv_truereturn=bv_truereturn+customerdata['FulfilledQty'][j]*customerdata['SalePrice'][j]
            FraudReturnValuepercent=(bv_truereturn-after_return)/before_return
            if(FraudReturnValuepercent>0.2):
                customerlist.append([returnlistCustWise['CustomerName'][i],"All","Percentile Analysis",returnlistCustWise['First Order date'][i],returnlistCustWise['Last order date'][i],returnlistCustWise['Total Orders'][i]])
        
        
        
#Basket Size analysis
orderdata=[]
customer=raw_data.CustomerName.unique()
for i in range (len(customer)):
    customerdata=raw_data[raw_data.CustomerName==customer[i]]
    customerdata=customerdata.reset_index(drop=True)
    date=customerdata.DeliveryDate.unique()
    orderdata.append([customer[i],customerdata['DeliveryDate'][0],customerdata['DeliveryDate'][len(customerdata)-1],len(date)])
orderdata=pd.DataFrame(orderdata,columns=['CustomerName','First Order Date','Last Order Date','Total Orders'])
date=raw_data.DeliveryDate.unique()
date=pd.DataFrame(date)
basketdata=[]
for i in date.index.values:
    datedata=raw_data[raw_data.DeliveryDate==date.ix[i].item()]
    datedata=pd.DataFrame(datedata)
    customer=datedata.CustomerName.unique()
    customer=pd.DataFrame(customer)
    for j in customer.index.values:
        customerdata=datedata[datedata.CustomerName==customer.ix[j].item()]
        customerdata=pd.DataFrame(customerdata)
        beforereturn=0
        afterreturn=0
        truereturn=0
        fraudreturn=0
        fraudreturnfactor=0
        truereturnfactor=0
        for k in customerdata.index.values:
            beforereturn=beforereturn + customerdata['BilledQty'][k]*customerdata['SalePrice'][k]
            afterreturn=afterreturn + (customerdata['BilledQty'][k]-customerdata['ReturnQty'][k])*customerdata['SalePrice'][k]
            if(customerdata['ReturnQty'][k]!=0):
                if(customerdata['Code'][k]==4 or customerdata['Code'][k]==5 or customerdata['Code'][k]==7 or customerdata['Code'][k]==9 or customerdata['Code'][k]==12):
                    fraudreturnfactor=fraudreturnfactor+customerdata['ReturnQty'][k]*customerdata['SalePrice'][k]
                else:
                    truereturnfactor=truereturnfactor+customerdata['ReturnQty'][k]*customerdata['SalePrice'][k]
        truereturn=beforereturn-truereturnfactor
        fraudreturn=beforereturn-(truereturnfactor+fraudreturnfactor)
        nreturn=0               
        nfraudreturn=0
        if(afterreturn<beforereturn):
            for k in customerdata.index.values:
                if(customerdata['ReturnQty'][k]!=0):
                    nreturn=nreturn+1
                    if(customerdata['Code'][k]==4 or customerdata['Code'][k]==5 or customerdata['Code'][k]==7 or customerdata['Code'][k]==9 or customerdata['Code'][k]==12 ):
                        nfraudreturn=nfraudreturn+1
        basketdata.append([date.ix[i].item(),customer.ix[j].item(),beforereturn,afterreturn,truereturn,fraudreturn,nreturn,nfraudreturn])

basketdata=pd.DataFrame(basketdata,columns=['DeliveryDate','CustomerName','Basket value before return','Basket value after return','Basket value after true return','Basket Vaue after false return','TotalReturn','Fraud Return'])


customer=basketdata.CustomerName.unique()
#Basket Value
for i in range(len(customer)):
    customerdata=basketdata[basketdata.CustomerName==customer[i]]
    date=customerdata.DeliveryDate.unique()
    norders=len(date)
    nreturns=norders
    nfraud=0
    if(norders>15):
        for j in range(len(date)):
            datedata=customerdata[customerdata.DeliveryDate==date[j]]
            for k in datedata.index.values:
                if(datedata['Basket value before return'][k]==datedata['Basket value after return'][k]):
                    nreturns=nreturns-1
                else:
                    if(datedata['Basket value after true return'][k]>=1000 and datedata['Basket Vaue after false return'][k]<1000):
                        if(datedata['Fraud Return'][k]!=0):
                            nfraud=nfraud+1
        fraudpercent=nfraud/norders
        if(fraudpercent>0.2):
            before_return=0
            after_return=0
            bv_truereturn=0
            customerdata=raw_data[raw_data.CustomerName==customer[i]]
            for j in customerdata.index.values:
                before_return=before_return+customerdata['BilledQty'][j]*customerdata['SalePrice'][j]
                after_return=after_return+customerdata['FulfilledQty'][j]*customerdata['SalePrice'][j]
                if(customerdata['Code'][j]==4 or customerdata['Code'][j]==5 or customerdata['Code'][j]==7 or customerdata['Code'][j]==9 or customerdata['Code'][j]==12):
                    bv_truereturn=bv_truereturn+customerdata['BilledQty'][j]*customerdata['SalePrice'][j]
                else:
                    bv_truereturn=bv_truereturn+customerdata['FulfilledQty'][j]*customerdata['SalePrice'][j]
            FraudReturnValuepercent=(bv_truereturn-after_return)/before_return
            if(FraudReturnValuepercent>0.2):
                firstorder=orderdata['First Order Date'][orderdata.CustomerName==customer[i]].reset_index(drop=True)
                lastorder=orderdata['Last Order Date'][orderdata.CustomerName==customer[i]].reset_index(drop=True)
                order=orderdata['Total Orders'][orderdata.CustomerName==customer[i]].reset_index(drop=True)
                customerlist.append([customer[i],"All","Basket Value",firstorder[0],lastorder[0],order[0]])
        
#Steep price increase
customer=raw_data.CustomerName.unique()
for i in range(len(customer)):
    customerdata=raw_data[raw_data.CustomerName==customer[i]]
    dates=customerdata.DeliveryDate.unique()
    sku=customerdata.SKU.unique()
    for j in range(len(sku)):
        skudata=customerdata[customerdata.SKU==sku[j]]
        skudata=skudata.reset_index(drop=True)
        date=skudata.DeliveryDate.unique()
        countcases=0
        countreturn=0
        countfraudreturn=0
        if(len(skudata)>=2):
            for k in range(2,len(skudata)):
                salepricetoday=skudata['SalePrice'][k]
                avgsalepricelasttwodays=(skudata['SalePrice'][k-1]+skudata['SalePrice'][k-2])/2
                percentrise=(salepricetoday-avgsalepricelasttwodays)/(avgsalepricelasttwodays)
                if(percentrise>0.2):
                   countcases=countcases+1
                   if(skudata['ReturnValue'][k]!=0):
                          countreturn=countreturn+1
                          if(skudata['Code'][k]==4 or skudata['Code'][k]==5 or skudata['Code'][k]==7 or skudata['Code'][k]==9 or skudata['Code'][k]==12):
                              countfraudreturn=countfraudreturn+1
            
            if(countcases>15):
                notreturned=countcases-countreturn
                if(countreturn>notreturned):
                    percentfraud=countfraudreturn/countreturn
                    if(percentfraud>0.5):
                        customerlist.append([customer[i],sku[j],"Steep Price Increase",skudata['DeliveryDate'][0],skudata['DeliveryDate'][len(skudata)-1],len(date)])

                
                        
                    
#SalesVsMarketPrice
customer=raw_data.CustomerName.unique()
for i in range(len(customer)):
    customerdata=raw_data[raw_data.CustomerName==customer[i]]
    customerdata=customerdata.reset_index(drop=True)
    sku=customerdata.SKU.unique()
    dates=customerdata.DeliveryDate.unique()
    for j in range(len(sku)):
        skudata=customerdata[customerdata.SKU==sku[j]]
        cases=skudata[skudata.MarketPrice<skudata.SalePrice]
        ncases=len(cases)
        if(ncases>15):                
            fraudcases=0
            returncases=cases[cases.ReturnValue!=0]
            if(len(returncases)>ncases-len(returncases)):
                for k in returncases.index.values:
                    if(returncases['Code'][k]==4 or returncases['Code'][k]==5 or returncases['Code'][k]==7 or returncases['Code'][k]==9 or returncases['Code'][k]==12):
                        fraudcases=fraudcases+1
                if(fraudcases/ncases>0.3 and fraudcases/len(returncases)>0.5):
                    customerlist.append([customer[i],sku[j],"Market Vs SalePrice Difference (logic based)",customerdata['DeliveryDate'][0],customerdata['DeliveryDate'][len(customerdata)-1],len(dates)])

#SalesVsMarketPrice
customer=raw_data.CustomerName.unique()
fraudmarketvssale=[]
for i in range(len(customer)):
    customerdata=raw_data[raw_data.CustomerName==customer[i]]
    customerdata=customerdata.reset_index(drop=True)
    sku=customerdata.SKU.unique()
    dates=customerdata.DeliveryDate.unique()
    for j in range(len(sku)):
        skudata=customerdata[customerdata.SKU==sku[j]]
        cases=skudata[skudata.MarketPrice<skudata.SalePrice]
        ncases=len(cases)
        if(ncases>15):                
            fraudcases=0
            returncases=cases[cases.ReturnValue!=0]
            if(len(returncases)>ncases-len(returncases)):
                for k in returncases.index.values:
                    if(returncases['Code'][k]==4 or returncases['Code'][k]==5 or returncases['Code'][k]==7 or returncases['Code'][k]==9 or returncases['Code'][k]==12):
                        fraudcases=fraudcases+1
                fraudmarketvssale.append([customer[i],sku[j],fraudcases/ncases,customerdata['DeliveryDate'][0],customerdata['DeliveryDate'][len(customerdata)-1],len(dates)])
                
fraudmarketvssale=pd.DataFrame(fraudmarketvssale,columns=["CustomerName","SKU","Fraud%","First Order Date","Last Order Date","Total Orders"])

for i in range(len(fraudmarketvssale)):
    if(fraudmarketvssale['Fraud%'][i]>np.percentile(fraudmarketvssale['Fraud%'],90)):
        customerlist.append([fraudmarketvssale['CustomerName'][i],fraudmarketvssale['SKU'][i],'MarketVsSalePriceDifference(PrcentileBased)',fraudmarketvssale['First Order Date'][i],fraudmarketvssale['Last Order Date'][i],fraudmarketvssale['Total Orders'][i]])

customerlist=pd.DataFrame(customerlist,columns=['CustomerName','SKU','Source','First Order Date','Last Order Date','Total Orders'])
customerlist.to_csv('customerlist.csv',index=False)


print((time.time()-start_time)/60)
