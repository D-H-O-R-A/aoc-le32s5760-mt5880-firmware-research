import QtQuick 1.1
import "../Common"
import "components"

Item {
    id: hsMainWindow
    width: 1280
    height: 720
    focus: true

    // --- Original SystemManager C++ Bridge Properties ---
    property int currLaunchId: (hsListModel.count > 0 && hsListView.currentIndex >= 0) ? hsListModel.get(hsListView.currentIndex).launchId : 3
    property int leftMaskIndex: -1
    property int rightMaskIndex: 5
    property bool isMainPointEnable: true
    property int fontSize: (typeof stageHS !== "undefined" && stageHS.isLangGreek()) ? 24 : 26
    property int fontSizeHL: (typeof stageHS !== "undefined" && stageHS.isLangGreek()) ? 32 : 36
    property int topMaskIndex: -1
    property int bottomMaskIndex: 3

    property bool colorKeyEnabled: (typeof stageHS !== "undefined") ? stageHS.isColorKeyBarShow() : false
    property bool isTvGuideOptHasInternet: (typeof stageHS !== "undefined") ? stageHS.isTvGuideOptHasInternet() : false
    property alias notificationVisible: notification.visible

    property int uPointMode: (typeof stageHS !== "undefined" && stageHS.isUPointSupport()) ? 0 : -1
    property bool isMousePressed: false
    property bool isClickable: false

    // --- Signals expected by SystemManager ---
    signal closeHS(int lastFocus)
    signal launch(int launchType)
    signal setTVGuide(bool isInternet)

    // --- UI State Management ---
    property int currentSection: 0
    property bool drawerFocused: false

    function onHsListClciked() {
        if (typeof stageHS !== "undefined") {
            if (stageHS.getTimeShiftMode() == 2) {
                showNotification(qsTranslate("QObject", "First press Stop to go to live broadcast."))
                return
            }

            if (stageHS.isPvrRecording() &&
                (currLaunchId == 1 || currLaunchId == 2 || currLaunchId == 3 ||
                 currLaunchId == 5 || (secondLevelList.visible && islListView.currentIndex != -1))) {
                showNotification(qsTranslate("QObject", "First press Stop to stop the recording."))
                return
            }
        }

        if (secondLevelList.visible && islListView.currentIndex != -1) {
            if (typeof stageHS !== "undefined") stageHS.setLastLaunchId(5)
            onIslListClciked()
        }
        else {
            if (currLaunchId == 2 || currLaunchId == 3) { // Satellite or TV
                launch(currLaunchId)
                var type = (currLaunchId == 2) ? "Satellite" : "TV"
                if (typeof stageHS !== "undefined" && stageHS.isChannelInstalled(type)) {
                    closeHS(currLaunchId)
                } else {
                    if (typeof stageHS !== "undefined" && !stageHS.isBDSModeOn())
                        showInstallDialog(type)
                }
            }
            else {
                launch(currLaunchId)
            }
        }
    }

    function onIslListClciked() {
        if (typeof devInfo !== "undefined" && islListView.currentIndex != -1) {
            var devIndex = islListModel.get(islListView.currentIndex).devIndex
            devInfo.launchDevice(devIndex)
        }
    }

    function showNotification(text) {
        notification.visible = true
        notification.text = text
    }

    function showInstallDialog(type) {
        showNotification(qsTranslate("QObject", "No channels found. Please tune TV."))
    }

    // Modern Deep Space Background
    Rectangle {
        anchors.fill: parent
        color: "#080c14"

        Rectangle {
            width: 700
            height: 350
            radius: 200
            anchors.top: parent.top
            anchors.right: parent.right
            color: "#1e3a8a"
            opacity: 0.25
        }
    }

    // Top Header Bar
    TopBar {
        id: topBar
        anchors.top: parent.top
        anchors.left: navDrawer.right
        anchors.right: parent.right
    }

    // Modern Navigation Rail (Left Drawer)
    NavDrawer {
        id: navDrawer
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        activeIndex: hsMainWindow.currentSection
        hasFocus: hsMainWindow.drawerFocused

        onSectionSelected: {
            hsMainWindow.currentSection = index
            hsMainWindow.drawerFocused = false
            mainBody.focus = true
        }
    }

    // Content Body Area
    Item {
        id: mainBody
        anchors.top: topBar.bottom
        anchors.bottom: parent.bottom
        anchors.left: navDrawer.right
        anchors.right: parent.right
        anchors.margins: 24
        anchors.topMargin: 10
        focus: !hsMainWindow.drawerFocused

        // SECTION 0: Home / Início
        Item {
            anchors.fill: parent
            visible: hsMainWindow.currentSection === 0

            Column {
                anchors.fill: parent
                spacing: 16

                HeroBanner {
                    id: hero
                }

                Text {
                    text: "GRADE DE APLICATIVOS & FONTES (AOC SMART TV)"
                    color: "#94a3b8"
                    font.bold: true
                    font.pixelSize: 12
                }

                // Horizontal Flowing List of Apps
                ListView {
                    id: hsListView
                    width: parent.width
                    height: 150
                    orientation: ListView.Horizontal
                    spacing: 16
                    keyNavigationWraps: true
                    model: hsListModel
                    delegate: AppCard {
                        title: model.title
                        category: (model.launchId == 3) ? "DTV" : (model.launchId == 5) ? "INPUT" : "SMART"
                        iconText: (model.launchId == 3) ? "[TV]" : (model.launchId == 5) ? "[IN]" : (model.launchId == 1) ? "[CFG]" : (model.launchId == 6) ? "[EPG]" : (model.launchId == 7) ? "[USB]" : "[NET]"
                        cardColor: (model.launchId == 3) ? "#1e3a8a" : (model.launchId == 5) ? "#065f46" : "#1e293b"
                        launchId: model.launchId
                        isFocused: (hsListView.currentIndex === index) && !hsMainWindow.drawerFocused && (hsMainWindow.currentSection === 0)
                        onCardActivated: {
                            hsListView.currentIndex = index
                            hsMainWindow.onHsListClciked()
                        }
                    }
                }
            }
        }

        // SECTION 1: Destaques & Streaming
        Item {
            anchors.fill: parent
            visible: hsMainWindow.currentSection === 1
            Column {
                anchors.fill: parent
                spacing: 14
                Text { text: "Recomendações de Conteúdo"; color: "#f8fafc"; font.bold: true; font.pixelSize: 20 }
                HeroBanner {
                    title: "Reprodução em Rede Local (DLNA / UPnP)"
                    subtitle: "Suporte a Jellyfin, Plex e Servidores Multimídia"
                    description: "Transmita vídeos H.264 diretamente para o reprodutor acelerado por hardware da TV."
                    badge: "STREAMING LOCAL"
                }
            }
        }

        // SECTION 2: Favoritos
        Item {
            anchors.fill: parent
            visible: hsMainWindow.currentSection === 2
            Column {
                anchors.fill: parent
                spacing: 14
                Text { text: "Canais & Entradas Favoritas"; color: "#f8fafc"; font.bold: true; font.pixelSize: 20 }
                Row {
                    spacing: 16
                    AppCard { title: "TV Digital Aberta"; category: "Favorito #1"; iconText: "DTV"; cardColor: "#1e3a8a"; isFocused: true }
                    AppCard { title: "HDMI 1"; category: "Favorito #2"; iconText: "HDMI"; cardColor: "#065f46" }
                    AppCard { title: "Mídia USB"; category: "Favorito #3"; iconText: "USB"; cardColor: "#831843" }
                }
            }
        }

        // SECTION 3: Configurações
        SettingsPanel { visible: hsMainWindow.currentSection === 3 }

        // SECTION 4: Rede & Conexões
        NetworkPanel { visible: hsMainWindow.currentSection === 4 }

        // SECTION 5: Mídia & DLNA
        MediaBrowserPanel { visible: hsMainWindow.currentSection === 5 }

        // SECTION 6: Sistema
        SystemInfoPanel { visible: hsMainWindow.currentSection === 6 }

        // SECTION 7: Armazenamento
        StoragePanel { visible: hsMainWindow.currentSection === 7 }
    }

    // Compatibility Models
    ListModel {
        id: hsListModel
        Component.onCompleted: appendData()

        function appendData() {
            hsListModel.clear()
            hsListModel.append({"title":"TV Digital", "launchId":3})
            hsListModel.append({"title":"Entradas (HDMI)", "launchId":5})
            hsListModel.append({"title":"Guia EPG", "launchId":6})
            hsListModel.append({"title":"Gravações PVR", "launchId":7})
            hsListModel.append({"title":"Ajustes TV", "launchId":1})
            hsListModel.append({"title":"Smart Portal", "launchId":4})
        }
    }

    ListModel { id: islListModel }
    Item { id: secondLevelList; visible: false }
    ListView { id: islListView; model: islListModel }

    // Notification Banner
    Rectangle {
        id: notification
        width: 480
        height: 50
        radius: 10
        color: "#0f172a"
        border.color: "#38bdf8"
        border.width: 1
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 30
        anchors.horizontalCenter: parent.horizontalCenter
        visible: false

        property alias text: notifText.text

        Text {
            id: notifText
            color: "#f8fafc"
            font.bold: true
            font.pixelSize: 13
            anchors.centerIn: parent
        }

        Timer {
            interval: 3500
            running: notification.visible
            onTriggered: notification.visible = false
        }
    }

    // Remote Control Navigation
    Keys.onPressed: {
        if (event.key === Qt.Key_Left) {
            if (!hsMainWindow.drawerFocused) {
                if (hsListView.currentIndex > 0) {
                    hsListView.decrementCurrentIndex()
                } else {
                    hsMainWindow.drawerFocused = true
                    navDrawer.isExpanded = true
                }
            }
            event.accepted = true
        } else if (event.key === Qt.Key_Right) {
            if (hsMainWindow.drawerFocused) {
                hsMainWindow.drawerFocused = false
                navDrawer.isExpanded = false
            } else {
                if (hsListView.currentIndex < hsListModel.count - 1) {
                    hsListView.incrementCurrentIndex()
                }
            }
            event.accepted = true
        } else if (event.key === Qt.Key_Up) {
            if (hsMainWindow.drawerFocused && hsMainWindow.currentSection > 0) {
                hsMainWindow.currentSection--
            }
            event.accepted = true
        } else if (event.key === Qt.Key_Down) {
            if (hsMainWindow.drawerFocused && hsMainWindow.currentSection < 7) {
                hsMainWindow.currentSection++
            }
            event.accepted = true
        } else if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter) {
            if (hsMainWindow.drawerFocused) {
                hsMainWindow.drawerFocused = false
                navDrawer.isExpanded = false
            } else {
                hsMainWindow.onHsListClciked()
            }
            event.accepted = true
        } else if (event.key === Qt.Key_Escape || event.key === Qt.Key_Back) {
            if (hsMainWindow.currentSection !== 0) {
                hsMainWindow.currentSection = 0
            } else {
                hsMainWindow.closeHS(hsMainWindow.currLaunchId)
            }
            event.accepted = true
        }
    }
}
