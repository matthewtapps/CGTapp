import datetime as dt
from dateutil.relativedelta import relativedelta
from enum import Enum
import xlrd
import pandas as pd
import re

pd.options.display.float_format = '{:,.2f}'.format

class TransactionType(Enum):
    Purchase = 1
    FIFO_Sale = 2
    Option_Sale = 3
    Split = 4
    Merge = 5
    Exercise = 6
    Expire = 7
    LIFO_Sale = 8
    HighestGain_Sale = 9
    LowestGain_Sale = 10

    def __lt__(self, other):
        custom_order = {
            TransactionType.Purchase: 1,
            TransactionType.FIFO_Sale: 2,
            TransactionType.Option_Sale: 3,
            TransactionType.Split: 4,
            TransactionType.Merge: 5,
            TransactionType.Exercise: 6,
            TransactionType.Expire: 7,
            TransactionType.LIFO_Sale: 8,
            TransactionType.HighestGain_Sale: 9,
            TransactionType.LowestGain_Sale: 10,
        }
        return custom_order[self] < custom_order[other]

    def __str__(self):
        return self.name

class AssetType(Enum):
    Option = 1
    Share = 2
    
    def __lt__(self, other):
        custom_order = {
            AssetType.Option: 1,
            AssetType.Share: 2,
        }
        return custom_order[self] < custom_order[other]
    
    def __str__(self):
        return self.name

class TransactionHistory():
    def __init__(self):
        self.transactions = pd.DataFrame(columns=['Date', 'AssetType', 'AssetID', 'TransactionType', 'Quantity', 'Value', 'OptionID', 'OptionSplitID'])
    
    def readData(self, transactions: pd.DataFrame):
        self.transactions = transactions
        self.transactions['AssetType'] = self.transactions['AssetType'].map(self.decodeAssetType)
        self.transactions['TransactionType'] = self.transactions.apply(lambda row: self.decodeTransactionType(row['TransactionType'], row['AssetType']), axis=1)
        self.transactions['Date'] = self.transactions['Date'].map(self.decodeDate)
        if type(self.transactions['Quantity'][0]) == str:
            self.transactions['Quantity'] = self.transactions['Quantity'].str.replace(',', '', regex=True).astype('float')
        else:
            self.transactions['Quantity'] = self.transactions['Quantity'].astype('float')
        if type(self.transactions['Value'][0]) == str:
            self.transactions['Value'] = self.transactions['Value'].str.replace(',', '', regex=True).astype('float')
        else:
            self.transactions['Value'] = self.transactions['Value'].astype('float')
        self.transactions.fillna('', inplace = True)
        self.transactions = self.sortByDate(self.transactions)
    
    def decodeAssetType(self, type: str) -> AssetType:
        type = type.lower()
        if type == 'share': 
            return AssetType.Share
        if type == 'option': 
            return AssetType.Option
        
        else: raise Exception('Asset type decoding error, check asset types are spelled correctly either  "Share" or "Option"')
    
    def decodeTransactionType(self, type: str, assetType: AssetType) -> pd.Series:
        type = type.lower()
        if type == 'purchase':
            return pd.Series([TransactionType.Purchase])
        if type == 'buy':
            return pd.Series([TransactionType.Purchase])
        elif type == 'fifosale':
            return pd.Series([TransactionType.FIFO_Sale])
        elif type == 'fifo_sale':
            return pd.Series([TransactionType.FIFO_Sale])
        elif type == 'lifosale':
            return pd.Series([TransactionType.LIFO_Sale])
        elif type == 'lifo_sale':
            return pd.Series([TransactionType.LIFO_Sale])
        elif type == 'sale':
            return pd.Series([TransactionType.Option_Sale if assetType == AssetType.Option else TransactionType.FIFO_Sale])
        elif type == 'sell':
            return pd.Series([TransactionType.Option_Sale if assetType == AssetType.Option else TransactionType.FIFO_Sale])
        elif type == 'sharesale':
            return pd.Series([TransactionType.FIFO_Sale])
        elif type == 'share_sale':
            return pd.Series([TransactionType.FIFO_Sale])
        elif type == 'optionsale':
            return pd.Series([TransactionType.Option_Sale])
        elif type == 'option_sale':
            return pd.Series([TransactionType.Option_Sale])
        elif type == 'merge':
            return pd.Series([TransactionType.Merge])
        elif type == 'split':
            return pd.Series([TransactionType.Split])
        elif type == 'exercise':
            return pd.Series([TransactionType.Exercise])
        elif type == 'expire':
            return pd.Series([TransactionType.Expire])
        elif type == 'expiry':
            return pd.Series([TransactionType.Expire])
        elif type == 'highest_gain_sale':
            return pd.Series([TransactionType.HighestGain_Sale])
        elif type == 'lowest_gain_sale':
            return pd.Series([TransactionType.LowestGain_Sale])
        else:
           raise Exception('Transaction type decoding error, check transaction types are spelled correctly in the input file')
    
    def decodeDate(self, date: str) -> dt.date:
        try:
            day, month, year = re.split('/|-', date)
            return dt.date(int(year), int(month), int(day))
        except ValueError:
            try:
                year, month, day = re.split('/|-', date)
                return dt.date(int(year), int(month), int(day))
            except:
                year, month, day, *rest = xlrd.xldate_as_tuple(int(float(date)), 0)
                return dt.date(year, month, day)
        except:
            raise Exception('Date formatting issue, please check date formats are either short date format "DD/MM/YYYY" or excel number format e.g., "44702"')

    def sortByDate(self, transactionListing: pd.DataFrame):
        return transactionListing.sort_values(['Date', 'AssetType'], ignore_index = True)
    
    def clearTransactions(self):
        self.transactions = pd.DataFrame(columns=['Date', 'AssetType', 'AssetID', 'TransactionType', 'Quantity', 'Value', 'OptionID', 'OptionSplitID'])
    
    def filterByDate(self, transactions: pd.DataFrame, startDate: dt.date | None = None, endDate: dt.date | None = None):
        filteredTransactions = transactions
        if (startDate) and (endDate):
            filteredTransactions = transactions[(transactions['Date'] >= startDate) & (transactions['Date'] <= endDate)]
        return filteredTransactions
    
class Portfolio:
    def __init__(self):
        self.assets = pd.DataFrame(columns=['AssetType', 'AssetIdentifier', 'PurchaseDate', 'Value', 'OptionID'])
        self.taxableTransactions = pd.DataFrame(columns=['Date', 'AssetID', 'AssetType', 'TransactionType', 'Quantity', 'AcquisitionDate', 'Proceeds', 'CostBase', 'GrossValue', 'Discountable'])
        self.optionExercises = {}
        
    def readTransactions(self, transactions: pd.DataFrame):
        for index, transaction in transactions.iterrows():
            transactionType = transaction['TransactionType']
            if transactionType == TransactionType.Purchase:
                self.purchase(transaction['AssetType'], transaction['AssetID'], transaction['Date'], transaction['Value'], transaction['Quantity'], transaction['OptionID'])
                
            elif transactionType == TransactionType.FIFO_Sale:
                new_row = pd.DataFrame(self.fifoSale(transaction['AssetType'], transaction['AssetID'], transaction['Date'], transaction['Value'], transaction['Quantity']))
                self.taxableTransactions = pd.concat(
                    [self.taxableTransactions, new_row], ignore_index = True)
            
            elif transactionType == TransactionType.LIFO_Sale:
                new_row = pd.DataFrame(self.lifoSale(transaction['AssetType'], transaction['AssetID'], transaction['Date'], transaction['Value'], transaction['Quantity']))
                self.taxableTransactions = pd.concat(
                    [self.taxableTransactions, new_row], ignore_index = True)
                        
            elif transactionType == TransactionType.Option_Sale:
                new_row = pd.DataFrame(self.optionSale(transaction['AssetType'], transaction['AssetID'], transaction['Date'], transaction['Value'], transaction['Quantity'], optionID = transaction['OptionID']))
                self.taxableTransactions = pd.concat(
                    [self.taxableTransactions, new_row], ignore_index = True)
            
            elif transactionType == TransactionType.Split:
                self.split(transaction['AssetType'], transaction['AssetID'], transaction['Date'], transaction['Value'] / transaction['Quantity'], transaction['Quantity'], transaction['OptionID'], transaction['OptionSplitID'] )
        
            elif transactionType == TransactionType.Merge:
                self.merge(transaction['AssetType'], transaction['AssetID'], transaction['Date'], transaction['Value'] / transaction['Quantity'], transaction['Quantity'], transaction['OptionID'], transaction['OptionSplitID'] )
        
            elif transactionType == TransactionType.Exercise:
                self.exercise(transaction['AssetType'], transaction['AssetID'], transaction['Date'], transaction['Value'] / transaction['Quantity'], transaction['Quantity'], transaction['OptionID'])

            elif transactionType == TransactionType.Expire:
                new_row = pd.DataFrame(self.expire(transaction['AssetType'], transaction['AssetID'], transaction['Date'], transaction['Value'] / transaction['Quantity'], transaction['Quantity'], transaction['OptionID']))
                self.taxableTransactions = pd.concat(
                    [self.taxableTransactions, new_row], ignore_index = True)
                
            elif transactionType == TransactionType.HighestGain_Sale:
                self.highestGainSale(transaction['AssetType'], transaction['AssetID'], transaction['Date'], transaction['Value'], transaction['Quantity'])

            elif transactionType == TransactionType.LowestGain_Sale:
                self.lowestGainSale(transaction['AssetType'], transaction['AssetID'], transaction['Date'], transaction['Value'], transaction['Quantity'])

            #else: raise Exception(f"{transaction['Date']} Transaction type error, please check transaction type")

    def purchase(self, assetType: AssetType, assetIdentifier: str, purchaseDate: dt.date, value: float, quantity: float, optionID: str | None = None):
        shares = []
        for _ in range(int(quantity)):
            shares.append({'AssetType': assetType,
            'AssetIdentifier': assetIdentifier,
            'PurchaseDate': purchaseDate,
            'Value': value / quantity,
            'OptionID' : optionID
            })
        new_rows = pd.DataFrame(shares)
        self.assets = pd.concat([self.assets, new_rows], ignore_index=True)
        self.assets.fillna('', inplace = True)
    
    def fifoSale(self, assetType: AssetType, assetIdentifier: str, date: dt.date, value: float, quantity: float) -> list:
        assert assetType == AssetType.Share, "FIFO sale transaction type called on option, options can only be sold specifically by ID - please check transaction types for validity"
        saleShares = self.assets[(self.assets['AssetType'] == assetType) & (self.assets['AssetIdentifier'] == assetIdentifier)].head(int(quantity))
        groups = saleShares.groupby('PurchaseDate')
        transactions = []
        for purchaseDate, group in groups:
            groupQuantity = len(group)
            groupCostBase = group['Value'].sum()
            groupProceeds = (value / quantity) * groupQuantity
            groupGrossValue = groupProceeds - groupCostBase
            acquisitionDate = group['PurchaseDate'].max()
            discountable = False
            if (date - relativedelta(years=1) > acquisitionDate) & (groupGrossValue > 0) : discountable = True
            if groupGrossValue < 0: discountable = 'Loss'
            transactions.append({
                'Date': date, 
                'AssetID': assetIdentifier, 
                'AssetType': assetType,
                'TransactionType': TransactionType.FIFO_Sale, 
                'Quantity': groupQuantity, 
                'AcquisitionDate': acquisitionDate, 
                'Proceeds': groupProceeds, 
                'CostBase': groupCostBase, 
                'GrossValue': groupGrossValue, 
                'Discountable': discountable
            })
        self.assets.drop(saleShares.index, inplace=True)
        self.assets.reset_index(drop=True, inplace=True)
        return transactions
            
    def optionSale(self, assetType: AssetType, assetIdentifier: str, date: dt.date, value: float, quantity: float, optionID: str):
        assert assetType == AssetType.Option, "Option sale transaction type called on share, please check transaction types for validity"
        saleOptions = self.assets[(self.assets['AssetType'] == assetType) 
                & (self.assets['AssetIdentifier'] == assetIdentifier) 
                & (self.assets['OptionID'] == optionID)].head(int(quantity))
        costBase = saleOptions['Value'].sum()
        grossValue = value - costBase
        acquisitionDate = saleOptions['PurchaseDate'].max()
        discountable = False
        if (date - relativedelta(years=1) > acquisitionDate) & (grossValue > 0) : discountable = True
        if grossValue < 0: discountable = 'Loss'
        transaction = [{
                'Date': date, 
                'AssetID': assetIdentifier,
                'AssetType': assetType,
                'TransactionType': TransactionType.Option_Sale, 
                'Quantity': quantity, 
                'AcquisitionDate': acquisitionDate, 
                'Proceeds': value, 
                'CostBase': costBase, 
                'GrossValue': grossValue, 
                'Discountable': discountable
            }]
        self.assets.drop(saleOptions.index, inplace=True)
        self.assets.reset_index(drop=True, inplace=True)
        return transaction
            
    def split(self, assetType: AssetType, assetIdentifier: str, date: dt.date, value: float, splitRatio: float, optionID: str | None = None, splitOptionID: str | None = None):
        if assetType == AssetType.Share:
            splitShares = self.assets[(self.assets['AssetType'] == assetType) & (self.assets['AssetIdentifier'] == assetIdentifier)]
            groups = splitShares.groupby('PurchaseDate')
            for purchaseDate, group in groups:
                groupQuantity = len(group)
                groupValue = group['Value'].sum()
                acquisitionDate = group['PurchaseDate'].max()
                self.purchase(assetType, assetIdentifier, acquisitionDate, groupValue, groupQuantity * splitRatio)
            self.assets.drop(splitShares.index, inplace=True)
            self.assets.reset_index(drop=True, inplace=True)
        
        if assetType == AssetType.Option:
            splitOptions = self.assets[(self.assets['AssetType'] == assetType) & (self.assets['AssetIdentifier'] == assetIdentifier) & (self.assets['OptionID'] == optionID)]
            quantity = len(splitOptions)
            value = splitOptions['Value'].sum()
            acquisitionDate = splitOptions['PurchaseDate'].max()
            self.purchase(assetType, assetIdentifier, acquisitionDate, value, quantity * splitRatio, splitOptionID)
            self.assets.drop(splitOptions.index, inplace=True)
            self.assets.reset_index(drop=True, inplace=True)

    def exercise(self, assetType: AssetType, assetIdentifier: str, date: dt.date, value: float, quantity: float, optionID: str):
        if assetType == AssetType.Option:
            exercisedOptions = self.assets[(self.assets['AssetType'] == assetType) 
                                & (self.assets['AssetIdentifier'] == assetIdentifier) 
                                & (self.assets['OptionID'] == optionID)].head(int(quantity))
            acquisitionDate = exercisedOptions['PurchaseDate'].min()
            value = exercisedOptions['Value'].sum()
            self.optionExercises.update({optionID : (value, acquisitionDate)})
            self.assets.drop(exercisedOptions.index, inplace=True)
            self.assets.reset_index(drop=True, inplace=True)
        if assetType == AssetType.Share:
            value = self.optionExercises[optionID][0] + value
            acquisitionDate = self.optionExercises[optionID][1]
            del self.optionExercises[optionID]
            self.purchase(assetType, assetIdentifier, acquisitionDate, value, quantity)
            
    def expire(self, assetType: AssetType, assetIdentifier: str, date: dt.date, value: float, quantity: float, optionID: str):
        assert assetType == AssetType.Option, f"{date} Share listed with Expire transaction type, please check transaction types"
        expiredOptions = self.assets[(self.assets['AssetType'] == assetType) & (self.assets['AssetIdentifier'] == assetIdentifier) & (self.assets['OptionID'] == optionID)]
        costBase = expiredOptions['Value'].sum()
        acquisitionDate = expiredOptions['PurchaseDate'].max()
        grossValue = value - costBase
        discountable = 'Loss'
        transaction = [{
                'Date': date, 
                'AssetID': assetIdentifier,
                'AssetType': assetType,
                'TransactionType': TransactionType.Expire, 
                'Quantity': quantity, 
                'AcquisitionDate': acquisitionDate, 
                'Proceeds': value, 
                'CostBase': costBase, 
                'GrossValue': grossValue, 
                'Discountable': discountable
            }]
        self.assets.drop(expiredOptions.index, inplace=True)
        self.assets.reset_index(drop=True, inplace=True)
        return transaction
    
    def merge(self, assetType: AssetType, assetIdentifier: str, date: dt.date, value: float, mergeRatio: float, optionID: str | None = None, splitOptionID: str | None = None):
        if assetType == AssetType.Share:
            mergeShares = self.assets[(self.assets['AssetType'] == assetType) & (self.assets['AssetIdentifier'] == assetIdentifier)]
            groups = mergeShares.groupby('PurchaseDate')
            for purchaseDate, group in groups:
                groupQuantity = len(group)
                groupValue = group['Value'].sum()
                acquisitionDate = group['PurchaseDate'].max()
                self.purchase(assetType, assetIdentifier, acquisitionDate, groupValue, groupQuantity / mergeRatio)
            self.assets.drop(mergeShares.index, inplace=True)
            self.assets.reset_index(drop=True, inplace=True)
        
        if assetType == AssetType.Option:
            mergeOptions = self.assets[(self.assets['AssetType'] == assetType) & (self.assets['AssetIdentifier'] == assetIdentifier) & (self.assets['OptionID'] == optionID)]
            quantity = len(mergeOptions)
            value = mergeOptions['Value'].sum()
            acquisitionDate = mergeOptions['PurchaseDate'].max()
            self.purchase(assetType, assetIdentifier, acquisitionDate, value, quantity / mergeRatio, splitOptionID)
            self.assets.drop(mergeOptions.index, inplace=True)
            self.assets.reset_index(drop=True, inplace=True)
            
    def lifoSale(self, assetType: AssetType, assetIdentifier: str, date: dt.date, value: float, quantity: float) -> list:
        assert assetType == AssetType.Share, "FIFO sale transaction type called on option, options can only be sold specifically by ID - please check transaction types for validity"
        saleShares = self.assets[(self.assets['AssetType'] == assetType) & (self.assets['AssetIdentifier'] == assetIdentifier)].tail(int(quantity))
        groups = saleShares.groupby('PurchaseDate')
        transactions = []
        for purchaseDate, group in groups:
            groupQuantity = len(group)
            groupCostBase = group['Value'].sum()
            groupProceeds = (value / quantity) * groupQuantity
            groupGrossValue = groupProceeds - groupCostBase
            acquisitionDate = group['PurchaseDate'].max()
            discountable = False
            if (date - relativedelta(years=1) > acquisitionDate) & (groupGrossValue > 0) : discountable = True
            if groupGrossValue < 0: discountable = 'Loss'
            transactions.append({
                'Date': date, 
                'AssetID': assetIdentifier, 
                'AssetType': assetType,
                'TransactionType': TransactionType.LIFO_Sale, 
                'Quantity': groupQuantity, 
                'AcquisitionDate': acquisitionDate, 
                'Proceeds': groupProceeds, 
                'CostBase': groupCostBase, 
                'GrossValue': groupGrossValue, 
                'Discountable': discountable
            })
        self.assets.drop(saleShares.index, inplace=True)
        self.assets.reset_index(drop=True, inplace=True)
        return transactions
    
    def highestGainSale(self, assetType: AssetType, assetIdentifier: str, date: dt.date, value: float, quantity: float):
        assert assetType == AssetType.Share, "Highest gain sale transaction type called on option, options can only be sold specifically by ID - please check transaction types for validity"
        saleShares = self.assets[(self.assets['AssetType'] == assetType) & (self.assets['AssetIdentifier'] == assetIdentifier)].sort_values(['Value']).head(int(quantity))
        groups = saleShares.groupby('PurchaseDate')
        transactions = []
        for purchaseDate, group in groups:
            groupQuantity = len(group)
            groupCostBase = group['Value'].sum()
            groupProceeds = (value / quantity) * groupQuantity
            groupGrossValue = groupProceeds - groupCostBase
            acquisitionDate = group['PurchaseDate'].max()
            discountable = False
            if (date - relativedelta(years=1) > acquisitionDate) & (groupGrossValue > 0) : discountable = True
            if groupGrossValue < 0: discountable = 'Loss'
            transactions.append({
                'Date': date, 
                'AssetID': assetIdentifier, 
                'AssetType': assetType,
                'TransactionType': TransactionType.HighestGain_Sale, 
                'Quantity': groupQuantity, 
                'AcquisitionDate': acquisitionDate, 
                'Proceeds': groupProceeds, 
                'CostBase': groupCostBase, 
                'GrossValue': groupGrossValue, 
                'Discountable': discountable
            })
        self.assets.drop(saleShares.index, inplace=True)
        self.assets.reset_index(drop=True, inplace=True)
        return transactions

    def lowestGainSale(self, assetType: AssetType, assetIdentifier: str, date: dt.date, value: float, quantity: float):
        assert assetType == AssetType.Share, "Lowest gain sale transaction type called on option, options can only be sold specifically by ID - please check transaction types for validity"
        calcPortfolio = self.assets[(self.assets['AssetType'] == assetType) & (self.assets['AssetIdentifier'] == assetIdentifier)]
        proceedsPerShare = value / quantity
        calcPortfolio['NetGain'] = proceedsPerShare - calcPortfolio['Value']
        calcPortfolio['NetGain'] = calcPortfolio.apply(
            lambda row: row['NetGain'] / 2 if (date - row['PurchaseDate']).days > 365 else row['NetGain'],
            axis=1
        )
        saleShares = calcPortfolio.sort_values(by=['NetGain']).head(int(quantity))
        groups = saleShares.groupby('PurchaseDate')
        transactions = []
        for purchaseDate, group in groups:
            groupQuantity = len(group)
            groupCostBase = group['Value'].sum()
            groupProceeds = (value / quantity) * groupQuantity
            groupGrossValue = groupProceeds - groupCostBase
            acquisitionDate = group['PurchaseDate'].max()
            discountable = False
            if (date - relativedelta(years=1) > acquisitionDate) & (groupGrossValue > 0) : discountable = True
            if groupGrossValue < 0: discountable = 'Loss'
            transactions.append({
                'Date': date, 
                'AssetID': assetIdentifier, 
                'AssetType': assetType,
                'TransactionType': TransactionType.LowestGain_Sale, 
                'Quantity': groupQuantity, 
                'AcquisitionDate': acquisitionDate, 
                'Proceeds': groupProceeds, 
                'CostBase': groupCostBase, 
                'GrossValue': groupGrossValue, 
                'Discountable': discountable
            })
        self.assets.drop(saleShares.index, inplace=True)
        self.assets.reset_index(drop=True, inplace=True)
        return transactions

    def clearAssets(self):
        self.assets = pd.DataFrame(columns=['AssetType', 'AssetIdentifier', 'PurchaseDate', 'Value', 'OptionID'])
    
    def clearTaxabaleTransactions(self):
        self.taxableTransactions = pd.DataFrame(columns=['Date', 'AssetID', 'AssetType', 'TransactionType', 'Quantity', 'AcquisitionDate', 'Proceeds', 'CostBase', 'GrossValue', 'Discountable'])
      
    def filterTaxTransactions(self, taxTransactions: pd.DataFrame, startDate: dt.date | None = None, endDate: dt.date | None = None, consolidationLevel: int | None = None) -> pd.DataFrame:
        if consolidationLevel == 1:
            consolidation = ['Date', 'AssetID', 'AssetType', 'Discountable']
        elif consolidationLevel == 2:
            consolidation = ['AssetID', 'AssetType', 'Discountable']
        else:
            consolidation = []

        if startDate and endDate and consolidationLevel:
            filteredTransactions = taxTransactions[(taxTransactions['Date'] >= startDate) & (taxTransactions['Date'] <= endDate)]
            filteredTransactions = filteredTransactions.groupby(consolidation).aggregate({'Quantity' : 'sum', 'Proceeds': 'sum', 'CostBase': 'sum', 'GrossValue' : 'sum'})
        elif (startDate and endDate) and not consolidationLevel:
            filteredTransactions = taxTransactions[(taxTransactions['Date'] >= startDate) & (taxTransactions['Date'] <= endDate)]
        elif consolidationLevel and (not startDate or not endDate):
            filteredTransactions = taxTransactions.groupby(consolidation).aggregate({'Quantity' : 'sum', 'Proceeds': 'sum', 'CostBase': 'sum', 'GrossValue' : 'sum'})
        else: 
            return taxTransactions
                
        filteredTransactions = filteredTransactions.reset_index(drop=True) if not consolidationLevel else filteredTransactions.reset_index()
    
        if 'Discountable' in filteredTransactions.columns:
            filteredTransactions = filteredTransactions[[c for c in filteredTransactions if c != 'Discountable'] + ['Discountable']]

        return filteredTransactions
    
    def consolidatePortfolio(self):
        df = self.assets.groupby(['AssetIdentifier', 'AssetType',  'OptionID', 'PurchaseDate']).agg({'Value' : 'sum'}).reset_index()

        quantity_series = self.assets.groupby(['AssetIdentifier', 'AssetType',  'OptionID', 'PurchaseDate']).size()
        df.insert(4, 'Quantity', quantity_series.values) # type: ignore

        df['PurchaseDate'] = pd.to_datetime(df['PurchaseDate']).dt.date

        current_date = dt.date.today()
        
        df['date_difference'] = ((current_date.year - df['PurchaseDate'].map(lambda x: x.year)) * 12 + 
                                (current_date.month - df['PurchaseDate'].map(lambda x: x.month)))
        
        
        df['Discountable'] = df['date_difference'] > 12

        df = df.drop(columns='date_difference')

        df.insert(6, 'Discountable', df.pop('Discountable'))

        return df