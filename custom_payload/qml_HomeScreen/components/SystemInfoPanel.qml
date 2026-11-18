import QtQuick 1.1

Item {
    id: sysPanel
    width: parent.width
    height: parent.height

    Column {
        anchors.fill: parent
        spacing: 16

        Text {
            text: "Informações do Sistema & Hardware"
            color: "#f8fafc"
            font.bold: true
            font.pixelSize: 22
        }

        Text {
            text: "Especificações técnicas validadas via engenharia reversa do firmware oficial"
            color: "#64748b"
            font.pixelSize: 13
        }

        Grid {
            columns: 2
            spacing: 14
            width: parent.width

            Repeater {
                model: [
                    { "label": "Modelo da Televisão", "val": "AOC LE32S5760 (Smart TV HD 32\")", "badge": "OFICIAL" },
                    { "label": "Chassis TPV / Fabricante", "val": "TPV TAM141L (TPVision Platform)", "badge": "TAM141L" },
                    { "label": "Processador & SoC", "val": "MediaTek MT5880 Dual-Core ARM Cortex-A9", "badge": "ARMv7" },
                    { "label": "Frequência & Recursos CPU", "val": "Dual-Core 1.0 GHz | VFPv3 | SMP Preempt", "badge": "SMP" },
                    { "label": "Memória RAM", "val": "1024 MB DDR3-1600 (Dual-Channel Ch A/B)", "badge": "DDR3" },
                    { "label": "Memória Flash", "val": "512 MB NAND Flash (MTD Partições 1-30)", "badge": "NAND" },
                    { "label": "Kernel Linux", "val": "Linux Kernel 3.0.13 SMP (Compilador GCC 4.5.1)", "badge": "LINUX" },
                    { "label": "C Library (glibc)", "val": "GNU C Library 2.14 (EABI5 /ld-linux.so.3)", "badge": "GLIBC" },
                    { "label": "Subsistema Gráfico", "val": "DirectFB 1.4.1 (Aceleração por Hardware 2D)", "badge": "DIRECTFB" },
                    { "label": "Interface & Framework", "val": "Qt 4.8.3 Embedded / QML 1.1 Declarative", "badge": "QT 4.8" },
                    { "label": "Resolução Nativa", "val": "1366 x 768 @ 60 Hz (Framebuffer 720p/1080p)", "badge": "HD" },
                    { "label": "Versão Customizada", "val": "MOD-TAM141L-V2.5-CUSTOM (Modern UI)", "badge": "CUSTOM" }
                ]

                Rectangle {
                    width: (sysPanel.width - 14) / 2
                    height: 54
                    radius: 10
                    color: "#111827"
                    border.color: "#1f2937"
                    border.width: 1

                    Row {
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 12

                        Column {
                            anchors.verticalCenter: parent.verticalCenter
                            width: parent.width - 90
                            spacing: 2

                            Text {
                                text: modelData.label
                                color: "#64748b"
                                font.pixelSize: 11
                            }
                            Text {
                                text: modelData.val
                                color: "#f8fafc"
                                font.bold: true
                                font.pixelSize: 13
                                elide: Text.ElideRight
                                width: parent.width
                            }
                        }

                        Rectangle {
                            width: badgeTxt.width + 12
                            height: 22
                            radius: 4
                            color: "#1e293b"
                            border.color: "#38bdf8"
                            border.width: 1
                            anchors.verticalCenter: parent.verticalCenter

                            Text {
                                id: badgeTxt
                                text: modelData.badge
                                color: "#38bdf8"
                                font.bold: true
                                font.pixelSize: 10
                                anchors.centerIn: parent
                            }
                        }
                    }
                }
            }
        }
    }
}
