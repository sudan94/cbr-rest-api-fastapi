def categorize_density(density, population):
    if (population >= 50000 and density >= 1500):
        return 3, "high"
    elif (population >= 5000 and density >= 300):
        return 2, "moderate"
    elif (density < 300):
        return 1, "low"
    else:
        return 0, "none"

def categorize_age(medain_age):
    if (medain_age > 30):
        return 3, "high"
    elif (medain_age >= 20 and medain_age <= 30):
        return 2, "moderate"
    elif (medain_age >= 1 and medain_age < 20):
        return 1, "low"
    else:
        return 0, "none"

def claculate_effectivness(start_case, end_case, start_icu, end_icu):
    if start_case == 0 and end_case !=0:
        percentage_change_case = end_case /(start_case + end_case) *100
    elif start_case ==0 and end_case == 0:
        percentage_change_case = 0
    else:
        percentage_change_case = ((end_case - start_case) / start_case) * 100
    if start_icu ==0 and end_icu != 0:
        percentage_change_icu = end_icu / (start_icu + end_case) * 100
    elif start_icu == 0 and end_icu == 0:
        percentage_change_icu =0
    else:
        percentage_change_icu = ((end_icu - start_icu) / start_icu) * 100
    average_perecentage = percentage_change_case + percentage_change_icu /2

    if average_perecentage > 0:
        return 1
    else:
        if abs(average_perecentage) > 70 or abs(average_perecentage) == 0:
            return 3
        elif abs(average_perecentage) > 50 and abs(average_perecentage) <=70:
            return 2
        else:
            return 1

def lockdown_policy(level):
    # Define the lockdown policy description based on the lockdown policy level
    if level == 0:
        lockdown_policy_description = "(no lockdown measures)"
    elif level == 1:
        lockdown_policy_description = "(recommend not leaving house)"
    elif level == 2:
        lockdown_policy_description = "(require not leaving house with exceptions for daily exercise, grocery shopping, and ‘essential’ trips)"
    else:
        lockdown_policy_description = "(require not leaving house with minimal exceptions (e.g., allowed to leave only once every few days, or only one person can leave at a time, etc.)not implementing any lockdown policy)"
    return lockdown_policy_description

def mask_policy(level):
    # Define the mask policy description based on the mask policy level
    if level == 0:
        mask_policy_description = "(not required to wear mask)"
    elif level == 1:
        mask_policy_description = "(recommended to wear mask)"
    elif level == 2:
        mask_policy_description = "(required mask in some specified shared/public spaces outside the home with other people present, or some situations when social distancing not possible)"
    elif level == 3:
        mask_policy_description = "(required mask in all shared/public spaces outside the home with other people present or all situations when social distancing not possible)"
    else:
        mask_policy_description = "(required mask outside the home at all times, regardless of location or presence of other people)"
    return mask_policy_description

def vaccine_policy(level):
    # Define the vaccine policy description based on the mask policy level
    if level == 0:
        vaccine_policy_description = "(vaccination not avilable)"
    elif level == 1:
        vaccine_policy_description = "(vaccination avilable for ONE of the following: key workers/ clinically vulnerable groups / elderly groups)"
    elif level == 2:
        vaccine_policy_description = "(vaccination avilable for TWO of the following: key workers/ clinically vulnerable groups / elderly groups)"
    elif level == 3:
        vaccine_policy_description = "(vaccination avilable for all the following: key workers/ clinically vulnerable groups / elderly groups)"
    else:
        vaccine_policy_description = "(vaccination avilable for all three, plus partial additional availability *select broad groups/ages*)"
    return vaccine_policy_description
