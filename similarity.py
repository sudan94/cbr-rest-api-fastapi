import numpy as np
from sklearn import metrics
from sklearn.model_selection import train_test_split
from sklearn import neighbors
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import StandardScaler
from sklearn import svm
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
def similar_cases_knn(new_problem, case_library):
    df = pd.DataFrame(case_library)
    X = df[['problem_population', 'problem_age_distribution', 'problem_start_number_of_active_cases', 'problem_end_number_of_active_cases', 'problem_start_number_of_icu_active_cases', 'problem_end_number_of_icu_active_cases', 'problem_start_number_of_deaths', 'problem_end_number_of_deaths', 'problem_vaccinated_population','problem_average_temperature','problem_average_humidity','problem_mortality_rate','problem_infection_rate']]
    y = df[['solution_lockdown_policy_level', 'solution_mask_policy_level', 'solution_vaccine_policy_level']]

    df1 = pd.DataFrame([new_problem],columns=new_problem.keys())
    test_data = df1[['problem_population', 'problem_age_distribution', 'problem_start_number_of_active_cases', 'problem_end_number_of_active_cases', 'problem_start_number_of_icu_active_cases', 'problem_end_number_of_icu_active_cases', 'problem_start_number_of_deaths', 'problem_end_number_of_deaths', 'problem_vaccinated_population','problem_average_temperature','problem_average_humidity','problem_mortality_rate','problem_infection_rate']]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=2)
    model = neighbors.KNeighborsClassifier(n_neighbors=5)
    model.fit(X_train, y_train)
    knn = model.predict(test_data)
    y_pred = model.predict(X_test)

    df_prediction = pd.DataFrame(knn,columns=['solution_lockdown_policy_level', 'solution_mask_policy_level', 'solution_vaccine_policy_level'])
    print("KNN")
    print(knn)

    y_test = y_test.transpose()
    df_prediction = df_prediction.transpose()


    model = DecisionTreeClassifier()
    model.fit(X_train, y_train)
    y_pred = model.predict(test_data)
    df_decision_tree = pd.DataFrame(y_pred,columns=['solution_lockdown_policy_level', 'solution_mask_policy_level', 'solution_vaccine_policy_level'])
    print("Decision tree")
    print(y_pred)
    # print (metrics.classification_report(list(y_test), list(df_decision_tree)))
    # print (metrics.confusion_matrix(list(y_test), list(df_decision_tree)))

    sc = StandardScaler()
    X_train = sc.fit_transform(X_train)
    X_test = sc.fit_transform(X_test)

    # linear regression
    # all parameters not specified are set to their defaults
    Linear_regression = LinearRegression()

    Linear_regression.fit(X_train, y_train)

    predictions = Linear_regression.predict(test_data)

    print(predictions)



def find_similar_cases_by_distance(new_problem, case_library, numerical_features, k=4, distance_metric='euclidean'):
    # define distance function for numerical features
    def numerical_distance(case1, case2):
        # select numerical features to normalize
        # numerical_features = ['problem_population', 'problem_age_distribution', 'problem_start_number_of_active_cases', 'problem_end_number_of_active_cases', 'problem_start_number_of_icu_active_cases', 'problem_end_number_of_icu_active_cases', 'problem_start_number_of_deaths', 'problem_end_number_of_deaths', 'problem_vaccinated_population','problem_average_temprature','problem_average_humidity','problem_mortality_rate','problem_infection_rate']

         # extract numerical features from inputs
        case1_num = np.array([case1[f] for f in numerical_features], dtype=float)
        case2_num = np.array([case2[f] for f in numerical_features], dtype=float)
                # calculate z-score normalization for both vectors
        case1_norm = (case1_num - np.mean(case1_num)) / np.std(case1_num)
        case2_norm = (case2_num - np.mean(case2_num)) / np.std(case2_num)
                # calculate Euclidean distance between the normalized vectors
        distance = np.linalg.norm(case1_norm - case2_norm)
                # return distance
        return distance

    # compute distance between new problem and each case in the case library
    distances = []
    for case in case_library:
        if distance_metric == 'euclidean':
            num_distance = numerical_distance(new_problem, case)
            distances.append((case['id'], num_distance))

    # sort distances in ascending order
    distances.sort(key=lambda x: x[1])
    print(numerical_features)

    # return the k most similar cases
    most_similar_cases = []
    for i in range(k):
        case_id = distances[i][0]
        case = next(
            (case for case in case_library if case['id'] == case_id), None)
        most_similar_cases.append(case)

    return most_similar_cases