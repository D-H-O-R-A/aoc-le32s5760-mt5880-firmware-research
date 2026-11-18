import QtQuick 1.1

Item {
    id: cinemaHub
    width: parent.width
    height: parent.height

    property string selectedService: "Pluto TV"
    property string streamStatus: "Reprodução Nativa HLS Ativa"

    signal launchService(string name, string method)

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
                color: "#e11d48" // Rose/Red
                Text { text: "CINE"; font.pixelSize: 13; font.bold: true; color: "#ffffff"; anchors.centerIn: parent }
            }

            Column {
                anchors.verticalCenter: parent.verticalCenter
                Text {
                    text: "Hub de Filmes, Séries & Streaming Global"
                    color: "#f8fafc"
                    font.bold: true
                    font.pixelSize: 18
                }
                Text {
                    text: "Netflix, Prime Video, Disney+, Max, Globoplay, Pluto TV, Apple TV+, Paramount+, Crunchyroll, Mubi & Plex"
                    color: "#fb7185"
                    font.pixelSize: 11
                }
            }
        }

        // Feature Banner: Cinema Moderno
        Rectangle {
            width: parent.width
            height: 140
            radius: 14
            color: "#0f172a"
            border.color: "#e11d48"
            border.width: 1

            gradient: Gradient {
                GradientStop { position: 0.0; color: "#881337" }
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
                        text: "[CINE]\nCINEMA"
                        color: "#fb7185"
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
                            width: badgeService.width + 12
                            height: 20
                            radius: 4
                            color: "#e11d48"
                            Text { id: badgeService; text: cinemaHub.selectedService.toUpperCase(); color: "#fff"; font.bold: true; font.pixelSize: 9; anchors.centerIn: parent }
                        }
                        Text { text: cinemaHub.streamStatus; color: "#38bdf8"; font.pixelSize: 11; anchors.verticalCenter: parent.verticalCenter }
                    }

                    Text {
                        text: "Acesse Catálogos Ilimitados em Alta Definição (1080p)"
                        color: "#f8fafc"
                        font.bold: true
                        font.pixelSize: 18
                    }

                    Text {
                        text: "Pluto TV e Plex rodam 100% nativos via HLS/DLNA no MT5880. Streamings protegidos por DRM comercial (Widevine L1) conectam-se via HDMI Inteligente."
                        color: "#94a3b8"
                        font.pixelSize: 12
                        width: parent.width - 20
                    }
                }
            }
        }

        Text {
            text: "CATÁLOGO DE SERVIÇOS DE VÍDEO (13 PLATAFORMAS INTEGRADAS)"
            color: "#94a3b8"
            font.bold: true
            font.pixelSize: 12
        }

        // Streaming Services Grid (13 apps)
        Grid {
            columns: 4
            spacing: 12
            width: parent.width

            Repeater {
                model: [
                    { "title": "Pluto TV", "type": "100+ Canais Ao Vivo (Grátis)", "icon": "PL", "color": "#0ea5e9", "method": "Nativo HLS" },
                    { "title": "Plex Media", "type": "Filmes & Séries em Rede", "icon": "PX", "color": "#eab308", "method": "Nativo DLNA" },
                    { "title": "Twitch TV", "type": "Lives & Games Ao Vivo", "icon": "TW", "color": "#a855f7", "method": "Stream H.264" },
                    { "title": "TikTok TV", "type": "Vídeos Curtos em Alta", "icon": "TT", "color": "#00f2fe", "method": "Feed H.264" },
                    { "title": "Netflix", "type": "Séries & Originais", "icon": "NF", "color": "#e50914", "method": "HDMI / Cast" },
                    { "title": "Prime Video", "type": "Amazon Filmes & Séries", "icon": "PV", "color": "#00a8e1", "method": "HDMI / Cast" },
                    { "title": "Disney+", "type": "Marvel, Star Wars, Pixar", "icon": "D+", "color": "#113ccf", "method": "HDMI / Cast" },
                    { "title": "Max", "type": "HBO, Warner, DC", "icon": "MX", "color": "#5822b4", "method": "HDMI / Cast" },
                    { "title": "Globoplay", "type": "Novelas & Séries Brasil", "icon": "GP", "color": "#fb5607", "method": "HDMI / Cast" },
                    { "title": "Apple TV+", "type": "Produções Exclusivas", "icon": "AT", "color": "#71717a", "method": "HDMI / Cast" },
                    { "title": "Paramount+", "type": "Filmes & Esportes", "icon": "P+", "color": "#0064ff", "method": "HDMI / Cast" },
                    { "title": "Crunchyroll", "type": "Animes & Mangás", "icon": "CR", "color": "#f97316", "method": "HDMI / Cast" }
                ]

                Rectangle {
                    width: (cinemaHub.width - 36) / 4
                    height: 66
                    radius: 10
                    color: (cinemaHub.selectedService === modelData.title) ? "#1e293b" : "#111827"
                    border.color: (cinemaHub.selectedService === modelData.title) ? modelData.color : "#1f2937"
                    border.width: (cinemaHub.selectedService === modelData.title) ? 2 : 1

                    Row {
                        anchors.fill: parent
                        anchors.margins: 10
                        spacing: 10

                        Rectangle {
                            width: 36
                            height: 36
                            radius: 8
                            color: "#0f172a"
                            Text { text: modelData.icon; color: "#f8fafc"; font.bold: true; font.pixelSize: 13; anchors.centerIn: parent }
                        }

                        Column {
                            anchors.verticalCenter: parent.verticalCenter
                            spacing: 2
                            Text { text: modelData.title; color: "#f8fafc"; font.bold: true; font.pixelSize: 13 }
                            Text { text: modelData.type; color: "#64748b"; font.pixelSize: 10; width: 140; elide: Text.ElideRight }
                        }
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: {
                            cinemaHub.selectedService = modelData.title
                            cinemaHub.streamStatus = "Modo: " + modelData.method
                            cinemaHub.launchService(modelData.title, modelData.method)
                        }
                    }
                }
            }
        }
    }
}
