import QtQuick 1.1

Item {
    id: ytView
    width: parent.width
    height: parent.height

    property int focusedIndex: 0
    property string currentVideoTitle: ""
    property bool isPlaying: false

    signal playVideo(string videoId, string title)

    Column {
        anchors.fill: parent
        spacing: 16

        // Top bar of YouTube
        Row {
            width: parent.width
            spacing: 14

            Rectangle {
                width: 38
                height: 38
                radius: 10
                color: "#e11d48"
                Text {
                    text: ">"
                    color: "#ffffff"
                    font.pixelSize: 18
                    anchors.centerIn: parent
                }
            }

            Column {
                anchors.verticalCenter: parent.verticalCenter
                Text {
                    text: "YouTube H.264 Player | AOC Smart TV"
                    color: "#f8fafc"
                    font.bold: true
                    font.pixelSize: 18
                }
                Text {
                    text: "Streaming direto acelerado por hardware (MP4 / H.264 720p/1080p sem VP9)"
                    color: "#94a3b8"
                    font.pixelSize: 11
                }
            }

            Item { width: 40; height: 1 }

            // Search Bar Button
            Rectangle {
                width: 280
                height: 36
                radius: 18
                color: "#1e293b"
                border.color: "#334155"
                border.width: 1
                anchors.verticalCenter: parent.verticalCenter

                Row {
                    anchors.centerIn: parent
                    spacing: 8
                    Text { text: "[BUSCA]"; color: "#94a3b8"; font.pixelSize: 11; font.bold: true; anchors.verticalCenter: parent.verticalCenter }
                    Text { text: "Pesquisar vídeos no YouTube..."; color: "#64748b"; font.pixelSize: 12; anchors.verticalCenter: parent.verticalCenter }
                }
            }
        }

        // Active Player View / Video Banner
        Rectangle {
            width: parent.width
            height: 160
            radius: 14
            color: "#0f172a"
            border.color: "#e11d48"
            border.width: 1

            gradient: Gradient {
                GradientStop { position: 0.0; color: "#4c0519" }
                GradientStop { position: 0.7; color: "#0f172a" }
            }

            Row {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 20

                Rectangle {
                    width: 200
                    height: parent.height
                    radius: 10
                    color: "#020617"
                    border.color: "#334155"
                    border.width: 1

                    Text {
                        text: "[HD]\nPREVIEW HD"
                        color: "#38bdf8"
                        font.bold: true
                        font.pixelSize: 16
                        horizontalAlignment: Text.AlignHCenter
                        anchors.centerIn: parent
                    }
                }

                Column {
                    anchors.verticalCenter: parent.verticalCenter
                    width: parent.width - 240
                    spacing: 8

                    Rectangle {
                        width: 90
                        height: 20
                        radius: 4
                        color: "#e11d48"
                        Text { text: "EM REPRODUÇÃO"; color: "#fff"; font.bold: true; font.pixelSize: 9; anchors.centerIn: parent }
                    }

                    Text {
                        text: ytView.currentVideoTitle !== "" ? ytView.currentVideoTitle : "Selecione um vídeo abaixo para reproduzir via decodificador MT5880"
                        color: "#f8fafc"
                        font.bold: true
                        font.pixelSize: 18
                        elide: Text.ElideRight
                        width: parent.width
                    }

                    Text {
                        text: "Qualidade: 720p HD @ 60fps | Codec: H.264 High Profile | Áudio: AAC 128kbps Stereo"
                        color: "#38bdf8"
                        font.pixelSize: 12
                    }

                    Row {
                        spacing: 12
                        Rectangle {
                            width: 130
                            height: 32
                            radius: 16
                            color: "#38bdf8"
                            Text { text: "> ASSISTIR (OK)"; color: "#0f172a"; font.bold: true; font.pixelSize: 11; anchors.centerIn: parent }
                        }
                        Rectangle {
                            width: 130
                            height: 32
                            radius: 16
                            color: "#1e293b"
                            border.color: "#334155"
                            border.width: 1
                            Text { text: "Parear Celular"; color: "#94a3b8"; font.bold: true; font.pixelSize: 11; anchors.centerIn: parent }
                        }
                    }
                }
            }
        }

        Text {
            text: "VÍDEOS POPULARES & RECOMENDADOS"
            color: "#94a3b8"
            font.bold: true
            font.pixelSize: 12
        }

        // Grid of Trending YouTube Videos
        Grid {
            columns: 4
            spacing: 14
            width: parent.width

            Repeater {
                model: [
                    { "title": "Música & Clipes em Alta Brasil", "channel": "Canal de Música", "duration": "3:45", "views": "1.2M", "id": "m1" },
                    { "title": "Jornalismo & Notícias 24h Ao Vivo", "channel": "Transmissão Noticiária", "duration": "AO VIVO", "views": "54k", "id": "m2" },
                    { "title": "Documentário Ciência & Espaço", "channel": "Ciência Hoje", "duration": "24:10", "views": "480k", "id": "m3" },
                    { "title": "Melhores Momentos do Esporte", "channel": "Esporte Digital", "duration": "12:30", "views": "920k", "id": "m4" }
                ]

                Rectangle {
                    width: (ytView.width - 42) / 4
                    height: 110
                    radius: 12
                    color: (ytView.focusedIndex === index) ? "#1e293b" : "#111827"
                    border.color: (ytView.focusedIndex === index) ? "#e11d48" : "#1f2937"
                    border.width: (ytView.focusedIndex === index) ? 2 : 1

                    Column {
                        anchors.fill: parent
                        anchors.margins: 10
                        spacing: 4

                        Rectangle {
                            width: parent.width
                            height: 40
                            radius: 6
                            color: "#0f172a"
                            Text { text: "> VÍDEO H.264"; color: "#64748b"; font.bold: true; font.pixelSize: 10; anchors.centerIn: parent }
                        }

                        Text {
                            text: modelData.title
                            color: "#f8fafc"
                            font.bold: true
                            font.pixelSize: 12
                            elide: Text.ElideRight
                            width: parent.width
                        }

                        Row {
                            width: parent.width
                            Text { text: modelData.channel; color: "#64748b"; font.pixelSize: 10; width: parent.width - 50; elide: Text.ElideRight }
                            Text { text: modelData.duration; color: "#38bdf8"; font.bold: true; font.pixelSize: 10; anchors.right: parent.right }
                        }
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: {
                            ytView.focusedIndex = index
                            ytView.currentVideoTitle = modelData.title
                            ytView.playVideo(modelData.id, modelData.title)
                        }
                    }
                }
            }
        }
    }
}
