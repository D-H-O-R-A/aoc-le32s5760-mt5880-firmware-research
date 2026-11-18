import QtQuick 1.1

Item {
    id: webView
    width: parent.width
    height: parent.height

    property int focusedBookmark: 0
    property string currentUrl: "https://www.google.com"
    property string statusText: "Acelerador Web Ativo | TLS 1.2 Conectado"

    signal openUrl(string url)

    Column {
        anchors.fill: parent
        spacing: 16

        // Browser Header & Navigation
        Row {
            width: parent.width
            spacing: 12

            Rectangle {
                width: 36
                height: 36
                radius: 18
                color: "#2563eb"
                Text { text: "WEB"; font.pixelSize: 13; font.bold: true; color: "#ffffff"; anchors.centerIn: parent }
            }

            Column {
                anchors.verticalCenter: parent.verticalCenter
                Text {
                    text: "Chrome TV | Navegador Web Modernizado"
                    color: "#f8fafc"
                    font.bold: true
                    font.pixelSize: 18
                }
                Text {
                    text: webView.statusText
                    color: "#10b981"
                    font.bold: true
                    font.pixelSize: 11
                }
            }

            Item { width: 30; height: 1 }

            // URL Address Input Bar
            Rectangle {
                width: 440
                height: 38
                radius: 19
                color: "#1e293b"
                border.color: "#38bdf8"
                border.width: 1
                anchors.verticalCenter: parent.verticalCenter

                Row {
                    anchors.centerIn: parent
                    spacing: 10
                    Text { text: "[SSL]"; font.pixelSize: 11; font.bold: true; color: "#22c55e"; anchors.verticalCenter: parent.verticalCenter }
                    Text {
                        text: webView.currentUrl
                        color: "#f8fafc"
                        font.bold: true
                        font.pixelSize: 13
                        anchors.verticalCenter: parent.verticalCenter
                    }
                }
            }

            Rectangle {
                width: 100
                height: 38
                radius: 19
                color: "#38bdf8"
                anchors.verticalCenter: parent.verticalCenter
                Text { text: "Acessar (OK)"; color: "#0f172a"; font.bold: true; font.pixelSize: 12; anchors.centerIn: parent }
            }
        }

        // Feature Banner
        Rectangle {
            width: parent.width
            height: 100
            radius: 14
            color: "#111827"
            border.color: "#1f2937"
            border.width: 1

            Row {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 16

                Rectangle {
                    width: 60
                    height: 60
                    radius: 12
                    color: "#0f172a"
                    border.color: "#334155"
                    border.width: 1
                    Text { text: "WEB"; font.pixelSize: 20; font.bold: true; color: "#ffffff"; anchors.centerIn: parent }
                }

                Column {
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 4

                    Text {
                        text: "Navegação Acelerada com Suporte a Certificados Modernos"
                        color: "#f8fafc"
                        font.bold: true
                        font.pixelSize: 15
                    }
                    Text {
                        text: "Navegador nativo Opera TV com TLS 1.1/1.2 habilitado, UserJS atualizado e bloqueio de anúncios via urlfilter.ini."
                        color: "#94a3b8"
                        font.pixelSize: 12
                        width: parent.width - 90
                    }
                }
            }
        }

        Text {
            text: "SITES & PORTAIS FAVORITOS"
            color: "#94a3b8"
            font.bold: true
            font.pixelSize: 12
        }

        // Bookmarks Grid
        Grid {
            columns: 3
            spacing: 14
            width: parent.width

            Repeater {
                model: [
                    { "title": "Google Busca", "url": "https://www.google.com", "desc": "Pesquisa na web rápida e leve", "icon": "G" },
                    { "title": "Wikipédia Brasil", "url": "https://pt.wikipedia.org", "desc": "Enciclopédia livre formatada para TV", "icon": "W" },
                    { "title": "G1 Notícias", "url": "https://g1.globo.com", "desc": "Últimas notícias do Brasil e do mundo", "icon": "G1" },
                    { "title": "Previsão do Tempo", "url": "https://tempo.com", "desc": "Meteorologia local atualizada", "icon": "SOL" },
                    { "title": "TV Brasil Online", "url": "https://tvbrasil.ebc.com.br", "desc": "Transmissões digitais abertas online", "icon": "TV" },
                    { "title": "Rádios Online", "url": "https://www.radios.com.br", "desc": "Transmissões de rádio e áudio online", "icon": "RAD" }
                ]

                Rectangle {
                    width: (webView.width - 28) / 3
                    height: 80
                    radius: 12
                    color: (webView.focusedBookmark === index) ? "#1e293b" : "#111827"
                    border.color: (webView.focusedBookmark === index) ? "#38bdf8" : "#1f2937"
                    border.width: (webView.focusedBookmark === index) ? 2 : 1

                    Row {
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 12

                        Rectangle {
                            width: 44
                            height: 44
                            radius: 10
                            color: "#0f172a"
                            border.color: "#334155"
                            border.width: 1
                            Text { text: modelData.icon; color: "#38bdf8"; font.bold: true; font.pixelSize: 13; anchors.centerIn: parent }
                        }

                        Column {
                            anchors.verticalCenter: parent.verticalCenter
                            spacing: 3

                            Text {
                                text: modelData.title
                                color: "#f8fafc"
                                font.bold: true
                                font.pixelSize: 14
                            }
                            Text {
                                text: modelData.desc
                                color: "#64748b"
                                font.pixelSize: 11
                                elide: Text.ElideRight
                                width: 180
                            }
                        }
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: {
                            webView.focusedBookmark = index
                            webView.currentUrl = modelData.url
                            webView.openUrl(modelData.url)
                        }
                    }
                }
            }
        }
    }
}
