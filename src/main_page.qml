import QtQuick 2.12
import QtQuick.Window 2.12
import QtQuick.Controls 2.0
import QtQuick.Layouts 1.0
import QtQuick.Dialogs 1.2

ApplicationWindow {
    width: 640
    height: 480
    visible: true
    title: qsTr("Генерация наборов данных")
    ColumnLayout {
        spacing: 10
        anchors.fill: parent
        anchors.margins: 25
        MyButton {
            id: button1
            text: "Сфотографировать детали"
            onClicked: {
                 button1.visible = false
                button2.visible = false
                button3.visible = false
            }
        }
        MyButton {
            id: button2
            text: "Получить маски деталей"
            onClicked: {
                button1.visible = false
                button2.visible = false
                button3.visible = false
            }
        }
        MyButton {
            id: button3
            text: "Сгенерировать наборы данных"
            onClicked: {
                button1.visible = false
                button2.visible = false
                button3.visible = false
            }
        }
    }
}
