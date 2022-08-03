import QtQuick 2.12
import QtQuick.Window 2.12
import QtQuick.Controls 2.0
import QtQuick.Dialogs 1.2
import QtQml 2.0
// Попытка сделать главную страницу
/*
1) Изменить кнопку "назад" так, чтобы не открывалось новое окно
2) Добавить скрипт с камерой и соединить его со скриптом про список
*/
import QtQuick.Layouts 1.1

import "."


ApplicationWindow {
    id: mainrect
    //color: Constants.backgroundColor
    width: 480
    height: 640
    visible: true
    title: qsTr("Dataset generator")

    // temp array for 1st step
    property var firstStepArray: ['qwe', 'wer', 'ert']

    Loader {
        id: mainLoader
        visible: true
        source: "mainview.qml"
        anchors.fill: parent
        property int loader_prop_index
        onLoaded: console.log("page is loaded: ", source)
    }

    Connections {
        target: mainLoader.item
        ignoreUnknownSignals: true
        function onGotoStep1() {
            mainLoader.source = "step1list.qml"
        }
        function onGotoStep2() {
            //mainLoader.source = "EditCamera.qml"
            console.log("page 2")
        }
        function onGotoStep3() {
            //mainLoader.source = "CameraOptions.qml"
            console.log("page 3")
        }
        function onGotoMainView() {
            mainLoader.source = "mainview.qml"
        }
        /*onLoadArray: {
            item.getArray(mainrect.firstStepArray)
        }*/
    }
}
