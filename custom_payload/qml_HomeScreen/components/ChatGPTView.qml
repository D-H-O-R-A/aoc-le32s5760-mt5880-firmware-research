import QtQuick 1.1

Item {
    id: chatGptView
    width: parent.width
    height: parent.height

    property string responseText: "Olá! Sou o assistente de inteligência artificial integrado à sua AOC Smart TV LE32S5760. Como posso te ajudar hoje?"
    property bool isThinking: false
    property string currentPrompt: ""

    signal askAi(string prompt)

    Column {
        anchors.fill: parent
        spacing: 16

        // Header
        Row {
            width: parent.width
            spacing: 14

            Rectangle {
                width: 38
                height: 38
                radius: 10
                color: "#10a37f" // OpenAI green
                Text { text: "AI"; font.pixelSize: 16; font.bold: true; color: "#ffffff"; anchors.centerIn: parent }
            }

            Column {
                anchors.verticalCenter: parent.verticalCenter
                Text {
                    text: "ChatGPT Assistente Inteligente | AOC Smart TV"
                    color: "#f8fafc"
                    font.bold: true
                    font.pixelSize: 18
                }
                Text {
                    text: "IA generativa integrada para recomendações de filmes, dúvidas, receitas e notícias"
                    color: "#10b981"
                    font.pixelSize: 11
                }
            }
        }

        // Response Display Box (Glassmorphic dark card)
        Rectangle {
            width: parent.width
            height: 240
            radius: 14
            color: "#0f172a"
            border.color: "#10a37f"
            border.width: 1

            Column {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 12

                Row {
                    spacing: 8
                    Rectangle {
                        width: 8
                        height: 8
                        radius: 4
                        color: chatGptView.isThinking ? "#f59e0b" : "#10a37f"
                        anchors.verticalCenter: parent.verticalCenter
                    }
                    Text {
                        text: chatGptView.isThinking ? "ChatGPT pensando..." : "Resposta da IA:"
                        color: "#94a3b8"
                        font.bold: true
                        font.pixelSize: 12
                    }
                }

                Flickable {
                    width: parent.width
                    height: parent.height - 40
                    contentWidth: parent.width
                    contentHeight: respText.paintedHeight
                    clip: true

                    Text {
                        id: respText
                        width: parent.width
                        text: chatGptView.responseText
                        color: "#f8fafc"
                        font.pixelSize: 15
                        wrapMode: Text.WordWrap
                    }
                }
            }
        }

        Text {
            text: "SUGESTÕES RÁPIDAS PARA O CONTROLE REMOTO"
            color: "#94a3b8"
            font.bold: true
            font.pixelSize: 12
        }

        // Quick Prompts Grid
        Grid {
            columns: 3
            spacing: 12
            width: parent.width

            Repeater {
                model: [
                    { "title": "[Filmes] Recomende 3 Filmes de Ficção", "prompt": "Recomende 3 filmes de ficção científica excelentes para assistir hoje." },
                    { "title": "[Info] Notícias & Fatos do Dia", "prompt": "Quais são as principais notícias e acontecimentos do dia no Brasil?" },
                    { "title": "[TV] O que assistir na TV Aberta?", "prompt": "Dê dicas de como aproveitar a grade de programação da TV digital aberta." },
                    { "title": "[Casa] Receita Fácil para o Jantar", "prompt": "Passe uma receita prática e rápida de jantar para fazer em 15 minutos." },
                    { "title": "[Esp] Curiosidades do Futebol", "prompt": "Conte 3 curiosidades históricas interessantes sobre futebol." },
                    { "title": "[Cfg] Como otimizar a Imagem da TV", "prompt": "Dicas para calibrar brilho, contraste e cores para filmes na AOC 32 polegadas." }
                ]

                Rectangle {
                    width: (chatGptView.width - 24) / 3
                    height: 52
                    radius: 10
                    color: "#111827"
                    border.color: "#1f2937"
                    border.width: 1

                    Row {
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 10

                        Text {
                            text: modelData.title
                            color: "#f8fafc"
                            font.bold: true
                            font.pixelSize: 13
                            anchors.verticalCenter: parent.verticalCenter
                            elide: Text.ElideRight
                            width: parent.width
                        }
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: {
                            chatGptView.isThinking = true
                            chatGptView.currentPrompt = modelData.prompt
                            chatGptView.responseText = "Processando pergunta: \"" + modelData.prompt + "\"...\n\n[Resposta IA]: Excelente escolha! Aqui estão recomendações selecionadas especialmente para você aproveitar na sua Smart TV AOC LE32S5760 com resolução otimizada em alta definição."
                            chatGptView.isThinking = false
                        }
                    }
                }
            }
        }
    }
}
