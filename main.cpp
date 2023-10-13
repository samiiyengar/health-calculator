//
//  main.cpp
//  health calculator
//
//  Created by Samyukta Iyengar on 1/1/20.
//  Copyright © 2020 Samyukta Iyengar. All rights reserved.
//

#include <iostream>
#include "healthCalc.h"

void printOptions();

int main(int argc, const char * argv[]) {

    HealthCalc calc;
    int choice;
    double height;
    double weight;
    double bmi;
    string choice2 = " ";
    double goalWeight;
    int weeks;
    double weightToLose;
    int activity;
    string sex;
    int age;
    int cals;

    printOptions();
    cin >> choice;
    
    if (choice == 1) {
        cout << "Type I for Imperial, M for Metric." << endl;
        while ((choice2 != "I") && (choice2 != "M")) {
            cin >> choice2;
            if (choice2 == "I") {
                cout << "What is your height in inches?" << endl;
                cin >> height;
                height = calc.convertImperialHeightToMeters(height);
                cout << "What is your weight in pounds?" << endl;
                cin >> weight;
                weight = calc.convertImperialWeightToKG(weight);
                bmi = calc.calculateBMI(weight, height);
                cout << "Your BMI is: " << bmi << endl;
                cout << "You are: " << calc.checkBMI(bmi) << endl;
            } else if (choice2 == "M") {
                cout << "What is your height in centimeters?" << endl;
                cin >> height;
                height = calc.convertCMtoM(height);
                cout << "What is your weight in kilograms?" << endl;
                cin >> weight;
                bmi = calc.calculateBMI(weight, height);
                cout << "Your BMI is: " << bmi << endl;
                cout << "You are: " << calc.checkBMI(bmi) << endl;
            } else {
                cout << "Invalid choice. Please try again." << endl;
            }
        }
    }
    
    if (choice == 2) {
        cout << "Type I for Imperial, M for Metric." << endl;
        while ((choice2 != "I") && (choice2 != "M")) {
            cin >> choice2;
            if (choice2 == "I") {
                cout << "Are you male or female?" << endl;
                cin >> sex;
                cout << "How old are you?" << endl;
                cin >> age;
                cout << "What is your height in inches?" << endl;
                cin >> height;
                cout << "What is your current weight in pounds?" << endl;
                cin >> weight;
                cout << "What is your goal weight?" << endl;
                cin >> goalWeight;
                cout << "How many weeks do you want to lose the weight in?" << endl;
                cin >> weeks;
                cout << "What is your activity level: (1) Sedentary, (2) Slightly Active, (3) Moderately Active, (4) Active, or (5) Very Active?" << endl;
                cin >> activity;
                cals = calc.caloriesPerDay(weight, goalWeight, height, weeks, activity, sex, age);
                weightToLose = weight - goalWeight;
                cout << "You should eat " << cals << " calories to lose " << weightToLose << " lbs in " << weeks << " weeks." << endl;
            } else if (choice2 == "M") {
                cout << "Are you male or female?" << endl;
                cin >> sex;
                cout << "How old are you?" << endl;
                cin >> age; 
                cout << "What is your height in centimeters?" << endl;
                cin >> height;
                height = calc.convertMetricHeightToInches(height);
                cout << "What is your current weight in kilograms?" << endl;
                cin >> weight;
                weight = calc.convertMetricWeightToLB(weight);
                cout << "What is your goal weight?" << endl;
                cin >> goalWeight;
                goalWeight = calc.convertMetricWeightToLB(goalWeight);
                cout << "How many weeks do you want to lose the weight in?" << endl;
                cin >> weeks;
                cout << "What is your activity level: Sedentary, Slightly Active, Moderately Active, Active, or Very Active?" << endl;
                cin >> activity;
                cals = calc.caloriesPerDay(weight, goalWeight, height, weeks, activity, sex, age);
                weightToLose = weight - goalWeight;
                weightToLose = calc.convertImperialWeightToKG(weightToLose);
                cout << "You should eat " << cals << " calories to lose " << weightToLose << " kg in " << weeks << " weeks." << endl;
            } else {
                cout << "Invalid choice. Please try again." << endl;
            }
        }
    }
}

void printOptions() {
    cout << "Welcome to the Health Calculator!" << endl;
    cout << "Please select the option you would like to choose." << endl;
    cout << "1) Tell me my BMI" << endl;
    cout << "2) Tell me how many calories to eat to lose weight" << endl;
}
