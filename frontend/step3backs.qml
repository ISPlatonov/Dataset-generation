import QtQuick 2.12
import QtQuick.Window 2.12
import QtQuick.Controls 2.0
import QtQuick.Layouts 1.0
import QtQuick.Dialogs 1.2
import QtQml 2.0
Item {
    id: step3backs
    signal gotoMainView()
    signal gotoGeneration()
    Button {
        id: button1
        text: qsTr("Выбрать папку с фонами")
        width: (parent.width / 2)
        anchors.centerIn: parent
        height: 50
        onClicked: {
            fileDialog.open()
        }
    }
    Button {
        id: button2
        text: qsTr("Назад")
        width: (parent.width / 6)
        anchors.margins: 20
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        onClicked: step3backs.gotoStep3()
    }
    Button {
        id: button3
        text: qsTr("Вперед")
        width: (parent.width / 6)
        anchors.margins: 20
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        onClicked: step3backs.gotoGeneration()
    }
    FileDialog {
        id: fileDialog
        nameFilters: ["*/"]
        selectFolder: true
    }
    Loader {
        id: backsloader
        anchors.fill: parent
    }
}
