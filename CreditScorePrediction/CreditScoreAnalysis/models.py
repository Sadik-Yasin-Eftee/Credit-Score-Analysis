from django.db import models


# Create your models here.
class CustomerData(models.Model):
    customerID = models.CharField(max_length=8, unique=True)
    month = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    age = models.FloatField()
    ssn = models.CharField(max_length=100)
    occupation = models.CharField(max_length=100)
    annualIncome = models.FloatField()
    monthlyInhaldSalary = models.FloatField()
    bankAccounts = models.FloatField()
    numOfCreditCards = models.FloatField()
    interestRate = models.FloatField()
    numOfLoan = models.FloatField()
    typeOfLoan = models.CharField(max_length=100)
    delayFromDueDate = models.FloatField()
    numOfDelayedPayment = models.FloatField()
    changedCreditLimit = models.FloatField()
    numOfCreditInquiries = models.FloatField()
    creditMix = models.CharField(max_length=100)
    outstandingDebt = models.FloatField()
    creditUtilizationRatio = models.FloatField()
    creditHistoryAge = models.CharField(max_length=10)
    paymentOfMinAmount = models.CharField(max_length=100)
    totalEMIPerMonth = models.FloatField()
    amountInvestedMonthly = models.FloatField()
    paymentBehavior = models.CharField(max_length=100)
    monthlyBalance = models.FloatField()
    creditScore = models.CharField(max_length=100)

    def __str__(self):
        return self.customerID
