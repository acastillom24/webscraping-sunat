Attribute VB_Name = "modMain"
Option Explicit

Public Sub main()

    Call modFunctions.consultaRuc
    
    MsgBox "Run Complite!"
    
End Sub

Public Sub cleanSh()

    Call modFunctions.cleanSh
    
    MsgBox "Se limpiaron todas las hojas de c�lculo"

End Sub
