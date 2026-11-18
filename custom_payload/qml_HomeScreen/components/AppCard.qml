import QtQuick 1.1

Item {
    id: appCard
    width: 220
    height: 140

    property string title: "Aplicativo"
    property string category: "Streaming"
    property string iconText: "TV"
    property color cardColor: "#1e293b"
    property int launchId: -1
    property bool isFocused: false

    signal cardActivated(int id, string title)

    scale: isFocused ? 1.06 : 1.0
    Behavior on scale {
        NumberAnimation { duration: 140; easing.type: Easing.OutQuad }
    }

    Rectangle {
        id: bg
        anchors.fill: parent
        radius: 14
        color: appCard.isFocused ? "#25344d" : appCard.cardColor
        border.color: appCard.isFocused ? "#38bdf8" : "#334155"
        border.width: appCard.isFocused ? 3 : 1

        // Glow indicator bar on top
        Rectangle {
            height: 4
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.margins: 2
            radius: 2
            color: appCard.isFocused ? "#38bdf8" : "transparent"
        }

        Column {
            anchors.fill: parent
            anchors.margins: 14
            spacing: 6

            Row {
                width: parent.width
                spacing: 10

                Rectangle {
                    width: 44
                    height: 44
                    radius: 10
                    color: "#0f172a"
                    border.color: "#334155"
                    border.width: 1

                    Text {
                        text: appCard.iconText
                        color: appCard.isFocused ? "#38bdf8" : "#f8fafc"
                        font.pixelSize: 13
                        font.bold: true
                        anchors.centerIn: parent
                    }
                }

                Column {
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 2

                    Text {
                        text: appCard.category.toUpperCase()
                        color: appCard.isFocused ? "#38bdf8" : "#64748b"
                        font.pixelSize: 10
                        font.bold: true
                    }

                    Text {
                        text: appCard.title
                        color: "#f8fafc"
                        font.bold: true
                        font.pixelSize: 15
                        elide: Text.ElideRight
                        width: 130
                    }
                }
            }

            Item {
                width: parent.width
                height: 1
            }

            Rectangle {
                width: parent.width
                height: 28
                radius: 6
                color: appCard.isFocused ? "#38bdf8" : "#0f172a"

                Text {
                    text: appCard.isFocused ? "> ABRIR (OK)" : "Pressione OK"
                    color: appCard.isFocused ? "#0f172a" : "#94a3b8"
                    font.bold: true
                    font.pixelSize: 11
                    anchors.centerIn: parent
                }
            }
        }

        MouseArea {
            anchors.fill: parent
            hoverEnabled: true
            onEntered: appCard.isFocused = true
            onExited: appCard.isFocused = false
            onClicked: appCard.cardActivated(appCard.launchId, appCard.title)
        }
    }
}
