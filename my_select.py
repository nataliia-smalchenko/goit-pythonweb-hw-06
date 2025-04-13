from sqlalchemy import func, desc, select, and_
from sqlalchemy.orm import Session

from conf.db import SessionLocal
from entity.models import teacher_subject, Student, Grade, Subject, Teacher, Group
from pprint import pprint


def select_1(session: Session) -> list[dict]:
    """
    Знайти 5 студентів із найбільшим середнім балом з усіх предметів
    """
    result = (
        session.query(
            Student.id,
            Student.full_name,
            func.avg(Grade.grade).label("avg_grade"),
        )
        .join(Grade, Student.id == Grade.student_id)
        .group_by(Student.id)
        .order_by(desc("avg_grade"))
        .limit(5)
        .all()
    )

    return [
        {
            "id": student.id,
            "full_name": student.full_name,
            "avg_grade": (
                round(student.avg_grade, 2) if student.avg_grade else student.avg_grade
            ),
        }
        for student in result
    ]


def select_2(session: Session, subject_id: int) -> dict:
    """
    Знайти студента із найвищим середнім балом з певного предмета.
    """
    result = (
        session.query(
            Student.id,
            Student.full_name,
            func.avg(Grade.grade).label("avg_grade"),
        )
        .join(Grade, Student.id == Grade.student_id)
        .filter(Grade.subject_id == subject_id)
        .group_by(Student.id)
        .order_by(desc("avg_grade"))
        .first()
    )

    if result:
        return {
            "id": result.id,
            "full_name": result.full_name,
            "avg_grade": (
                round(result.avg_grade, 2) if result.avg_grade else result.avg_grade
            ),
        }
    return {}


def select_3(session: Session, subject_id: int) -> list[dict]:
    """
    Знайти середній бал у групах з певного предмета
    """
    result = (
        session.query(
            Group.id,
            Group.name,
            func.avg(Grade.grade).label("avg_grade"),
            func.count(Grade.student_id).label("student_count"),
        )
        .select_from(Grade)
        .join(Student, Grade.student_id == Student.id)
        .join(Group, Student.group_id == Group.id)
        .filter(Grade.subject_id == subject_id)
        .group_by(Group.id)
        .order_by(desc("avg_grade"))
        .all()
    )

    return [
        {
            "id": group.id,
            "name": group.name,
            "avg_grade": (
                round(group.avg_grade, 2) if group.avg_grade else group.avg_grade
            ),
            "student_count": group.student_count,
        }
        for group in result
    ]


def select_4(session: Session) -> list[dict]:
    """
    Знайти середній бал на потоці (по всій таблиці оцінок)
    """
    result = (
        session.query(
            Group.id,
            Group.name,
            func.avg(Grade.grade).label("avg_grade"),
        )
        .select_from(Grade)
        .join(Student, Grade.student_id == Student.id)
        .join(Group, Student.group_id == Group.id)
        .group_by(Group.id)
        .order_by(Group.name)
        .all()
    )

    return [
        {
            "id": group.id,
            "name": group.name,
            "avg_grade": (
                round(group.avg_grade, 2) if group.avg_grade else group.avg_grade
            ),
        }
        for group in result
    ]


def select_4_1(session: Session) -> float:
    """
    Знайти середній бал серед усіх оцінок (якщо усі групи стосуються одного потоку)
    """
    result = session.query(func.avg(Grade.grade).label("avg_grade")).scalar()

    return round(result, 2) if result else result


def select_5(session: Session, teacher_id: int) -> list[dict]:
    """
    Знайти які курси читає певний викладач
    """
    result = (
        session.query(Subject.id, Subject.name)
        .join(Subject.teachers)
        .filter(Teacher.id == teacher_id)
        .all()
    )

    return [{"id": subject.id, "name": subject.name} for subject in result]


def select_6(session: Session, group_id: int) -> list[dict]:
    """
    Знайти список студентів у певній групі
    """
    result = (
        session.query(
            Student.id,
            Student.full_name,
            Student.email,
        )
        .filter(Student.group_id == group_id)
        .order_by(Student.last_name, Student.first_name)
        .all()
    )

    return [
        {
            "id": student.id,
            "full_name": student.full_name,
            "email": student.email,
        }
        for student in result
    ]


def select_7(session: Session, group_id: int, subject_id: int) -> list[dict]:
    """
    Знайти оцінки студентів у окремій групі з певного предмета
    """
    result = (
        session.query(
            Student.id,
            Student.full_name,
            Grade.grade,
            Grade.date_received,
        )
        .select_from(Grade)
        .join(Student, Grade.student_id == Student.id)
        .filter(and_(Student.group_id == group_id, Grade.subject_id == subject_id))
        .order_by(Student.full_name, Grade.date_received)
        .all()
    )

    return [
        {
            "student_id": record.id,
            "full_name": record.full_name,
            "grade": record.grade,
            "date_received": record.date_received.strftime("%Y-%m-%d"),
        }
        for record in result
    ]


def select_8(session: Session, teacher_id: int) -> list[dict]:
    """
    Знайти середній бал, який ставить певний викладач зі своїх предметів
    (окремо по кожному з предметів)
    """
    result = (
        session.query(
            Subject.id.label("subject_id"),
            Subject.name.label("subject_name"),
            func.avg(Grade.grade).label("avg_grade"),
        )
        .join(Grade, Grade.subject_id == Subject.id)
        .join(teacher_subject, teacher_subject.c.subject_id == Subject.id)
        .filter(teacher_subject.c.teacher_id == teacher_id)
        .group_by(Subject.id, Subject.name)
        .all()
    )

    return [
        {
            "subject_id": subject.subject_id,
            "subject_name": subject.subject_name,
            "avg_grade": subject.avg_grade,
        }
        for subject in result
    ]


def select_9(session: Session, student_id: int) -> list[dict]:
    """
    Знайти список курсів, які відвідує певний студент
    """
    result = (
        session.query(Subject.id, Subject.name)
        .join(Grade, Subject.id == Grade.subject_id)
        .filter(Grade.student_id == student_id)
        .group_by(Subject.id)
        .order_by(Subject.name)
        .all()
    )

    return [{"id": subject.id, "name": subject.name} for subject in result]


def select_10(session: Session, student_id: int, teacher_id: int) -> list[dict]:
    """
    Список курсів, які певному студенту читає певний викладач
    """
    # First find all subjects taught by the teacher
    teacher_subjects_subquery = (
        select(Subject.id)
        .join(Subject.teachers)
        .where(Teacher.id == teacher_id)
        .subquery()
    )

    # Then find all subjects that the student is taking from those subjects
    result = (
        session.query(Subject.id, Subject.name)
        .join(Grade, Subject.id == Grade.subject_id)
        .filter(
            and_(
                Grade.student_id == student_id,
                Subject.id.in_(teacher_subjects_subquery),
            )
        )
        .group_by(Subject.id)
        .order_by(Subject.name)
        .all()
    )

    return [{"id": subject.id, "name": subject.name} for subject in result]


if __name__ == "__main__":
    with SessionLocal() as session:

        result_1 = select_1(session)
        result_2 = select_2(session, 8)
        result_3 = select_3(session, 8)
        result_4 = select_4(session)
        result_4_1 = select_4_1(session)
        result_5 = select_5(session, 1)
        result_6 = select_6(session, 1)
        result_7 = select_7(session, 1, 8)
        result_8 = select_8(session, 1)
        result_9 = select_9(session, 9)
        result_10 = select_10(session, 9, 1)

        print(
            "\nЗнайти 5 студентів із найбільшим середнім балом з усіх предметів:",
        )
        pprint(result_1)

        print("\nЗнайти студента із найвищим середнім балом з певного предмета:")
        pprint(result_2)

        print("\nЗнайти середній бал у групах з певного предмета:")
        pprint(result_3)

        print("\nЗнайти середній бал на потоці (по всій таблиці оцінок):")
        pprint(result_4)

        print("\nСередній бал серед усіх оцінок:")
        pprint(result_4_1)

        print("\nЗнайти які курси читає певний викладач:")
        pprint(result_5)

        print("\nЗнайти список студентів у певній групі:")
        pprint(result_6)

        print("\nЗнайти оцінки студентів у окремій групі з певного предмета:")
        pprint(result_7)

        print("\nЗнайти середній бал, який ставить певний викладач зі своїх предметів:")
        pprint(result_8)

        print("\nЗнайти список курсів, які відвідує певний студент:")
        pprint(result_9)

        print("\nСписок курсів, які певному студенту читає певний викладач:")
        pprint(result_10)
