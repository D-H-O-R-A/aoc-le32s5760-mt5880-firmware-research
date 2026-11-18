import QtQuick 1.1

Item {
    id: navDrawer
    width: isExpanded ? 240 : 72
    height: parent.height

    property int activeIndex: 0
    property bool isExpanded: false
    property bool hasFocus: false

    signal sectionSelected(int index)

    Behavior on width {
        NumberAnimation { duration: 180; easing.type: Easing.OutQuad }
    }

    Rectangle {
        anchors.fill: parent
        color: navDrawer.isExpanded ? "#0d131f" : "#080c14"
        border.color: "#1e293b"
        border.width: 1

        Column {
            anchors.fill: parent
            anchors.topMargin: 56
            spacing: 4

            Repeater {
                model: [
                    { "title": "Início", "icon": "INI", "id": 0 },
                    { "title": "Filmes & Séries", "icon": "MOV", "id": 1 },
                    { "title": "YouTube H.264", "icon": "YT", "id": 2 },
                    { "title": "Música & Rádios", "icon": "MUS", "id": 3 },
                    { "title": "Chrome Web", "icon": "WEB", "id": 4 },
                    { "title": "Media Player", "icon": "PLY", "id": 5 },
                    { "title": "ChatGPT & Apps", "icon": "AI", "id": 6 },
                    { "title": "TV Aberta & HDMI", "icon": "TV", "id": 7 },
                    { "title": "Configurações", "icon": "CFG", "id": 8 }
                ]

                Rectangle {
                    width: navDrawer.width - 16
                    height: 44
                    anchors.horizontalCenter: parent.horizontalCenter
                    radius: 10
                    color: (navDrawer.activeIndex === modelData.id) 
                           ? (navDrawer.hasFocus ? "#38bdf8" : "#1e293b") 
                           : "transparent"

                    Row {
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.left: parent.left
                        anchors.leftMargin: 14
                        spacing: 14

                        Text {
                            text: modelData.icon
                            color: (navDrawer.activeIndex === modelData.id && navDrawer.hasFocus)
                                   ? "#0f172a"
                                   : ((navDrawer.activeIndex === modelData.id) ? "#38bdf8" : "#cbd5e1")
                            font.bold: true
                            font.pixelSize: 13
                            anchors.verticalCenter: parent.verticalCenter
                        }

                        Text {
                            text: modelData.title
                            color: (navDrawer.activeIndex === modelData.id && navDrawer.hasFocus) 
                                   ? "#0f172a" 
                                   : ((navDrawer.activeIndex === modelData.id) ? "#38bdf8" : "#94a3b8")
                            font.bold: navDrawer.activeIndex === modelData.id
                            font.pixelSize: 13
                            visible: navDrawer.isExpanded
                            anchors.verticalCenter: parent.verticalCenter
                        }
                    }

                    MouseArea {
                        anchors.fill: parent
                        hoverEnabled: true
                        onEntered: navDrawer.isExpanded = true
                        onExited: navDrawer.isExpanded = navDrawer.hasFocus
                        onClicked: {
                            navDrawer.activeIndex = modelData.id
                            navDrawer.sectionSelected(modelData.id)
                        }
                    }
                }
            }
        }
    }
}
