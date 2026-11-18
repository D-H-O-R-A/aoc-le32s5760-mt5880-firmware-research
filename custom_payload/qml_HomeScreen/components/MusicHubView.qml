import QtQuick 1.1

Item {
    id: musicHub
    width: parent.width
    height: parent.height

    property string currentService: "Spotify"
    property string currentTrack: "As It Was | Harry Styles"
    property string currentArtist: "Pop Hits 2024 | Alta Fidelidade"
    property bool isPlaying: true
    property real progress: 0.42

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
                color: "#1db954" // Spotify Green
                Text { text: "MUS"; font.pixelSize: 13; font.bold: true; color: "#ffffff"; anchors.centerIn: parent }
            }

            Column {
                anchors.verticalCenter: parent.verticalCenter
                Text {
                    text: "Hub de Música & Rádios Globais | Áudio Hi-Fi"
                    color: "#f8fafc"
                    font.bold: true
                    font.pixelSize: 18
                }
                Text {
                    text: "Spotify, Deezer, Apple Music, Tidal, Amazon Music, TuneIn, SoundCloud & YouTube Music"
                    color: "#10b981"
                    font.pixelSize: 11
                }
            }
        }

        // Active Music Playing Card
        Rectangle {
            width: parent.width
            height: 140
            radius: 14
            color: "#0f172a"
            border.color: "#1db954"
            border.width: 1

            gradient: Gradient {
                GradientStop { position: 0.0; color: "#064e3b" }
                GradientStop { position: 0.7; color: "#0f172a" }
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
                        text: "[MUS]\nÁUDIO"
                        color: "#1db954"
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
                            width: badgeTxt.width + 12
                            height: 20
                            radius: 4
                            color: "#1db954"
                            Text { id: badgeTxt; text: musicHub.currentService.toUpperCase(); color: "#000"; font.bold: true; font.pixelSize: 9; anchors.centerIn: parent }
                        }
                        Text { text: "ÁUDIO ACELERADO DSP (MT5880)"; color: "#38bdf8"; font.pixelSize: 11; anchors.verticalCenter: parent.verticalCenter }
                    }

                    Text {
                        text: musicHub.currentTrack
                        color: "#f8fafc"
                        font.bold: true
                        font.pixelSize: 18
                        elide: Text.ElideRight
                        width: parent.width
                    }

                    Text {
                        text: musicHub.currentArtist
                        color: "#94a3b8"
                        font.pixelSize: 13
                    }

                    // Progress Bar
                    Rectangle {
                        width: parent.width - 40
                        height: 6
                        radius: 3
                        color: "#334155"

                        Rectangle {
                            width: parent.width * musicHub.progress
                            height: parent.height
                            radius: 3
                            color: "#1db954"
                        }
                    }
                }
            }
        }

        Text {
            text: "SERVIÇOS DE STREAMING DE MÚSICA & RÁDIOS"
            color: "#94a3b8"
            font.bold: true
            font.pixelSize: 12
        }

        // Music Services Grid
        Grid {
            columns: 4
            spacing: 14
            width: parent.width

            Repeater {
                model: [
                    { "title": "Spotify", "type": "Connect & Playlists", "icon": "SP", "color": "#1db954" },
                    { "title": "Deezer HiFi", "type": "Áudio FLAC / MP3", "icon": "DZ", "color": "#a855f7" },
                    { "title": "Apple Music", "type": "Lossless Web Audio", "icon": "AM", "color": "#f43f5e" },
                    { "title": "Tidal Hi-Res", "type": "Master Quality Audio", "icon": "TD", "color": "#06b6d4" },
                    { "title": "TuneIn Rádios", "type": "100.000 Rádios Ao Vivo", "icon": "TI", "color": "#14b8a6" },
                    { "title": "Amazon Music", "type": "Prime & Unlimited", "icon": "AZ", "color": "#0284c7" },
                    { "title": "SoundCloud", "type": "Independentes & DJs", "icon": "SC", "color": "#f97316" },
                    { "title": "YouTube Music", "type": "Videoclipes & Áudio", "icon": "YM", "color": "#dc2626" }
                ]

                Rectangle {
                    width: (musicHub.width - 42) / 4
                    height: 72
                    radius: 12
                    color: "#111827"
                    border.color: (musicHub.currentService === modelData.title) ? modelData.color : "#1f2937"
                    border.width: (musicHub.currentService === modelData.title) ? 2 : 1

                    Row {
                        anchors.fill: parent
                        anchors.margins: 10
                        spacing: 12

                        Rectangle {
                            width: 38
                            height: 38
                            radius: 8
                            color: "#0f172a"
                            Text { text: modelData.icon; color: "#f8fafc"; font.bold: true; font.pixelSize: 13; anchors.centerIn: parent }
                        }

                        Column {
                            anchors.verticalCenter: parent.verticalCenter
                            spacing: 3
                            Text { text: modelData.title; color: "#f8fafc"; font.bold: true; font.pixelSize: 13 }
                            Text { text: modelData.type; color: "#64748b"; font.pixelSize: 10 }
                        }
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: {
                            musicHub.currentService = modelData.title
                            musicHub.currentTrack = "Tocando estação: " + modelData.title + " Hits"
                            musicHub.currentArtist = "Qualidade 320 kbps | Aceleração Nativa"
                        }
                    }
                }
            }
        }
    }
}
