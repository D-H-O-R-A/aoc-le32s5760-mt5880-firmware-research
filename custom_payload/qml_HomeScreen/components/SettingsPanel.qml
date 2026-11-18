import QtQuick 1.1

Item {
    id: settingsPanel
    width: parent.width
    height: parent.height

    property int focusedSetting: 0

    Column {
        anchors.fill: parent
        spacing: 16

        Text {
            text: "Configurações do Sistema"
            color: "#f8fafc"
            font.bold: true
            font.pixelSize: 22
        }

        Text {
            text: "Ajuste os parâmetros de imagem, áudio, canais e conexões da LE32S5760"
            color: "#64748b"
            font.pixelSize: 13
        }

        Grid {
            columns: 2
            spacing: 16
            width: parent.width

            Repeater {
                model: [
                    { "title": "Modo de Imagem", "value": "Cinema (Cores Calibradas)", "icon": "IMG", "desc": "Brilho 50 | Contraste 55 | Cor 48 | Temp: Quente" },
                    { "title": "Configuração de Som", "value": "Estéreo Espacial + Bass Boost", "icon": "SOM", "desc": "Equalizador MT5880 DSP | AVL Ativado" },
                    { "title": "Entradas de Vídeo (Input)", "value": "HDMI 1 (Automático)", "icon": "IN", "desc": "HDMI 1, HDMI 2, AV Composto, Antena DTV" },
                    { "title": "Resolução do Painel", "value": "1366 x 768 @ 60Hz", "icon": "LCD", "desc": "Painel 32\" HD Ready | Escala Nativa 1:1" },
                    { "title": "Sintonia de Canais DTV", "value": "ISDB-T Brasil / Ginga", "icon": "DTV", "desc": "Busca automática de canais digitais abertos" },
                    { "title": "Temporizador de Desligamento", "value": "Desativado", "icon": "CLK", "desc": "Desligamento automático programável" }
                ]

                Rectangle {
                    width: (settingsPanel.width - 16) / 2
                    height: 90
                    radius: 12
                    color: (settingsPanel.focusedSetting === index) ? "#1e293b" : "#111827"
                    border.color: (settingsPanel.focusedSetting === index) ? "#38bdf8" : "#1f2937"
                    border.width: (settingsPanel.focusedSetting === index) ? 2 : 1

                    Row {
                        anchors.fill: parent
                        anchors.margins: 16
                        spacing: 14

                        Rectangle {
                            width: 48
                            height: 48
                            radius: 10
                            color: "#0f172a"
                            border.color: "#334155"
                            border.width: 1

                            Text {
                                text: modelData.icon
                                color: "#38bdf8"
                                font.bold: true
                                font.pixelSize: 13
                                anchors.centerIn: parent
                            }
                        }

                        Column {
                            anchors.verticalCenter: parent.verticalCenter
                            spacing: 4

                            Text {
                                text: modelData.title
                                color: "#f8fafc"
                                font.bold: true
                                font.pixelSize: 15
                            }
                            Text {
                                text: modelData.value
                                color: "#38bdf8"
                                font.bold: true
                                font.pixelSize: 12
                            }
                            Text {
                                text: modelData.desc
                                color: "#64748b"
                                font.pixelSize: 11
                            }
                        }
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: settingsPanel.focusedSetting = index
                    }
                }
            }
        }
    }
}
