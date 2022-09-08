import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import QtQml


Item {
    id: step3generation
    signal gotoMainView()
    signal gotoBacks()
    signal gotoPhotoNum()
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
            value: manager.backsGenerationPercent
        }
    }
    Button {
        id: button2
        text: qsTr("Назад")
        width: (parent.width / 6)
        anchors.margins: 20
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        onClicked: step3generation.gotoPhotoNum()
    }
    Button {
        id: button3
        text: qsTr("Вперед")
        width: (parent.width / 6)
        anchors.margins: 20
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        onClicked: {
            manager.filtration()
            manager.backsGeneration()
            step3generation.gotoMainView()
        }
    }
    Loader {
        id: dirloader
        anchors.fill: parent
    }
    Keys.onEnterPressed: {
        manager.filtration()
        manager.backsGeneration()
        step3generation.gotoMainView()
    }
    Keys.onEscapePressed: step3generation.gotoPhotoNum()
}
