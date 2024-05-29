from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from flask_cors import CORS
from utils import tupleToArrayDict
from enum import Enum

#Tipo Consultas
class TipoConsulta(Enum):
    PEDRIATRIA = 'Pediatria'
    URGENCIA = 'Urgencia'
    CGI = 'CGI'

#Estados Paciente
class EstadosPaciente(Enum):
    ATENDIDO = 'atendido'
    SALA_DE_ESPERA = 'sala de espera'
    PENDIENTE = 'pendiente'



app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = '<your_user>'
app.config['MYSQL_PASSWORD'] = '<your_password>'
app.config['MYSQL_DB'] = 'fonasa'
mysql = MySQL(app)

@app.route('/api/v1/hospitals', methods=['GET'])
def getAllHospitals():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT h.id, h.nombre, h.direccion, COUNT(DISTINCT c.id) AS consultasDisponibles, COUNT(DISTINCT co.id) AS consultasOcupadas, COUNT(DISTINCT p.id) AS pacientesPendientes,COUNT(DISTINCT pe.id) AS pacientesEnEspera FROM Hospital h LEFT JOIN Consulta c ON h.id = c.idHospital AND c.estado = 'en espera' LEFT JOIN Consulta co ON h.id = co.idHospital AND co.estado = 'ocupada' LEFT JOIN Paciente p ON h.id = p.idHospital AND p.estado = 'pendiente' LEFT JOIN Paciente pe ON h.id = pe.idHospital AND pe.estado = 'sala de espera' GROUP BY h.id;")
        column_names = [desc[0] for desc in cur.description]
        data = cur.fetchall()
        hospitals = tupleToArrayDict(column_names, data)
        if len(hospitals) > 0:
            return jsonify({ "status":200, "hospitals": hospitals})
        return jsonify({ "status": 204, "message": "Hospitals not found" })
    except:
        return jsonify({ "status": 500, "message": "Internal Server Error" })

@app.route('/api/v1/hospitals/<string:id_hospital>', methods=['GET'])
def getHospitalById(id_hospital):
    try:
        cur = mysql.connection.cursor()
        if not id_hospital.isnumeric():
            return jsonify({ "status": 400, "message": "Bad Request", "details": "ID hospital must be a number" })
        cur.execute("SELECT * FROM Hospital WHERE id = %s", (id_hospital,))
        column_names = [desc[0] for desc in cur.description]
        data = cur.fetchone()
        if data is not None:
            hospital = dict(zip(column_names, data))
            return jsonify({ "status":200, "hospital": hospital })
        return jsonify({ "status":404, "message":"Hospital not found" })
    except:
        return jsonify({ "status": 500, "message": "Internal Server Error" })

@app.route('/api/v1/hospitals', methods=['POST'])
def createHospital():
    try:
        _json = request.json
        _nombre = _json['nombre']
        _direccion = _json['direccion']
        if(_nombre and _direccion):
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO Hospital (nombre, direccion) VALUES (%s, %s)", (_nombre, _direccion))
            mysql.connection.commit()
            cur.execute("SELECT h.id, h.nombre, h.direccion, COUNT(DISTINCT c.id) AS consultasDisponibles, COUNT(DISTINCT co.id) AS consultasOcupadas, COUNT(DISTINCT p.id) AS pacientesPendientes, COUNT(DISTINCT pe.id) AS pacientesEnEspera FROM Hospital h LEFT JOIN Consulta c ON h.id = c.idHospital AND c.estado = 'en espera' LEFT JOIN Consulta co ON h.id = co.idHospital AND co.estado = 'ocupada' LEFT JOIN Paciente p ON h.id = p.idHospital AND p.estado = 'pendiente' LEFT JOIN Paciente pe ON h.id = pe.idHospital AND pe.estado = 'sala de espera' WHERE h.nombre = %s AND h.direccion = %s GROUP BY h.id;", (_nombre, _direccion))
            column_names = [desc[0] for desc in cur.description]
            data = cur.fetchone()
            if data is not None:
                hospital = dict(zip(column_names, data))
                return jsonify({ "status":201, "message": "Hospital created successfully", "hospital": hospital })
        
        return jsonify({ "status": 400, "message":"Bad Request" })
    except:
        return jsonify({ "status": 500, "message": "Internal Server Error" })

@app.route('/api/v1/hospitals/<string:id_hospital>', methods=['PUT'])
def updateHospital(id_hospital):
    try:
        _json = request.json
        _nombre = _json['nombre']
        _direccion = _json['direccion']
        if(_nombre and _direccion):
            cur = mysql.connection.cursor()
            if not id_hospital.isnumeric():
                return jsonify({ "status": 400, "message": "Bad Request", "details": "ID hospital must be a number" })
            cur.execute("UPDATE Hospital SET nombre = %s, direccion = %s WHERE id = %s", (_nombre, _direccion, id_hospital))
            mysql.connection.commit()
            return jsonify({ "status":200, "message": "Hospital updated successfully" })
        return jsonify({ "status": 400, "message":"Bad Request" })
    except:
        return jsonify({ "status": 500, "message": "Internal Server Error" })

@app.route('/api/v1/consultas', methods=['GET'])
def getAllConsultas():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Consulta")
        column_names = [desc[0] for desc in cur.description]
        data = cur.fetchall()
        consultas = tupleToArrayDict(column_names, data)
        return jsonify({ "status":200, "consultas": consultas })
    except:
        return jsonify({ "status": 500, "message": "Internal Server Error" })

@app.route('/api/v1/consultas/<string:id_consulta>', methods=['GET'])
def getConsultaById(id_consulta):
    try:
        cur = mysql.connection.cursor()
        if not id_consulta.isnumeric():
            return jsonify({ "status": 400, "message": "Bad Request", "details": "ID consulta must be a number" })
        cur.execute("SELECT * FROM Consulta WHERE id = %s", id_consulta)
        column_names = [desc[0] for desc in cur.description]
        data = cur.fetchone()
        if data is not None:
            consulta = dict(zip(column_names, data))
            return jsonify({ "status":200, "consulta": consulta })
        return jsonify({ "status": 404, "message": "Consulta not found" })
    except:
        return jsonify({ "status": 500, "message": "Internal Server Error" })

@app.route('/api/v1/hospitals/<string:id_hospital>/consultas', methods=['GET'])
def getConsultaByIdHospital(id_hospital):
    try:
        cur = mysql.connection.cursor()
        if not id_hospital.isnumeric():
            return jsonify({ "status": 400, "message": "Bad Request", "details": "ID hospital must be a number" })
        cur.execute("SELECT * FROM Consulta WHERE idHospital = %s", id_hospital)
        column_names = [desc[0] for desc in cur.description]
        data = cur.fetchall()
        consultas = tupleToArrayDict(column_names, data)
        return jsonify({ "status":200, "consultas": consultas })
    except:
        return jsonify({ "status": 500, "message": "Internal Server Error" })

@app.route('/api/v1/consultas', methods=['POST'])
def createConsulta():
    try:
        _json = request.json
        _nombreEspecialista = _json['nombreEspecialista']
        _tipoConsulta = _json['tipoConsulta']
        _idHospital = _json['idHospital']
        if(_nombreEspecialista and _tipoConsulta and _idHospital):
            if (_tipoConsulta not in TipoConsulta):
                return jsonify({ "status": 400, "message": "Bad Request", "details": "Tipo Consulta Not Allowed" })
            if type(_idHospital) != int:
                return jsonify({ "status": 400, "message": "Bad Request", "details": "idHospital must be a number" })
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM Hospital WHERE id=%s",(_idHospital,))
            hospital = cur.fetchone()
            if hospital is None:
                return jsonify({ "status": 404, "message": "Hospital not found" })
            
            cur.execute("INSERT INTO Consulta (nombreEspecialista, tipoConsulta, idHospital) VALUES (%s,%s,%s)",(_nombreEspecialista, _tipoConsulta, _idHospital))
            mysql.connection.commit()
            return jsonify({ "status":201, "message": "Consulta created successfully" })
        return jsonify({ "status": 400, "message": "Bad Request" })
    except:
        return jsonify({ "status": 500, "message": "Internal Server Error" })

@app.route('/api/v1/pacientes', methods=['GET'])
def getAllPacientes():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Paciente")
        column_names = [desc[0] for desc in cur.description]
        data = cur.fetchall()
        pacientes = tupleToArrayDict(column_names, data)
        return jsonify({ "status":200, "pacientes": pacientes })
    except:
        return jsonify({ "status": 500, "message": "Internal Server Error" })
    
@app.route('/api/v1/hospitals/<string:id_hospital>/pacientes', methods=['GET'])
def getPacientesByIdHospital(id_hospital):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Paciente WHERE idHospital=%s",(id_hospital,))
        column_names = [desc[0] for desc in cur.description]
        data = cur.fetchall()
        pacientes = tupleToArrayDict(column_names, data)
        if pacientes is None or len(pacientes) == 0:
            return jsonify({ "status": 404, "message": "Pacientes not found", "pacientes": [] })
        return jsonify({ "status":200, "pacientes": pacientes })
    except:
        return jsonify({ "status": 500, "message": "Internal Server Error" })


@app.route('/api/v1/pacientes/<string:id_paciente>', methods=['GET'])
def getPacienteById(id_paciente):
    try:
        if not id_paciente.isnumeric():
            return jsonify({ "status": 400, "message": "Bad Request", "details": "ID paciente must be a number" })
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Paciente WHERE id=%s",(id_paciente,))
        column_names = [desc[0] for desc in cur.description]
        data = cur.fetchone()
        if data is None:
            return jsonify({ "status": 404, "message": "Paciente not found" })
        paciente = dict(zip(column_names, data))
        return jsonify({ "status":200, "paciente": paciente })
    except:
        return jsonify({ "status": 500, "message": "Internal Server Error" })

@app.route('/api/v1/pacientes', methods=['POST'])
def createPaciente():
    try:
        _json = request.json
        _nombre = _json['nombre']
        _edad = _json['edad']
        _noHistoriaClinica = _json['noHistoriaClinica']
        _idHospital = _json['idHospital']
        if(_nombre and type(_edad) == int and type(_noHistoriaClinica) == int and _idHospital):
            if type(_idHospital) != int:
                return jsonify({ "status": 400, "message": "Bad Request", "details": "ID hospital must be a number" })
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM Hospital WHERE id=%s",(_idHospital,))
            if cur.fetchone() is None:
                return jsonify({ "status": 404, "message": "Hospital not found" })
            cur.execute("INSERT INTO Paciente (nombre, edad, noHistoriaClinica, idHospital) VALUES (%s, %s, %s, %s)",(_nombre, _edad, _noHistoriaClinica, _idHospital))
            mysql.connection.commit()
            cur.execute("SELECT * FROM Paciente WHERE nombre=%s AND edad=%s",(_nombre, _edad));
            column_names = [desc[0] for desc in cur.description]
            data = cur.fetchone()
            if data is None:
                return jsonify({ "status": 404, "message": "Paciente not found" })
            paciente = dict(zip(column_names, data))
            return jsonify({ "status":201, "message": "Paciente created successfully", "paciente": paciente })
        return jsonify({ "status": 400, "message":"Bad Request", "details": "Lack of properties" })
    except:
        return jsonify({ "status": 500, "message": "Internal Server Error" })

@app.route('/api/v1/pacientes/status', methods=['PUT'])
def changePatientStatus():
    try:
        _json = request.json
        _idPaciente = _json['id']
        _estado = _json['estado']
        if(_idPaciente and _estado):
            if not type(_idPaciente) == int:
                return jsonify({ "status": 400, "message": "Bad Request", "details":"ID paciente must be a number"})
            cur = mysql.connection.cursor()
            cur.execute("UPDATE Paciente SET estado = %s WHERE id=%s",( _estado, _idPaciente))
            print('error')
            mysql.connection.commit()
            cur.execute("SELECT * FROM Paciente WHERE id=%s",(_idPaciente,))
            column_names = [desc[0] for desc in cur.description]
            data = cur.fetchone()
            if data is None:
                return jsonify({ "status": 404, "message": "Paciente not found" })
            paciente = dict(zip(column_names, data))
            return jsonify({ "status":204, "paciente": paciente, "message":"Paciente updated successfully" })
    except:
        return jsonify({ "status": 500, "message": "Internal Server Error"})

@app.route('/api/v1/pacientes/ancianos', methods=['POST'])
def createPacienteAnciano():
    try:
        _json = request.json
        _tieneDieta = _json['tieneDieta']
        _idPaciente = _json['idPaciente']
        if(type(_tieneDieta) == bool and _idPaciente):
            if type(_idPaciente) != int:
                return jsonify({ "status": 400, "message": "Bad Request", "details": "ID paciente must be a number" })
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO PAnciano (tieneDieta, idPaciente) VALUES (%s, %s)", (_tieneDieta, _idPaciente))
            mysql.connection.commit()
            return jsonify({ "status":201, "message": "Paciente anciano created successfully" })
        return jsonify({ "status": 400, "message":"Bad Request", "details": "Incorrect Propertie/Value" })
    except:
        return jsonify({ "status": 500, "message": "Internal Server Error" })

@app.route('/api/v1/pacientes/ancianos', methods=['GET'])
def getAllPacientesAncianos():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT p.id, p.nombre, p.edad, p.noHistoriaClinica, p.idHospital, pa.tieneDieta FROM Paciente AS p INNER JOIN PAnciano as pa ON p.id = pa.idPaciente")
        column_names = [desc[0] for desc in cur.description]
        data = cur.fetchall()
        pacientes = tupleToArrayDict(column_names, data)
        return jsonify({ "status":200, "pacientes_ancianos": pacientes })
    except:
        return jsonify({ "status": 500, "message": "Internal Server Error"})

@app.route('/api/v1/pacientes/jovenes', methods=['POST'])
def createPacientesJovenes():
    try:
        _json = request.json
        _fumador = _json['fumador']
        _periodoFumando = _json['periodoFumando']
        _idPaciente = _json['idPaciente']
        if(type(_fumador) == bool and type(_periodoFumando) == int and _idPaciente):
            if type(_idPaciente) != int:
                return jsonify({ "status": 400, "message": "Bad Request", "details": "ID paciente must be a number" })
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO PJoven (fumador, periodoFumando, idPaciente) VALUES (%s, %s, %s)", (_fumador, _periodoFumando, _idPaciente))
            mysql.connection.commit()
            return jsonify({ "status":201, "message": "Paciente joven created successfully" })
        return jsonify({ "status": 400, "message":"Bad Request", "details": "Incorrect Property/Value" })
    except:
        return jsonify({ "status": 500, "message": "Internal Server Error" })

@app.route('/api/v1/pacientes/jovenes', methods=['GET'])
def getAllPacientesJovenes():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT p.id, p.nombre, p.edad, p.noHistoriaClinica, p.idHospital, pj.fumador, pj.periodoFumando FROM Paciente AS p INNER JOIN PJoven as pj ON p.id = pj.idPaciente")
        column_names = [desc[0] for desc in cur.description]
        data = cur.fetchall()
        pacientes = tupleToArrayDict(column_names, data)
        return jsonify({ "status":200, "pacientes_jovenes": pacientes })
    except:
        return jsonify({ "status": 500, "message": "Internal Server Error"})


@app.route('/api/v1/pacientes/ninnos', methods=['POST'])
def createPacientesNinnos():
    try:
        _json = request.json
        _relacionPesoEstatura = _json['relacionPesoEstatura']
        _idPaciente = _json['idPaciente']
        if(type(_relacionPesoEstatura) == int and _idPaciente):
            if type(_idPaciente) != int:
                return jsonify({ "status": 400, "message": "Bad Request", "details": "ID paciente must be an number" })
            if _relacionPesoEstatura <= 0 or _relacionPesoEstatura > 4:
                return jsonify({ "status": 400, "message": "Bad Request", "details": "Relación peso estatura must be greater than 0 and less than 4"})
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO PNinno (relacionPesoEstatura, idPaciente) VALUES (%s, %s)", (_relacionPesoEstatura, _idPaciente))
            mysql.connection.commit()
            return jsonify({ "status":201, "message": "Paciente ninno created successfully" })
        return jsonify({ "status": 400, "message":"Bad Request", "details": "Incorrect Property/Value" })
    except:
        return jsonify({ "status": 500, "message": "Internal Server Error" })


@app.route('/api/v1/pacientes/ninnos', methods=['GET'])
def getAllPacientesNinnos():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT p.id, p.nombre, p.edad, p.noHistoriaClinica, p.idHospital, pn.relacionPesoEstatura FROM Paciente AS p INNER JOIN PNinno as pn ON p.id = pn.idPaciente")
        column_names = [desc[0] for desc in cur.description]
        data = cur.fetchall()
        pacientes = tupleToArrayDict(column_names, data)
        return jsonify({ "status":200, "pacientes_ninnos": pacientes })
    except:
        return jsonify({ "status": 500, "message": "Internal Server Error"})

if __name__ == '__main__':
    app.run(port=4000, debug=True)