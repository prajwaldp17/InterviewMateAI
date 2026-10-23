
def count_words(answer):
    words = answer.split()
    return len(words)



def normalize_word(word):
    word = word.lower().strip(".,!?;:")

    if word.endswith("ing") and len(word) > 5:
        word = word[:-3]

    elif word.endswith("ed") and len(word) > 4:
        word = word[:-2]

    elif word.endswith("s") and len(word) > 4:
        word = word[:-1]

    return word


def check_keywords(answer, keywords):
    answer_words = answer.split()
    normalized_words = []

    for word in answer_words:
        normalized_words.append(normalize_word(word))

    matched = []
    missing = []

    for keyword in keywords:
        normalized_keyword = normalize_word(keyword)

        if normalized_keyword in normalized_words:
            matched.append(keyword)
        else:
            missing.append(keyword)

    return matched, missing



def calculate_score(word_count, matched_count, total_keywords):
    length_score = min(word_count / 30, 1) * 5

    if total_keywords > 0:
        keyword_score = (matched_count / total_keywords) * 5
    else:
        keyword_score = 0

    total_score = round(length_score + keyword_score, 1)

    return (
        total_score,
        round(length_score, 1),
        round(keyword_score, 1)
    )


def give_suggestions(word_count, missing):
    suggestions = []

    if word_count < 15:
        suggestions.append(
            "Your answer is short. Explain your point in more detail."
        )

    if missing:
        suggestions.append(
            "Try covering these concepts: " + ", ".join(missing)
        )

    if word_count >= 15 and not missing:
        suggestions.append(
            "Good start! Try adding a real example to strengthen your answer."
        )

    return suggestions
