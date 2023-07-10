import json

import numpy as np
import pandas as pd
import xgboost as xgb
from catboost import CatBoostClassifier
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from joblib import load
from lightgbm import LGBMClassifier
from sklearn.preprocessing import (OneHotEncoder, PowerTransformer,
                                   StandardScaler)
from xgboost import XGBClassifier

from .models import CustomerData

model = load('./SaveModel/newFinalModel2.h5')
# model2 = load('./SaveModel/newFinalModel.h5')

name = None
age = None
occupation = None
month = None
ssn = None
bankAccounts = None
numOfCreditCards = None
annualIncome = None
monthlyInhaldSalary = None
typeOfLoan = None
numOfLoan = None
interestRate = None
delayFromDueDate = None
numOfDelayedPayment = None
changedCreditLimit = None
numOfCreditInquiries = None
outstandingDebt = None
creditUtilizationRatio = None
creditHistoryAge = None
totalEMIPerMonth = None
amountInvestedMonthly = None
monthlyBalance = None
creditMix = None
paymentOfMinAmount = None
paymentBehavior = None


def Welcome(request):
    return render(request, 'first.html')


def generateCustomerID():
    lastCustomer = CustomerData.objects.order_by('customerID').first()
    if lastCustomer:
        lastID = int(lastCustomer.customerID)
        newID = lastID+1
    else:
        newID = 1
    customerID = str(newID).zfill(8)
    return customerID


def first_view(request):
    global name, age, occupation, month, ssn, bankAccounts, numOfCreditCards, annualIncome, monthlyInhaldSalary, typeOfLoan, numOfLoan, interestRate
    if request.method == 'POST':
        name = request.POST.get('Name')
        age = int(request.POST.get('Age'))
        occupation = request.POST.get('Occupation')
        month = request.POST.get('Month')
        ssn = request.POST.get('SSN')
        bankAccounts = int(request.POST.get('Num_Bank_Accounts'))
        numOfCreditCards = int(request.POST.get('Num_Credit_Card'))
        annualIncome = int(request.POST.get('Annual_Income'))
        monthlyInhaldSalary = np.float64(
            request.POST.get('Monthly_Inhald_Salary'))
        typeOfLoan = request.POST.get('Type_of_Loan')
        numOfLoan = np.float64(request.POST.get('Num_of_Loan'))
        interestRate = np.float64(request.POST.get('Interest_Rate'))
        return redirect('second_view')
    return render(request, 'first.html')


def second_view(request):
    global delayFromDueDate, numOfDelayedPayment, changedCreditLimit, numOfCreditInquiries, outstandingDebt, creditUtilizationRatio, creditHistoryAge, totalEMIPerMonth, amountInvestedMonthly, monthlyBalance
    if request.method == 'POST':
        delayFromDueDate = np.float64(request.POST.get('Delay_from_due_date'))
        numOfDelayedPayment = np.float64(
            request.POST.get('Num_of_Delayed_Payment'))
        changedCreditLimit = np.float64(
            request.POST.get('Changed_Credit_Limit'))
        numOfCreditInquiries = np.float64(
            request.POST.get('Num_Credit_Inquiries'))
        outstandingDebt = np.float64(request.POST.get('Outstanding_Debt'))
        creditUtilizationRatio = np.float64(
            request.POST.get('Credit_Utilization_Ratio'))
        creditHistoryAge = request.POST.get('Credit_History_Age')
        totalEMIPerMonth = np.float64(request.POST.get('Total_EMI_per_month'))
        amountInvestedMonthly = np.float64(
            request.POST.get('Amount_invested_monthly'))
        monthlyBalance = np.float64(request.POST.get('Monthly_Balance'))
        return redirect('third_view')
    return render(request, 'second.html')


def third_view(request):
    global creditMix, paymentOfMinAmount, paymentBehavior
    data = CustomerData.objects.all()
    if request.method == 'POST':
        creditMix = request.POST.get('Credit_Mix')
        paymentOfMinAmount = request.POST.get('Payment_of_Min_Amount')
        paymentBehavior = request.POST.get('Payment_Behaviour')
        preProcessing()
        redirect('result_view')
    return render(request, 'third.html')


def result_view(request):
    return None


def preProcessing():
    # customerID = request.GET.get('Customer_ID')
    global name, age, occupation, month, ssn, bankAccounts, numOfCreditCards, annualIncome, monthlyInhaldSalary, typeOfLoan, numOfLoan, interestRate

    global delayFromDueDate, numOfDelayedPayment, changedCreditLimit, numOfCreditInquiries, outstandingDebt, creditUtilizationRatio, creditHistoryAge, totalEMIPerMonth, amountInvestedMonthly, monthlyBalance

    global creditMix, paymentOfMinAmount, paymentBehavior

    customerID = generateCustomerID()
    print(name)
    print(creditHistoryAge)
    print(creditMix)

    parts = creditHistoryAge.split()
    years = np.float64(parts[0])
    months = np.float64(parts[2])
    totalMonths = years*12
    print(totalMonths)

    lowCardinality = np.array([numOfCreditInquiries, bankAccounts,
                               numOfCreditCards, numOfLoan, numOfDelayedPayment])
    # Reshape lowCardinality array to (1, -1)
    lowCardinality = np.reshape(lowCardinality, (1, -1))
    print(lowCardinality)

    highCardinality = [[delayFromDueDate, creditUtilizationRatio,
                       totalMonths, amountInvestedMonthly, monthlyBalance, age, annualIncome, interestRate, monthlyInhaldSalary, changedCreditLimit, outstandingDebt, totalEMIPerMonth]]

    print(highCardinality)

    categoricalData = [paymentOfMinAmount, creditMix]
    print(categoricalData)

    # normalization is done using PowerTransformer
    powerTransformer = PowerTransformer()
    powerTransformer.fit(highCardinality)
    scalingFactors = [0.35811907, 0.73102899, 0.87353617, 0.04911475, 0.25766935,
                      0.57149655, 0.04951728, 0.45428343, 0.08418477, 0.40267339,
                      0.34897038, 0.29316206]
    powerTransformer.lambdas_ = scalingFactors
    numeric = powerTransformer.transform(highCardinality)
    print(numeric)

    # onehot encoder implemented
    categories = [['NM', 'No', 'Yes'], ['Bad', 'Good', 'Standard']]
    encoder = OneHotEncoder(categories=categories, drop="first")
    one_hot = encoder.fit_transform([categoricalData]).toarray()
    print(one_hot)
    print(encoder.categories_)

    numeric = np.reshape(numeric, (1, -1))  # Reshape numeric array to (1, -1)
    one_hot = np.array(one_hot)

    X = np.concatenate([numeric, one_hot, lowCardinality], axis=1)
    print(X)

    y_pred = model.predict(X)
    print(y_pred[0])

    # y_pred2 = model2.predict(X)
    # print(y_pred2[0])

    if y_pred == 0:
        y_pred = "Good"
    elif y_pred == 1:
        y_pred = "Bad"
    else:
        y_pred = "Standard"

    print(y_pred)

    data = CustomerData(customerID=customerID, month=month, name=name, age=age, ssn=ssn,
                        occupation=occupation, annualIncome=annualIncome,
                        monthlyInhaldSalary=monthlyInhaldSalary, bankAccounts=bankAccounts,
                        numOfCreditCards=numOfCreditCards, interestRate=interestRate,
                        numOfLoan=numOfLoan, typeOfLoan=typeOfLoan,
                        delayFromDueDate=delayFromDueDate,
                        numOfDelayedPayment=numOfDelayedPayment,
                        changedCreditLimit=changedCreditLimit,
                        numOfCreditInquiries=numOfCreditInquiries,
                        creditMix=creditMix, outstandingDebt=outstandingDebt,
                        creditUtilizationRatio=creditUtilizationRatio,
                        creditHistoryAge=creditHistoryAge,
                        paymentOfMinAmount=paymentOfMinAmount,
                        totalEMIPerMonth=totalEMIPerMonth,
                        amountInvestedMonthly=amountInvestedMonthly,
                        paymentBehavior=paymentBehavior,
                        monthlyBalance=monthlyBalance,
                        creditScore=y_pred)
    data.save()
    return None
    # return render(request, 'result.html')

# def predictor():
#     print(name)
#     return None
