Attribute VB_Name = "modFunctions"
Option Explicit
Option Base 1

Private Function establishConnection() As Boolean
    Dim url As String
    Dim headers As Object
    Dim Solicitud As New MSXML2.XMLHTTP60
    Dim intentos As Integer
    Const maxIntentos As Integer = 3 ' Maximum number of attempts.

    ' Loop to retry the connection up to three times.
    For intentos = 1 To maxIntentos
        On Error Resume Next

        ' Set up the URL and headers.
        url = "https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/jcrS00Alias"
        Solicitud.Open "POST", url, False
        Solicitud.setRequestHeader "User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        Solicitud.setRequestHeader "Content-type", "application/x-www-form-urlencoded"
        Solicitud.send "accion=consPorRazonSoc&razSoc=alin"

        If Err.Number = 0 Then
            On Error GoTo 0
            establishConnection = True
            Exit Function
        Else
            Err.Clear
        End If
    Next intentos

    Set Solicitud = Nothing
    establishConnection = False
End Function

Private Function getRandom() As String

    Dim Solicitud As New MSXML2.XMLHTTP60
    Dim HTML As New HTMLDocument
    Dim url As String
    Dim respuesta As String
    Dim numRndInput As Object

    ' Set up the URL and headers.
    url = "https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/jcrS00Alias"
    Solicitud.Open "POST", url, False
    Solicitud.setRequestHeader "User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    Solicitud.setRequestHeader "Content-type", "application/x-www-form-urlencoded"
    Solicitud.send "accion=consPorRazonSoc&razSoc=alin"

    If Solicitud.Status = 200 Then
        respuesta = Solicitud.responseText
        HTML.body.innerHTML = respuesta
        Set numRndInput = HTML.getElementsByName("numRnd")(0)
        If Not numRndInput Is Nothing Then
            getRandom = numRndInput.value
        End If
    End If

    Set numRndInput = Nothing
    Set HTML = Nothing
    Set Solicitud = Nothing
End Function

Public Function consultaRuc() As Boolean

    Dim HTML As New HTMLDocument
    Dim codDocum As String
    Dim result as Object
    dim data as object
    Dim htmlText As String
    Dim random As String
    Dim numRndInput As Object
    Dim lr As Long
    Dim i As Long
    Dim allResults As Object

    Set allResults = CreateObject("Scripting.Dictionary")

    lr = shMain.Range("B" & Rows.Count).End(xlUp).Row
    htmlText = ""

    Call establishConnection

    For i = 2 To lr
        Application.StatusBar = "Progreso: [" & _
        String((i - 1), ChrW(9608)) & String((lr - 1) - (i - 1), " ") & "] " & _
        Format((i - 1) / (lr - 1), "0%")
        Application.Wait Now + TimeValue("0:00:01")

        If shMain.Range("C" & i) <> "ok" Then
            Set numRndInput = Nothing
            Set HTML = Nothing

            HTML.body.innerHTML = Trim(htmlText)
            Set numRndInput = HTML.getElementsByName("numRnd")(0)

            If Not numRndInput Is Nothing Then
                random = numRndInput.value
            Else
                random = getRandom
            End If

            codDocum = shMain.Range("B" & i).value

            If validateRuc(codDocum) Then
                If random <> "" Then
                    result = getDatos(codDocum, random)
                    data = result("data")
                    htmlText = result("respuesta")
                    allResults.Add codDocum, data
                End If
            End If
        End If
    Next i

    ExportToJson allResults, "ruta/del/archivo.json"

    Set numRndInput = Nothing
    Set HTML = Nothing
    Set allResults = Nothing

    Application.StatusBar = False
End Function

Private Sub ExportToJson(data As Object, filePath As String)
    Dim jsonText As String
    Dim jsonFile As Object

    Set jsonFile = CreateObject("Scripting.FileSystemObject").CreateTextFile(filePath, True)

    jsonText = JsonConverter.ConvertToJson(data)
    jsonFile.Write jsonText

    jsonFile.Close
End Sub

Private Function getDatos(codDocum$, random$) As Object
    Dim Solicitud As New MSXML2.XMLHTTP60
    Dim result As Object
    Dim url As String
    Dim respuesta As String
    Dim data As Object
    Dim divElementos As Object
    Dim divElemento As Object
    Dim i As Long
    Dim lr As Long

    Set result = CreateObject("Scripting.Dictionary")

    ' Set up the URL and headers.
    url = "https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/jcrS00Alias"
    Solicitud.Open "POST", url, False
    Solicitud.setRequestHeader "User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    Solicitud.setRequestHeader "Content-type", "application/x-www-form-urlencoded"
    Solicitud.send "?accion=consPorRuc&actReturn=1&modo=1&nroRuc=" & codDocum & "&numRnd=" & random

    If Solicitud.Status = 200 Then
        respuesta = Solicitud.ResponseText
        Set data = ParseResponse(respuesta)

        result.Add "data", data
        result.Add "respuesta", respuesta

        getDatos = result
    End If

    Set Solicitud = Nothing
End Function

Private Function ParseResponse(htmlText As String) As Object

    Dim data As Object
    Dim IE As Object
    Dim div_tags As Object
    Dim div_tag As Object
    Dim h4_tags As Object
    Dim h4_tag As Object
    Dim h4 As Object
    Dim keys As Object, values As Object, value As Object
    Dim key As String

    Set data = CreateObject("Scripting.Dictionary")
    Set IE = CreateObject("InternetExplorer.Application")
    Set keys = CreateObject("Scripting.Dictionary")
    Set values = CreateObject("Scripting.Dictionary")

    IE.Visible = False
    IE.Navigate "about:blank"
    Do While IE.ReadyState <> 4 Or IE.Busy
        DoEvents
    Loop

    IE.Document.body.innerHTML = htmlText
    
    Set div_tags = IE.Document.querySelector("div.list-group-item")

    If Not div_tags Is Nothing Then
        For Each div_tag In div_tags
            Set h4_tag = div_tag.querySelector("h4.list-group-item-heading")
            If Not h4_tag Is Nothing Then
                key = Replace(h4_tag.innerText, ":", "")

                If key = "N" & ChrW(&H00FA) & "mero de RUC" Then
                    Set h4_tags = div_tag.getElementsByTagName("h4")
                    Set value = h4_tags(1).innerText

                ElseIf key Like "Fecha de Inscripci" & ChrW(&H00F3) & "n" Or key Like "Sistema Emisi" & ChrW(&H00F3) & "n de Comprobante" Then
                    Set h4_tags = div_tag.getElementsByTagName("h4")

                    For Each h4 In h4_tags
                        keys.Add h4.innerText, h4.innerText
                    Next h4

                    Set values = ExtractValue(div_tag)
                
                Else
                    Set value = ExtractValue(div_tag)

                End If

                On Error Resume Next

                If Not keys Is Nothing Then
                    data.Add key, values.items
                ElseIf value Is Nothing Then
                    data.Add key, "-"
                ElseIf IsArray(value) Then
                    For i = LBound(value) To UBound(value)
                        data.Add key & " " & i + 1, value(i)
                    Next i
                Else
                    data.Add key, value
                End If
                
                On Error GoTo 0
            End If

        Next div_tag
    End If

    ' Cerrar el objeto IE
    IE.Quit
    Set IE = Nothing

    ' Devolver el diccionario con los datos
    Set ParseResponse = data
End Function

Private Function ExtractValue(div_tag As Object) As Object

    Dim p_tags As Object, td_elements As Object

    Set p_tags = div_tag.getElementsByTagName("p")
    Set td_elements = div_tag.getElementsByTagName("td")

    If Not p_tags Is Nothing Then
        Set ExtractValue = p_tags
    ElseIf Not td_elements Is Nothing Then
        Set ExtractValue = td_elements
    Else
        Set ExtractValue = Nothing
    End If

End Function

Private Function validateRuc(codRuc$) As Boolean

    Dim list As Variant
    list = Array(10, 15, 17, 20)
    validateRuc = True
    If Len(codRuc) <> 11 Or Not inList(Val(Left(codRuc, 2)), list) Or Not algoritmoValidarRuc(codRuc) Then
        validateRuc = False
    End If

End Function

Private Function inList(value As Variant, list As Variant) As Boolean

    Dim el As Variant
    inList = False
    For Each el In list
        If value = el Then
            inList = True
         Exit Function
        End If
    Next el

End Function

Private Function algoritmoValidarRuc(codRuc) As Boolean
    Dim suma As Integer
    Dim resto As Integer
    Dim complemento As Byte

    algoritmoValidarRuc = False

    suma = Val(Mid(codRuc, 1, 1)) * 5 + Val(Mid(codRuc, 2, 1)) * 4 + _
    Val(Mid(codRuc, 3, 1)) * 3 + Val(Mid(codRuc, 4, 1)) * 2 + _
    Val(Mid(codRuc, 5, 1)) * 7 + Val(Mid(codRuc, 6, 1)) * 6 + _
    Val(Mid(codRuc, 7, 1)) * 5 + Val(Mid(codRuc, 8, 1)) * 4 + _
    Val(Mid(codRuc, 9, 1)) * 3 + Val(Mid(codRuc, 10, 1)) * 2

    resto = suma Mod 11

    complemento = IIf(resto = 1, 0, Val(Left(11 - resto, 1)))

    If Val(Mid(codRuc, 11, 1)) = complemento Then
        algoritmoValidarRuc = True
     Exit Function
    End If

End Function

Private Function validateDni(codDni$) As Variant
    Dim codRuc$
    Dim suma As Integer
    Dim resto As Integer
    Dim complemento As Byte

    If Len(codRuc) <> 8 Then
        validateDni = False
     Exit Function
    End If

    codRuc = 10 & codDni
    suma = Val(Mid(codRuc, 1, 1)) * 5 + Val(Mid(codRuc, 2, 1)) * 4 + _
    Val(Mid(codRuc, 3, 1)) * 3 + Val(Mid(codRuc, 4, 1)) * 2 + _
    Val(Mid(codRuc, 5, 1)) * 7 + Val(Mid(codRuc, 6, 1)) * 6 + _
    Val(Mid(codRuc, 7, 1)) * 5 + Val(Mid(codRuc, 8, 1)) * 4 + _
    Val(Mid(codRuc, 9, 1)) * 3 + Val(Mid(codRuc, 10, 1)) * 2
    resto = suma Mod 11
    complemento = IIf(resto = 1, 0, Val(Left(11 - resto, 1)))

    validateDni = "10" & codDni & complemento

End Function

Private Function getRepresentanteLegal(nomRazonSocial$, codDocum$, nrow As Long)
    Dim Solicitud As New MSXML2.XMLHTTP60
    Dim payload$, respuesta$
    Dim HTML As New HTMLDocument
    Dim trElements As Object
    Dim url$
    Dim lr As Long, i As Long, j As Long

    url = "https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/jcrS00Alias"
    payload = "accion=getRepLeg&contexto=ti-it&modo=1&desRuc=" & nomRazonSocial & "&nroRuc=" & codDocum

    Solicitud.Open "POST", url, False
    Solicitud.setrequestheader "Content-type", "application/x-www-form-urlencoded"
    Solicitud.send payload
    respuesta = Solicitud.ResponseText
    Set Solicitud = Nothing

    HTML.body.innerHTML = Trim(respuesta)
    Set trElements = HTML.getElementsByTagName("tbody")(0).getElementsByTagName("tr")

    If trElements > 0 Then
        lr = shRepLeg.Range("A" & Rows.Count).End(xlUp).Row + 1
        For i = 0 To trElements.Length - 1
            shData.Range("P" & nrow) = "ok"
            shRepLeg.Cells(lr + i, 1).NumberFormat = "@"
            shRepLeg.Cells(lr + i, 1) = codDocum
            For j = 0 To 3
                shRepLeg.Cells(lr + i, j + 2).NumberFormat = "@"
                shRepLeg.Cells(lr + i, j + 2) = trElements.Item(i).getElementsByTagName("td")(j).innerText
            Next j
        Next i
    Else:
        shData.Range("P" & nrow) = "Sin Representantes Legales"
    End If

    Set HTML = Nothing
    Set trElements = Nothing
End Function

Public Function cleanSh()
    Dim lr As Long

    lr = shData.Range("A" & Rows.Count).End(xlUp).Row
    If lr > 1 Then
        shData.Range("A2:P" & lr).ClearContents
    End If

    lr = shRepLeg.Range("A" & Rows.Count).End(xlUp).Row
    If lr > 1 Then
        shRepLeg.Range("A2:P" & lr).ClearContents
    End If

    lr = shActividadEconomica.Range("A" & Rows.Count).End(xlUp).Row
    If lr > 1 Then
        shActividadEconomica.Range("A2:P" & lr).ClearContents
    End If

    lr = shComprobantesPago.Range("A" & Rows.Count).End(xlUp).Row
    If lr > 1 Then
        shComprobantesPago.Range("A2:P" & lr).ClearContents
    End If

    lr = shSistemaEmision.Range("A" & Rows.Count).End(xlUp).Row
    If lr > 1 Then
        shSistemaEmision.Range("A2:P" & lr).ClearContents
    End If

    lr = shPadron.Range("A" & Rows.Count).End(xlUp).Row
    If lr > 1 Then
        shPadron.Range("A2:P" & lr).ClearContents
    End If

End Function
