import requests
from typing import Literal
from random import randint
import numpy as np

url = "https://e1kf0882p7.execute-api.us-east-1.amazonaws.com/default/latex2image"


def pngify(q: str) -> str:
    q = f"\\color{{white}}{{{q}}}"
    data = {"latexInput": q, "outputScale": "125%", "outputFormat": "PNG"}
    response = requests.post(url, json=data)
    return response.json()["imageUrl"]


def term(coeff, var):
    if coeff == 0:
        return ""
    if coeff == 1:
        return f"{var}"
    return f"{coeff}{var}"


def gen_easy_question() -> tuple[str, int]:
    a = randint(2, 20)
    b = randint(2, 20)
    c = randint(2, 20)

    eqtn_type = randint(0, 2)

    if eqtn_type == 0:
        q = f"{term(a, '$x$')} + {b} = {c}"
        a = (c - b) / a
    elif eqtn_type == 1:
        q = f"{term(a, '$x$')} - {b} = {c}"
        a = (c + b) / a
    elif eqtn_type == 2:
        q = f"{term(a, '$x$')} - {b} = -{c}"
        a = (b - c) / a

    return q, a


def gen_matrix():
    while True:
        matrix = np.random.randint(1, 10, (3, 3))
        if np.linalg.det(matrix) != 0:
            return matrix


def gen_matrix_question() -> tuple[str, int]:
    A = gen_matrix()
    v2 = np.random.randint(1, 10, (3, 1))
    Ainv = np.linalg.inv(A)
    v1 = np.dot(Ainv, v2)

    q = f"""\\noindent What is $x + y + z$ if  \\\\\\\\ \\noindent
$ {term(A[0][0], 'x')} + {term(A[0][1], 'y')} + {term(A[0][2], 'z')} = {v2[0][0]} $ \\\\
$ {term(A[1][0], 'x')} + {term(A[1][1], 'y')} + {term(A[1][2], 'z')} = {v2[1][0]} $ \\\\
$ {term(A[2][0], 'x')} + {term(A[2][1], 'y')} + {term(A[2][2], 'z')} = {v2[2][0]}$\\\\
    """
    # get the sum in one number
    a = v1[0] + v1[1] + v1[2]
    a = a[0]

    return (q, a)


def gen_hard_question() -> tuple[str, int]:
    a = randint(1, 20)
    b = randint(1, 20)
    c = randint(1, 10)

    q = f"Evaluate $\\int_0^{c}$ {a}$x$ + {b} $dx$"
    a = (a * (c**2) / 2) + (b * c)

    return q, a


impossible_qs = [
    {"q": "Solve the riemann hypothesis", "a": None},
    {
        "q": "Solve the navier-stokes existence and smoothness problem for the $n$-dimensional case",
        "a": None,
    },
    {"q": "Prove that $P = NP$", "a": None},
    {"q": "Prove that $P \\neq NP$", "a": None},
    {"q": "Prove that the continuum hypothesis is independent of ZFC", "a": None},
]


def get_question_and_answer(
    diff: Literal["easy", "medium", "hard", "impossible"]
) -> tuple[str, int]:
    if diff == "easy":
        q, a = gen_easy_question()
        return pngify(q), a
    elif diff == "medium":
        q, a = gen_matrix_question()
        return pngify(q), a
    elif diff == "hard":
        q, a = gen_hard_question()
        return pngify(q), a
    elif diff == "impossible":
        index = randint(0, len(impossible_qs) - 1)
        q, a = impossible_qs[index]["q"], impossible_qs[index]["a"]
        return pngify(q), None
    else:
        raise ValueError("Invalid difficulty")
