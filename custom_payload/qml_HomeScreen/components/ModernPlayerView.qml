import QtQuick 1.1

Item {
    id: playerView
    width: parent.width
    height: parent.height

    property string currentMediaTitle: "Filme_Exemplo_1080p.mkv"
    property string currentSource: "USB: /mnt/usb/Filmes/"
    property string codecInfo: "Vídeo: H.264 High@L4.1 | Áudio: Dolby Digital AC-3 5.1 | 1080p"
    property bool isPlaying: true
    property real progress: 0.35 // 35%
    property string timeCurrent: "00:42:15"
    property string timeTotal: "02:01:30"
    property int selectedSourceTab: 0 // 0: USB, 1: DLNA, 2: IPTV

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
                color: "#8b5cf6"
                Text { text: "PLAY"; font.pixelSize: 13; font.bold: true; color: "#ffffff"; anchors.centerIn: parent }
            }

            Column {
                anchors.verticalCenter: parent.verticalCenter
                Text {
                    text: "Media Player Pro | Decodificador CMPB Hardware"
                    color: "#f8fafc"
                    font.bold: true
                    font.pixelSize: 18
                }
                Text {
                    text: playerView.codecInfo
                    color: "#a78bfa"
                    font.pixelSize: 11
                }
            }

            Item { width: 30; height: 1 }

            // Source Selector Tabs
            Row {
                spacing: 8
                anchors.verticalCenter: parent.verticalCenter

                Repeater {
                    model: [
                        { "title": "USB (/mnt/usb)", "id": 0 },
                        { "title": "DLNA / Rede", "id": 1 },
                        { "title": "IPTV / HLS", "id": 2 }
                    ]

                    Rectangle {
                        width: tabTxt.width + 20
                        height: 32
                        radius: 16
                        color: (playerView.selectedSourceTab === modelData.id) ? "#8b5cf6" : "#1e293b"

                        Text {
                            id: tabTxt
                            text: modelData.title
                            color: (playerView.selectedSourceTab === modelData.id) ? "#ffffff" : "#94a3b8"
                            font.bold: true
                            font.pixelSize: 12
                            anchors.centerIn: parent
                        }

                        MouseArea {
                            anchors.fill: parent
                            onClicked: playerView.selectedSourceTab = modelData.id
                        }
                    }
                }
            }
        }

        // Active Playback Video Screen & OSD Bar
        Rectangle {
            width: parent.width
            height: 230
            radius: 14
            color: "#030712"
            border.color: "#8b5cf6"
            border.width: 1

            // Video Simulated Surface / Backdrop
            Rectangle {
                anchors.fill: parent
                anchors.margins: 2
                radius: 12
                gradient: Gradient {
                    GradientStop { position: 0.0; color: "#1e1b4b" }
                    GradientStop { position: 1.0; color: "#030712" }
                }

                // OSD Top Info Bar
                Row {
                    anchors.top: parent.top
                    anchors.left: parent.left
                    anchors.margins: 16
                    spacing: 10

                    Rectangle {
                        width: 70
                        height: 22
                        radius: 4
                        color: playerView.isPlaying ? "#10b981" : "#f59e0b"
                        Text {
                            text: playerView.isPlaying ? "REPRODUZINDO" : "PAUSADO"
                            color: "#fff"
                            font.bold: true
                            font.pixelSize: 9
                            anchors.centerIn: parent
                        }
                    }

                    Text {
                        text: playerView.currentMediaTitle
                        color: "#f8fafc"
                        font.bold: true
                        font.pixelSize: 15
                    }

                    Text {
                        text: "(" + playerView.currentSource + ")"
                        color: "#94a3b8"
                        font.pixelSize: 13
                    }
                }

                // OSD Bottom Controls & Timeline Bar
                Rectangle {
                    width: parent.width - 32
                    height: 70
                    radius: 10
                    color: "#800f172a"
                    anchors.bottom: parent.bottom
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.bottomMargin: 14

                    Column {
                        anchors.fill: parent
                        anchors.margins: 10
                        spacing: 8

                        // Progress Timeline
                        Row {
                            width: parent.width
                            spacing: 12

                            Text {
                                text: playerView.timeCurrent
                                color: "#38bdf8"
                                font.bold: true
                                font.pixelSize: 12
                                anchors.verticalCenter: parent.verticalCenter
                            }

                            // Progress Bar Track
                            Rectangle {
                                width: parent.width - 150
                                height: 8
                                radius: 4
                                color: "#334155"
                                anchors.verticalCenter: parent.verticalCenter

                                Rectangle {
                                    width: parent.width * playerView.progress
                                    height: parent.height
                                    radius: 4
                                    gradient: Gradient {
                                        GradientStop { position: 0.0; color: "#8b5cf6" }
                                        GradientStop { position: 1.0; color: "#38bdf8" }
                                    }
                                }

                                // Scrub Knob
                                Rectangle {
                                    width: 14
                                    height: 14
                                    radius: 7
                                    color: "#ffffff"
                                    x: (parent.width * playerView.progress) - 7
                                    anchors.verticalCenter: parent.verticalCenter
                                }
                            }

                            Text {
                                text: playerView.timeTotal
                                color: "#94a3b8"
                                font.pixelSize: 12
                                anchors.verticalCenter: parent.verticalCenter
                            }
                        }

                        // Playback Buttons
                        Row {
                            anchors.horizontalCenter: parent.horizontalCenter
                            spacing: 24

                            Text { text: "<< 10s"; color: "#94a3b8"; font.pixelSize: 12 }
                            Text {
                                text: playerView.isPlaying ? "|| PAUSAR (OK)" : "> REPRODUZIR (OK)"
                                color: "#38bdf8"
                                font.bold: true
                                font.pixelSize: 13
                            }
                            Text { text: "10s >>"; color: "#94a3b8"; font.pixelSize: 12 }
                            Text { text: "[Parar]"; color: "#ef4444"; font.pixelSize: 12 }
                            Text { text: "Áudio 1 (Português)"; color: "#a78bfa"; font.pixelSize: 12 }
                            Text { text: "Legenda: SRT"; color: "#94a3b8"; font.pixelSize: 12 }
                        }
                    }
                }
            }
        }

        // Media Library Grid
        Text {
            text: (playerView.selectedSourceTab === 0) ? "ARQUIVOS DISPONÍVEIS NO PENDRIVE USB" : (playerView.selectedSourceTab === 1) ? "SERVIDORES MULTIMÍDIA NA REDE LOCAL (DLNA)" : "CANAIS E STREAMS IPTV AO VIVO"
            color: "#94a3b8"
            font.bold: true
            font.pixelSize: 12
        }

        Grid {
            columns: 3
            spacing: 12
            width: parent.width

            Repeater {
                model: (playerView.selectedSourceTab === 0) ? [
                    { "title": "Avatar_Caminho_das_Aguas.mkv", "meta": "1080p | 3.2 GB | H.264", "icon": "MKV" },
                    { "title": "Interestelar_Dublado.mp4", "meta": "1080p | 2.6 GB | H.264", "icon": "MP4" },
                    { "title": "Show_Ao_Vivo_Acustico.mkv", "meta": "720p | 1.4 GB | AAC 5.1", "icon": "AAC" }
                ] : (playerView.selectedSourceTab === 1) ? [
                    { "title": "Jellyfin Media Server", "meta": "Servidor Local | 192.168.1.100", "icon": "DLN" },
                    { "title": "Plex (Transcodificação H.264)", "meta": "Servidor Local | 192.168.1.50", "icon": "PLX" },
                    { "title": "Compartilhamento Windows PC", "meta": "DLNA / UPnP | Online", "icon": "SMB" }
                ] : [
                    { "title": "TV Brasil Ao Vivo HD", "meta": "Canal Digital Aberto | HLS", "icon": "HLS" },
                    { "title": "Canal Notícias 24 Horas", "meta": "Stream 720p | 60fps", "icon": "TV" },
                    { "title": "Canal Cultura & Documentários", "meta": "Transmissão Pública", "icon": "DOC" }
                ]

                Rectangle {
                    width: (playerView.width - 24) / 3
                    height: 60
                    radius: 10
                    color: "#111827"
                    border.color: "#1f2937"
                    border.width: 1

                    Row {
                        anchors.fill: parent
                        anchors.margins: 10
                        spacing: 12

                        Rectangle {
                            width: 38
                            height: 38
                            radius: 8
                            color: "#0f172a"
                            Text { text: modelData.icon; color: "#a78bfa"; font.bold: true; font.pixelSize: 13; anchors.centerIn: parent }
                        }

                        Column {
                            anchors.verticalCenter: parent.verticalCenter
                            spacing: 2
                            Text { text: modelData.title; color: "#f8fafc"; font.bold: true; font.pixelSize: 13; width: 220; elide: Text.ElideRight }
                            Text { text: modelData.meta; color: "#38bdf8"; font.pixelSize: 11 }
                        }
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: {
                            playerView.currentMediaTitle = modelData.title
                            playerView.isPlaying = true
                        }
                    }
                }
            }
        }
    }
}
