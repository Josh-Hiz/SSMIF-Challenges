#Set default values of 0.02 and 0.25 as per the header provided
def redistribute(weights, minL=0.02, maxL=0.25):
    '''
        Redistribute weights to fall within [min, max]
        Returns: weights (and prints sum)
    '''  
    #The amount lost when making the value and must be positive
    amountLost = 0
    #The denominator to be used within our proportion
    proportion = 0
    
    #While values within weights are not within the max and min
    while(min(weights) < minL or max(weights) > maxL):
        #Loop through weights
        for i in range(len(weights)):
            #Reduce any value that is greater than max to the max value and add to the net loss
            if(weights[i] > maxL):
                amountLost += weights[i] - maxL
                weights[i] = maxL
            #Increase any value that is less than min to the min value and add to the net loss
            elif(weights[i] < minL):
                amountLost += weights[i] - minL
                weights[i] = minL
                proportion += weights[i]
            #If the weight falls within bounds then there isnt anything we need to do, just add to the denominator
            elif(weights[i] > minL and weights[i] < maxL):
                proportion += weights[i]
        #When the final net loss and total for the denominator is calculated from the previous loop, multiply each value in the list by the fraction (proportion) and add to the list
        for i in range(len(weights)):
            #Do not need to distribute to max values
            if(weights[i] != maxL):
                #Make values of weights proportional
                weights[i] += (amountLost*(weights[i]/proportion))
    #Returns the total sum and the list of weights on a new line
    return "Total Sum: " + str(sum(weights)) + "\n  List of weights: " + str(weights)