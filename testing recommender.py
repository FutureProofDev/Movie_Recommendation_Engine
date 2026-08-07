from backend.recommender import predict_rating, get_user_cluster, get_model_info

print(get_model_info())

rating = predict_rating(age=25, gender="M", occupation="student",
                         genre_flags={"Action": 1, "Comedy": 1})
print("Predicted rating:", rating)

cluster = get_user_cluster(age=25, gender="M", occupation="student",
                            genre_avg_ratings={"Action": 4.5, "Comedy": 3.8})
print("Assigned cluster:", cluster)