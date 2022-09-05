import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import QtQml

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
        height: manager.config["graphics"]["unit_height"]
        spacing: manager.config["graphics"]["unit_height"] * .2
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        Button {
            // llbe fixed later
            id: button0
            text: qsTr("Загрузить список деталей")
            width: (parent.width / 3)
            height: parent.height
            onClicked: listDialog.open()
        }
        Button {
            id: button1
            text: qsTr("Добавить новую деталь")
            width: (parent.width / 3)
            height: parent.height
            onClicked: manager.addName("")
        }
        Button {
            id: button2
            text: qsTr("Удалить деталь")
            width: (parent.width / 3)
            height: parent.height
            onClicked: {
                console.log("removing " + manager.name_list[focusedItemIndex] + " on index " + focusedItemIndex)
                manager.removeName(manager.name_list[focusedItemIndex])
            }
        }
    }

    // ScrollView is needed
    /*ScrollView {
        anchors.top: row.bottom
        //anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        //contentHeight: columnLayout1.height
        //ScrollBar.vertical.policy: ScrollBar.AlwaysOn
        contentWidth: columnLayout1.implicitWidth    // The important part
        contentHeight: columnLayout1.implicitHeight  // Same
        */
        ColumnLayout {
            id: columnLayout1
            anchors.fill: parent
            //spacing: 20
            visible: true
            Layout.fillHeight: true
            Layout.fillWidth: true

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
                    Layout.preferredHeight: manager.config.graphics.unit_height * .5
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
                                focusedItemIndex = index
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
    //}

    Rectangle {
        id: bottom
        height: manager.config["graphics"]["unit_height"]
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
                console.log("manager.name_list.length: " + manager.name_list.length)
                if (manager.name_list.length > 1) {
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
