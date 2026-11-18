import QtQuick 1.1

Item {
    id: storagePanel
    width: parent.width
    height: parent.height

    Column {
        anchors.fill: parent
        spacing: 16

        Text {
            text: "Gerenciamento de Armazenamento"
            color: "#f8fafc"
            font.bold: true
            font.pixelSize: 22
        }

        Text {
            text: "Mapa de alocação de memória NAND Flash e dispositivos USB externos"
            color: "#64748b"
            font.pixelSize: 13
        }

        Grid {
            columns: 2
            spacing: 16
            width: parent.width

            Repeater {
                model: [
                    { "name": "3rd Party Apps (Partição 9: 3rdA)", "fs": "SquashFS 4.0 (LZO)", "used": "92.8 MB", "total": "97.7 MB", "percent": 0.95, "color": "#38bdf8" },
                    { "name": "Sistema Base (Partição 6: rfsA)", "fs": "SquashFS 4.0 (LZO)", "used": "48.9 MB", "total": "51.5 MB", "percent": 0.94, "color": "#10b981" },
                    { "name": "Armazenamento RW (/3rd_rw: 3rdw)", "fs": "UBIFS (NAND Flash MTD)", "used": "4.2 MB", "total": "32.0 MB", "percent": 0.13, "color": "#f59e0b" },
                    { "name": "Dados Permanentes (/perm: perm)", "fs": "UBIFS (Calibração / MAC)", "used": "1.8 MB", "total": "16.0 MB", "percent": 0.11, "color": "#8b5cf6" },
                    { "name": "Kernel Linux Primário (kerA)", "fs": "uImage ARMv7 Kernel", "used": "2.4 MB", "total": "2.6 MB", "percent": 0.92, "color": "#ec4899" },
                    { "name": "Dispositivo USB (/mnt/usb)", "fs": "FAT32 / NTFS Externo", "used": "8.5 GB", "total": "32.0 GB", "percent": 0.26, "color": "#06b6d4" }
                ]

                Rectangle {
                    width: (storagePanel.width - 16) / 2
                    height: 84
                    radius: 12
                    color: "#111827"
                    border.color: "#1f2937"
                    border.width: 1

                    Column {
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 6

                        Row {
                            width: parent.width
                            Text {
                                text: modelData.name
                                color: "#f8fafc"
                                font.bold: true
                                font.pixelSize: 13
                                width: parent.width - 120
                                elide: Text.ElideRight
                            }
                            Text {
                                text: modelData.used + " / " + modelData.total
                                color: "#94a3b8"
                                font.pixelSize: 11
                                anchors.right: parent.right
                            }
                        }

                        Text {
                            text: "Sistema de Arquivos: " + modelData.fs
                            color: "#64748b"
                            font.pixelSize: 11
                        }

                        // Progress Bar
                        Rectangle {
                            width: parent.width
                            height: 6
                            radius: 3
                            color: "#1e293b"

                            Rectangle {
                                width: parent.width * modelData.percent
                                height: parent.height
                                radius: 3
                                color: modelData.color
                            }
                        }
                    }
                }
            }
        }
    }
}
