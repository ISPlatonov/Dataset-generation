import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.1

import "."


Item {
    id: mainview
    anchors.fill: parent
    visible: true

    signal gotoStep1()
    signal gotoStep2()
    signal gotoStep3()

    ColumnLayout {
        spacing: 10
        anchors.fill: parent
        anchors.margins: 25
        Button {
            id: button1
            text: "Сфотографировать детали"
            Layout.fillWidth: true
            width: 200
            height: 100
            onClicked: {
                mainview.gotoStep1()
                console.log("button 1 is pressed")
            }
        }
        Button {
            id: button2
            text: "Получить маски деталей"
            Layout.fillWidth: true
            width: 200
            height: 100
            onClicked: {
                mainview.gotoStep2()
                console.log("button 2 is pressed")
            }
        }
        Button {
            id: button3
            text: "Сгенерировать наборы данных"
            Layout.fillWidth: true
            width: 200
            height: 100
            onClicked: {
                mainview.gotoStep3()
                console.log("button 3 is pressed")
            }
        }
    }
}
