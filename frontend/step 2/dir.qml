import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import QtQml
/*
Ручки:
1) сколько фоток сделать на первом этапе
1') куда сохранять фотки
2) цветопорог
3) директория с фонами

2 этап: директория - ползунок - прогрессБар
3 этап: директория с масками - директория с фонами - прогрессБар
*/
Item {
    id: step2dir
    signal gotoMainView()
    signal gotoThreshold()
    Button {
        id: button1
        text: qsTr("Выбрать папку с фото деталей")
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
        onClicked: step2dir.gotoMainView()
    }
    Button {
        id: button3
        text: qsTr("Вперед")
        width: (parent.width / 6)
        anchors.margins: 20
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        onClicked: step2dir.gotoThreshold()
    }
    FolderDialog  {
        id: fileDialog
        //nameFilters: ["*/"]
        //selectFolder: true
    }
    Loader {
        id: dirloader
        anchors.fill: parent
    }
}
