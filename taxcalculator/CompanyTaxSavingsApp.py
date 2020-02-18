#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 19 12:46:12 2018

@author: CTF Team
"""
from PyQt5 import uic,QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QSize, Qt
import CompanyTaxUI
import sys
import pandas as pd
import csv
import numpy as np

class ApplicationWindow(QtWidgets.QMainWindow):
	def __init__(self):
		super(ApplicationWindow, self).__init__()
		self.ui = CompanyTaxUI.Ui_MainWindow()
		self.ui.setupUi(self)
		# Connects the calculate button in CompanyTaxUI to CompanyTaxSavingsApp.py
		self.ui.calculate.clicked.connect(self.taxCalculate)

	def taxCalculate(self):

		# Gets the string input from company_netIncome
		companySGDIncome = self.ui.company_netIncome.text()

		# Checks if companySGDIncome is empty
		if not companySGDIncome:
			self.ui.list_top10.setColumnCount(1)
			self.ui.list_top10.setHorizontalHeaderLabels(["Output"])
			self.ui.list_top10.setRowCount(1)
			self.ui.list_top10.horizontalHeaderItem(0).setTextAlignment(Qt.AlignLeft)
			self.ui.list_top10.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
			self.ui.list_top10.setItem(0 , 0, QtWidgets.QTableWidgetItem("You have not inputted any SGD Net Income !"))

		else:
			# Gets the category input from list_companyindustry
			selectedCategoryData = self.ui.list_companyindustry.currentText()

			calCountriesTaxAmt = ApplicationWindow.taxComputation(companySGDIncome, selectedCategoryData)

			# Gets the option 1 - 5 to indicate the option to generate the tax output
			if self.ui.option1.isChecked():
				# Filter countries that have 0% tax rates for the respective tax rates
				# Looking at 0 index value for national + branch rate
				filteredCountries1 = {k:v for k, v in calCountriesTaxAmt.items() if v[0] > 0}
				minimumTaxCountry1 = min(filteredCountries1.items(), key = lambda x : x[1][0])

				# Set ui list to the following parameters for the required output for option 5
				self.ui.list_top10.setColumnCount(3)
				self.ui.list_top10.setHorizontalHeaderLabels(["Country", "Tax Amount", "Tax Option #"])
				self.ui.list_top10.setRowCount(1)
				self.ui.list_top10.horizontalHeaderItem(0).setTextAlignment(Qt.AlignLeft)
				self.ui.list_top10.horizontalHeaderItem(1).setTextAlignment(Qt.AlignLeft)
				self.ui.list_top10.horizontalHeaderItem(2).setTextAlignment(Qt.AlignLeft)

				# Setting output for option 1
				self.ui.list_top10.setItem(0 , 0, QtWidgets.QTableWidgetItem(minimumTaxCountry1[0]))
				value = '%.3f' % minimumTaxCountry1[1][0]
				self.ui.list_top10.setItem(0 , 1, QtWidgets.QTableWidgetItem(value))
				self.ui.list_top10.setItem(0 , 2, QtWidgets.QTableWidgetItem("Tax Option 1"))

			elif self.ui.option2.isChecked():
				# Looking at index 1 value for min tax
				filteredCountries2 = {k:v for k, v in calCountriesTaxAmt.items() if v[1] > 0}
				minimumTaxCountry2 = min(filteredCountries2.items(), key = lambda x: x[1][1])

				self.ui.list_top10.setColumnCount(3)
				self.ui.list_top10.setHorizontalHeaderLabels(["Country", "Tax Amount", "Tax Option #"])
				self.ui.list_top10.setRowCount(1)
				self.ui.list_top10.horizontalHeaderItem(0).setTextAlignment(Qt.AlignLeft)
				self.ui.list_top10.horizontalHeaderItem(1).setTextAlignment(Qt.AlignLeft)
				self.ui.list_top10.horizontalHeaderItem(2).setTextAlignment(Qt.AlignLeft)

				# Setting output for option 2
				self.ui.list_top10.setItem(0 , 0, QtWidgets.QTableWidgetItem(minimumTaxCountry2[0]))
				value = '%.3f' % minimumTaxCountry2[1][1]
				self.ui.list_top10.setItem(0 , 1, QtWidgets.QTableWidgetItem(value))
				self.ui.list_top10.setItem(0 , 2, QtWidgets.QTableWidgetItem("Tax Option 2"))

			elif self.ui.option3.isChecked():
				# Looking at index 2 value for progressive tax
				filteredCountries3 = {k:v for k, v in calCountriesTaxAmt.items() if v[2] > 0}
				minimumTaxCountry3 = min(filteredCountries3.items(), key = lambda x: x[1][2])

				self.ui.list_top10.setColumnCount(3)
				self.ui.list_top10.setHorizontalHeaderLabels(["Country", "Tax Amount", "Tax Option #"])
				self.ui.list_top10.setRowCount(1)
				self.ui.list_top10.horizontalHeaderItem(0).setTextAlignment(Qt.AlignLeft)
				self.ui.list_top10.horizontalHeaderItem(1).setTextAlignment(Qt.AlignLeft)
				self.ui.list_top10.horizontalHeaderItem(2).setTextAlignment(Qt.AlignLeft)

				# Setting output for option 3
				self.ui.list_top10.setItem(0 , 0, QtWidgets.QTableWidgetItem(minimumTaxCountry3[0]))
				value = '%.3f' % minimumTaxCountry3[1][2]
				self.ui.list_top10.setItem(0 , 1, QtWidgets.QTableWidgetItem(value))
				self.ui.list_top10.setItem(0 , 2, QtWidgets.QTableWidgetItem("Tax Option 3"))

			elif self.ui.option4.isChecked():
				# Looking at index 3 value for category tax
				filteredCountries4 = {k:v for k, v in calCountriesTaxAmt.items() if v[3] > 0}

				# If Category is not inputted
				if bool(filteredCountries4) == False :
					self.ui.list_top10.setColumnCount(1)
					self.ui.list_top10.setHorizontalHeaderLabels(["Output"])
					self.ui.list_top10.setRowCount(1)
					self.ui.list_top10.horizontalHeaderItem(0).setTextAlignment(Qt.AlignLeft)
					self.ui.list_top10.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
					self.ui.list_top10.setItem(0 , 0, QtWidgets.QTableWidgetItem("You have not chosen any category !"))

				# Else shows the category data
				else:
					minimumTaxCountry4 = min(filteredCountries4.items(), key=lambda x: x[1][3])
					self.ui.list_top10.setColumnCount(3)
					self.ui.list_top10.setHorizontalHeaderLabels(["Country", "Tax Amount", "Tax Option #"])
					self.ui.list_top10.setRowCount(1)
					self.ui.list_top10.horizontalHeaderItem(0).setTextAlignment(Qt.AlignLeft)
					self.ui.list_top10.horizontalHeaderItem(1).setTextAlignment(Qt.AlignLeft)
					self.ui.list_top10.horizontalHeaderItem(2).setTextAlignment(Qt.AlignLeft)

					# Setting output for option 4
					self.ui.list_top10.setItem(0 , 0, QtWidgets.QTableWidgetItem(minimumTaxCountry4[0]))
					value = '%.3f' % minimumTaxCountry4[1][3]
					self.ui.list_top10.setItem(0 , 1, QtWidgets.QTableWidgetItem(value))
					self.ui.list_top10.setItem(0 , 2, QtWidgets.QTableWidgetItem("Tax Option 3"))

			elif self.ui.option5.isChecked():
				# Loops through calCountrieTaxAmt and store least tax amount and index as a tuple for key countryName
				topTenCountriesLowestTaxes = {}
				for value in calCountriesTaxAmt.items():
					val = min((x for x in value[1] if x > 0), default = 0)
					index = value[1].index(val)
					topTenCountriesLowestTaxes[value[0]] = (val,index)

				# Filters countries with 0 values
				filteredCountries5 = {k:v for k, v in topTenCountriesLowestTaxes.items() if v[0] > 0}
				minimumTaxCountry5 = sorted(filteredCountries5.items(), key=lambda x:x[1])

				self.ui.list_top10.setColumnCount(3)
				self.ui.list_top10.setHorizontalHeaderLabels(["Country", "Tax Amount", "Tax Option #"])
				self.ui.list_top10.setRowCount(10)
				self.ui.list_top10.horizontalHeaderItem(0).setTextAlignment(Qt.AlignLeft)
				self.ui.list_top10.horizontalHeaderItem(1).setTextAlignment(Qt.AlignLeft)
				self.ui.list_top10.horizontalHeaderItem(2).setTextAlignment(Qt.AlignLeft)

				# Setting the top 10 least minimum tax and their options onto the output
				for row in range(10):
					self.ui.list_top10.setItem(row, 0, QtWidgets.QTableWidgetItem(minimumTaxCountry5[row][0]))
					value = '%.3f' % minimumTaxCountry5[row][1][0]
					self.ui.list_top10.setItem(row , 1, QtWidgets.QTableWidgetItem(value))
					option = minimumTaxCountry5[row][1][1] + 1
					option = "Tax Option " +  '%.f' % + option
					self.ui.list_top10.setItem(row, 2, QtWidgets.QTableWidgetItem(option))


	# Convert SGD Net Income to USD Net Income
	def convertSGDToUSD(companySGDIncome):
		usdIncome = companySGDIncome * 0.75

		return usdIncome

	# Generate dictionary with key as Country and tuple with 4 spaces containing the different tax rates
	def generateTaxForOptions(taxData, companyUSDIncome, companyCode):
		countryTaxAmount = {}

		for row in taxData.itertuples(index=False, name="None"):
				# Initialize 4 taxes amount to be stored
				# 1st tax amount is normal rate + branch rate
				# 2nd tax amount is minimum tax rate
				# 3rd tax amount is progressive tax rate
				# 4th tax amount is pertaining to the specific type of industry

				differentTaxAmount = [0,0,0,0]
				
				# 1st Tax
				# Finding the tax in USD for tax amount # 1 with normal rate + branch rate
				differentTaxAmount[0] = round(companyUSDIncome * (row[1] + row[8]), 3)
				# 2nd Tax
				# Find the tax in USD for tax amount # 2 with minimum tax rate
				differentTaxAmount[1] = round(companyUSDIncome * (row[4]), 3)

				# 3rd Tax
				# If native currency is not in USD, find the tax in USD and convert to native currency for progressive tax computation
				nativeCurrency = companyUSDIncome
				if row[2] != "USD":
					nativeCurrency = (1.0 / row[3]) * nativeCurrency

				# Evaluates for fields that are not empty in ProgressiveTaxRate
				if row[7]:
					# Split by , for progressive tax condition
					progressiveTax = row[7].split(',')

					# For loop inside the progressiveTax and split by white space
					conditionStatement = [x.split() for x in progressiveTax] 
					
					# For loop through the condition statement for each list of conditions
					for x in conditionStatement:
						# If value is present, break out of loop
						valuePresent = False

						# Round off native currency to 3 decimal places and declare it as a string
						roundedNativeCurrency = round(nativeCurrency, 3)
						strRoundedNativeCurrency = '%.3f' % roundedNativeCurrency

						# Use if condition to check for the length of the list of conditionStatement 
						if len(x) == 5:
							# Evaluate the conditions before final statement
							lowerBound = x[0]
							evaluationCondition = x[1]
							upperBound = x[2]
							taxPercentage = x[4]

							# Use eval function to test the test case
							lowerBoundStatement = "> " + lowerBound
							upperBoundStatement = evaluationCondition + " " + upperBound
							
							# 1st condition to check if figure is bigger than amount
							lowerCondition = strRoundedNativeCurrency + " " + lowerBoundStatement
							
							# 2nd condition to check if figure is smaller than or equal to amount
							upperCondition = strRoundedNativeCurrency + " " + upperBoundStatement

							# Checks if 1st and 2nd condition is fulfilled to know if nativeCurrency falls within this range
							if (eval(lowerCondition)) and (eval(upperCondition)):
								nativeCalculatedTax = roundedNativeCurrency * float(taxPercentage)
								# Calculate back the amount in USD
								USDCalTax1 = nativeCalculatedTax * (row[3])
								USDCalTax1 = round(USDCalTax1, 3)
								# Assign the CalTax into differentTaxAmount
								differentTaxAmount[2] = USDCalTax1
								valuePresent = True
								break

						if (valuePresent == True):
							break

						elif len(x) == 4:
							# Evaluate the conditions for final statement
							lastEvaluationCondition = x[0]
							lastLowerBound = x[1]
							lastTaxPercentage = x[3]

							# last condition to check if figure is bigger than last lower bound
							lastLowerBoundStatement = lastEvaluationCondition + " " + lastLowerBound

							# Adding strRoundedNativeCurrency to lastCondition
							lastCondition = strRoundedNativeCurrency + " " + lastLowerBoundStatement

							# Checks if last condition is fulfilled
							if eval(lastCondition):
								nativeCalculatedTax = roundedNativeCurrency * float(lastTaxPercentage)
								# Calculate back the amount in USD
								USDCalTax2 = nativeCalculatedTax * (row[3])
								USDCalTax2 = round(USDCalTax2, 3)
								# Assign the CalTax into differentTaxAmount
								differentTaxAmount[2] = USDCalTax2
								valuePresent = True
								break

				# 4th Tax
				# Calculates the tax amount if categoryTaxCondition1 fulfils the companyCode defined by the user
				if row[9]:
					if "," in row[9]:
						# Split the string by , to get the string statement out
						categoryStatement1 = row[9].split(',')
						# For loop inside the categoryStatement and split by white space
						categoryTaxCondition1 = [x.split() for x in categoryStatement1]

						# For loop inside the tuple and retrieve dictCode for comparison and multiplication by assigned tax rate if it matches 
						for x in categoryTaxCondition1:
							dictCode1 = x[0]
							categoryTax1 = x[2]
							if (companyCode == dictCode1):
								categoryTaxAmount1 = companyUSDIncome * float(categoryTax1)
								differentTaxAmount[3] = categoryTaxAmount1
								break

					# For loop inside the tuple and multiply by taxRate if it matches 
					else:
						# Account for countries with only 1 type of category special tax rate
						categoryTaxCondition2 = row[9].split()
						dictCode2 = categoryTaxCondition2[0]
						categoryTax2 = categoryTaxCondition2[2]

						if (companyCode == dictCode2):
							categoryTaxAmount2 = companyUSDIncome * float(categoryTax2)
							differentTaxAmount[3] = categoryTaxAmount2

				# Assigning the countryName as key, the differentTaxAmount tuple as the value
				countryTaxAmount[row[0]] = differentTaxAmount
		return countryTaxAmount

	# Generate dictionary with key as CategoryName and value as 3 characters code for category
	def generateCategoryData(categoryData):
		# Use list comprehension to assign key and data to categoryDict
		categoryDict = {x['CategoryName']: x['CategoryCode'] for x in categoryData.to_dict(orient="records")}

		return categoryDict

	def taxComputation(companySGDIncome, selectedCategoryData):
		# Load csv data into pandas and na values are not being evaluated as NaN
		taxData = pd.read_csv('countryTax.csv', keep_default_na=False)

		# Fill empty fields with blank spaces
		taxData.fillna({'ProgressiveTaxRange':'', 'CategoryRate': ''})

		# Load csv data for company category and load into companyDict dictionary
		categoryData = pd.read_csv('categoryDict.csv',  keep_default_na=False)

		# Generate categoryDict for categoryData
		categoryDict = ApplicationWindow.generateCategoryData(categoryData)

		companyCode = categoryDict.get(selectedCategoryData)

		companySGDIncome = float(companySGDIncome)
		companyUSDIncome = ApplicationWindow.convertSGDToUSD(companySGDIncome)

		# Assign countryName as key, and calculate the value for differentTaxAmount in option 1, 2, 3, 4 in USD
		countriesTaxAmt = ApplicationWindow.generateTaxForOptions(taxData, companyUSDIncome, companyCode)

		return countriesTaxAmt

if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)
	application = ApplicationWindow()
	application.show()
	sys.exit(app.exec_())