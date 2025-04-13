import random
from datetime import datetime, timedelta
from faker import Faker
from sqlalchemy.orm import Session
from conf.db import SessionLocal
from entity.models import Student, Grade, Subject, Teacher, Group

fake = Faker("uk_UA")
Faker.seed(42)


def seed_database():
    # Create a session
    session: Session = SessionLocal()
    try:
        # Create groups
        groups = create_group(session)
        # Create teachers
        teachers = create_teacher(session)
        # Create subjects and assign teachers
        subjects = create_subject(session)
        # Assign teachers to subjects (many-to-many)
        assign_teachers_to_subjects(session, teachers, subjects)
        # Create students
        students = create_student(session, groups)
        # Create grades
        create_grades(session, students, subjects)
        # Commit the session
        session.commit()
        print("Database seeded successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
        session.rollback()
    finally:
        # Close the session
        session.close()


def create_group(session: Session):
    group_name = ["КН1", "ІПЗ4", "ПМ2"]
    groups = []
    for name in group_name:
        group = Group(name=name)
        session.add(group)
        groups.append(group)
    session.flush()
    return groups


def create_teacher(session: Session):
    teachers = []
    for _ in range(5):
        teacher = Teacher(
            first_name=fake.first_name(),
            second_name=fake.last_name(),
            email=fake.email(),
            phone=fake.phone_number(),
        )
        session.add(teacher)
        teachers.append(teacher)
    session.flush()
    return teachers


def create_subject(session: Session):
    subject_names = [
        "Хмарні обчислення",
        "Обʼєктно-орієнтоване програмування",
        "Математичне моделювання",
        "Аналіз інформаційних систем",
        "Засоби та методи обробки інформації",
        "Математичний аналіз",
        "Вступ до програмування",
        "Алгоритми і структури даних",
    ]
    subjects = []
    for name in subject_names:
        # Create subject without assigning teachers yet
        subject = Subject(name=name)
        session.add(subject)
        subjects.append(subject)
    session.flush()
    return subjects


def assign_teachers_to_subjects(session: Session, teachers: list, subjects: list):
    # For each subject, assign 1-3 teachers randomly
    for subject in subjects:
        # Select random number of teachers for this subject (1-3)
        num_teachers = random.randint(1, 3)
        # Select random teachers and assign them to this subject
        selected_teachers = random.sample(teachers, num_teachers)
        subject.teachers = selected_teachers
    session.flush()


def create_student(session: Session, groups: list):
    students = []
    for _ in range(50):
        student = Student(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            phone=fake.phone_number(),
            group=random.choice(groups),
        )
        session.add(student)
        students.append(student)
    session.flush()
    return students


def create_grades(session: Session, students: list, subjects: list):
    start_date = datetime.now() - timedelta(days=180)
    end_date = datetime.now()
    for student in students:
        student_subjects = random.sample(subjects, random.randint(5, 8))
        for subject in student_subjects:
            num_grades = random.randint(10, 20)
            for _ in range(num_grades):
                grade = Grade(
                    student_id=student.id,
                    subject_id=subject.id,
                    grade=random.randint(60, 100),
                    date_received=start_date
                    + timedelta(days=random.randint(0, (end_date - start_date).days)),
                )
                session.add(grade)
    session.flush()


if __name__ == "__main__":
    seed_database()
