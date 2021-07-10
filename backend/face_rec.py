import face_recognition
import numpy


def json_face_to_numpy_face(data):
    out = numpy.zeros(128, dtype=numpy.float64)
    for i in range(128):
        out[i] = data[str(i)]
    return out


def face_compare(faces, face):
    for f in faces:
        value = face_recognition.compare_faces([f[1]], face)[0]
        if value:
            return f[0]
    return -1


def detect_face(name_file):
    open_image = face_recognition.load_image_file(name_file)
    encoded_face = face_recognition.face_encodings(open_image)[0]
    return encoded_face


def load(conn):
    from db_post import get_faces
    tmp = get_faces(conn)
    out = []
    for i in tmp:
        row = [
            i[0],
            numpy.array(i[1], dtype=numpy.float64)
        ]
        out.append(row)
    return out


if __name__ == '__main__':
    from server_app import connection
    face_db = load(connection)
    print(face_db)
