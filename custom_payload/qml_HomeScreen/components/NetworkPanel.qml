import QtQuick 1.1

Item {
    id: netPanel
    width: parent.width
    height: parent.height

    property bool isWifiConnected: true
    property string wifiSsid: "MinhaRede_5G"
    property int wifiSignal: 85
    property string ipAddress: "192.168.1.105"
    property string macAddress: "00:E0:4C:58:80:A1"
    property string gateway: "192.168.1.1"
    property string dnsServer: "1.1.1.1 / 8.8.8.8"
    property string pingStatus: "Conexão ativa | Latência: 18ms"

    Column {
        anchors.fill: parent
        spacing: 16

        Text {
            text: "Gerenciador de Rede & Conexões"
            color: "#f8fafc"
            font.bold: true
            font.pixelSize: 22
        }

        Text {
            text: "Gerencie as interfaces Wi-Fi (Ralink RT5572) e Ethernet da TV"
            color: "#64748b"
            font.pixelSize: 13
        }

        Row {
            spacing: 16
            width: parent.width

            // Wi-Fi Status Card
            Rectangle {
                width: (netPanel.width - 16) / 2
                height: 180
                radius: 14
                color: "#111827"
                border.color: "#1f2937"
                border.width: 1

                Column {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 10

                    Row {
                        spacing: 10
                        Rectangle {
                            width: 36
                            height: 36
                            radius: 8
                            color: "#059669"
                            Text {
                                text: "WI-FI"
                                color: "#ffffff"
                                font.bold: true
                                font.pixelSize: 11
                                anchors.centerIn: parent
                            }
                        }
                        Column {
                            anchors.verticalCenter: parent.verticalCenter
                            Text {
                                text: "Wi-Fi (RT5572sta)"
                                color: "#f8fafc"
                                font.bold: true
                                font.pixelSize: 15
                            }
                            Text {
                                text: "Conectado | 802.11n 300Mbps"
                                color: "#10b981"
                                font.bold: true
                                font.pixelSize: 11
                            }
                        }
                    }

                    Text { text: "SSID: " + netPanel.wifiSsid; color: "#e2e8f0"; font.pixelSize: 13 }
                    Text { text: "Endereço IP: " + netPanel.ipAddress; color: "#94a3b8"; font.pixelSize: 12 }
                    Text { text: "Força do Sinal: " + netPanel.wifiSignal + "% (Excelente)"; color: "#38bdf8"; font.pixelSize: 12 }
                    Text { text: "MAC Hardware: " + netPanel.macAddress; color: "#64748b"; font.pixelSize: 11 }
                }
            }

            // Ethernet & Diagnostics Card
            Rectangle {
                width: (netPanel.width - 16) / 2
                height: 180
                radius: 14
                color: "#111827"
                border.color: "#1f2937"
                border.width: 1

                Column {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 10

                    Row {
                        spacing: 10
                        Rectangle {
                            width: 36
                            height: 36
                            radius: 8
                            color: "#2563eb"
                            Text {
                                text: "NET"
                                color: "#ffffff"
                                font.bold: true
                                font.pixelSize: 11
                                anchors.centerIn: parent
                            }
                        }
                        Column {
                            anchors.verticalCenter: parent.verticalCenter
                            Text {
                                text: "Diagnóstico de Rede"
                                color: "#f8fafc"
                                font.bold: true
                                font.pixelSize: 15
                            }
                            Text {
                                text: netPanel.pingStatus
                                color: "#38bdf8"
                                font.bold: true
                                font.pixelSize: 11
                            }
                        }
                    }

                    Text { text: "Gateway Padrão: " + netPanel.gateway; color: "#e2e8f0"; font.pixelSize: 13 }
                    Text { text: "Servidores DNS: " + netPanel.dnsServer; color: "#94a3b8"; font.pixelSize: 12 }
                    Text { text: "Porta Ethernet: 10/100 Mbps (Auto MDIX)"; color: "#94a3b8"; font.pixelSize: 12 }
                    Text { text: "Protocolos: IPv4, DHCP, DLNA, UPnP, DIAL Cast"; color: "#64748b"; font.pixelSize: 11 }
                }
            }
        }
    }
}
