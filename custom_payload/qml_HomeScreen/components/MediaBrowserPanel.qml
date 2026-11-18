import QtQuick 1.1

Item {
    id: mediaPanel
    width: parent.width
    height: parent.height

    property int activeTab: 0 // 0: USB, 1: DLNA / Rede, 2: IPTV / HLS

    Column {
        anchors.fill: parent
        spacing: 16

        Row {
            width: parent.width
            spacing: 12

            Text {
                text: "Reprodução de Mídia"
                color: "#f8fafc"
                font.bold: true
                font.pixelSize: 22
                anchors.verticalCenter: parent.verticalCenter
            }

            Item { width: 20; height: 1 }

            // Category Tabs
            Repeater {
                model: [
                    { "title": "Pendrive USB (/mnt/usb)", "id": 0 },
                    { "title": "Servidores DLNA / UPnP", "id": 1 },
                    { "title": "Listas IPTV (HLS / M3U)", "id": 2 }
                ]

                Rectangle {
                    width: tabTxt.width + 24
                    height: 32
                    radius: 16
                    color: (mediaPanel.activeTab === modelData.id) ? "#38bdf8" : "#1e293b"
                    anchors.verticalCenter: parent.verticalCenter

                    Text {
                        id: tabTxt
                        text: modelData.title
                        color: (mediaPanel.activeTab === modelData.id) ? "#0f172a" : "#94a3b8"
                        font.bold: true
                        font.pixelSize: 12
                        anchors.centerIn: parent
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: mediaPanel.activeTab = modelData.id
                    }
                }
            }
        }

        Text {
            text: "Decodificação acelerada por hardware (MT5880 CMPB): H.264 / AVC, MPEG-2, AAC, AC3"
            color: "#64748b"
            font.pixelSize: 13
        }

        // Media Item Cards Grid
        Grid {
            columns: 3
            spacing: 16
            width: parent.width

            Repeater {
                model: (mediaPanel.activeTab === 0) ? [
                    { "title": "Filme_Exemplo_1080p.mkv", "meta": "Vídeo | H.264 / AAC | 2.4 GB", "icon": "MKV" },
                    { "title": "Musicas_Favoritas/", "meta": "Pasta | 142 faixas MP3", "icon": "DIR" },
                    { "title": "Fotos_Viagem/", "meta": "Pasta | 89 imagens JPEG", "icon": "DIR" },
                    { "title": "Video_Gravado_DTV.ts", "meta": "Gravação PVR | 1366x768", "icon": "PVR" },
                    { "title": "Documentario_Natureza.mp4", "meta": "Vídeo | H.264 / MP4 | 1.1 GB", "icon": "MP4" },
                    { "title": "Podcast_Audio.mp3", "meta": "Áudio | 320 kbps | 45 MB", "icon": "MP3" }
                ] : (mediaPanel.activeTab === 1) ? [
                    { "title": "Servidor Jellyfin Local", "meta": "DLNA DMR | 192.168.1.100", "icon": "DLN" },
                    { "title": "Plex Media Server (UPnP)", "meta": "DLNA DMR | 192.168.1.50", "icon": "PLX" },
                    { "title": "Storage NAS Doméstico", "meta": "DLNA / SMB | Online", "icon": "NAS" }
                ] : [
                    { "title": "Canais Abertos Nacionais", "meta": "HLS Stream | Legítimo M3U", "icon": "HLS" },
                    { "title": "Transmissão Noticiária Ao Vivo", "meta": "HLS Stream | 720p", "icon": "LIVE" },
                    { "title": "Rádios Online", "meta": "Icecast / AAC Audio Stream", "icon": "RAD" }
                ]

                Rectangle {
                    width: (mediaPanel.width - 32) / 3
                    height: 80
                    radius: 12
                    color: "#111827"
                    border.color: "#1f2937"
                    border.width: 1

                    Row {
                        anchors.fill: parent
                        anchors.margins: 14
                        spacing: 12

                        Rectangle {
                            width: 44
                            height: 44
                            radius: 10
                            color: "#0f172a"
                            border.color: "#334155"
                            border.width: 1

                            Text {
                                text: modelData.icon
                                color: "#38bdf8"
                                font.bold: true
                                font.pixelSize: 12
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
                                font.pixelSize: 13
                                elide: Text.ElideRight
                                width: 170
                            }
                            Text {
                                text: modelData.meta
                                color: "#38bdf8"
                                font.pixelSize: 11
                            }
                        }
                    }
                }
            }
        }
    }
}
