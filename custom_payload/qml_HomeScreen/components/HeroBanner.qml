import QtQuick 1.1

Item {
    id: hero
    width: parent.width
    height: 180

    property string title: "Central de Entretenimento AOC"
    property string subtitle: "Firmware Modernizado para LE32S5760 | MT5880 Dual-Core"
    property string description: "Acesse canais de TV digital ISDB-T, streaming local via DLNA/UPnP, entradas HDMI de alta definição e reprodutor multimídia USB otimizado."
    property string badge: "FIRMWARE CUSTOM V2.5"

    Rectangle {
        anchors.fill: parent
        radius: 16
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#1e3a8a" }
            GradientStop { position: 0.5; color: "#0f172a" }
            GradientStop { position: 1.0; color: "#020617" }
        }
        border.color: "#3b82f6"
        border.width: 1

        Column {
            anchors.fill: parent
            anchors.margins: 20
            spacing: 8

            Rectangle {
                width: badgeText.width + 16
                height: 22
                radius: 4
                color: "#3b82f6"

                Text {
                    id: badgeText
                    text: hero.badge
                    color: "#ffffff"
                    font.bold: true
                    font.pixelSize: 10
                    anchors.centerIn: parent
                }
            }

            Text {
                text: hero.title
                color: "#f8fafc"
                font.bold: true
                font.pixelSize: 22
            }

            Text {
                text: hero.subtitle
                color: "#38bdf8"
                font.bold: true
                font.pixelSize: 13
            }

            Text {
                text: hero.description
                color: "#94a3b8"
                font.pixelSize: 12
                width: parent.width - 40
                wrapMode: Text.WordWrap
            }
        }
    }
}
