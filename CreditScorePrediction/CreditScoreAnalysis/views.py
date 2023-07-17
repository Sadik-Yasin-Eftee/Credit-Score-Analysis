import json
from collections import Counter

import numpy as np
import pandas as pd
import xgboost as xgb
from catboost import CatBoostClassifier
from django.db.models import Max
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from joblib import load
from lightgbm import LGBMClassifier
from sklearn.preprocessing import (OneHotEncoder, PowerTransformer,
                                   StandardScaler)
from xgboost import XGBClassifier

from .models import CustomerData

# model = load('./SaveModel/newFinalModel2.h5')
models = load('./SaveModel/models')
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


def welcome(request):
    return render(request, "home.html")


def formPage(request):
    return render(request, 'first.html')


def profile_view(request, customer_id):
    customerData = get_object_or_404(CustomerData, customerID=customer_id)
    context = {'customer_data': customerData}
    return render(request, 'details.html', context)


def generateCustomerID():
    lastCustomer = CustomerData.objects.all().aggregate(Max('customerID'))
    lastID = lastCustomer['customerID__max']
    if lastID:
        newID = int(lastID) + 1
    else:
        newID = 1
    customerID = str(newID).zfill(8)
    return customerID


def first_view(request):
    global name, age, occupation, month, ssn, bankAccounts, numOfCreditCards, annualIncome, monthlyInhaldSalary, numOfLoan, interestRate, changedCreditLimit
    if request.method == 'POST':
        name = request.POST.get('Name')
        age = int(request.POST.get('Age'))
        occupation = request.POST.get('Occupation')
        month = request.POST.get('Month')
        ssn = request.POST.get('SSN')
        bankAccounts = int(request.POST.get('Num_Bank_Accounts'))
        numOfCreditCards = int(request.POST.get('Num_Credit_Card'))
        annualIncome = np.float64(request.POST.get('Annual_Income'))
        monthlyInhaldSalary = np.float64(
            request.POST.get('Monthly_Inhald_Salary'))
        changedCreditLimit = np.float64(
            request.POST.get('Changed_Credit_Limit'))
        numOfLoan = np.float64(request.POST.get('Num_of_Loan'))
        interestRate = np.float64(request.POST.get('Interest_Rate'))
        # print(changedCreditLimit)
    return render(request, 'second.html')


def second_view(request):
    global delayFromDueDate, numOfDelayedPayment, numOfCreditInquiries, outstandingDebt, creditUtilizationRatio, totalEMIPerMonth, amountInvestedMonthly, monthlyBalance, typeOfLoan
    if request.method == 'POST':
        delayFromDueDate = np.float64(request.POST.get('Delay_from_due_date'))
        numOfDelayedPayment = np.float64(
            request.POST.get('Num_of_Delayed_Payment'))
        typeOfLoan = request.POST.get('Type_of_Loan')
        numOfCreditInquiries = np.float64(
            request.POST.get('Num_Credit_Inquiries'))
        outstandingDebt = np.float64(request.POST.get('Outstanding_Debt'))
        creditUtilizationRatio = np.float64(
            request.POST.get('Credit_Utilization_Ratio'))
        totalEMIPerMonth = np.float64(request.POST.get('Total_EMI_per_month'))
        amountInvestedMonthly = np.float64(
            request.POST.get('Amount_invested_monthly'))
        monthlyBalance = np.float64(request.POST.get('Monthly_Balance'))
        print(numOfCreditInquiries)
        print(type(numOfCreditInquiries))
    return render(request, 'third.html')


def third_view(request):
    global creditMix, paymentOfMinAmount, paymentBehavior, creditHistoryAgeYear, creditHistoryAgeMonth
    if request.method == 'POST':
        creditHistoryAgeYear = int(request.POST.get('Credit_History_Age_Year'))
        creditHistoryAgeMonth = int(
            request.POST.get('Credit_History_Age_Month'))

        if creditHistoryAgeMonth > 12:
            creditHistoryAgeYear += creditHistoryAgeMonth // 12
            creditHistoryAgeMonth = creditHistoryAgeMonth % 12

        creditMix = request.POST.get('Credit_Mix')
        paymentOfMinAmount = request.POST.get('Payment_of_Min_Amount')
        paymentBehavior = request.POST.get('Payment_Behaviour')
        customerID, creditScore = preProcessing()
        print(customerID, creditScore)
    return render(request, 'fourth.html', {
        "customerName": name,
        "customerID": customerID,
        "result": creditScore
    })


def cutomerList(request):
    data = CustomerData.objects.all()
    return render(request, 'member.html', {
        'customerList': data
    })


def preProcessing():
    global name, age, occupation, month, ssn, bankAccounts, numOfCreditCards, annualIncome, monthlyInhaldSalary, typeOfLoan, numOfLoan, interestRate

    global delayFromDueDate, numOfDelayedPayment, changedCreditLimit, numOfCreditInquiries, outstandingDebt, creditUtilizationRatio, creditHistoryAgeYear, creditHistoryAgeMonth, totalEMIPerMonth, amountInvestedMonthly, monthlyBalance

    global creditMix, paymentOfMinAmount, paymentBehavior

    customerID = generateCustomerID()

    totalMonths = creditHistoryAgeYear*12 + creditHistoryAgeMonth
    creditHistoryAge = "{} Year{} {} Month{}".format(
        creditHistoryAgeYear, 's' if creditHistoryAgeYear != 1 else '', creditHistoryAgeMonth, 's' if creditHistoryAgeMonth != 1 else '')

    lowCardinality = np.array([numOfCreditInquiries, bankAccounts,
                               numOfCreditCards, numOfLoan, numOfDelayedPayment], dtype=np.float64)
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

    predictions = []
    for model_name, model in models.items():
        preds = model.predict(X)
        predictions.append(preds)

    # Perform majority voting to get the final prediction
    y_pred = []
    for i in range(len(X)):
        counts = Counter([preds[i] for preds in predictions])
        majority_vote = counts.most_common(1)[0][0]
        y_pred.append(majority_vote)

    # Print the final prediction
    print("Final prediction:", y_pred[0])

    if y_pred[0] == 0:
        y_pred[0] = "Good"
    elif y_pred[0] == 1:
        y_pred[0] = "Bad"
    else:
        y_pred[0] = "Standard"

    print(y_pred[0])

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
                        creditScore=y_pred[0])
    data.save()
    return customerID, y_pred[0]
