import QtQuick 2.12
import QtQuick.Window 2.12
import QtQuick.Controls 2.0
import QtQuick.Layouts 1.0
import QtQuick.Dialogs 1.2
import QtQml 2.0
Item {
    id: step3generation
    signal gotoMainView()
    signal gotoBacks()
    property var filtr_progress: 1
    property var gen_progress: 0.2
    Column {
        anchors.centerIn: parent
        spacing: 2
        Text {
            text: qsTr("Фильтрация данных...")
        }
        ProgressBar {
            value: filtr_progress
        }
        Text {
            text: qsTr("Генерация данных...")
        }
        ProgressBar {
            value: gen_progress
        }
    }
    Button {
        id: button2
        text: qsTr("Назад")
        width: (parent.width / 6)
        anchors.margins: 20
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        onClicked: step3generation.gotoBacks()
    }
    Button {
        id: button3
        text: qsTr("Вперед")
        width: (parent.width / 6)
        anchors.margins: 20
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        onClicked: step3generation.gotoMainView()
    }
    Loader {
        id: dirloader
        anchors.fill: parent
    }
}
