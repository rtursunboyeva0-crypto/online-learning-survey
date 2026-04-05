import streamlit as st
import json
import csv
from datetime import datetime

APP_VERSION = 1.0
MAX_QUESTIONS = 25
MIN_QUESTIONS = 15
TOPIC_TITLE = "Online Resource Utilization and Digital Learning Engagement"
SUPPORTED_FORMATS = ("json", "txt", "csv")
VALID_ID_RANGE = range(1, 1000000000)
ALLOWED_EXTRA_CHARS = set(["-", "'", " "])
IMMUTABLE_FORMATS = frozenset({"json", "txt", "csv"})

PSYCHOLOGICAL_STATES = {
    "Excellent Psychological Adaptation": (0, 10),
    "Good Psychological State": (11, 20),
    "Average / Manageable State": (21, 30),
    "Mild Psychological Strain": (31, 40),
    "High Psychological Strain": (41, 50),
    "Critical Psychological Strain": (51, 60)
}


def load_questions(filename: str) -> list:
    with open(filename, "r", encoding="utf-8") as file:
        questions = json.load(file)

    if not isinstance(questions, list):
        raise ValueError("Questions file must contain a list.")

    if len(questions) < MIN_QUESTIONS or len(questions) > MAX_QUESTIONS:
        raise ValueError("The questionnaire must contain between 15 and 25 questions.")

    return questions


def validate_name(name: str) -> bool:
    if not name or not name.strip():
        return False

    cleaned_name = name.strip()
    index = 0

    while index < len(cleaned_name):
        ch = cleaned_name[index]
        if not (ch.isalpha() or ch in ALLOWED_EXTRA_CHARS):
            return False
        index += 1

    return True


def validate_student_id(student_id: str) -> bool:
    if not student_id.isdigit():
        return False

    numeric_id = int(student_id)
    if numeric_id not in VALID_ID_RANGE:
        return False

    return True


def validate_dob(dob: str) -> bool:
    try:
        parsed_date = datetime.strptime(dob, "%Y-%m-%d")
        today = datetime.today()

        if parsed_date >= today:
            return False

        age = today.year - parsed_date.year
        if age < 10 or age > 100:
            return False

        return True
    except ValueError:
        return False


def interpret_score(score: int) -> str:
    for state, score_range in PSYCHOLOGICAL_STATES.items():
        low, high = score_range
        if low <= score <= high:
            return state
    return "Unknown State"


def save_as_json(filename: str, data: dict) -> None:
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def save_as_txt(filename: str, data: dict) -> None:
    with open(filename, "w", encoding="utf-8") as file:
        file.write("ONLINE RESOURCE UTILIZATION AND DIGITAL LEARNING ENGAGEMENT\n")
        file.write("=" * 65 + "\n")
        file.write(f"Given Name: {data['given_name']}\n")
        file.write(f"Surname: {data['surname']}\n")
        file.write(f"Date of Birth: {data['date_of_birth']}\n")
        file.write(f"Student ID: {data['student_id']}\n")
        file.write(f"Total Score: {data['total_score']}\n")
        file.write(f"Psychological State: {data['psychological_state']}\n\n")

        file.write("Answers:\n")
        for answer in data["answers"]:
            file.write(
                f"Q{answer['question_id']}: {answer['question']}\n"
                f"Selected: {answer['selected_option']} | Score: {answer['score']}\n\n"
            )


def save_as_csv(filename: str, data: dict) -> None:
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Field", "Value"])
        writer.writerow(["Given Name", data["given_name"]])
        writer.writerow(["Surname", data["surname"]])
        writer.writerow(["Date of Birth", data["date_of_birth"]])
        writer.writerow(["Student ID", data["student_id"]])
        writer.writerow(["Total Score", data["total_score"]])
        writer.writerow(["Psychological State", data["psychological_state"]])
        writer.writerow([])
        writer.writerow(["Question ID", "Question", "Selected Option", "Score"])

        for answer in data["answers"]:
            writer.writerow([
                answer["question_id"],
                answer["question"],
                answer["selected_option"],
                answer["score"]
            ])


def build_result_record(given_name: str, surname: str, dob: str, student_id: str,
                        answers: list, total_score: int, state: str) -> dict:
    return {
        "topic_title": TOPIC_TITLE,
        "version": APP_VERSION,
        "given_name": given_name,
        "surname": surname,
        "date_of_birth": dob,
        "student_id": student_id,
        "total_score": total_score,
        "psychological_state": state,
        "answers": answers
    }


st.set_page_config(page_title=TOPIC_TITLE, page_icon="🧠", layout="centered")
st.title("🧠 Online Resource Utilization and Digital Learning Engagement")
st.write("This survey evaluates the student's psychological state in online learning.")

try:
    questions = load_questions("questions.json")
except Exception as e:
    st.error(f"Error loading questions: {e}")
    st.stop()

menu_choice = st.radio(
    "Choose an option:",
    ["Start a new questionnaire", "Load an existing result"]
)

if menu_choice == "Load an existing result":
    uploaded_file = st.file_uploader(
        "Upload a saved result file (JSON only for display):",
        type=["json"]
    )

    if uploaded_file is not None:
        try:
            loaded_data = json.load(uploaded_file)

            st.subheader("Loaded Result")
            st.write(f"**Given Name:** {loaded_data.get('given_name', '')}")
            st.write(f"**Surname:** {loaded_data.get('surname', '')}")
            st.write(f"**Date of Birth:** {loaded_data.get('date_of_birth', '')}")
            st.write(f"**Student ID:** {loaded_data.get('student_id', '')}")
            st.write(f"**Total Score:** {loaded_data.get('total_score', '')}")
            st.write(f"**Psychological State:** {loaded_data.get('psychological_state', '')}")

            with st.expander("Show Answers"):
                for ans in loaded_data.get("answers", []):
                    st.write(
                        f"Q{ans['question_id']}: {ans['question']} — "
                        f"{ans['selected_option']} (Score: {ans['score']})"
                    )
        except Exception as e:
            st.error(f"Could not load file: {e}")

elif menu_choice == "Start a new questionnaire":
    st.subheader("Student Information")

    given_name = st.text_input("Given Name")
    surname = st.text_input("Surname")
    dob = st.text_input("Date of Birth (YYYY-MM-DD)")
    student_id = st.text_input("Student ID Number")

    st.subheader("Questionnaire")

    selected_answers = []
    total_score = 0

    for q in questions:
        question_text = q["question"]
        option_labels = [option[0] for option in q["options"]]

        selected_label = st.radio(
            f"Q{q['id']}. {question_text}",
            option_labels,
            key=f"question_{q['id']}"
        )

        selected_score = 0
        for label, score in q["options"]:
            if label == selected_label:
                selected_score = score
                break

        selected_answers.append({
            "question_id": q["id"],
            "question": question_text,
            "selected_option": selected_label,
            "score": selected_score
        })

    save_format = st.selectbox(
        "Choose file format to save result:",
        ["json", "txt", "csv"]
    )

    if st.button("Submit Questionnaire"):
        errors = []

        if not validate_name(given_name):
            errors.append("Invalid given name. Only letters, spaces, hyphens, and apostrophes are allowed.")

        if not validate_name(surname):
            errors.append("Invalid surname. Only letters, spaces, hyphens, and apostrophes are allowed.")

        if not validate_dob(dob):
            errors.append("Invalid date of birth. Use YYYY-MM-DD and enter a logical past date.")

        if not validate_student_id(student_id):
            errors.append("Invalid student ID. Digits only are allowed.")

        is_valid = len(errors) == 0

        if not is_valid:
            for err in errors:
                st.error(err)
        else:
            total_score = 0
            for ans in selected_answers:
                total_score += ans["score"]

            if total_score < 0:
                state = "Invalid Score"
            elif 0 <= total_score <= 60:
                state = interpret_score(total_score)
            else:
                state = "Out of Range"

            result_record = build_result_record(
                given_name=given_name.strip(),
                surname=surname.strip(),
                dob=dob.strip(),
                student_id=student_id.strip(),
                answers=selected_answers,
                total_score=total_score,
                state=state
            )

            st.success("Questionnaire submitted successfully.")
            st.write(f"**Total Score:** {total_score}")
            st.write(f"**Psychological State:** {state}")

            base_filename = f"{student_id}_{given_name}_{surname}".replace(" ", "_")

            if save_format == "json":
                filename = f"{base_filename}.json"
                save_as_json(filename, result_record)
                with open(filename, "r", encoding="utf-8") as file:
                    st.download_button(
                        "Download JSON Result",
                        data=file.read(),
                        file_name=filename,
                        mime="application/json"
                    )

            elif save_format == "txt":
                filename = f"{base_filename}.txt"
                save_as_txt(filename, result_record)
                with open(filename, "r", encoding="utf-8") as file:
                    st.download_button(
                        "Download TXT Result",
                        data=file.read(),
                        file_name=filename,
                        mime="text/plain"
                    )

            else:
                filename = f"{base_filename}.csv"
                save_as_csv(filename, result_record)
                with open(filename, "r", encoding="utf-8") as file:
                    st.download_button(
                        "Download CSV Result",
                        data=file.read(),
                        file_name=filename,
                        mime="text/csv"
                    )