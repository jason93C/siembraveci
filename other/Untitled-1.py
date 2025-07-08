#en esta seccion se ppiedne las variables

nombre_estudiante = input("digite el nombre del estudiante: ")
horas_de_curso = int(input("digite las horas del curso: "))
faltas = int(input("digite las horas de falta: "))
nota1 = float(input("digite la nota uno: "))
nota2 = float(input("digite la nota dos: "))
nota3 = float(input("digite la nota tres: "))
nota4 = float(input("digite la nota cuatro: "))


# en esta seccion calcula el porcentaje de inaciestencia de faltas
porsentaje_inasistencias = horas_de_curso * 0.2
print("el limite de faltas es : ",porsentaje_inasistencias)

#pregunetarse si pierde o no pierde por inacistencia

if faltas >= porsentaje_inasistencias:
    nota_definiotiva = 1.5
else:
    nota_definiotiva = (nota1+nota2+nota3 + nota4)/4

#imprimo la nota 
print ( "la nota definitiva de " , nombre_estudiante ,"es:",nota_definiotiva)

jaan = 3