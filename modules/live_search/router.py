from .analyzer import analyze_question


def route(question):

    result = analyze_question(question)

    return result