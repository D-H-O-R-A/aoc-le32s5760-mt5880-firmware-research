import QtQuick 1.1

Item {
    id: topBar
    width: parent.width
    height: 64

    property string currentTime: "19:45"
    property string currentDate: "Quinta-feira, 17 de Novembro"
    property string activeInput: "TV Digital (ISDB-T)"
    property bool networkConnected: true
    property string networkType: "Wi-Fi (Conectado)"

    Timer {
        interval: 1000
        running: true
        repeat: true
        onTriggered: {
            var date = new Date()
            var h = date.getHours()
            var m = date.getMinutes()
            if (h < 10) h = "0" + h
            if (m < 10) m = "0" + m
            topBar.currentTime = h + ":" + m
        }
    }

    // Gradient background subtle top shadow
    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#40000000" }
            GradientStop { position: 1.0; color: "#00000000" }
        }
    }

    Row {
        anchors.left: parent.left
        anchors.leftMargin: 36
        anchors.verticalCenter: parent.verticalCenter
        spacing: 12

        Rectangle {
            width: 34
            height: 34
            radius: 8
            color: "#2563eb"

            Text {
                text: "AOC"
                color: "#ffffff"
                font.bold: true
                font.pixelSize: 13
                anchors.centerIn: parent
            }
        }

        Column {
            anchors.verticalCenter: parent.verticalCenter
            spacing: 2

            Text {
                text: "LE32S5760 MOD"
                color: "#f8fafc"
                font.bold: true
                font.pixelSize: 15
            }
            Text {
                text: "MediaTek MT5880 | Linux Embedded"
                color: "#64748b"
                font.pixelSize: 11
            }
        }
    }

    Row {
        anchors.right: parent.right
        anchors.rightMargin: 36
        anchors.verticalCenter: parent.verticalCenter
        spacing: 20

        // Active Input Badge
        Rectangle {
            width: inputLabel.width + 24
            height: 30
            radius: 15
            color: "#1e293b"
            border.color: "#334155"
            border.width: 1

            Row {
                anchors.centerIn: parent
                spacing: 6

                Rectangle {
                    width: 8
                    height: 8
                    radius: 4
                    color: "#38bdf8"
                    anchors.verticalCenter: parent.verticalCenter
                }

                Text {
                    id: inputLabel
                    text: topBar.activeInput
                    color: "#94a3b8"
                    font.pixelSize: 12
                    font.bold: true
                    anchors.verticalCenter: parent.verticalCenter
                }
            }
        }

        // Network Status Badge
        Rectangle {
            width: netLabel.width + 24
            height: 30
            radius: 15
            color: "#1e293b"
            border.color: topBar.networkConnected ? "#10b981" : "#ef4444"
            border.width: 1

            Row {
                anchors.centerIn: parent
                spacing: 6

                Rectangle {
                    width: 8
                    height: 8
                    radius: 4
                    color: topBar.networkConnected ? "#10b981" : "#ef4444"
                    anchors.verticalCenter: parent.verticalCenter
                }

                Text {
                    id: netLabel
                    text: topBar.networkType
                    color: "#e2e8f0"
                    font.pixelSize: 12
                    anchors.verticalCenter: parent.verticalCenter
                }
            }
        }

        // Clock
        Text {
            text: topBar.currentTime
            color: "#f8fafc"
            font.pixelSize: 22
            font.bold: true
            anchors.verticalCenter: parent.verticalCenter
        }
    }
}
