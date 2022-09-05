import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import QtQml


Item {
    id: step3backs
    signal gotoMainView()
    signal gotoGeneration()
    Button {
        id: button1
        text: qsTr("Выбрать папку с фонами")
        width: (parent.width / 2)
        anchors.centerIn: parent
        height: manager.config.graphics.unit_height
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
    FolderDialog {
        id: fileDialog
        //nameFilters: ["*/"]
        //selectFolder: true
    }
    Loader {
        id: backsloader
        anchors.fill: parent
    }
}
