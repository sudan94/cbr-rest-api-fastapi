
import numpy as np
from sklearn import metrics
from sklearn.model_selection import train_test_split
from sklearn import neighbors
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

def similar_cases_knn(new_problem, case_library,numerical_features):
    df = pd.DataFrame(case_library)

    X = df[numerical_features]
    y = df[['solution_lockdown_policy_level', 'solution_mask_policy_level', 'solution_vaccine_policy_level']]

    df1 = pd.DataFrame([new_problem],columns=new_problem.keys())
    test_data = df1[numerical_features]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=2)
    model = neighbors.KNeighborsClassifier(n_neighbors=5)
    model.fit(X_train, y_train)
    knn = model.predict(test_data)
    df_prediction = pd.DataFrame(knn,columns=['solution_lockdown_policy_level', 'solution_mask_policy_level', 'solution_vaccine_policy_level'])
    return df_prediction

def similar_cases_decison_tree(new_problem, case_library,numerical_features):
    df = pd.DataFrame(case_library)
    X = df[numerical_features]
    y = df[['solution_lockdown_policy_level', 'solution_mask_policy_level', 'solution_vaccine_policy_level']]

    df1 = pd.DataFrame([new_problem],columns=new_problem.keys())
    test_data = df1[numerical_features]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=2)

    model = DecisionTreeClassifier()
    model.fit(X_train, y_train)
    y_pred = model.predict(test_data)
    df_decision_tree = pd.DataFrame(y_pred,columns=['solution_lockdown_policy_level', 'solution_mask_policy_level', 'solution_vaccine_policy_level'])
    return df_decision_tree

def similar_cases_random_forest(new_problem, case_library,numerical_features):
    df = pd.DataFrame(case_library)
    X = df[numerical_features]
    y = df[['solution_lockdown_policy_level', 'solution_mask_policy_level', 'solution_vaccine_policy_level']]

    df1 = pd.DataFrame([new_problem],columns=new_problem.keys())
    test_data = df1[numerical_features]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=2)

    model = DecisionTreeClassifier()
    model.fit(X_train, y_train)
    y_pred = model.predict(test_data)
    df_decision_tree = pd.DataFrame(y_pred,columns=['solution_lockdown_policy_level', 'solution_mask_policy_level', 'solution_vaccine_policy_level'])
    return df_decision_tree


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

    # return the k most similar cases
    most_similar_cases = []
    for i in range(k):
        case_id = distances[i][0]
        case = next(
            (case for case in case_library if case['id'] == case_id), None)
        most_similar_cases.append(case)

    return most_similar_cases

def calculate_metrices(case_library):
    df = pd.DataFrame(case_library)
    X = df[['problem_population', 'problem_age_distribution', 'problem_start_number_of_active_cases', 'problem_end_number_of_active_cases', 'problem_start_number_of_icu_active_cases', 'problem_end_number_of_icu_active_cases', 'problem_start_number_of_deaths', 'problem_end_number_of_deaths', 'problem_vaccinated_population','problem_average_temperature','problem_average_humidity','problem_mortality_rate','problem_infection_rate']]

    lables = ['solution_lockdown_policy_level', 'solution_mask_policy_level', 'solution_vaccine_policy_level']
    for i in lables:
        z = df[i]
        X_train_1, X_test_1, y_train_1, y_test_1 = train_test_split(X, z, test_size=0.15, random_state=2)
        evaluation_model = neighbors.KNeighborsClassifier(n_neighbors=5)
        evaluation_model.fit(X_train_1, y_train_1)
        y_pred = evaluation_model.predict(X_test_1)
        classification_report = metrics.classification_report(y_test_1, y_pred)
        confusion_matrix = metrics.confusion_matrix(y_test_1, y_pred)
        print(f"KNN ",i)
        print(classification_report)
        print(confusion_matrix)

        model = DecisionTreeClassifier()
        model.fit(X_train_1, y_train_1)
        decison_predict = model.predict(X_test_1)
        classification_report = metrics.classification_report(y_test_1, decison_predict)
        confusion_matrix = metrics.confusion_matrix(y_test_1, decison_predict)
        print(f"Decision Tree ",i)
        print(classification_report)
        print(confusion_matrix)
    return 0