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
    property int number: 0
    
    Row {
        id: row
        height: 50
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        Button {
            id: button0
            text: qsTr("Загрузить список деталей")
            width: (parent.width / 3)
            height: 50
            onClicked: listDialog.open()
        }
        Button {
            id: button1
            text: qsTr("Добавить деталь")
            width: (parent.width / 3)
            height: 50
            onClicked: {
                listModel.append({idshnik: "TextEditor " + (++number)})

            }
        }
        Button {
            id: button2
            text: qsTr("Удалить деталь")
            width: (parent.width / 3)
            height: 50
            onClicked: {
                if (number != 0) {
                    listModel.remove(--number)
                    textIndex.text = ""
                }
            }
        }
    }

    ListView {
        id: listView1
        anchors.top: row.bottom
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right

        delegate: Item {
            id: item
            anchors.left: parent.left
            anchors.right: parent.right
            height: 40
            TextField {
                anchors.fill: parent
                anchors.margins: 3
                height: 20
                Keys.onReturnPressed: {
                    listModel.append({idshnik: "Button " + (++number)})
                    textIndex.text = index

                }

            }
        }

        model: ListModel {
            id: listModel
        }
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
