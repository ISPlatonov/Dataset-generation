import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "."


Item {
    id: mainview
    anchors.fill: parent
    visible: true

    signal gotoStep1()
    signal gotoStep2()
    signal gotoStep3()

    ColumnLayout {
        spacing: 1
        anchors.fill: parent
        anchors.margins: 25
        Button {
            id: button1
            text: "Сфотографировать детали"
            Layout.fillWidth: true
            Layout.preferredHeight: manager.config["graphics"]["unit_height"]
            onClicked: {
                mainview.gotoStep1()
                console.log("button 1 is pressed")
            }
        }
        Button {
            id: button2
            text: "Получить маски деталей"
            Layout.fillWidth: true
            Layout.preferredHeight: manager.config["graphics"]["unit_height"]
            onClicked: {
                mainview.gotoStep2()
                console.log("button 2 is pressed")
            }
        }
        Button {
            id: button3
            text: "Сгенерировать наборы данных"
            Layout.fillWidth: true
            Layout.preferredHeight: manager.config["graphics"]["unit_height"]
            onClicked: {
                mainview.gotoStep3()
                console.log("button 3 is pressed")
            }
        }
    }
}
