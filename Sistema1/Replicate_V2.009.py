SW="Replicate_V1.009"
HW="1.000"
Lista_Capacidades=['dth','ldr','ph','ec','wls','wp','sv','nd','led']
#""Bibliotecas.
import distutils.log
import json
import os
from pickle import TRUE
import socket
import threading
import time
import logging
import random
#""end

#""Variables_Globales.

global Coordinador
Coordinador=False

global DirCoordinador
DirCoordinador=('0.0.0.0',38020)

global UltimaVotacion
UltimaVotacion= time.monotonic()

global ListaDeSeguidores
ListaDeSeguidores=[]

global Seguidor
Seguidor=[]

global InicioEnsamblaje
global FinEnsamblaje

PuertoEscuchaLiderSupervivencia=38020
PuertoEscuchaSeguidorBuscaLider=44444
PuertoEscuchaGeneralSeguidor=37020
TiempoDeConsultaSupervivencia=5
PuertoEscuchaSeguidorPreguntaSupervivencia=39020
PuertoEscuchaParticularCoordinador=36020

#""end

#""Clases_Activas_FuncionalidadP.

#**PH.
class Ph:
    Lista_Capacidades_Necesaria=['ph']
    def ph(self):#Sensor de ph
        x=random.randint(100,400)
        return x
#**end
#**EC.
class Ec:
    Lista_Capacidades_Necesaria=['ec']
    def ec(self):#Sensor de electrocundictividad
        x=random.randint(10,500)
        return x
#**end
#**WLS.
class Wls:
    Lista_Capacidades_Necesaria=['wls']
    def wls(self):#Sensor de nivel de agua
        x=random.randint(1,20)
        return x
#**end
#**WP.
class Wp:
    Lista_Capacidades_Necesaria=['wp']
    EstadoBomba=False#Bomba de agua
    Nivel=10
    def wp(self,niveldeawa):
        if(niveldeawa<=9 and EstadoBomba==False):
            EstadoBomba=True
            print("bomba encendida")
        elif(niveldeawa>=10 and EstadoBomba==True):
            EstadoBomba=False
            print("bomba apagada")
#**end
#**SV.
class Sv:
    Lista_Capacidades_Necesaria=['sv']
    UltimoRiego= time.monotonic()
    def sv(self):#Valvula Selenoide
        HoraActual= time.monotonic()
        if((pow(pow((HoraActual-UltimoRiego),2),0.5)<2000.0)):
            print("flujo de agua encendido")
#**end
#**ND.
class Nd:
    Lista_Capacidades_Necesaria=['nd']
    def nd(self, electroconductividad):#Dosificador de nutrientes
        if(electroconductividad<100):
            print("docificado de nutrientes")
#**end
#**LED.
class Led:
    Lista_Capacidades_Necesaria=['led']
    def led(self, intensidadluminica):#Leds
        if(intensidadluminica<5):
            print("luz encendida")
#**end
#""end

#""Clases_Activas_CapacidadesSyS.
#**LecturaDeArchivos.
#region lectura
def Lee(Archivo):
    ArchivoLeer=open(Archivo,"r")
    ArchivoLeerLineas=ArchivoLeer.readlines()
    swlect=""
    hwlect=""
    Capacidades=[]
    Bibliotecas=[]
    Var_Globales=[]
    ClasesA_FP=[]
    ClasesA_CSyS=[]
    Hilos_FP_Activo=[]
    Hilos_SyS_Activo=[]
    Hilos_FP_Pasivo=[]
    ClasesP_FP=[]
    for NumeroLineaLectura in range(len(ArchivoLeerLineas)):
        aux=[]
        if NumeroLineaLectura==0:
            swlect=ArchivoLeerLineas[NumeroLineaLectura][15:20]

        elif NumeroLineaLectura==1:
            hwlect=ArchivoLeerLineas[NumeroLineaLectura][4:9]

        elif NumeroLineaLectura==2:
            Capacidades_Aux=ArchivoLeerLineas[NumeroLineaLectura][ArchivoLeerLineas[NumeroLineaLectura].find('[')+1 :ArchivoLeerLineas[NumeroLineaLectura].find(']')]
            Capacidades_Aux=Capacidades_Aux.replace("'", '')
            Capacidades=Capacidades_Aux.split(",")

        elif ArchivoLeerLineas[NumeroLineaLectura][0:15]=='#""Bibliotecas.':
            for i in range(NumeroLineaLectura , len(ArchivoLeerLineas)):
                aux.append(ArchivoLeerLineas[i])
                if ArchivoLeerLineas[i][0:6]=='#""end':
                    break
            Bibliotecas=aux
            aux=[]

        elif ArchivoLeerLineas[NumeroLineaLectura][0:22]=='#""Variables_Globales.':
                for i in range(NumeroLineaLectura , len(ArchivoLeerLineas)):
                    aux.append(ArchivoLeerLineas[i])
                    if ArchivoLeerLineas[i][0:6]=='#""end':
                        break
                Var_Globales=aux
                aux=[]

        elif ArchivoLeerLineas[NumeroLineaLectura][0:33]=='#""Clases_Activas_FuncionalidadP.':
            aux.append(ArchivoLeerLineas[NumeroLineaLectura])
            for i in range(NumeroLineaLectura+1 , len(ArchivoLeerLineas)):
                aux2=[]
                if ArchivoLeerLineas[i][0:3]=='#**' and ArchivoLeerLineas[i][0:6]!='#**end':
                    for j in range(i , len(ArchivoLeerLineas)):
                        aux2.append(ArchivoLeerLineas[j])
                        if ArchivoLeerLineas[j][0:6]=='#**end':
                            break
                    aux.append(aux2)
                if ArchivoLeerLineas[i][0:6]=='#""end':
                    aux.append(ArchivoLeerLineas[i])
                    break
            ClasesA_FP=aux
            aux=[]

        elif ArchivoLeerLineas[NumeroLineaLectura][0:33]=='#""Clases_Activas_CapacidadesSyS.':
            aux.append(ArchivoLeerLineas[NumeroLineaLectura])
            for i in range(NumeroLineaLectura+1 , len(ArchivoLeerLineas)):
                aux2=[]
                if ArchivoLeerLineas[i][0:3]=='#**' and ArchivoLeerLineas[i][0:6]!='#**end':
                    for j in range(i , len(ArchivoLeerLineas)):
                        aux2.append(ArchivoLeerLineas[j])
                        if ArchivoLeerLineas[j][0:6]=='#**end':
                            break
                    aux.append(aux2)
                if ArchivoLeerLineas[i][0:6]=='#""end':
                    aux.append(ArchivoLeerLineas[i])
                    break
            ClasesA_CSyS=aux
            aux=[]

        elif ArchivoLeerLineas[NumeroLineaLectura][0:20]=='#""Hilos_FP_Activos.':
            aux.append(ArchivoLeerLineas[NumeroLineaLectura])
            aux.append(ArchivoLeerLineas[NumeroLineaLectura+1])
            for i in range(NumeroLineaLectura+2 , len(ArchivoLeerLineas)):
                aux2=[]
                if ArchivoLeerLineas[i][0:3]=='#**' and ArchivoLeerLineas[i][0:6]!='#**end':
                    for j in range(i , len(ArchivoLeerLineas)):
                        aux2.append(ArchivoLeerLineas[j])
                        if ArchivoLeerLineas[j][0:6]=='#**end':
                            break
                    aux.append(aux2)
                if ArchivoLeerLineas[i][0:6]=='#""end':
                    aux.append(ArchivoLeerLineas[i])
                    break
            Hilos_FP_Activo=aux
            aux=[]

        elif ArchivoLeerLineas[NumeroLineaLectura][0:25]=='#""Hilos_Sistema_Activos.':
            aux.append(ArchivoLeerLineas[NumeroLineaLectura])
            for i in range(NumeroLineaLectura+1 , len(ArchivoLeerLineas)):
                if ArchivoLeerLineas[i][0:3]=='#**':
                    break
                aux.append(ArchivoLeerLineas[i])
            
            for i in range(NumeroLineaLectura+2 , len(ArchivoLeerLineas)):
                aux2=[]
                if ArchivoLeerLineas[i][0:3]=='#**' and ArchivoLeerLineas[i][0:6]!='#**end':
                    for j in range(i , len(ArchivoLeerLineas)):
                        aux2.append(ArchivoLeerLineas[j])
                        if ArchivoLeerLineas[j][0:6]=='#**end':
                            break
                    aux.append(aux2)
                if ArchivoLeerLineas[i][0:6]=='#""end':
                    aux.append(ArchivoLeerLineas[i])
                    break
            Hilos_SyS_Activo=aux
            aux=[]

        elif ArchivoLeerLineas[NumeroLineaLectura][0:32]=='#""Clases_Pasivo_FuncionalidadP.':
            aux.append(ArchivoLeerLineas[NumeroLineaLectura])
            for i in range(NumeroLineaLectura+1 , len(ArchivoLeerLineas)):
                aux2=[]
                if ArchivoLeerLineas[i][0:3]=='#**' and ArchivoLeerLineas[i][0:6]!='#**end':
                    for j in range(i , len(ArchivoLeerLineas)):
                        aux2.append(ArchivoLeerLineas[j])
                        if ArchivoLeerLineas[j][0:6]=='#**end':
                            break
                    aux.append(aux2)
                if ArchivoLeerLineas[i][0:6]=='#""end':
                    aux.append(ArchivoLeerLineas[i])
                    break
            ClasesP_FP=aux
            aux=[]

        elif ArchivoLeerLineas[NumeroLineaLectura][0:19]=='#""Hilos_FP_Pasivo.':
            aux.append(ArchivoLeerLineas[NumeroLineaLectura])
            
            for i in range(NumeroLineaLectura+1 , len(ArchivoLeerLineas)):
                aux2=[]
                if ArchivoLeerLineas[i][0:3]=='#**' and ArchivoLeerLineas[i][0:6]!='#**end':
                    for j in range(i , len(ArchivoLeerLineas)):
                        aux2.append(ArchivoLeerLineas[j])
                        if ArchivoLeerLineas[j][0:6]=='#**end':
                            break
                    aux.append(aux2)
                if ArchivoLeerLineas[i][0:6]=='#""end':
                    aux.append(ArchivoLeerLineas[i])
                    break
            Hilos_FP_Pasivo=aux
            aux=[]

        
    Desplegado=[]
    Desplegado.append(swlect)
    Desplegado.append(hwlect)
    Desplegado.append(Capacidades)
    Desplegado.append(Bibliotecas)
    Desplegado.append(Var_Globales)
    Desplegado.append(ClasesA_FP)
    Desplegado.append(ClasesA_CSyS)
    Desplegado.append(Hilos_FP_Activo)
    Desplegado.append(Hilos_SyS_Activo)
    Desplegado.append(ClasesP_FP)
    Desplegado.append(Hilos_FP_Pasivo)
    return Desplegado
#endregion
#**end

#**EnsambladorDeArvhivos
#region Ensamblador_archivos_pide_2_archivos
def EnsambladorDeArvhivos(TipoDeComposicion, Ar1, Ar2):
    ArchivoPropio=Lee(Ar1)
    ArchivoEntrante=Lee(Ar2)
    ArchivoNuevaComposicion=[]

    # concatenacion y creacion del numero de version de software.
    aux=0
    if float(ArchivoPropio[0])>float(ArchivoEntrante[0]):
        aux = float(ArchivoPropio[0])
    else:
        aux = float(ArchivoEntrante[0])
    Newsw=aux+0.001
    ArchivoNuevaComposicion.append(Newsw)

    # concatenacion de la version de hardware.
    ArchivoNuevaComposicion.append(ArchivoPropio[1])

    # concatenacion de lista de capacidades.
    # modificar esta linea es la que manda las capacidades y solo estan en forma de vector.    
    ArchivoNuevaComposicion.append(ArchivoPropio[2])

    # armado de seccion de bibliotecas
    NewBibliotecas=[]
    NewBibliotecas.append(ArchivoPropio[3][0])
    for lib_Indx in range(1,len(ArchivoPropio[3])-1):
        if not ArchivoPropio[3][lib_Indx] in NewBibliotecas:
            NewBibliotecas.append(ArchivoPropio[3][lib_Indx])
    for lib_Indx in range(1,len(ArchivoEntrante[3])-1):
        if not ArchivoEntrante[3][lib_Indx] in NewBibliotecas:
            NewBibliotecas.append(ArchivoEntrante[3][lib_Indx])
    NewBibliotecas.append(ArchivoPropio[3][len(ArchivoPropio[3])-1])
    ArchivoNuevaComposicion.append(NewBibliotecas)
    #armado de seccion de variables globales

    NewGlobalVars=[]
    NewGlobalVars.append(ArchivoPropio[4][0])
    aux=[]
    for indexGlobalVars1 in range(1,len(ArchivoPropio[4])-1):
        IndexEqualVar1=ArchivoPropio[4][indexGlobalVars1].find('=')
        if IndexEqualVar1<0:
                IndexEqualVar1=0
        aux.append(ArchivoPropio[4][indexGlobalVars1][0:IndexEqualVar1])

        NewGlobalVars.append(ArchivoPropio[4][indexGlobalVars1])
    for indexGlobalVars2 in range(1,len(ArchivoEntrante[4])-1) :
        IndexEqualVar2=ArchivoEntrante[4][indexGlobalVars2].find('=')
        if IndexEqualVar2<0:
                IndexEqualVar2=0
        comp=ArchivoEntrante[4][indexGlobalVars2][0:IndexEqualVar2]
        if not comp in aux:
            aux.append(ArchivoEntrante[4][indexGlobalVars2][0:IndexEqualVar2])
            NewGlobalVars.append(ArchivoEntrante[4][indexGlobalVars2])
        else:
            for gvar in range(0,len(aux)-1):
                if aux[gvar] == ArchivoEntrante[4][indexGlobalVars2][0:IndexEqualVar2]:
                    NewGlobalVars[gvar+1]=ArchivoEntrante[4][indexGlobalVars2]
                    break
    NewGlobalVars.append(ArchivoPropio[4][len(ArchivoPropio[4])-1])
    ArchivoNuevaComposicion.append(NewGlobalVars)
    #armado de clases de funcionalidad principal- activas y pasivas
    NewClases_FPAux=[]
    aux=[]
    for IndexCA_FP in range(1,len(ArchivoPropio[9])-1):
        aux.append(ArchivoPropio[9][IndexCA_FP][0])
        NewClases_FPAux.append(ArchivoPropio[9][IndexCA_FP])
    for IndexCA_FP in range(1,len(ArchivoEntrante[9])-1) :
        comp=ArchivoEntrante[9][IndexCA_FP][0]
        if not comp in aux:
            aux.append(ArchivoEntrante[9][IndexCA_FP][0])
            NewClases_FPAux.append(ArchivoEntrante[9][IndexCA_FP])
        else:
            for gvar in range(0,len(aux)-1):
                if aux[gvar] == ArchivoEntrante[9][IndexCA_FP][0]:
                    NewClases_FPAux[gvar]=ArchivoEntrante[9][IndexCA_FP]
                    break
    for IndexCA_FP in range(1,len(ArchivoPropio[5])-1) :
        comp=ArchivoPropio[5][IndexCA_FP][0]
        if not comp in aux:
            aux.append(ArchivoPropio[5][IndexCA_FP][0])
            NewClases_FPAux.append(ArchivoPropio[5][IndexCA_FP])
        else:
            for gvar in range(0,len(aux)-1):
                if aux[gvar] == ArchivoPropio[5][IndexCA_FP][0]:
                    NewClases_FPAux[gvar]=ArchivoPropio[5][IndexCA_FP]
                    break

    for IndexCA_FP in range(1,len(ArchivoEntrante[5])-1) :
        comp=ArchivoEntrante[5][IndexCA_FP][0]
        if not comp in aux:
            aux.append(ArchivoEntrante[5][IndexCA_FP][0])
            NewClases_FPAux.append(ArchivoEntrante[5][IndexCA_FP])
        else:
            Capacidades_ClaseNEntrante=ArchivoEntrante[5][IndexCA_FP][2][ArchivoEntrante[5][IndexCA_FP][2].find('[')+1 :ArchivoEntrante[5][IndexCA_FP][2].find(']')]
            Capacidades_ClaseNEntrante=Capacidades_ClaseNEntrante.replace("'", '')
            Capacidades=Capacidades_ClaseNEntrante.split(",")
            comparador = True
            for i in Capacidades:
                if not i in ArchivoPropio[2]:
                    comparador=False
            if comparador:
                for gvar in range(0,len(aux)-1):
                    if aux[gvar] == ArchivoEntrante[5][IndexCA_FP][0]:
                        NewClases_FPAux[gvar]=ArchivoEntrante[5][IndexCA_FP]
                        break
    NewClasesAFP=[]
    NewClasesPFP=[]
    NewClasesAFP.append(ArchivoPropio[5][0])
    NewClasesPFP.append(ArchivoPropio[9][0])
    for clase in NewClases_FPAux:
        Capacidades_C=clase[2][clase[2].find('[')+1 :clase[2].find(']')]
        Capacidades_C=Capacidades_C.replace("'", '')
        Capacidades_C=Capacidades_C.split(",")
        comparador = True
        for i in Capacidades_C:
            if not i in ArchivoPropio[2]:
                comparador=False
        if comparador:
            NewClasesAFP.append(clase)
        else:
            NewClasesPFP.append(clase)

    NewClasesAFP.append(ArchivoPropio[5][len(ArchivoPropio[5])-1])
    NewClasesPFP.append(ArchivoPropio[9][len(ArchivoPropio[9])-1])
    ArchivoNuevaComposicion.append(NewClasesAFP)

    #armado de clases de funcionalidad de sistema- activas y pasivas
    NewClases_SySAux=[]
    aux=[]
    for IndexCA_SyS in range(1,len(ArchivoPropio[6])-1):
        aux.append(ArchivoPropio[6][IndexCA_SyS][0])
        NewClases_SySAux.append(ArchivoPropio[6][IndexCA_SyS])

    for IndexCA_SyS in range(1,len(ArchivoEntrante[6])-1) :
        comp=ArchivoEntrante[6][IndexCA_SyS][0]
        if not comp in aux:
            aux.append(ArchivoEntrante[6][IndexCA_SyS][0])
            NewClases_SySAux.append(ArchivoEntrante[6][IndexCA_SyS])
        else:
            for gvar in range(0,len(aux)-1):
                if aux[gvar] == ArchivoEntrante[6][IndexCA_SyS][0]:
                    NewClases_SySAux[gvar]=ArchivoEntrante[6][IndexCA_SyS]
                    break
    NewClasesASyS=[]
    NewClasesASyS.append(ArchivoPropio[6][0])
    for clase in NewClases_SySAux:
        NewClasesASyS.append(clase)
    NewClasesASyS.append(ArchivoPropio[6][len(ArchivoPropio[6])-1])
    ArchivoNuevaComposicion.append(NewClasesASyS)

    #armado de hilos de funcionalidad principal- activas y pasivas
    NewHiosFPAux=[]
    aux=[]
    for IndexHilos_FP in range(1,len(ArchivoPropio[10])-1):
        aux.append(ArchivoPropio[10][IndexHilos_FP][0])
        NewHiosFPAux.append(ArchivoPropio[10][IndexHilos_FP])

    for IndexHilos_FP in range(1,len(ArchivoEntrante[10])-1) :
        comp=ArchivoEntrante[10][IndexHilos_FP][0]
        if not comp in aux:
            aux.append(ArchivoEntrante[10][IndexHilos_FP][0])
            NewHiosFPAux.append(ArchivoEntrante[10][IndexHilos_FP])
        else:
            for gvar in range(0,len(aux)-1):
                if aux[gvar] == ArchivoEntrante[10][IndexHilos_FP][0]:
                    NewHiosFPAux[gvar]=ArchivoEntrante[10][IndexHilos_FP]
                    break

    for IndexHilos_FP in range(2,len(ArchivoPropio[7])-1) :
        comp=ArchivoPropio[7][IndexHilos_FP][0]
        if not comp in aux:
            aux.append(ArchivoPropio[7][IndexHilos_FP][0])
            NewHiosFPAux.append(ArchivoPropio[7][IndexHilos_FP])
        else:
            for gvar in range(0,len(aux)-1):
                if aux[gvar] == ArchivoPropio[7][IndexHilos_FP][0]:
                    NewHiosFPAux[gvar]=ArchivoPropio[7][IndexHilos_FP]
                    break

    for IndexHilos_FP in range(2,len(ArchivoEntrante[7])-1) :
        comp=ArchivoEntrante[7][IndexHilos_FP][0]
        if not comp in aux:
            aux.append(ArchivoEntrante[7][IndexHilos_FP][0])
            NewHiosFPAux.append(ArchivoEntrante[7][IndexHilos_FP])
        else:
            Capacidades_ClaseNEntrante=ArchivoEntrante[7][IndexHilos_FP][2][ArchivoEntrante[7][IndexHilos_FP][2].find('[')+1 :ArchivoEntrante[7][IndexHilos_FP][2].find(']')]
            Capacidades_ClaseNEntrante=Capacidades_ClaseNEntrante.replace("'", '')
            Capacidades=Capacidades_ClaseNEntrante.split(",")
            comparador = True
            for i in Capacidades:
                if not i in ArchivoPropio[2]:
                    comparador=False
            if comparador:
                for gvar in range(0,len(aux)-1):
                    if aux[gvar] == ArchivoEntrante[7][IndexHilos_FP][0]:
                        NewHiosFPAux[gvar]=ArchivoEntrante[7][IndexHilos_FP]
                        break
    NewHilosFPA=[]
    NewHilosFPP=[]
    NewHilosFPA.append(ArchivoPropio[7][0])
    NewHilosFPA.append(ArchivoPropio[7][1])
    NewHilosFPP.append(ArchivoPropio[10][0])
    for clase in NewHiosFPAux:
        Capacidades_C=clase[3][clase[3].find('[')+1 :clase[3].find(']')]
        Capacidades_C=Capacidades_C.replace("'", '')
        Capacidades_C=Capacidades_C.split(",")
        comparador = True
        for i in Capacidades_C:
            if not i in ArchivoPropio[2]:
                comparador=False
        if comparador:
            NewHilosFPA.append(clase)
        else:
            NewHilosFPP.append(clase)
    NewHilosFPA.append(ArchivoPropio[7][len(ArchivoPropio[7])-1])
    NewHilosFPP.append(ArchivoPropio[10][len(ArchivoPropio[10])-1])
    ArchivoNuevaComposicion.append(NewHilosFPA)

    #armado de hilos de sistema- activos y pasivos
    NewHiosSySAux=[]
    aux=[]
    for IndexHilos_SyS in range(3,len(ArchivoPropio[8])-1):
        aux.append(ArchivoPropio[8][IndexHilos_SyS][0])
        NewHiosSySAux.append(ArchivoPropio[8][IndexHilos_SyS])

    for IndexHilos_SyS in range(3,len(ArchivoEntrante[8])-1) :
        comp=ArchivoEntrante[8][IndexHilos_SyS][0]
        if not comp in aux:
            aux.append(ArchivoEntrante[8][IndexHilos_SyS][0])
            NewHiosSySAux.append(ArchivoEntrante[8][IndexHilos_SyS])
        else:
            for gvar in range(0,len(aux)-1):
                if aux[gvar] == ArchivoEntrante[8][IndexHilos_SyS][0]:
                    NewHiosSySAux[gvar]=ArchivoEntrante[8][IndexHilos_SyS]
                    break
    NewHilosSySA=[]
    NewHilosSySA.append(ArchivoPropio[8][0])
    NewHilosSySA.append(ArchivoPropio[8][1])
    NewHilosSySA.append(ArchivoPropio[8][2])
    for clase in NewHiosSySAux:
        NewHilosSySA.append(clase)
    NewHilosSySA.append(ArchivoPropio[8][len(ArchivoPropio[8])-1])
    ArchivoNuevaComposicion.append(NewHilosSySA)
    #agregar creacion del main e invocaciones

    #agregado de codigo pasivo
    ArchivoNuevaComposicion.append(NewClasesPFP)
    ArchivoNuevaComposicion.append(NewHilosFPP)
    return ArchivoNuevaComposicion
#endregion
#**end

#**ArmadodeDocumento.
#region EnsambladorDeArvhivos    
def ArmadodeDocumento(Arch1, Arch2):
    nuevoArchivo=EnsambladorDeArvhivos(0, Arch1, Arch2)
    """
    if os.path.exists("Aux.py"):
        os.remove("Aux.py")
        print("Archivo Antiguo Removido")
    else:
        print("Auxiliar Antiguo No Encontrado")
    """
    if os.path.exists("auxi.py"):
        os.remove("auxi.py")
        print("Archivo Antiguo Removido")
    else:
        print("Auxiliar Antiguo No Encontrado")
        
    nombrenuevo="Replicate_V"+str(nuevoArchivo[0])+".py"
    f=open("Replicate_V"+str(nuevoArchivo[0])+".py","w")
    f.write('SW="Replicate_V' + str(nuevoArchivo[0]) + '"\n')

    f.write('HW="'+nuevoArchivo[1]+'"\n')

    aux="Lista_Capacidades=['"
    for i in range(0,len(nuevoArchivo[2])-1):
        aux=aux + nuevoArchivo[2][i] + "','"
    aux=aux + nuevoArchivo[2][(len(nuevoArchivo[2])-1)] + "']"
    f.write(aux +'\n')

    f.writelines(nuevoArchivo[3])
    f.write('\n')

    f.writelines(nuevoArchivo[4])
    f.write('\n')

    f.write(nuevoArchivo[5][0])
    f.write('\n')
    for i in range(1,len(nuevoArchivo[5])-1):
        f.writelines(nuevoArchivo[5][i])
    f.write(nuevoArchivo[5][len(nuevoArchivo[5])-1])
    f.write('\n')

    f.write(nuevoArchivo[6][0])
    for i in range(1,len(nuevoArchivo[6])-1):
        f.writelines(nuevoArchivo[6][i])
        f.write('\n')
    f.write(nuevoArchivo[6][len(nuevoArchivo[6])-1])
    f.write('\n')
    
    f.write(nuevoArchivo[7][0])
    f.write(nuevoArchivo[7][1])
    for i in range(2,len(nuevoArchivo[7])-1):
        f.writelines(nuevoArchivo[7][i])
    f.write(nuevoArchivo[7][len(nuevoArchivo[7])-1])
    f.write('\n')

    f.write(nuevoArchivo[8][0])
    f.write(nuevoArchivo[8][1])
    f.write(nuevoArchivo[8][2])
    for i in range(3,len(nuevoArchivo[8])-1):
        f.writelines(nuevoArchivo[8][i])
    f.write(nuevoArchivo[8][len(nuevoArchivo[8])-1])
    f.write('\n')

    f.write('#""main\n')
    f.write("time.sleep(1)\n")

    for i in range(2,len(nuevoArchivo[7])-1):
        aux=nuevoArchivo[7][i][2][8:nuevoArchivo[7][i][2].find('(')]
        f.write('Hilo' + aux +' = threading.Thread(target=Hilos_FP.'+ aux +', args=(), daemon=False)\n')
        f.write('Hilo' + aux +'.start()\n')
        f.write('\n')

    for i in range(4,len(nuevoArchivo[8])-1):
        aux=nuevoArchivo[8][i][1][8:nuevoArchivo[8][i][1].find('(')]
        f.write('Hilo' + aux +' = threading.Thread(target=Hilos_Sistema.'+ aux +', args=(), daemon=False)\n')
        f.write('Hilo' + aux +'.start()\n')
        f.write('\n')

    i=nuevoArchivo[8][3]
    f.write('Hilo' + i[1][8:i[1].find('(')] +' = threading.Thread(target=Hilos_Sistema.'+  i[1][8:i[1].find('(')] +', args=(), daemon=False)\n')
    f.write('Hilo' +  i[1][8:i[1].find('(')] +'.start()\n')

    f.write('#""end')

    f.write('\n')
    f.write('"""')
    f.write('\n')
    f.write(nuevoArchivo[9][0])
    f.write('\n')
    for i in range(1,len(nuevoArchivo[9])-1):
        f.writelines(nuevoArchivo[9][i])
    f.write(nuevoArchivo[9][len(nuevoArchivo[9])-1])
    f.write('\n')

    f.write(nuevoArchivo[10][0])
    for i in range(1,len(nuevoArchivo[10])-1):
        f.writelines(nuevoArchivo[10][i])
        f.write('\n')
    f.write(nuevoArchivo[10][len(nuevoArchivo[10])-1])
    f.write('\n')
    f.write('"""')
    f.close()
    return nombrenuevo

#endregion
#**end

#**SupervivenciaRespuesta
#region SupervivenciaRespuesta
def SupervivenciaRespuesta():
    SupervivenciaLider = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    SupervivenciaLider.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    SupervivenciaLider.bind(("", PuertoEscuchaLiderSupervivencia))
    while True:
        try:
            data, addr = SupervivenciaLider.recvfrom(1024)
            a="SiAqui"
            global Seguidor
            global ListaDeSeguidores
            Seguidor=[addr[0],time.monotonic()]
            Estado=False
            for i in range(0,len(ListaDeSeguidores)-1):
                if (ListaDeSeguidores[i][0]==Seguidor[0]):
                    ListaDeSeguidores[i]=Seguidor
                    Estado=True
            if(Estado==False):
                ListaDeSeguidores.append(Seguidor)
            SupervivenciaLider.sendto(a.encode(),(addr))#ip a donde mando y puerto por donde lo mando-completo
        except NameError:
            print("NameError")
#endregion
#**end

#**BusquedaDeLider
#region BusquedaDeLider
def BusquedaDeLider ():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    server.bind(("", PuertoEscuchaSeguidorBuscaLider))#interfaces donde escucho y puerto por el que escucho
    message = "QuienEsElCoordinador"
    server.sendto(message.encode(), ('<broadcast>', PuertoEscuchaLiderSupervivencia))#interface a donde mando y puerto por donde lo mando
    print("BusquedaDeLider")
    try:
        global DirCoordinador
        server.settimeout(10)
        data, addr = server.recvfrom(1024)
        DirCoordinador=addr
    except:
        print("coordinador no encontrado")
        time.sleep(random.randint(5,40))
        message = "MePostulo"
        if(DirCoordinador[0]=='0.0.0.0' ): # DirCoordinador=='0.0.0.0'
            server.sendto(message.encode(), ('<broadcast>', PuertoEscuchaGeneralSeguidor))#interface a donde mando y puerto por donde lo mando
            VotosPositivos=0
            VotosNegativos=0
            Respuesta="si"
            Respuesta=Respuesta.encode()
            while True:
                try:
                    server.settimeout(5)
                    data, addr = server.recvfrom(1024)
                    if(data==Respuesta):
                        VotosPositivos+=1
                    else:
                        VotosNegativos+=1
                except:
                    print("Fin de la votacion")
                    print(str(VotosPositivos)+" contra "+str(VotosNegativos))
                    break
            if VotosPositivos>VotosNegativos:
                print("Se Gano la votacion")
                message = "SoyElLider"
                global Coordinador
                Coordinador=True
                server.sendto(message.encode(), ('<broadcast>', PuertoEscuchaGeneralSeguidor))#interface a donde mando y puerto por donde lo mando
            else:
                print("Se perdio la votacion")
        else:
            print("Se cancela la postulacion")
    server.close()
    #endregion
#**end

#**SupervivenciaPregunta
#region SupervivenciaPregunta
def SupervivenciaPregunta():
    global DirCoordinador
    print("supervivenciapregunta")
    SupervivenciaSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    SupervivenciaSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    SupervivenciaSocket.bind(("", PuertoEscuchaSeguidorPreguntaSupervivencia))#interfaces donde escucho y puerto por el que escucho
    message = "SiguesAhi"
    Respuesta="SiAqui"
    Respuesta=Respuesta.encode()
    while True:
        time.sleep(Hilos_Sistema.TiempoDeConsultaSupervivencia)#tiempo que espera antes de preguntar de nuevo
        if(Hilos_Sistema.killhilos==False):
            break
        SupervivenciaSocket.sendto(message.encode(), (DirCoordinador))#interface a donde mando y puerto por donde lo mando-Completo
        try:
            SupervivenciaSocket.settimeout(5)#tiempo que espera la respuesta
            data, addr = SupervivenciaSocket.recvfrom(1024)
            if(data==Respuesta):
                print("sigueaqui")
            else:
                print("el coordinador se fue")
                DirCoordinador=("0.0.0.0",38020)
        except:
            print("except supervivencia pregunta")
            DirCoordinador=("0.0.0.0",38020)
            break
    #endregion
#**end

#**EscuchaGeneralSeguidor
#region EscuchaGeneralSeguidor
def EscuchaGeneralSeguidor():
    print("escuchageral seguidor")
    EscuchaGeneralSeguidorSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    EscuchaGeneralSeguidorSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    EscuchaGeneralSeguidorSocket.bind(("", PuertoEscuchaGeneralSeguidor))#interfaces donde escucho y puerto por el que escucho
    Votacion="MePostulo"
    NuevoLider="SoyElLider"
    SolicitudDeCF="SCF"
    EntregaDeNuevoCF="ECF"
    CambioDePoliticas="CPC"
    Reiniciate="RESET"
    while True:
        try:
            #EscuchaGeneralSeguidorSocket.settimeout(10)#tiempo que espera la respuesta
            try:    
                data, addr = EscuchaGeneralSeguidorSocket.recvfrom(1024)
                if(data==Votacion.encode()):
                    VotacionActual=time.monotonic()#if sobre mensaje recivido como parte de una postulacvion
                    global DirCoordinador
                    if((pow(pow((VotacionActual-UltimaVotacion),2),0.5)<2000.0) and DirCoordinador[0]=='0.0.0.0' ): #and DirCoordinador=='0.0.0.0'
                        message = "si"
                        EscuchaGeneralSeguidorSocket.sendto(message.encode(), (addr))#interface a donde mando y puerto por donde lo mando-Completo
                    else:
                        message = "no"
                        EscuchaGeneralSeguidorSocket.sendto(message.encode(), (addr))#interface a donde mando y puerto por donde lo mando-Completo
                elif(data==NuevoLider.encode()):
                    DirCoordinador=addr#mensaje comunicado de nuevo cooridnador
                    print(addr)
                    time.sleep(5)
                    print("tengo nuevo coordiandor")
                    intentos=10
                    while(intentos!=0):
                        try:
                            message="cv"
                            EscuchaGeneralSeguidorSocket.sendto(message.encode(), (DirCoordinador[0], PuertoEscuchaParticularCoordinador))
                            EscuchaGeneralSeguidorSocket.settimeout(2)
                            data, addr = EscuchaGeneralSeguidorSocket.recvfrom(1024)
                            message=SW
                            EscuchaGeneralSeguidorSocket.sendto(message.encode(), (DirCoordinador[0], PuertoEscuchaParticularCoordinador))
                            EscuchaGeneralSeguidorSocket.settimeout(None)
                            break
                        except ValueError:
                            EscuchaGeneralSeguidorSocket.settimeout(None)
                            print("comunicacion ocupada")
                            intentos=intentos-1
                            time.sleep(1)
                elif(data==SolicitudDeCF.encode()):
                    print("me estan solicitando mi cf")
                    message="nca"
                    EscuchaGeneralSeguidorSocket.sendto(message.encode(), (DirCoordinador[0], PuertoEscuchaParticularCoordinador))
                    time.sleep(1)
                    s = socket.socket()         # Create a socket object
                    host = socket.gethostname() # Get local machine name
                    port = 12345                 # Reserve a port for your service.
                    s.connect(addr)
                    a="Hello server!"
                    s.send(a.encode())
                    f = open(SW+".py",'rb')
                    print ('Sending...')
                    l = f.read(1024)
                    while (l):
                        print ('Sending...')
                        s.send(l)
                        l = f.read(1024)
                    f.close()
                    print ("Done Sending")
                    s.shutdown(socket.SHUT_WR)
                    print (s.recv(1024))
                    s.close()
                elif(data==EntregaDeNuevoCF.encode()):
                    print("me estan dando un nuevo documento de cf")
                    message="nca"
                    EscuchaGeneralSeguidorSocket.sendto(message.encode(), (DirCoordinador[0], PuertoEscuchaParticularCoordinador))

                    s = socket.socket()         # Create a socket object
                    host = socket.gethostname() # Get local machine name
                    port = 12345                 # Reserve a port for your service.
                    s.bind((host, port))        # Bind to the port
                    f = open("Q"+data.decode()+'.py','wb')
                    s.listen(1)                 # Now wait for client connection.
                    c, addr = s.accept()     # Establish connection with client.
                    print ('Got connection from', addr)
                    print ("Receiving-egs...")
                    l = c.recv(1024)
                    while (l):
                        print ("Receiving...")
                        f.write(l)
                        l = c.recv(1024)
                    f.close()
                    print ("Done Receiving")
                    b='Thank you for connecting'
                    c.send(b.encode())
                    c.close()
                    Hilos_Sistema.killhilos=True
                    break
                elif(data==CambioDePoliticas.encode()):
                    message = "Escuchando"
                    EscuchaGeneralSeguidorSocket.sendto(message.encode(), (addr))
                    try:
                        data, addr = EscuchaGeneralSeguidorSocket.recvfrom(1024)
                        Var_Json= json.loads(data)
                        Hilos_FP.tempo=Var_Json["tempo"]
                    except ValueError:
                        print("error")
                    print("cambio de politicas de control")
                elif(data==Reiniciate.encode()):
                    Hilos_Sistema.killhilos=True
                    break
            except:
                EscuchaGeneralSeguidorSocket.settimeout(None)
                print("comunicacion ocupada")
                intentos=intentos-1
                time.sleep(1)
        except:
            print("ningun mensaje recivido en el hilo escucha general de seguidor")
    #endregion
#**end
       
#**EscuchaParticularCoordinador
    #region EscuchaParticularCoordinador
def EscuchaParticularCoordinador():
    print("EscuchaParticularCoordinador")
    EscuchaParticularCoordinadorSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    EscuchaParticularCoordinadorSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    EscuchaParticularCoordinadorSocket.bind(("", PuertoEscuchaParticularCoordinador))#interfaces donde escucho y puerto por el que escucho
    SolicitudDeCF_actualizador="sca"
    EntregaDeNuevoCF_actualizador="nca"
    CambioDePoliticas_Actualizador="npc"
    #AvisoIngreso_NuevoSeguidor="ns"
    ComparacionDeVersiones="cv"
    while True:
        try: 
            data, addr = EscuchaParticularCoordinadorSocket.recvfrom(1024)
            if(data==ComparacionDeVersiones.encode()):
                print("Comparacion de versiones de cf")

                Seguidor=[addr[0],time.monotonic()]
                Estado=False
                for i in range(0,len(ListaDeSeguidores)-1):
                    if (ListaDeSeguidores[i][0]==Seguidor[0]):
                        ListaDeSeguidores[i]=Seguidor
                        Estado=True
                if(Estado==False):
                    ListaDeSeguidores.append(Seguidor)

                message="dame"
                EscuchaParticularCoordinadorSocket.sendto(message.encode(), (addr))
                data, addr = EscuchaParticularCoordinadorSocket.recvfrom(1024)
                if(data==SW.encode()):
                    print("MismaVersion")
                else:
                    if(float(data.decode()[11:15])>float(SW.decode()[11:15])):
                        #Soloenviar version actual NOTA
                        message="ECF"
                        EscuchaParticularCoordinadorSocket.sendto(message.encode(), (addr))
                        data, addr = EscuchaParticularCoordinadorSocket.recvfrom(1024)
                        message=SW
                        EscuchaParticularCoordinadorSocket.sendto(message.encode(), (addr))
                        s = socket.socket()         # Create a socket object
                        host = socket.gethostname() # Get local machine name
                        port = 12345                 # Reserve a port for your service.
                        s.connect(addr)
                        a="Hello server!"
                        s.send(a.encode())
                        f = open("T"+SW+".py",'rb')
                        print ('Sending...')
                        l = f.read(1024)
                        while (l):
                            print ('Sending...')
                            s.send(l)
                            l = f.read(1024)
                        f.close()
                        print ("Done Sending")
                        s.shutdown(socket.SHUT_WR)
                        print (s.recv(1024))
                        s.close()
                    else:
                        message="SCF"
                        EscuchaParticularCoordinadorSocket.sendto(message.encode(), (addr))
            #elif(data==AvisoIngreso_NuevoSeguidor.encode()):
            #    print("nuevo dispositivo en la cominidad")
            elif(data==CambioDePoliticas_Actualizador.encode()):
                print("nueva politicade control")

            elif(data==SolicitudDeCF_actualizador.encode()):
                print("me piden cf")

            elif(data==EntregaDeNuevoCF_actualizador.encode()):
                global InicioEnsamblaje
                InicioEnsamblaje=time.monotonic()
                print("me entregan cf")
                s = socket.socket()         # Create a socket object
                host = socket.gethostname() # Get local machine name
                port = 12345                 # Reserve a port for your service.
                s.bind((host, port))        # Bind to the port
                f = open('auxi.py','wb')
                s.listen(1)                 # Now wait for client connection.
                s.settimeout(5)
                c, addr = s.accept()     # Establish connection with client.
                print ('Got connection from', addr)
                print ("Receiving...")
                l = c.recv(1024)
                while (l):
                    print ("Receiving...")
                    f.write(l)
                    l = c.recv(1024)
                f.close()
                print ("Done Receiving")
                b='Thank you for connecting'
                c.send(b.encode())
                c.close()                # Close the connection
                nuevoarmado=ArmadodeDocumento(SW+".py","auxi.py")

                global FinEnsamblaje
                FinEnsamblaje =time.monotonic()
                #global ListaDeSeguidores
                print(FinEnsamblaje-InicioEnsamblaje)
                for i in ListaDeSeguidores:
                #decidir como repartir el cf en la comunidad
                    message="ECF"
                    addr=(i[0],PuertoEscuchaGeneralSeguidor)
                    EscuchaParticularCoordinadorSocket.sendto(message.encode(), (addr))
                    data, addr = EscuchaParticularCoordinadorSocket.recvfrom(1024)

                    s = socket.socket()         # Create a socket object
                    host = socket.gethostname() # Get local machine name
                    port = 12345                 # Reserve a port for your service.
                    s.connect((addr[0],port))
                    a="Hello server!"
                    s.send(a.encode())
                    f = open(nuevoarmado,'rb')
                    print ('Sending...')
                    l = f.read(1024)
                    while (l):
                        print ('Sending...')
                        s.send(l)
                        l = f.read(1024)
                    f.close()
                    print ("Done Sending")
                    s.shutdown(socket.SHUT_WR)
                    print (s.recv(1024))
                    s.close()
                #enviar version de cf a todos y reiniciarse
                message="RESET"
                EscuchaParticularCoordinadorSocket.sendto(message.encode(), (addr))
                Hilos_Sistema.killhilos=True
                break
        except NameError:
            print(NameError)
            print("ningun mensaje recivido en el hilo escucha general de seguidor")
    #endregion
#**end

#""end

#""Hilos_FP_Activos.
class Hilos_FP:       
#**Bombadeagua.
    tempo_WP=5
    def UsarBombaDeAgua():
        Lista_Capacidades_Necesaria=['wp','wls']
        wp=Wp()
        wls=Wls()
        niveldeawa=wls.wls()
        while True:
            wp.wp(niveldeawa)
            print("El Nivel del agua para la bomba es:"+str(niveldeawa))
            niveldeawa=wls.wls()
            time.sleep(Hilos_FP.tempo_WP)
#**end
#**Niveldeagua.
    tempo_NA=5
    def LeerNivelDeAgua():
        Lista_Capacidades_Necesaria=['wls']
        wls=Wls()
        niveldeawa=wls.wls()
        while True:
            print("El Nivel del agua es:"+str(niveldeawa))
            niveldeawa=wls.wls()
            time.sleep(Hilos_FP.tempo_NA)
#**end
#**Ph.
    tempo_PH=5
    def ControldeNiveldePh():
        Lista_Capacidades_Necesaria=['ph','sv']
        nivelph=Ph()
        lecturaph=nivelph.ph()
        Bomaselenoideph=Sv()
        while True:
            print("El nivel de ph en la cama es:"+str(lecturaph))
            Bomaselenoideph.sv()
            lecturaph=nivelph.ph()
            time.sleep(Hilos_FP.tempo_PH)
#**end
#**Nutrientes.
    tempo_EC=5
    def ControldeNiveldeNutrientes():
        Lista_Capacidades_Necesaria=['ec','nd']
        SensorEC=Ec()
        LecturaEC=SensorEC.ec()
        DosificadorNutrientes=Nd()
        while True:
            print("El nivel de electroconductividad es:"+str(LecturaEC))
            DosificadorNutrientes.nd(LecturaEC)
            LecturaEC=SensorEC.ec()
            time.sleep(Hilos_FP.tempo_PH)
#**end
#**EncenderLuz.
    tempo_LED=5
    def LeerintensidadLuz():
        Lista_Capacidades_Necesaria=['ldr','led']
        ldronj=Intensidad()
        Intensidadluz=ldronj.nivelluz()
        ledobj=Led()
        while True:
            print("El Nivel de intensidad luminca es:"+str(Intensidadluz))
            ledobj.led(Intensidadluz)
            Intensidadluz=ldronj.nivelluz()
            time.sleep(Hilos_FP.tempo_LED)
#**end
#""end

#""Hilos_Sistema_Activos.
class Hilos_Sistema:
    killhilos, FinDelMandato,TiempoDeConsultaSupervivencia = False, False, 30
#**Inicial
    def Inicial():
        global Coordinador
        #region Inicial
        while True:
            if Coordinador:
                HiloSupervivenciaRespuesta = threading.Thread(target=SupervivenciaRespuesta, name="hilo-SupervivenciaRespuesta", daemon=True)
                HiloSupervivenciaRespuesta.start()
                
                HiloEscuchaParticularCoordinador = threading.Thread(target=EscuchaParticularCoordinador, args=(), daemon=True)
                HiloEscuchaParticularCoordinador.start()
                HiloEscuchaParticularCoordinador.join()
                break
            else:
                HiloBusquedadelider = threading.Thread(target=BusquedaDeLider, args=(), daemon=False )
                HiloBusquedadelider.start()
                HiloBusquedadelider.join()
                time.sleep(1)
                if Coordinador==False:
                    HiloSupervivencia= threading.Thread(target=SupervivenciaPregunta,args=(), daemon=False)
                    HiloSupervivencia.start()
                    HiloSupervivencia.join()
        #endregion
#**end
#**EscuchaGeneral
    def EscuchaGeneral():
        #region EscuchaGeneral
        HiloEscuchaGeneralSeguidor = threading.Thread(target=EscuchaGeneralSeguidor, args=(), daemon=False)
        HiloEscuchaGeneralSeguidor.start()
        #endregion 
#**end
#""end

#""main
time.sleep(1)

HiloEscuchaGeneral = threading.Thread(target=Hilos_Sistema.EscuchaGeneral,args=(), daemon=True)
HiloEscuchaGeneral.start()

HiloInicial1 = threading.Thread(target=Hilos_Sistema.Inicial,args=())
HiloInicial1.start()
#""end

"""
#""Clases_Pasivo_FuncionalidadP.
#**DTH233.
class DTH2:
    Lista_Capacidades_Necesaria=["Temp233"]
    def Temp(self):
        x=random.randint(10,40)
        return x
    def Hum(self):
        x=random.randint(1,100)
        return x
#**end
#""end

#""Hilos_FP_Pasivo.
#**MedirTemperatura2.
    tempo=4
    def MedirTemperatura2():
        Lista_Capacidades_Necesaria=['Temp2233']
        
        dth=DTH()
        Temp=dth.Temp()
        while True:
            print("holi")
            print("Temperatura:"+str(Temp))
            Temp=dth.Temp()
            time.sleep(Hilos_Sistema.tempo)
#**end

#""end
"""



