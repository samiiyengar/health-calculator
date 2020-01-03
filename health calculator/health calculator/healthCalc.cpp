//
//  healthCalc.cpp
//  health calculator
//
//  Created by Samyukta Iyengar on 1/1/20.
//  Copyright © 2020 Samyukta Iyengar. All rights reserved.
//

#include "healthCalc.h"
#define calsInPound 3500

double HealthCalc::calculateBMI(double weight, double height) {
    double bmi = weight / (height * height);
    return bmi; 
}

string HealthCalc::checkBMI(double bmi) {
    if (bmi < 18.5) {
        return "Underweight";
    } else if ((bmi >= 18.5) && (bmi < 25)) {
        return "Healthy";
    } else if ((bmi >= 25) && (bmi < 30)) {
        return "Overweight";
    } else if (bmi >= 30) {
        return "Obese";
    }
    return "";
}

double HealthCalc::convertImperialHeightToMeters(double height) {
    height = (height * 2.54)/100;
    return height;
}

double HealthCalc::convertImperialWeightToKG(double weight) {
    weight = weight * 0.454;
    return weight;
}

double HealthCalc::convertMetricHeightToInches(double height) {
    height = height/2.54;
    return height;
}

double HealthCalc::convertMetricWeightToLB(double weight) {
    weight = weight / 0.454;
    return weight; 
}

double HealthCalc::convertCMtoM(double height) {
    height = height/100;
    return height; 
}

int HealthCalc::caloriesPerDay(double weight, double goalWeight, double height, int weeks, int activity, string sex, int age) {
    double poundsPerWeek = (weight - goalWeight)/weeks;
    int calsPerWeek = poundsPerWeek * calsInPound;
    int calsPerDay = calsPerWeek / 7;
    int baseMetabolicRate = 0;
    double caloricNeed = 0;
    if ((sex == "male") || (sex == "m") || (sex == "M")) {
        baseMetabolicRate = 66 + (6.3 * weight) + (12.9 * height) - (6.8 * age);
    } else if ((sex == "female") || (sex == "f") || (sex == "F")) {
        baseMetabolicRate = 655 + (4.3 * weight) + (4.7 * height) - (4.7 * age);
    }
    
    if (activity == 1) {
        caloricNeed = baseMetabolicRate * 1.2;
    } else if (activity == 2) {
        caloricNeed = baseMetabolicRate * 1.375;
    } else if (activity == 3) {
        caloricNeed = baseMetabolicRate * 1.55;
    } else if (activity == 4) {
        caloricNeed = baseMetabolicRate * 1.725;
    } else if (activity == 5) {
        caloricNeed = baseMetabolicRate * 1.9;
    }
    
    double caloriesToEat = caloricNeed - calsPerDay;
    caloriesToEat = (int) caloriesToEat;
    return caloriesToEat;
}

