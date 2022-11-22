import psycopg
from psycopg import sql
import os
from typing import Union


# problem 1
def entire_search(CONNECTION: str, table_name: str) -> list:
    with psycopg.connect(CONNECTION) as conn:
        with conn.cursor() as cur:
            cur.execute(f"Select * from myschema.{table_name}")
            record = cur.fetchall()
            print(record)
            return


# problem 2
def search_by_studentID(CONNECTION: str, student_id: str) -> Union[list, None]:
    with psycopg.connect(CONNECTION) as conn:
        with conn.cursor() as cur:
            # 학번이 존재하는지 확인
            sql_str = """
                Select * from myschema.students as s where s."STUDENT_ID" = %s
            """
            cur.execute(sql_str, student_id.split())
            student_exists = cur.fetchone()
            if student_exists is None:
                print("Not Exist student with STUDENT ID : " + student_id)
                return

            # 입력된 학번 조회

            sql_str = """
                select 
                    s."NAME", 
                    s."STUDENT_ID", 
                    s."ADMISSION_YEAR", 
                    s."GRADE", 
                    c."MAJOR_NAME", 
                    c."COLLEGE_NAME", 
                    CASE WHEN s."GRADE" = 0 or s."GRADUATE_YEAR" != NULL THEN true ELSE false END AS "GRADUATED"
                from myschema.students as s, myschema.college as c
                where s."MAJOR_ID" = c."MAJOR_ID" and s."STUDENT_ID" = %s
            """

            cur.execute(sql_str, student_id.split())
            record = cur.fetchall()
            print(record)
            return


# problem 3
def search_by_studentname(CONNECTION: str, student_name: str) -> Union[list, None]:
    with psycopg.connect(CONNECTION) as conn:
        with conn.cursor() as cur:

            # 이름 존재 확인
            sql_str = """
                        Select * from myschema.students as s where s."NAME"
                    """

            if "%" in student_name:
                sql_str += f" LIKE %s"
                student_name.replace("%", "%%")
            else:
                sql_str += f" = %s"

            cur.execute(sql_str, [student_name])
            student_exists = cur.fetchone()
            if student_exists is None:
                print("Not Exist student with NAME Like: " + student_name)
                return

            # 입력된 이름 조회

            sql_str = """
                select 
                    s."NAME", 
                    s."STUDENT_ID", 
                    s."ADMISSION_YEAR", 
                    s."GRADE", 
                    c."MAJOR_NAME", 
                    c."COLLEGE_NAME", 
                    CASE WHEN s."GRADE" = 0 or s."GRADUATE_YEAR" != NULL THEN true ELSE false END AS "GRADUATED"
                from myschema.students as s, myschema.college as c
                where s."MAJOR_ID" = c."MAJOR_ID" and s."NAME"
            """

            if "%" in student_name:
                sql_str += f" LIKE %s"
            else:
                sql_str += f" = %s"

            cur.execute(sql_str, [student_name])
            record = cur.fetchall()
            print(record)
            return


# problem 4
def registration_history(CONNECTION: str, student_id: str) -> Union[list, None]:
    with psycopg.connect(CONNECTION) as conn:
        with conn.cursor() as cur:
            sql_str = """
                    select c."YEAR", c."SEMESTER", c."COURSE_ID_PREFIX", c."COURSE_ID_NO", c."DIVISION_NO", c."COURSE_NAME", f."NAME" as "PROF_NAME", g."GRADE"::float
                    from myschema.course_registration as cr, myschema.course as c, myschema.faculty as f, myschema.grade as g
                    where c."PROF_ID" = f."ID" and cr."STUDENT_ID" = %s and cr."COURSE_ID" = c."COURSE_ID" and cr."COURSE_ID" = g."COURSE_ID" and cr."STUDENT_ID" = g."STUDENT_ID"
                    order by c."YEAR", c."SEMESTER", c."COURSE_NAME" ASC
                """
            cur.execute(sql_str, student_id.split())
            record = cur.fetchall()
            if record is None or len(record) == 0:
                print("Not Exist student with STUDENT ID: " + student_id)
                return
            else:
                print(record)
                return


# problem 5
def registration(CONNECTION: str, course_id: int, student_id: str) -> Union[list, None]:
    with psycopg.connect(CONNECTION) as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("""
                select * from myschema.course as c where c."COURSE_ID" = %s and c."YEAR" = 2022 and c."SEMESTER" = 2
                """, [course_id])
            course_exists = cur.fetchone()
            if course_exists is None:
                print("Not Exist course with COURSE ID: " + str(course_id))
                return

            cur.execute("""
                    select * from myschema.students as s where s."STUDENT_ID" = %s and (s."GRADE" != 0 or s."GRADUATE_YEAR" = NULL)
                    """, student_id.split())
            student_exists = cur.fetchone()
            if student_exists is None:
                print("Not Exist student with STUDENT ID: " + student_id)
                return

            cur.execute("""
                    select s."NAME", c."COURSE_NAME" 
                    from myschema.course_registration as cr, myschema.students as s, myschema.course as c 
                    where cr."STUDENT_ID" = s."STUDENT_ID" and cr."COURSE_ID" = c."COURSE_ID" and cr."STUDENT_ID" = %s and cr."COURSE_ID" = %s
                    """, [student_id, course_id])

            already_registered = cur.fetchone()
            if already_registered is not None:
                print(already_registered[0] + " is already registered in " + already_registered[1])
                return
            else:
                sql_str = """INSERT INTO myschema.course_registration("COURSE_ID", "STUDENT_ID") VALUES (%s, %s)"""
                cur.execute(sql_str, [course_id, student_id])
                entire_search(CONNECTION, 'course_registration')

# problem 6
def withdrawal_registration(CONNECTION: str, course_id: int, student_id: str) -> Union[list, None]:
    with psycopg.connect(CONNECTION) as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("""
                        select c."COURSE_NAME" from myschema.course as c where c."COURSE_ID" = %s and c."YEAR" = 2022 and c."SEMESTER" = 2
                        """, [course_id])
            course_exists = cur.fetchone()
            if course_exists is None:
                print("Not Exist course with COURSE ID: " + str(course_id))
                return
            else:
                course_name = course_exists[0]

            cur.execute("""
                        select s."NAME" from myschema.students as s where s."STUDENT_ID" = %s and (s."GRADE" != 0 or s."GRADUATE_YEAR" = NULL)
                        """, student_id.split())
            student_exists = cur.fetchone()
            if student_exists is None or len(student_exists) == 0:
                print("Not Exist student with STUDENT ID: " + student_id)
                return
            else:
                student_name = student_exists[0]

            cur.execute("""
                        select *
                        from myschema.course_registration as cr
                        where cr."STUDENT_ID" = %s and cr."COURSE_ID" = %s
                        """, [student_id, course_id])

            registered = cur.fetchone()
            if registered is None:
                print(student_name + " is not registrated in " + course_name)
                return
            else:
                sql_str = """delete from myschema.course_registration as cr where cr."COURSE_ID" = %s and cr."STUDENT_ID" = %s"""
                cur.execute(sql_str, [course_id, student_id])
                entire_search(CONNECTION, 'course_registration')



# problem 7
def modify_lectureroom(CONNECTION: str, course_id: int, buildno: str, roomno: str) -> Union[list, None]:
    with psycopg.connect(CONNECTION) as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("""select * from myschema.course as c where c."COURSE_ID" = %s and c."YEAR" = 2022 and c."SEMESTER" = 2""", [course_id])
            course_exists = cur.fetchone()
            if course_exists is None:
                print("Not Exist course with COURSE ID: " + str(course_id))
                return

            cur.execute("""select * from myschema.lectureroom as l where l."BUILDNO" = %s and l."ROOMNO" = %s""", [buildno, roomno])
            lectureroom_exists = cur.fetchone()
            if lectureroom_exists is None:
                print("Not Exist lecture room with BUILD NO: " + buildno + " / ROOM NO: " + roomno)
                return
            else:
                sql_str = """update myschema.course set "BUILDNO" = %s, "ROOMNO" = %s where "COURSE_ID" = %s"""
                cur.execute(sql_str, [buildno, roomno, course_id])
                entire_search(CONNECTION, 'course')



# sql file execute ( Not Edit )
def execute_sql(CONNECTION, path):
    folder_path = '/'.join(path.split('/')[:-1])
    file = path.split('/')[-1]
    if file in os.listdir(folder_path):
        with psycopg.connect(CONNECTION) as conn:
            conn.execute(open(path, 'r', encoding='utf-8').read())
            conn.commit()
        print("{} EXECUTRED!".format(file))
    else:
        print("{} File Not Exist in {}".format(file, folder_path))