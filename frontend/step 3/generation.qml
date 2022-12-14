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
    GridLayout {
        anchors.centerIn: parent
        rows: 4
        columns: 2
        Text {
            text: qsTr("Фильтрация данных")
            Layout.row: 0
            Layout.column: 0
        }
        ProgressBar {
            value: filtr_progress
            Layout.row: 1
            Layout.column: 0
        }
        Button {
            text: qsTr("Запустить")
            Layout.row: 0
            Layout.column: 1
            Layout.rowSpan: 2
            onClicked: {
                manager.filtration()
            }
        }
        Text {
            text: qsTr("Генерация данных")
            Layout.row: 2
            Layout.column: 0
        }
        ProgressBar {
            value: manager.backsGenerationPercent
            Layout.row: 3
            Layout.column: 0
        }
        Button {
            text: qsTr("Запустить")
            
            Layout.row: 2
            Layout.column: 1
            Layout.rowSpan: 2
            onClicked: {
                manager.backsGeneration()
                
            }
        }
    }
    Button {
        text: qsTr("Назад")
        width: (parent.width / 6)
        anchors.margins: 20
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        onClicked: step3generation.gotoPhotoNum()
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
    Connections {
        target: manager
        onBacksGenerationEnded: {
            step3generation.gotoMainView()
        }
    }
}
