import numpy as np


def find_similar_cases_by_distance(new_problem, case_library, k=4, distance_metric='euclidean'):
    # define distance function for numerical features
    def numerical_distance(case1, case2):
        # select numerical features to normalize
        numerical_features = ['problem_population', 'problem_age_distribution', 'problem_start_number_of_active_cases', 'problem_end_number_of_active_cases', 'problem_start_number_of_icu_active_cases', 'problem_end_number_of_icu_active_cases', 'problem_start_number_of_deaths', 'problem_end_number_of_deaths', 'problem_vaccinated_population','problem_average_temprature','problem_average_humidity','problem_mortality_rate','problem_infection_rate']

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