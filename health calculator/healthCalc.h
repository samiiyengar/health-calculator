//
//  healthCalc.h
//  health calculator
//
//  Created by Samyukta Iyengar on 1/1/20.
//  Copyright © 2020 Samyukta Iyengar. All rights reserved.
//

#ifndef healthCalc_h
#define healthCalc_h

#include <iostream>
#include <string>

using namespace std;

#endif /* healthCalc_h */

class HealthCalc {
    
public:
    
    double calculateBMI(double weight, double height);
    
    string checkBMI(double bmi);
    
    
    double convertImperialHeightToMeters(double height);
    
    double convertImperialWeightToKG(double weight);
    
    double convertMetricHeightToInches(double height);
    
    double convertMetricWeightToLB(double weight);
    
    double convertCMtoM(double height);
    
    int caloriesPerDay(double weight, double goalWeight, double height, int weeks, int activity, string sex, int age);
    
private:
    
    double b;
    
};

