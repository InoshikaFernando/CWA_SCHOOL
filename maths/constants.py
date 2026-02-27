# Year-to-topics mapping for dashboard display and question loading.
# Maps year number to list of (topic_name, url_name, display_name).
# This is the single source of truth used by views.py and add_questions_from_json.py.
YEAR_TOPICS_MAP = {
    2: [
        ("Measurements", "measurements_questions", "Measurements"),
        ("Place Values", "place_values_questions", "Place Values"),
    ],
    3: [
        ("Measurements", "measurements_questions", "Measurements"),
        ("Fractions", "fractions_questions", "Fractions"),
        ("Finance", "finance_questions", "Finance"),
        ("Date and Time", "date_time_questions", "Date and Time"),
    ],
    4: [
        ("Fractions", "fractions_questions", "Fractions"),
        ("Integers", "integers_questions", "Integers"),
        ("Place Values", "place_values_questions", "Place Values"),
    ],
    5: [
        ("Measurements", "measurements_questions", "Measurements"),
        ("BODMAS/PEMDAS", "bodmas_questions", "BODMAS/PEMDAS"),
    ],
    6: [
        ("Measurements", "measurements_questions", "Measurements"),
        ("BODMAS/PEMDAS", "bodmas_questions", "BODMAS/PEMDAS"),
        ("Whole Numbers", "whole_numbers_questions", "Whole Numbers"),
        ("Factors", "factors_questions", "Factors"),
        ("Angles", "angles_questions", "Angles"),
    ],
    7: [
        ("Measurements", "measurements_questions", "Measurements"),
        ("BODMAS/PEMDAS", "bodmas_questions", "BODMAS/PEMDAS"),
        ("Integers", "integers_questions", "Integers"),
        ("Factors", "factors_questions", "Factors"),
        ("Fractions", "fractions_questions", "Fractions"),
    ],
    8: [
        ("Trigonometry", "trigonometry_questions", "Trigonometry"),
        ("Integers", "integers_questions", "Integers"),
        ("Factors", "factors_questions", "Factors"),
        ("Fractions", "fractions_questions", "Fractions"),
    ],
}
