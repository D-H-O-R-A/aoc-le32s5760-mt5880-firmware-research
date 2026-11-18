import QtQuick 1.1
import "components"

FocusScope {
    id: root
    width: 1280
    height: 720
    focus: true

    property int currentSection: 0
    property int selectedAppIndex: 0
    property bool drawerFocused: false

    // Dark background with ambient blue glow
    Rectangle {
        anchors.fill: parent
        color: "#070a10"

        Rectangle {
            width: 700
            height: 350
            radius: 200
            anchors.top: parent.top
            anchors.right: parent.right
            color: "#1e3a8a"
            opacity: 0.3
        }
    }

    // Top Header
    TopBar {
        id: topBar
        anchors.top: parent.top
        anchors.left: navDrawer.right
        anchors.right: parent.right
    }

    // Navigation Drawer
    NavDrawer {
        id: navDrawer
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        activeIndex: root.currentSection
        hasFocus: root.drawerFocused

        onSectionSelected: {
            root.currentSection = index
            root.drawerFocused = false
            contentArea.focus = true
        }
    }

    // Main Dynamic Content Area
    Item {
        id: contentArea
        anchors.top: topBar.bottom
        anchors.bottom: parent.bottom
        anchors.left: navDrawer.right
        anchors.right: parent.right
        anchors.margins: 20
        anchors.topMargin: 8
        focus: !root.drawerFocused

        // SECTION 0: Início (Home)
        Item {
            id: homeView
            anchors.fill: parent
            visible: root.currentSection === 0

            Column {
                anchors.fill: parent
                spacing: 14

                HeroBanner {
                    id: heroBanner
                    title: "Central de Entretenimento AOC | Smart Hub 2026"
                    subtitle: "Smart TV Interface | MediaTek MT5880 Custom Firmware"
                    description: "27 Aplicativos e Serviços Integrados: YouTube, Netflix, Spotify, Prime Video, Disney+, Max, Globoplay, Pluto TV, ChatGPT, WhatsApp e muito mais."
                    badge: "GOOGLE TV EXPERIENCE"
                }

                Text {
                    text: "APLICATIVOS POPULARES & SERVIÇOS EM ALTA"
                    color: "#94a3b8"
                    font.bold: true
                    font.pixelSize: 12
                }

                Grid {
                    id: appGrid
                    columns: 4
                    spacing: 12
                    width: parent.width

                    Repeater {
                        model: [
                            { "title": "YouTube H.264", "cat": "Streaming", "icon": "YT", "color": "#991b1b", "section": 2 },
                            { "title": "Netflix", "cat": "Filmes & Séries", "icon": "NF", "color": "#831843", "section": 1 },
                            { "title": "Spotify Música", "cat": "Áudio HiFi", "icon": "SP", "color": "#065f46", "section": 3 },
                            { "title": "ChatGPT Assistente", "cat": "Inteligência Artificial", "icon": "AI", "color": "#0f766e", "section": 6 },
                            { "title": "Chrome Web", "cat": "Navegação TLS 1.2", "icon": "WEB", "color": "#1d4ed8", "section": 4 },
                            { "title": "Media Player Pro", "cat": "USB & DLNA", "icon": "MED", "color": "#6d28d9", "section": 5 },
                            { "title": "TV Aberta Digital", "cat": "ISDB-T DTV", "icon": "DTV", "color": "#1e3a8a", "section": 7 },
                            { "title": "WhatsApp TV", "cat": "Mensagens & Alertas", "icon": "MSG", "color": "#15803d", "section": 6 }
                        ]

                        AppCard {
                            title: modelData.title
                            category: modelData.cat
                            iconText: modelData.icon
                            cardColor: modelData.color
                            isFocused: !root.drawerFocused && (root.selectedAppIndex === index) && (root.currentSection === 0)
                            onCardActivated: {
                                root.currentSection = modelData.section
                            }
                        }
                    }
                }
            }
        }

        // SECTION 1: Filmes & Séries (Cinema Hub)
        CinemaHubView {
            visible: root.currentSection === 1
        }

        // SECTION 2: YouTube H.264 Player
        YouTubeView {
            visible: root.currentSection === 2
        }

        // SECTION 3: Música & Rádios (Music Hub)
        MusicHubView {
            visible: root.currentSection === 3
        }

        // SECTION 4: Chrome Web Browser
        ChromeWebView {
            visible: root.currentSection === 4
        }

        // SECTION 5: Media Player Pro (USB, DLNA, IPTV)
        ModernPlayerView {
            visible: root.currentSection === 5
        }

        // SECTION 6: ChatGPT, WhatsApp & Utilitários
        Item {
            anchors.fill: parent
            visible: root.currentSection === 6

            Column {
                anchors.fill: parent
                spacing: 14

                ChatGPTView {
                    width: parent.width
                    height: 330
                }

                ToolsHubView {
                    width: parent.width
                    height: 200
                }
            }
        }

        // SECTION 7: TV Digital Ao Vivo & Entradas HDMI
        Item {
            anchors.fill: parent
            visible: root.currentSection === 7

            Column {
                anchors.fill: parent
                spacing: 16

                Text { text: "TV Aberta (ISDB-T) & Conexões HDMI"; color: "#f8fafc"; font.bold: true; font.pixelSize: 22 }

                HeroBanner {
                    title: "Sintonizador Digital Aberto de Alta Resolução"
                    subtitle: "Canais abertos nacionais em 1080i/720p com áudio estéreo AAC"
                    description: "Pressione OK para abrir o sintonizador de TV em tela cheia ou selecione abaixo a entrada HDMI para videogames, computadores e conversores."
                    badge: "ISDB-T ATIVO"
                }

                Row {
                    spacing: 16
                    AppCard { title: "Assistir TV Aberta"; category: "Ao Vivo"; iconText: "DTV"; cardColor: "#1e3a8a"; isFocused: true }
                    AppCard { title: "HDMI 1 (Consoles / Box)"; category: "Vídeo 1080p"; iconText: "HD1"; cardColor: "#065f46" }
                    AppCard { title: "HDMI 2 (PC / Laptop)"; category: "Vídeo 1080p"; iconText: "HD2"; cardColor: "#0f766e" }
                    AppCard { title: "Guia de TV EPG"; category: "Programação"; iconText: "EPG"; cardColor: "#4c1d95" }
                }
            }
        }

        // SECTION 8: Configurações & Sistema
        Item {
            anchors.fill: parent
            visible: root.currentSection === 8

            Column {
                anchors.fill: parent
                spacing: 16

                SettingsPanel {
                    width: parent.width
                    height: 240
                }

                SystemInfoPanel {
                    width: parent.width
                    height: 240
                }
            }
        }
    }

    // Remote Control Navigation Keys
    Keys.onPressed: {
        if (event.key === Qt.Key_Left) {
            if (!root.drawerFocused) {
                if (root.currentSection === 0 && (root.selectedAppIndex % 4 === 0)) {
                    root.drawerFocused = true
                    navDrawer.isExpanded = true
                } else if (root.selectedAppIndex > 0) {
                    root.selectedAppIndex--
                }
            }
            event.accepted = true
        } else if (event.key === Qt.Key_Right) {
            if (root.drawerFocused) {
                root.drawerFocused = false
                navDrawer.isExpanded = false
            } else {
                if (root.selectedAppIndex < 7) {
                    root.selectedAppIndex++
                }
            }
            event.accepted = true
        } else if (event.key === Qt.Key_Up) {
            if (root.drawerFocused) {
                if (root.currentSection > 0) root.currentSection--
            } else {
                if (root.selectedAppIndex >= 4) {
                    root.selectedAppIndex -= 4
                }
            }
            event.accepted = true
        } else if (event.key === Qt.Key_Down) {
            if (root.drawerFocused) {
                if (root.currentSection < 8) root.currentSection++
            } else {
                if (root.selectedAppIndex <= 3) {
                    root.selectedAppIndex += 4
                }
            }
            event.accepted = true
        } else if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter) {
            if (root.drawerFocused) {
                root.drawerFocused = false
                navDrawer.isExpanded = false
            } else if (root.currentSection === 0) {
                if (root.selectedAppIndex === 0) root.currentSection = 2 // YouTube
                else if (root.selectedAppIndex === 1) root.currentSection = 1 // Netflix / Cinema
                else if (root.selectedAppIndex === 2) root.currentSection = 3 // Spotify / Musica
                else if (root.selectedAppIndex === 3) root.currentSection = 6 // ChatGPT / IA
                else if (root.selectedAppIndex === 4) root.currentSection = 4 // Chrome
                else if (root.selectedAppIndex === 5) root.currentSection = 5 // Media Player
                else if (root.selectedAppIndex === 6) root.currentSection = 7 // TV Aberta
                else if (root.selectedAppIndex === 7) root.currentSection = 6 // WhatsApp
            }
            event.accepted = true
        } else if (event.key === Qt.Key_Escape || event.key === Qt.Key_Back) {
            if (root.currentSection !== 0) {
                root.currentSection = 0
            } else {
                root.drawerFocused = !root.drawerFocused
                navDrawer.isExpanded = root.drawerFocused
            }
            event.accepted = true
        }
    }
}
