import QtQuick 2.12
import QtQuick.Window 2.12
import QtQuick.Controls 2.0
import QtQuick.Layouts 1.0
import QtQuick.Dialogs 1.2
import QtQml 2.0

import "."
/*
Цель: страница по внесению названий деталей
Сделано: добавляются новые поля ввода при нажатии на кнопку/EnterKey
+ удаляется последнее поле при нажатии на кнопку удаления
+ добавлена кнопка "Готово" и если список деталей не создан - появляется окно-подсказка при нажатии на нее
Доделать:
1) Перенос клика при создании нового поля (курсор в новом поле для ввода) + перемещение по клавишам "вверх-вниз"
2) Загрузка списка деталей вместо ввода по полям - как аналог ввода
*/
//ApplicationWindow {
//    visible: true
//    width: 640
//    height: 480
//    title: qsTr("Генерация наборов данных")
Item {
    anchors.fill: parent
    visible: true

    id: step1list

    signal gotoMainView()

    /* Number created buttons for her visual identification of the demonstration project
     */
    property int number: 0

    /* The string field that displays dynamically pressed the button index button
     * to create dynamic buttons, and a button to delete the index of dynamic buttons
     * */
    /*QtObject {
        id: d
        property int itemHeight: root.height > root.width ? root.width / 10 : root.height / 10
        property int buttonHeight: 0.8 * itemHeight
        property int margins: 5
    }*/
    Row {
        id: row
        // Set line size and nailed to the top of the application window
        height: 50
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        Button {
            id: button0
            text: qsTr("Загрузить список деталей")
            width: (parent.width / 3)
            height: 50
            onClicked: {

            }
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

        // Button to remove the dynamic texteditors
        Button {
            id: button2
            text: qsTr("Удалить деталь")
            width: (parent.width / 3)
            height: 50

            // Remove the last texteditor
            onClicked: {
                if (number != 0) {
                    listModel.remove(--number)
                    textIndex.text = ""
                }
            }
        }
    }

    // ListView to represent the data as a list
    ListView {
        id: listView1
        // We place it in the remainder of the application window
        anchors.top: row.bottom
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right

        /* in this property we specify the layout of the object
         * that will be displayed in the list as a list item
         * */
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
            width: (parent.width / 3)
            anchors.bottom: parent.bottom
            anchors.horizontalCenter: parent.horizontalCenter
            height: 50


            // Remove the last texteditor
            onClicked: {
                if (number != 0) {
                        loader.setSource("main.qml")
                        /*button1.visible = true
                        button2.visible = true
                        button3.visible = true*/
                    } else {
                    messagedialog.visible = true
                }
            }
        }
        Button {
            id: button4
            text: qsTr("Назад")
            width: (parent.width / 6)
            anchors.margins: 10
          //  anchors.bottom: parent.bottom
            anchors.right: parent.right
            height: 0.6 * button3.height
            anchors.verticalCenter: button3.verticalCenter
            // Remove the last texteditor
            onClicked: {
                step1list.gotoMainView()
            }
        }
        Loader {
            id: nextloader
            anchors.fill: parent
        }

        MessageDialog {
            id: messagedialog
            title: "Ошибка заполнения"
            text: "Добавьте названия деталей. Воспользуйтесь кнопкой \"Добавить деталь\" и введите название детали в появившееся поле."
        }
    }
}

