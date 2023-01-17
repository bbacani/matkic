import random


def generate_question(game_mode, level):
    # Generate two random numbers based on the level
    if game_mode == "addition" or game_mode == "subtraction":
        num_range = generate_numbers_add_or_sub(level)
    elif game_mode == "multiplication" or game_mode == "division":
        num_range = generate_numbers_mul_or_div(level)
    else:
        raise ValueError("Invalid game mode")
    num1 = random.randint(*num_range)
    num2 = random.randint(*num_range)

    if game_mode == "addition":
        question = f"Koliko je \n{num1} + {num2}?"
        answer = num1 + num2
    elif game_mode == "subtraction":
        question = f"Koliko je \n{num1} - {num2}?"
        answer = num1 - num2
    elif game_mode == "multiplication":
        question = f"Koliko je \n{num1} * {num2}?"
        answer = num1 * num2
    elif game_mode == "division":
        # Make sure the dividend is divisible by the divisor
        dividend = num1 * num2
        divisor = num1
        question = f"Koliko je \n{dividend} / {divisor}?"
        answer = round(dividend / divisor)
    else:
        raise ValueError("Invalid game mode")

    return question, answer


def generate_choices(answer, level):
    # Generate three random numbers between the answer and the number range of the level
    num_range = generate_numbers_add_or_sub(level)
    choices = []
    max_iterations = 1000
    num_iterations = 0
    while len(choices) < 3:
        if num_iterations == max_iterations:
            break
        choice = round(random.uniform(min(num_range), answer))
        if choice not in choices and choice != answer:
            choices.append(choice)
        num_iterations += 1
    while len(choices) < 3:
        choice = random.randint(*num_range)
        if choice not in choices and choice != answer:
            choices.append(choice)
    # Append the correct answer to the list and shuffle it
    choices.append(answer)
    random.shuffle(choices)
    return choices


def generate_numbers_add_or_sub(level):
    if level == 1:
        num_range = (1, 10)
    elif level == 2:
        num_range = (10, 50)
    elif level == 3:
        num_range = (50, 100)
    elif level == 4:
        num_range = (100, 200)
    else:
        raise ValueError("Invalid level")
    return num_range


def generate_numbers_mul_or_div(level):
    if level == 1:
        num_range = (1, 5)
    elif level == 2:
        num_range = (1, 10)
    elif level == 3:
        num_range = (5, 15)
    elif level == 4:
        num_range = (10, 20)
    else:
        raise ValueError("Invalid level")
    return num_range
