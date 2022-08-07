import QtQuick 2.12
import QtQuick.Window 2.12
import QtQuick.Controls 2.0
import QtQuick.Layouts 1.0
import QtQuick.Dialogs 1.2
import QtQml 2.0

import "."
/*
Доделать:
1) Перенос клика при создании нового поля (курсор в новом поле для ввода) + перемещение по клавишам "вверх-вниз"
2) Загрузка списка деталей вместо ввода по полям - как аналог ввода
*/
Item {
    anchors.fill: parent
    visible: true

    id: step1list

    signal gotoMainView()
    signal gotoChoosingDir()
    signal gotoCamera()

    property int focusedItemIndex
    
    Row {
        id: row
        height: 50
        spacing: 10
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        Button {
            id: button0
            text: qsTr("Загрузить список деталей")
            width: (parent.width / 2)
            height: parent.height
            onClicked: listDialog.open()
        }
        Button {
            id: button2
            text: qsTr("Удалить деталь")
            width: (parent.width / 2)
            height: parent.height
            onClicked: {
                manager.removeName(manager.name_list[focusedItemIndex])
            }
        }
    }

    // ScrollView is needed
    ColumnLayout {
        id: columnLayout1
        anchors.top: row.bottom
        //anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        //spacing: 20
        visible: true

        Repeater {
            id: columnLayout1Repeater
            model: manager.name_list
            visible: true

            onItemAdded: {
                manager.addName("")
                item.focus = true
                console.log("onItemAdded")
            }

            Rectangle {
                id: columnLayout1RepeaterRect
                visible: true
                Layout.preferredWidth: columnLayout1.width - 10
                Layout.preferredHeight: columnLayout1.width * .05
                Layout.margins: 5
                Layout.topMargin: 15
                TextField  {
                    id: columnLayout1RepeaterRectTextField
                    anchors.centerIn: parent
                    width: parent.width
                    text: qsTr(model.modelData)
                    visible: true
                    focus: parent.focus
                    placeholderText: "Введите название новой детали"
                    onAccepted: {
                        manager.changeName(index, text)
                        console.log(text + " changed")
                        console.log("\"" + manager.name_list + "\"")
                    }
                    onFocusChanged: {
                        if (focus) {
                            focusedItemIndex: index
                            console.log("focusedItemIndex: " + index)
                        }
                    }
                }
                Component.onCompleted: {
                    console.log("repeater done")
                }
            }
        }
    }

    Rectangle {
        id: bottom
        height: 50
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right

        Button {
            id: button3
            text: qsTr("Готово")
            width: (parent.width / 6)
            anchors.margins: 20
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            onClicked: {
                if (number != 0) {
                    step1list.gotoCamera()
                    } else {
                    messagedialog.visible = true
                }
            }
        }
        Button {
            id: button4
            text: qsTr("Назад")
            width: (parent.width / 6)
            anchors.margins: 20
            anchors.left: parent.left
            anchors.bottom: parent.bottom
            onClicked: step1list.gotoMainView()
        }
        Loader {
            id: nextloader
            anchors.fill: parent
        }
        FileDialog {
            id: listDialog
            nameFilters: ["*.txt"]
        }
        MessageDialog {
            id: messagedialog
            title: "Ошибка заполнения"
            text: "Добавьте названия деталей. Воспользуйтесь кнопкой \"Добавить деталь\" и введите название детали в появившееся поле."
        }
    }
}
