from flask import *
from pysnmp.hlapi import *

from pysnmp.entity.rfc3413.oneliner import cmdgen # ใช้กับ getblukCmd


# ipAddress = '192.168.204.131' #IP ที่ต้องการ SNMP ไป


ListDic = {}
ListName = {}
app = Flask(__name__)

def getSNMP(Community,ipAddress,OID):
        errorIndication, errorStatus, errorIndex, varBinds = next(
            getCmd(SnmpEngine(),
                CommunityData(Community, mpModel=0),
                UdpTransportTarget((ipAddress, 161)),
                ContextData(),
                ObjectType(ObjectIdentity(OID))))
            #สร้าง metdic ไว้เก็บข้อมูล
        for varBind in varBinds:
            return varBind[1]

def setSNMP(AdminStatus,OID):
    next(
        setCmd(SnmpEngine(),
            CommunityData(RW),
            UdpTransportTarget((ipAddress, 161)),
            ContextData(),
            ObjectType(ObjectIdentity(OID), Integer(2 if AdminStatus == 'Up' else 1)))
    )

def getblukCmd(Community,ipAddress):
    errorIndication, errorStatus, errorIndex, varBinds = cmdgen.CommandGenerator().bulkCmd(
                CommunityData(Community, mpModel=0),
                UdpTransportTarget((ipAddress, 161)),
                0,
                25,
                (1,3,6,1,2,1,2,2,1,2),
                (1,3,6,1,2,1,2,2,1,7),
                (1,3,6,1,2,1,2,2,1,8),
                (1,3,6,1,2,1,2,2,1,3)
            )
    for varBindsRow in varBinds:
        count = 1
        for name, val in varBindsRow:
            if count == 1 :
                interface=val.prettyPrint()
                ListDic[str(interface)]={}
            if count == 2:
                ListDic[str(interface)]['ROW'] = int(str(name)[-1])%2
                ListDic[str(interface)]['OIDadmin'] = str(name)
                ListDic[str(interface)]['AdminStatus'] = "Up" if val.prettyPrint() == '1' else "Down"
            if count == 3:
                ListDic[str(interface)]['OIDopen'] = str(name)
                ListDic[str(interface)]['OpenStatus'] =" Up" if val.prettyPrint() == '1' else "Down"
            if count == 4:
                ListDic[str(interface)]['Type'] = val.prettyPrint()
                if(val.prettyPrint() == '22'):
                    ListName['Serial_PORT'] = 1
            count+=1
@app.route("/")
def hello_word():
    # if request.method == 'POST': #ถ้า re เว็บ มี POST เข้ามา
    #     AdminStatus = request.form['AdminStatus']
    #     OID = request.form['OID']
    #     setSNMP(AdminStatus,OID)
    # # getSNMP()
    # getblukCmd()
    return render_template('index.html')#ไปเรียก index.html แล้วส่ง ListDic


@app.route("/monitor", methods=['GET', 'POST'])
def monitor():
    if request.method == 'POST': #ถ้า re เว็บ มี POST เข้ามา
        try:
            AdminStatus = request.form['AdminStatus']
            OID = request.form['OID']
            setSNMP(AdminStatus,OID)
        except :
            ListName.clear()
            global ipAddress 
            ipAddress = request.form['IP']
            global RO
            RO = request.form['RO']
            global RW 
            RW = request.form['RW']
            ListName['Name'] = getSNMP(RO,ipAddress,'.1.3.6.1.2.1.1.5.0')
    # getSNMP()
    
    ListDic.clear()
    getblukCmd(RO,ipAddress)
    return render_template('monitor.html',ListDic=ListDic,ListName=ListName,)#ไปเรียก index.html แล้วส่ง ListDic



if __name__ == '__main__':
    app.run(debug=True)
