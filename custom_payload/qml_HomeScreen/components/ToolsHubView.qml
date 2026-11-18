import QtQuick 1.1

Item {
    id: toolsHub
    width: parent.width
    height: parent.height

    property string activeTool: "WhatsApp"

    Column {
        anchors.fill: parent
        spacing: 16

        // Header
        Row {
            width: parent.width
            spacing: 14

            Rectangle {
                width: 38
                height: 38
                radius: 10
                color: "#25d366" // WhatsApp Green
                Text { text: "APP"; font.pixelSize: 13; font.bold: true; color: "#ffffff"; anchors.centerIn: parent }
            }

            Column {
                anchors.verticalCenter: parent.verticalCenter
                Text {
                    text: "Utilitários Inteligentes, Fotos & Comunicação"
                    color: "#f8fafc"
                    font.bold: true
                    font.pixelSize: 18
                }
                Text {
                    text: "WhatsApp TV, Google Photos, Google Earth Satélite, Chrome Web & ChatGPT IA"
                    color: "#4ade80"
                    font.pixelSize: 11
                }
            }
        }

        // Active Feature Banner
        Rectangle {
            width: parent.width
            height: 140
            radius: 14
            color: "#0f172a"
            border.color: "#25d366"
            border.width: 1

            gradient: Gradient {
                GradientStop { position: 0.0; color: "#064e3b" }
                GradientStop { position: 0.8; color: "#0f172a" }
            }

            Row {
                anchors.fill: parent
                anchors.margins: 18
                spacing: 18

                Rectangle {
                    width: 104
                    height: 104
                    radius: 10
                    color: "#020617"
                    border.color: "#334155"
                    border.width: 1

                    Text {
                        text: "[HUB]\nCENTRAL"
                        color: "#4ade80"
                        font.bold: true
                        font.pixelSize: 16
                        horizontalAlignment: Text.AlignHCenter
                        anchors.centerIn: parent
                    }
                }

                Column {
                    anchors.verticalCenter: parent.verticalCenter
                    width: parent.width - 150
                    spacing: 6

                    Row {
                        spacing: 8
                        Rectangle {
                            width: badgeTool.width + 12
                            height: 20
                            radius: 4
                            color: "#25d366"
                            Text { id: badgeTool; text: toolsHub.activeTool.toUpperCase(); color: "#000"; font.bold: true; font.pixelSize: 9; anchors.centerIn: parent }
                        }
                        Text { text: "CONECTIVIDADE MULTIDISPOSITIVOS"; color: "#38bdf8"; font.pixelSize: 11; anchors.verticalCenter: parent.verticalCenter }
                    }

                    Text {
                        text: "Notificações na Tela, Fotos em Família e Inteligência Artificial"
                        color: "#f8fafc"
                        font.bold: true
                        font.pixelSize: 18
                    }

                    Text {
                        text: "Receba alertas de mensagens do WhatsApp enquanto assiste TV, exiba seus álbuns do Google Fotos em slideshow de alta resolução e explore o planeta via mapas orbitais."
                        color: "#94a3b8"
                        font.pixelSize: 12
                        width: parent.width - 20
                    }
                }
            }
        }

        Text {
            text: "APLICATIVOS UTILITÁRIOS INTEGRADOS"
            color: "#94a3b8"
            font.bold: true
            font.pixelSize: 12
        }

        // Tools Grid (5 tools)
        Grid {
            columns: 3
            spacing: 14
            width: parent.width

            Repeater {
                model: [
                    { "title": "WhatsApp TV Notifier", "desc": "Alertas e mensagens na tela", "icon": "WA", "color": "#25d366" },
                    { "title": "Google Photos", "desc": "Álbuns e porta-retrato digital", "icon": "GP", "color": "#ea4335" },
                    { "title": "Google Earth Satélite", "desc": "Mapas globais e visão orbital", "icon": "GE", "color": "#4285f4" },
                    { "title": "Chrome Web Accelerator", "desc": "Navegador com proxy TLS 1.2", "icon": "WEB", "color": "#fbbc05" },
                    { "title": "ChatGPT Assistente IA", "desc": "Consultas inteligentes por texto", "icon": "AI", "color": "#10a37f" },
                    { "title": "Clima & Previsão Tempo", "desc": "Meteorologia local em tempo real", "icon": "SOL", "color": "#38bdf8" }
                ]

                Rectangle {
                    width: (toolsHub.width - 28) / 3
                    height: 70
                    radius: 12
                    color: (toolsHub.activeTool === modelData.title) ? "#1e293b" : "#111827"
                    border.color: (toolsHub.activeTool === modelData.title) ? modelData.color : "#1f2937"
                    border.width: (toolsHub.activeTool === modelData.title) ? 2 : 1

                    Row {
                        anchors.fill: parent
                        anchors.margins: 10
                        spacing: 12

                        Rectangle {
                            width: 42
                            height: 42
                            radius: 10
                            color: "#0f172a"
                            Text { text: modelData.icon; color: "#f8fafc"; font.bold: true; font.pixelSize: 13; anchors.centerIn: parent }
                        }

                        Column {
                            anchors.verticalCenter: parent.verticalCenter
                            spacing: 3
                            Text { text: modelData.title; color: "#f8fafc"; font.bold: true; font.pixelSize: 13 }
                            Text { text: modelData.desc; color: "#64748b"; font.pixelSize: 11; width: 170; elide: Text.ElideRight }
                        }
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: {
                            toolsHub.activeTool = modelData.title
                        }
                    }
                }
            }
        }
    }
}
