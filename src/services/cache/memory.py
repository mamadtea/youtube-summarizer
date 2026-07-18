users = {}



def set_language(
    user_id,
    language
):

    if user_id not in users:
        users[user_id] = {}

    users[user_id]["language"] = language





def get_language(
    user_id
):

    return users.get(
        user_id,
        {}
    ).get(
        "language",
        "English"
    )





def set_summary_type(
    user_id,
    summary_type
):

    if user_id not in users:
        users[user_id] = {}

    users[user_id]["summary_type"] = summary_type





def get_summary_type(
    user_id
):

    return users.get(
        user_id,
        {}
    ).get(
        "summary_type",
        "detailed"
    )