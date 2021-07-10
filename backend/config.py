
import naming

database_setting = {
    naming.name: "AR_TESIS",
    naming.user: "postgres",
    naming.password: "Lang",
    naming.host: "localhost",
    naming.port: 5432
}

database_tables = {
    naming.users: [naming.id_user, naming.name, naming.middle_name, naming.surname, naming.semester, naming.id_group],
    naming.study_groups: [naming.id_group, naming.name],
    naming.courses: [naming.id_course, naming.name],
    naming.faces: [naming.id_face, naming.id_user, naming.face],
    naming.statuses: [naming.id_status, naming.type],
    naming.grades: [naming.id_grade, naming.id_user, naming.id_course, naming.semester, naming.id_status]
}

image_folder = "./src/Faces/"

info_to_client = [
    naming.name,
    naming.group,
    naming.grades
]

default_answer = [
    "Не учится",
    ""
]
