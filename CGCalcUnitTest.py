import unittest
import datetime as dt
from pandasCGcalc import Portfolio, AssetType

class PortfolioTestCase(unittest.TestCase):
    def setUp(self):
        self.portfolio = Portfolio()
        
    def test_sharePurchase(self):
        """
        Confirms assets are added to the register with the expected
        values, quantity and IDs
        """
        assetType = AssetType.Share
        assetIdentifier = 'TEST'
        purchaseDate = dt.date(2022, 3, 30)
        value = 10000.00
        quantity = 10.00
        optionID = None
        splitOptionID = None
        self.portfolio.purchase(
            assetType,
            assetIdentifier,
            purchaseDate,
            value,
            quantity,
            optionID
        )
        assert len(self.portfolio.assets) == 10, "share purchase() failed test: quantity does not match expected value"
        assert self.portfolio.assets['Value'].sum() == value, "share purchase() failed test: portfolio value does not match expected value"
        assert self.portfolio.assets['AssetIdentifier'][0] == assetIdentifier,  "share purchase() failed test: assetID does not match expected value"

    def standardSharePurchase(self, value: float, quantity: float, purchaseDate: dt.date):
        """
        Standard purchase to use in tests to avoid code
        duplication
        """
        assetType = AssetType.Share
        assetIdentifier = 'TEST'
        self.portfolio.purchase(
            assetType,
            assetIdentifier,
            purchaseDate,
            value,
            quantity
        )

    def test_fifoSale1(self):
        """
        Confirms fifosale is functioning correctly and removing assets from the
        register after sale as expected
        """
        self.standardSharePurchase(value = 10000.00, quantity = 10.00, purchaseDate = dt.date(2022, 3, 30))
        purchaseDate = dt.date(2022, 3, 30) # expected purchaseDate from standardPurchase
        
        # Begin fifoSale test case:
        assetType = AssetType.Share
        assetIdentifier = 'TEST'
        saleDate = dt.date(2023, 4, 1)
        value = 10000.00
        quantity = 5.00
        testValues = self.portfolio.fifoSale(
            assetType,
            assetIdentifier,
            saleDate,
            value,
            quantity
        )
        assert len(self.portfolio.assets) == 5, "fifoSale() failed test 1: quantity does not match expected value"
        assert self.portfolio.assets['Value'].sum() == 5000.00, "fifoSale() failed test 1: remaining portfolio value does not match expected value"
        assert testValues[0]['CostBase'] == 5000.00, "fifoSale() failed test 1: cost base of transaction output does not match expected value"
        assert testValues[0]['Date'] == saleDate, "fifoSale() failed test 1: date of transaction output does not match expected value"
        assert testValues[0]['Quantity'] == 5.00, "fifoSale() failed test 1: quantity of transaction output does not match expected value"
        assert testValues[0]['AcquisitionDate'] == purchaseDate, "fifoSale() failed test 1: acquisition date of transaction output does not match expected value"
        assert testValues[0]['Proceeds'] == 10000.00, "fifoSale() failed test 1: proceeds of transaction output does not match expected value"
        assert testValues[0]['GrossValue'] == 5000.00, "fifoSale() failed test 1: gross value of transaction output does not match expected value"
        assert testValues[0]['Discountable'] == True, "fifoSale() failed test 1: discountable (bool) of transaction output does not match expected value"

    def test_fifoSale2(self):
        """
        Uses two standard purchases with different dates
        Confirms that fifosale is selling the earliest acquisition of
        shares first by assessing purchase date of shares on hand after sale
        as well as confirming expected value and quantity on hand
        """
        self.standardSharePurchase(value = 10000.00, quantity = 10.00, purchaseDate = dt.date(2022, 3, 30))
        self.standardSharePurchase(value = 10000.00, quantity = 10.00, purchaseDate = dt.date(2022, 4, 30)) # Purchase later than first purchase
        purchaseDate = dt.date(2022, 3, 30) # expected purchaseDate from first standardPurchase
        
        # Begin fifoSale test case:
        assetType = AssetType.Share
        assetIdentifier = 'TEST'
        saleDate = dt.date(2023, 4, 1)
        value = 10000.00
        quantity = 5.00 # five shares sold from first parcel of shares, remaining quantity: 5, remaining cost base: 5,000
        testValues = self.portfolio.fifoSale(
            assetType,
            assetIdentifier,
            saleDate,
            value,
            quantity
        )
        assert len(self.portfolio.assets) == 15, "fifoSale() failed test 2: quantity does not match expected value"
        assert self.portfolio.assets['Value'].sum() == 15000.00, "fifoSale() failed test 2: remaining portfolio value does not match expected value"
        assert testValues[0]['CostBase'] == 5000.00, "fifoSale() failed test 2: cost base of transaction output does not match expected value"
        assert testValues[0]['Date'] == saleDate, "fifoSale() failed test 2: date of transaction output does not match expected value"
        assert testValues[0]['Quantity'] == 5.00, "fifoSale() failed test 2: quantity of transaction output does not match expected value"
        assert testValues[0]['AcquisitionDate'] == purchaseDate, "fifoSale() failed test 2: acquisition date of transaction output does not match expected value"
        assert testValues[0]['Proceeds'] == 10000.00, "fifoSale() failed test 2: proceeds of transaction output does not match expected value"
        assert testValues[0]['GrossValue'] == 5000.00, "fifoSale() failed test 2: gross value of transaction output does not match expected value"
        assert testValues[0]['Discountable'] == True, "fifoSale() failed test 2: discountable (bool) of transaction output does not match expected value"
        dateGroups = self.portfolio.assets.groupby('PurchaseDate')
        assert len(dateGroups) == 2, "fifoSale() failed test 2: number of purchase dates present in portfolio does not match expected value"
        testParcels = []
        for purchaseDate, group in self.portfolio.assets.groupby('PurchaseDate'):
            testParcels.append((len(group), group['Value'].sum()))
        assert testParcels[0][0] == 5.00, "fifoSale() failed test 2: remaining shares in first parcel does not match expected value"
        assert testParcels[1][0] == 10.00, "fifoSale() failed test 2: remaining shares in second parcel does not match expected value"
        assert testParcels[0][1] == 5000.00, "fifoSale() failed test 2: cost base of shares in first parcel does not match expected value"
        assert testParcels[1][1] == 10000.00, "fifoSale() failed test 2: cost base of shares in second parcel does not match expected value"

    def test_shareSplit(self):
        """
        Test split for shares using standard purchase confirmed in test_purchase
        Confirms correct amount of shares with correct value are present in asset
        register following split, and that purchase date has been carried over
        to new shares correctly
        """
        self.standardSharePurchase(value = 10000.00, quantity = 10.00, purchaseDate = dt.date(2022, 3, 30))
        purchaseDate = dt.date(2022, 3, 30) # expected purchaseDate from standardPurchase
        assetType = AssetType.Share
        assetIdentifier = 'TEST'
        splitDate = dt.date(2023, 4, 1)
        value = 0.00
        splitRatio = 2.00
        self.portfolio.split(
            assetType,
            assetIdentifier,
            splitDate,
            value,
            splitRatio            
        )
        assert len(self.portfolio.assets) == 20, "split() shares failed test: quantity does not match expected value"
        assert self.portfolio.assets['Value'].sum() == 10000.00, "split() shares failed test: remaining portfolio value does not match expected value"
        assert self.portfolio.assets['PurchaseDate'][0] == purchaseDate, "split() shares failed test: purchase date of shares post-split does not match original purchase date from standardPurchase"
    
    def test_optionPurchase(self):
        """
        Confirm option purchase is functioning correctly,
        with correct quantity and total value being added to the asset 
        portfolio with correct asset ID and option ID
        """
        assetType = AssetType.Option
        assetIdentifier = 'TEST'
        purchaseDate = dt.date(2022, 3, 30)
        value = 10000.00
        quantity = 10.00
        optionID = 'TEST1'
        splitOptionID = None
        self.portfolio.purchase(
            assetType,
            assetIdentifier,
            purchaseDate,
            value,
            quantity,
            optionID
        )
        assert len(self.portfolio.assets) == 10, "option purchase() failed test: quantity does not match expected value"
        assert self.portfolio.assets['Value'].sum() == value, "option purchase() failed test: value does not match expected value"
        assert self.portfolio.assets['AssetIdentifier'][0] == assetIdentifier,  "option purchase() failed test: assetID does not match expected value"
        assert self.portfolio.assets['OptionID'][0] == optionID,  "option purchase() failed test: optionID does not match expected value"
       
    def standardOptionPurchase(self, value: float, quantity: float, purchaseDate: dt.date, optionID: str):
        """
        Standard option purchase to be called in tests to avoid
        code duplication
        """
        assetType = AssetType.Option
        assetIdentifier = 'TEST'
        splitOptionID = None
        self.portfolio.purchase(
            assetType,
            assetIdentifier,
            purchaseDate,
            value,
            quantity,
            optionID
        )
    
    def test_optionSale(self):
        """
        Confirms optionSale is functioning correctly, with intended options
        removed from the asset register after the sale, and that the function
        returns the expected values to be added to the transaction register
        """
        self.standardOptionPurchase(value = 10000.00, quantity = 10.00, purchaseDate = dt.date(2022, 3, 30), optionID = 'TEST1')
        purchaseDate = dt.date(2022, 3, 30) # expected purchaseDate from standardPurchase
        
        # Begin optionSale test case:
        assetType = AssetType.Option
        assetIdentifier = 'TEST'
        saleDate = dt.date(2023, 4, 1)
        value = 10000.00
        quantity = 5.00
        optionID = 'TEST1'
        testValues = self.portfolio.optionSale(
            assetType,
            assetIdentifier,
            saleDate,
            value,
            quantity,
            optionID
        )
        assert len(self.portfolio.assets) == 5, "optionSale() failed test: quantity does not match expected value"
        assert self.portfolio.assets['Value'].sum() == 5000.00, "optionSale() failed test: remaining portfolio value does not match expected value"
        assert testValues[0]['CostBase'] == 5000.00, "optionSale() failed test: cost base of transaction output does not match expected value"
        assert testValues[0]['Date'] == saleDate, "optionSale() failed test: date of transaction output does not match expected value"
        assert testValues[0]['Quantity'] == 5.00, "optionSale() failed test: quantity of transaction output does not match expected value"
        assert testValues[0]['AcquisitionDate'] == purchaseDate, "optionSale() failed test: acquisition date of transaction output does not match expected value"
        assert testValues[0]['Proceeds'] == 10000.00, "optionSale() failed test: proceeds of transaction output does not match expected value"
        assert testValues[0]['GrossValue'] == 5000.00, "optionSale() failed test: gross value of transaction output does not match expected value"
        assert testValues[0]['Discountable'] == True, "optionSale() failed test: discountable (bool) of transaction output does not match expected value"

    def test_optionSplit(self):
        """
        Test split for options using standard purchase confirmed in test_purchase
        Confirms options have split correctly, with expected quantity and value 
        of options after the split
        """
        self.standardOptionPurchase(value = 10000.00, quantity = 10.00, purchaseDate = dt.date(2022, 3, 30), optionID = 'TEST1')
        purchaseDate = dt.date(2022, 3, 30) # expected purchaseDate from standardPurchase
        assetType = AssetType.Option
        assetIdentifier = 'TEST'
        splitDate = dt.date(2023, 4, 1)
        value = 0.00
        splitRatio = 2.00
        optionID = 'TEST1'
        splitOptionID = 'TEST2'
        self.portfolio.split(
            assetType,
            assetIdentifier,
            splitDate,
            value,
            splitRatio,
            optionID,
            splitOptionID
        )
        assert len(self.portfolio.assets) == 20, "split() options failed test: quantity does not match expected value"
        assert self.portfolio.assets['Value'].sum() == 10000.00, "split() options failed test: remaining portfolio value does not match expected value"
        assert self.portfolio.assets['PurchaseDate'][0] == purchaseDate, "split() options failed test: purchase date of shares post-split does not match original purchase date from standardPurchase"
        assert self.portfolio.assets['OptionID'][0] == splitOptionID, "split() options failed test: purchase date of shares post-split does not match original purchase date from standardPurchase"

    def test_shareMerge(self):
        """
        Test merge for shares using standard purchase confirmed in test_purchase
        Confirms shares have merged correctly, with expected quantity and value 
        of shares after the merge
        """
        self.standardSharePurchase(value = 10000.00, quantity = 10.00, purchaseDate = dt.date(2022, 3, 30))
        purchaseDate = dt.date(2022, 3, 30) # expected purchaseDate from standardPurchase
        assetType = AssetType.Share
        assetIdentifier = 'TEST'
        splitDate = dt.date(2023, 4, 1)
        value = 0.00
        mergeRatio = 2.00
        self.portfolio.merge(
            assetType,
            assetIdentifier,
            splitDate,
            value,
            mergeRatio
        )
        assert len(self.portfolio.assets) == 5, "merge() shares failed test: quantity does not match expected value"
        assert self.portfolio.assets['Value'].sum() == 10000.00, "merge() shares failed test: remaining portfolio value does not match expected value"
        assert self.portfolio.assets['PurchaseDate'][0] == purchaseDate, "merge() shares failed test: purchase date of shares post-split does not match original purchase date from standardPurchase"
    
    def test_optionMerge(self):
        """
        Test merge for options using standard purchase confirmed in test_purchase
        Confirms options have merged correctly, with expected quantity and value 
        of options after the merge
        """
        self.standardOptionPurchase(value = 10000.00, quantity = 10.00, purchaseDate = dt.date(2022, 3, 30), optionID = 'TEST1')
        purchaseDate = dt.date(2022, 3, 30) # expected purchaseDate from standardPurchase
        assetType = AssetType.Option
        assetIdentifier = 'TEST'
        mergeDate = dt.date(2023, 4, 1)
        value = 0.00
        mergeRatio = 2.00
        optionID = 'TEST1'
        mergeOptionID = 'TEST2'
        self.portfolio.merge(
            assetType,
            assetIdentifier,
            mergeDate,
            value,
            mergeRatio,
            optionID,
            mergeOptionID
        )
        assert len(self.portfolio.assets) == 5, "merge() options failed test: quantity does not match expected value"
        assert self.portfolio.assets['Value'].sum() == 10000.00, "merge() options failed test: remaining portfolio value does not match expected value"
        assert self.portfolio.assets['PurchaseDate'][0] == purchaseDate, "merge() options failed test: purchase date of shares post-split does not match original purchase date from standardPurchase"
        assert self.portfolio.assets['OptionID'][0] == mergeOptionID, "merge() options failed test: purchase date of shares post-split does not match original purchase date from standardPurchase"

    def test_lifoSale1(self):
        """
        lifoSale test using the standard purchase that is confirmed in test_purchase
        Confirms that lifoSale is functioning correctly and deleting assets from the register
        as intended
        """
        self.standardSharePurchase(value = 10000.00, quantity = 10.00, purchaseDate = dt.date(2022, 3, 30))
        purchaseDate = dt.date(2022, 3, 30) # expected purchaseDate from standardPurchase
        
        # Begin lifoSale test case:
        assetType = AssetType.Share
        assetIdentifier = 'TEST'
        saleDate = dt.date(2023, 4, 1)
        value = 10000.00
        quantity = 5.00
        testValues = self.portfolio.lifoSale(
            assetType,
            assetIdentifier,
            saleDate,
            value,
            quantity
        )
        assert len(self.portfolio.assets) == 5, "lifoSale() failed test 1: quantity does not match expected value"
        assert self.portfolio.assets['Value'].sum() == 5000.00, "lifoSale() failed test 1: remaining portfolio value does not match expected value"
        assert testValues[0]['CostBase'] == 5000.00, "lifoSale() failed test 1: cost base of transaction output does not match expected value"
        assert testValues[0]['Date'] == saleDate, "lifoSale() failed test 1: date of transaction output does not match expected value"
        assert testValues[0]['Quantity'] == 5.00, "lifoSale() failed test 1: quantity of transaction output does not match expected value"
        assert testValues[0]['AcquisitionDate'] == purchaseDate, "lifoSale() failed test 1: acquisition date of transaction output does not match expected value"
        assert testValues[0]['Proceeds'] == 10000.00, "lifoSale() failed test 1: proceeds of transaction output does not match expected value"
        assert testValues[0]['GrossValue'] == 5000.00, "lifoSale() failed test 1: gross value of transaction output does not match expected value"
        assert testValues[0]['Discountable'] == True, "lifoSale() failed test 1: discountable (bool) of transaction output does not match expected value"

    def test_lifoSale2(self):
        """
        lifoSale test that has two purchases with different dates
        Confirms that lifo sells shares from the later purchase date
        """
        self.standardSharePurchase(value = 10000.00, quantity = 10.00, purchaseDate = dt.date(2022, 3, 30))
        self.standardSharePurchase(value = 10000.00, quantity = 10.00, purchaseDate = dt.date(2022, 4, 30)) # Purchase later than first purchase
        purchaseDate = dt.date(2022, 4, 30) # expected purchaseDate from second standardPurchase
        
        # Begin lifoSale test case:
        assetType = AssetType.Share
        assetIdentifier = 'TEST'
        saleDate = dt.date(2023, 4, 1)
        value = 10000.00
        quantity = 5.00 # five shares sold from first parcel of shares, remaining quantity: 5, remaining cost base: 5,000
        testValues = self.portfolio.lifoSale(
            assetType,
            assetIdentifier,
            saleDate,
            value,
            quantity
        )
        assert len(self.portfolio.assets) == 15, "lifoSale() failed test 2: quantity does not match expected value"
        assert self.portfolio.assets['Value'].sum() == 15000.00, "lifoSale() failed test 2: remaining portfolio value does not match expected value"
        assert testValues[0]['CostBase'] == 5000.00, "lifoSale() failed test 2: cost base of transaction output does not match expected value"
        assert testValues[0]['Date'] == saleDate, "lifoSale() failed test 2: date of transaction output does not match expected value"
        assert testValues[0]['Quantity'] == 5.00, "lifoSale() failed test 2: quantity of transaction output does not match expected value"
        assert testValues[0]['AcquisitionDate'] == purchaseDate, "lifoSale() failed test 2: acquisition date of transaction output does not match expected value"
        assert testValues[0]['Proceeds'] == 10000.00, "lifoSale() failed test 2: proceeds of transaction output does not match expected value"
        assert testValues[0]['GrossValue'] == 5000.00, "lifoSale() failed test 2: gross value of transaction output does not match expected value"
        assert testValues[0]['Discountable'] == False, "lifoSale() failed test 2: discountable (bool) of transaction output does not match expected value"
        dateGroups = self.portfolio.assets.groupby('PurchaseDate')
        assert len(dateGroups) == 2, "lifoSale() failed test 2: number of purchase dates present in portfolio does not match expected value"
        testParcels = []
        for purchaseDate, group in self.portfolio.assets.groupby('PurchaseDate'):
            testParcels.append((len(group), group['Value'].sum()))
        assert testParcels[0][0] == 10.00, "lifoSale() failed test 2: remaining shares in first parcel does not match expected value"
        assert testParcels[1][0] == 5.00, "lifoSale() failed test 2: remaining shares in second parcel does not match expected value"
        assert testParcels[0][1] == 10000.00, "lifoSale() failed test 2: cost base of shares in first parcel does not match expected value"
        assert testParcels[1][1] == 5000.00, "lifoSale() failed test 2: cost base of shares in second parcel does not match expected value"

    def test_exercise(self):
        # Test option part of exercise
        self.standardOptionPurchase(value = 10000.00, quantity = 10.00, purchaseDate = dt.date(2022, 3, 30), optionID = 'TEST1')
        assetType = AssetType.Option
        assetIdentifier = 'TEST'
        date = dt.date(2022, 4, 5)
        value = 0
        quantity = 5.00
        optionID = 'TEST1'
        self.portfolio.exercise(
            assetType = assetType,
            assetIdentifier = assetIdentifier,
            date = date,
            value = value,
            quantity = quantity,
            optionID = optionID
        )
        assert self.portfolio.optionExercises['TEST1'][0] == 5000.00, "exercise() failed test: cost base of option input to optionExercises dict does not match expected value"
        assert self.portfolio.optionExercises['TEST1'][1] == dt.date(2022, 3, 30), "exercise() failed test: cost base of option input to optionExercises dict does not match expected value"
        assert len(self.portfolio.assets) == 5, "exercise() failed test: quantity of remaining options does not match expected value"
        assert self.portfolio.assets['Value'].sum() == 5000.00, "exercise() failed test: remaining portfolio value does not match expected value"
        
        # Test share part of exercise
        assetType = AssetType.Share
        assetIdentifier = 'TEST'
        date = dt.date(2022, 4, 5)
        value = 2000.00
        quantity = 5.00
        optionID = 'TEST1'
        self.portfolio.exercise(
            assetType = assetType,
            assetIdentifier = assetIdentifier,
            date = date,
            value = value,
            quantity = quantity,
            optionID = optionID
        )
        assert optionID not in self.portfolio.optionExercises.keys(), "exercise() failed test: option exercise details not removed from optionExercsises dict"
        # Total assets post exercise are 5 options remaining + 5 shares purchased
        assert len(self.portfolio.assets) == 10, "exercise() failed test: quantity of total assets in portfolio does not match expected value"
        # Total portfolio value post-sale: 5,000 in options remaining + 5,000 cost base of options exercised + 2,000 exercise price == 12,000 total value
        assert self.portfolio.assets['Value'].sum() == 12000.00, "exercise() failed test: portfolio value post exercise does not match expected value"
        assert self.portfolio.assets[(self.portfolio.assets['AssetType'] == AssetType.Share)]['PurchaseDate'].min() == dt.date(2022, 3, 30), "exercise() failed test: acquisition date of shares acquired in exercise does not match original acquisition date of options"
        
    def test_expire(self):
        self.standardOptionPurchase(value = 10000.00, quantity = 10.00, purchaseDate = dt.date(2022, 3, 30), optionID = 'TEST1')
        assetType = AssetType.Option
        assetIdentifier = 'TEST'
        date = dt.date(2022, 4, 5)
        value = 0
        quantity = 10.00
        optionID = 'TEST1'
        testValues = self.portfolio.expire(
            assetType = assetType,
            assetIdentifier = assetIdentifier,
            date = date,
            value = value,
            quantity = quantity,
            optionID = optionID
        )
        assert len(self.portfolio.assets) == 0, "expire() failed test: quantity does not match expected value"
        assert self.portfolio.assets['Value'].sum() == 0.00, "expire() failed test: remaining portfolio value does not match expected value"
        assert testValues[0]['CostBase'] == 10000.00, "expire() failed test: cost base of transaction output does not match expected value"
        assert testValues[0]['Date'] == date, "expire() failed test: date of transaction output does not match expected value"
        assert testValues[0]['Quantity'] == 10.00, "expire() failed test: quantity of transaction output does not match expected value"
        assert testValues[0]['AcquisitionDate'] == dt.date(2022, 3, 30), "expire() failed test 1: acquisition date of transaction output does not match expected value"
        assert testValues[0]['Proceeds'] == 0, "expire() failed test: proceeds of transaction output does not match expected value"
        assert testValues[0]['GrossValue'] == -10000.00, "expire() failed test: gross value of transaction output does not match expected value"
        assert testValues[0]['Discountable'] == 'Loss', "expire() failed test: discountable status of transaction output does not match expected value"

    def test_highestgain_sale(self):
        """
        highestgain_sale test that has two purchases with different cost bases
        Highest cost base is purchased first to confirm sorting is working correctly
        """
        self.standardSharePurchase(value = 10000.00, quantity = 10.00, purchaseDate = dt.date(2022, 3, 30))
        self.standardSharePurchase(value = 5000.00, quantity = 10.00, purchaseDate = dt.date(2022, 4, 30)) # Purchase later than first purchase
        purchaseDate = dt.date(2022, 4, 30) # expected purchaseDate from second standardPurchase
        
        # Begin highestgain_sale test case:
        assetType = AssetType.Share
        assetIdentifier = 'TEST'
        saleDate = dt.date(2023, 4, 1)
        value = 10000.00
        quantity = 5.00 # five shares sold from first parcel of shares
        testValues = self.portfolio.highestGainSale(
            assetType,
            assetIdentifier,
            saleDate,
            value,
            quantity
        )
        assert len(self.portfolio.assets) == 15, "highestgain_sale() failed test: quantity does not match expected value"
        assert self.portfolio.assets['Value'].sum() == 12500.00, "highestgain_sale() failed test: remaining portfolio value does not match expected value"
        assert testValues[0]['CostBase'] == 2500.00, "highestgain_sale() failed test: cost base of transaction output does not match expected value"
        assert testValues[0]['Date'] == saleDate, "highestgain_sale() failed test: date of transaction output does not match expected value"
        assert testValues[0]['Quantity'] == 5.00, "highestgain_sale() failed test: quantity of transaction output does not match expected value"
        assert testValues[0]['AcquisitionDate'] == purchaseDate, "highestgain_sale() failed test: acquisition date of transaction output does not match expected value"
        assert testValues[0]['Proceeds'] == 10000.00, "highestgain_sale() failed test: proceeds of transaction output does not match expected value"
        assert testValues[0]['GrossValue'] == 7500.00, "highestgain_sale() failed test: gross value of transaction output does not match expected value"
        assert testValues[0]['Discountable'] == False, "highestgain_sale() failed test: discountable (bool) of transaction output does not match expected value"
        dateGroups = self.portfolio.assets.groupby('Value')
        assert len(dateGroups) == 2, "highestgain_sale() failed test 2: number of values present in portfolio does not match expected value"
        testParcels = []
        for purchaseDate, group in self.portfolio.assets.groupby('PurchaseDate'):
            testParcels.append((len(group), group['Value'].sum()))
        assert testParcels[0][0] == 10.00, "highestgain_sale() failed test: remaining shares in first parcel does not match expected value"
        assert testParcels[1][0] == 5.00, "highestgain_sale() failed test: remaining shares in second parcel does not match expected value"
        assert testParcels[0][1] == 10000.00, "highestgain_sale() failed test: cost base of shares in first parcel does not match expected value"
        assert testParcels[1][1] == 2500.00, "highestgain_sale() failed test: cost base of shares in second parcel does not match expected value"

    def test_lowestgain_sale(self):
        """
        lowestgain_sale test that has two purchases with different cost bases
        Lowest cost base is purchased first to confirm sorting is working correctly
        """
        self.standardSharePurchase(value = 10000.00, quantity = 10.00, purchaseDate = dt.date(2022, 3, 30))
        self.standardSharePurchase(value = 5000.00, quantity = 10.00, purchaseDate = dt.date(2022, 4, 30)) # Purchase later than first purchase
        purchaseDate = dt.date(2022, 3, 30) # expected purchaseDate from first standardPurchase
        
        # Begin lowestgain_sale test case:
        assetType = AssetType.Share
        assetIdentifier = 'TEST'
        saleDate = dt.date(2023, 4, 1)
        value = 10000.00
        quantity = 5.00 # five shares sold from second parcel of shares
        testValues = self.portfolio.lowestGainSale(
            assetType,
            assetIdentifier,
            saleDate,
            value,
            quantity
        )
        assert len(self.portfolio.assets) == 15, "lowestgain_sale() failed test: quantity does not match expected value"
        print (self.portfolio.assets['Value'].sum())
        assert self.portfolio.assets['Value'].sum() == 10000.00, "lowestgain_sale() failed test: remaining portfolio value does not match expected value"
        assert testValues[0]['CostBase'] == 5000.00, "lowestgain_sale() failed test: cost base of transaction output does not match expected value"
        assert testValues[0]['Date'] == saleDate, "lowestgain_sale() failed test: date of transaction output does not match expected value"
        assert testValues[0]['Quantity'] == 5.00, "lowestgain_sale() failed test: quantity of transaction output does not match expected value"
        assert testValues[0]['AcquisitionDate'] == purchaseDate, "lowestgain_sale() failed test: acquisition date of transaction output does not match expected value"
        assert testValues[0]['Proceeds'] == 10000.00, "lowestgain_sale() failed test: proceeds of transaction output does not match expected value"
        assert testValues[0]['GrossValue'] == 5000.00, "lowestgain_sale() failed test: gross value of transaction output does not match expected value"
        assert testValues[0]['Discountable'] == True, "lowestgain_sale() failed test: discountable (bool) of transaction output does not match expected value"
        dateGroups = self.portfolio.assets.groupby('Value')
        assert len(dateGroups) == 2, "lowestgain_sale() failed test 2: number of values present in portfolio does not match expected value"
        testParcels = []
        for purchaseDate, group in self.portfolio.assets.groupby('PurchaseDate'):
            testParcels.append((len(group), group['Value'].sum()))
        assert testParcels[0][0] == 5.00, "lowestgain_sale() failed test: remaining shares in first parcel does not match expected value"
        assert testParcels[1][0] == 10.00, "lowestgain_sale() failed test: remaining shares in second parcel does not match expected value"
        assert testParcels[0][1] == 5000.00, "lowestgain_sale() failed test: cost base of shares in first parcel does not match expected value"
        assert testParcels[1][1] == 5000.00, "lowestgain_sale() failed test: cost base of shares in second parcel does not match expected value"

if __name__ == '__main__':
    unittest.main()