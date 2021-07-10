from psycopg2.extensions import AsIs

from config import database_tables, image_folder, info_to_client, default_answer
from face_rec import detect_face
import src.test_data as data
import naming

insert_sql = "insert into {} ({}) values ({});"

select_sql = "select ({}) from %s;"

select_grades_from_user_sql = "select c.{0}, s.{1}" \
                   " from {2} g inner join {3} u on g.{4} = u.{4} and g.{5} = u.{5}" \
                   " inner join {6} c on g.{7} = c.{7} inner join {8} s on g.{9} = s.{9}" \
                   " where u.{5} = %s;".format(
    naming.name, naming.type,
    naming.grades, naming.users, naming.semester, naming.id_user,
    naming.courses, naming.id_course, naming.statuses, naming.id_status
)

select_user_info_sql = "select u.{0}, s.{0}" \
                       " from {1} u inner join {2} s on u.{3} = s.{3}" \
                       " where u.{4} = %s;".format(
    naming.name,
    naming.users, naming.study_groups, naming.id_group,
    naming.id_user
)


def format_insert(table_name, table_column):
    return insert_sql.format(table_name, ','.join(table_column[1:]), ','.join(["%s"] * (len(table_column) - 1)))


def format_select(column):
    return select_sql.format(','.join(["%s"] * (len(column))))


def append_data(conn, table, d):
    sql_q = format_insert(*table)
    cur = conn.cursor()
    cur.executemany(sql_q, d)
    cur.close()
    conn.commit()


def append_faces(conn, img_folder, table, d):
    sql_q = format_insert(naming.faces, table)
    cur = conn.cursor()
    for face in d:
        img_name = img_folder + face[1]
        d_face = list(detect_face(img_name))
        cur.execute(sql_q, [face[0], d_face])
    cur.close()
    conn.commit()


def _select_all(conn, col, table):
    cur = conn.cursor()
    sql_q = format_select(col)
    cur.execute(sql_q, [*map(AsIs, col), AsIs(table)])
    d = cur.fetchall()
    cur.close()
    return d


def get_faces(conn):
    out = [[*u_id, *u_face] for u_id, u_face in zip(
        _select_all(conn, [naming.id_user], naming.faces),
        _select_all(conn, [naming.face], naming.faces)
    )]
    return out


def get_info(conn, user_id):
    cur = conn.cursor()
    out = dict()

    cur.execute(select_user_info_sql, [AsIs(user_id)])
    try:
        out_info = cur.fetchall()[0]
    except IndexError:
        out_info = default_answer

    for i in range(len(out_info)):
        out[info_to_client[i]] = out_info[i]

    cur.execute(select_grades_from_user_sql, [AsIs(user_id)])
    out_grades = cur.fetchall()
    out[info_to_client[-1]] = out_grades

    cur.close()
    return out


def init_data(conn):
    # init study groups
    #append_data(conn, [naming.study_groups, database_tables[naming.study_groups]], data.data_study)
    # init user
    #append_data(conn, [naming.users, database_tables[naming.users]], data.data_users)
    # init courses
    #append_data(conn, [naming.courses, database_tables[naming.courses]], data.data_courses)
    # init statuses
    #append_data(conn, [naming.statuses, database_tables[naming.statuses]], data.data_statuses)
    # init grades
    #append_data(conn, [naming.grades, database_tables[naming.grades]], data.data_grades)
    # init face
    append_faces(conn, image_folder, database_tables[naming.faces], data.data_faces)


if __name__ == '__main__':
    from server_app import connection
    init_data(connection)
    #print(get_info(connection, 14))
    connection.close()
