with open("logic_input.txt", 'r') as f:
    lines = [entry.strip() for entry in f.readlines()]

def part1():
    #Init the number of ones as the number of zeros is not needed 
    oneCount = 0
    
    #Have alpha & sigma as strings
    alpha = ''
    sigma = ''
    
    #Start to loop through the input file
    for i in range (len(lines[0])):
        # Get the number of ones per "column" of bits
        oneCount = sum(int(lines[j][i]) for j in range(len(lines)))
       
        #Since I know the number of ones, I dont need the number of zeros because that is just the difference of the number of nums in the column
        if(oneCount > (len(lines) - oneCount)):
            # Alpha will just take the most common bit, sigma is just the opposite 
            alpha += '1'
            sigma += '0'
        else:
            alpha += '0'
            sigma += '1'
    #Return their product by using int(string, base) as a way to quickly convert from binary to decimal
    return int(alpha,2) * int(sigma, 2)

def part2():
    #Have delta and omega equal lines so we can effectivley 'filter' them
    delta = lines
    omega = lines

    #Loop through input file
    for i in range(len(lines[0])):
        
        #Count number of ones per column for delta only
        D_oneCount = sum(int(delta[j][i]) for j in range(len(delta)) if delta[j][i] == '1')
        #Count number of 0's per column, this may or may not be neccessary but I want to make sure I can account for a tie in counting within delta
        D_zeroCount = sum(int(delta[j][i])+1 for j in range(len(delta)) if delta[j][i] == '0')
       
        #Count number of ones per column for omega only
        O_oneCount = sum(int(omega[j][i]) for j in range(len(omega)) if omega[j][i] == '1')
        #Count number of 0's per column, this may or may not be neccessary but I want to make sure I can account for a tie in counting within omega
        O_zeroCount = sum(int(omega[j][i])+1 for j in range(len(omega)) if omega[j][i] == '0')

        #Keep going until length of delta = 1 then we are done 
        if(len(delta) != 1):
            #Check the counts of zeros & ones
            if(D_oneCount >= D_zeroCount):
                #Basically 'filter' delta and setting it equal to itself for next cycle
                delta = [item for item in delta if item[i][0] == '1']
            else:
                delta = [item for item in delta if item[i][0] == '0']
        #Keep going until length of omega = 1 then we are done with omega 
        if(len(omega) != 1):
            if(O_oneCount >= O_zeroCount):
                #Basically 'filter' omega and setting it equal to itself for next cycle
                omega = [item for item in omega if item[i][0] == '0']
            else:
                omega = [item for item in omega if item[i][0] == '1']
    #Convert binary to actual numbers
    return int(omega[0],2) * int(delta[0], 2)

#Main function to print the results of part 1 and part 2
def main():
    print("Part One: " + str(part1()))
    print("Part Two: " + str(part2()))
#Call main()
if __name__ == "__main__":
    main()